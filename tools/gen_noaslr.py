#!/usr/bin/env python3
"""Minimal aarch64 static PIE: disable ASLR then execvp(argv[1], argv+1)."""
from __future__ import annotations

import struct
from pathlib import Path

OUT = Path(__file__).resolve().parent / "libnoaslr.so"


def pack_ins(words: list[int]) -> bytes:
    return b"".join(struct.pack("<I", w) for w in words)


def adr(rd: int, byte_off: int) -> int:
    """ADR Xd, #byte_off (from this instruction). byte_off must be 0..1MB."""
    immlo = byte_off & 3
    immhi = (byte_off >> 2) & 0x7FFFF
    return 0x10000000 | (immlo << 29) | (immhi << 5) | rd


def main() -> None:
    # Stack at _start: [argc][argv...][NULL][envp...][NULL][auxv]
    # envp = sp + 16 + 8*argc. SP cannot be Rn of ADD-shifted, so copy first.
    fail = 18
    code = [
        0xF94003E9,  # 0  ldr x9, [sp]
        0xF100093F,  # 1  cmp x9, #2
        0x00000000,  # 2  b.lt fail
        0x92800000,  # 3  movn x0, #0
        0xD2800B88,  # 4  mov x8, #92 personality
        0xD4000001,  # 5  svc #0
        0x52800081,  # 6  mov w1, #4
        0x53103C21,  # 7  lsl w1, w1, #16   ADDR_NO_RANDOMIZE
        0xAA010000,  # 8  orr x0, x0, x1
        0xD2800B88,  # 9  mov x8, #92
        0xD4000001,  # 10 svc #0
        0xF9400BE0,  # 11 ldr x0, [sp, #16] pathname = argv[1]
        0x910043E1,  # 12 add x1, sp, #16   argv = &argv[1]
        0x910003E2,  # 13 add x2, sp, #0
        0x8B090C42,  # 14 add x2, x2, x9, lsl #3
        0x91004042,  # 15 add x2, x2, #16   envp
        0xD2801BA8,  # 16 mov x8, #221 execve
        0xD4000001,  # 17 svc #0
        0xD2800FE0,  # 18 fail: mov x0, #127
        0xD2800BA8,  # 19 mov x8, #93 exit
        0xD4000001,  # 20 svc #0
    ]
    code[2] = 0x54000000 | (((fail - 2) & 0x7FFFF) << 5) | 0xB
    text = pack_ins(code)

    ehsize, phentsize = 64, 56
    headers = ehsize + phentsize
    entry = headers
    total = headers + len(text)

    ehdr = struct.pack(
        "<16sHHIQQQIHHHHHH",
        b"\x7fELF" + bytes([2, 1, 1, 0]) + bytes(8),
        3,
        183,
        1,
        entry,
        64,
        0,
        0,
        ehsize,
        phentsize,
        1,
        0,
        0,
        0,
    )
    phdr = struct.pack(
        "<IIQQQQQQ",
        1,
        5,
        0,
        0,
        0,
        total,
        total,
        0x10000,
    )
    elf = ehdr + phdr + text
    OUT.write_bytes(elf)
    print("wrote", OUT, len(elf), "bytes")


if __name__ == "__main__":
    main()
