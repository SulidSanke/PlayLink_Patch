#!/usr/bin/env python3
"""Skip UnityDefaultAllocator's fatal >16GB abort without rewriting pointer math.

Old Unity aborts when it thinks a pointer lives above 4GB. On modern Android,
camera/HAL buffers and tagged pointers trip that check (KiP Decades finale).

Changing the earlier LSR/CBZ guard corrupts Scudo bookkeeping on startup. Instead
we only force the branch that skips the "Using memoryadresses from more that
16GB of memory" fatal path, leaving normal allocator logic intact.
"""
from __future__ import annotations

import struct
from pathlib import Path

MSG = b"Using memoryadresses from more that 16GB of memory"


def _decode_adrp(word: int, pc: int) -> tuple[int, int] | None:
    if (word & 0x9F000000) != 0x90000000:
        return None
    rd = word & 0x1F
    immlo = (word >> 29) & 3
    immhi = (word >> 5) & 0x7FFFF
    imm = (immhi << 2) | immlo
    if imm & (1 << 20):
        imm -= 1 << 21
    return rd, (pc & ~0xFFF) + (imm << 12)


def _decode_add_imm(word: int) -> tuple[int, int, int] | None:
    if (word & 0xFF800000) != 0x91000000:
        return None
    rd = word & 0x1F
    rn = (word >> 5) & 0x1F
    imm12 = (word >> 10) & 0xFFF
    if (word >> 22) & 1:
        imm12 <<= 12
    return rd, rn, imm12


def _string_code_sites(data: bytes, msg_off: int) -> list[int]:
    page = msg_off & ~0xFFF
    off = msg_off & 0xFFF
    sites: list[int] = []
    for i in range(0, len(data) - 8, 4):
        word = struct.unpack_from("<I", data, i)[0]
        adrp = _decode_adrp(word, i)
        if not adrp or adrp[1] != page:
            continue
        rd = adrp[0]
        for j in range(1, 8):
            add = _decode_add_imm(struct.unpack_from("<I", data, i + 4 * j)[0])
            if add and add[1] == rd and add[2] == off:
                sites.append(i)
                break
    return sites


def patch_libunity_bytes(data: bytearray) -> int:
    msg_off = data.find(MSG)
    if msg_off < 0:
        return 0
    sites = _string_code_sites(data, msg_off)
    if not sites:
        return 0

    patched = 0
    for site in sites:
        # Expected: CMP Wn,#1 ; B.NE <skip> ; ADRP ... string
        if site < 8:
            continue
        cmp_w = struct.unpack_from("<I", data, site - 8)[0]
        bne = struct.unpack_from("<I", data, site - 4)[0]
        # CMP Wn, #1  => SUBS/ADDS-style compare with Rd=WZR and imm=1
        if (cmp_w & 0xFFFFFC1F) != 0x3100041F:
            continue
        # B.cond: 0x54xxxxxx, cond in low nibble; NE=1
        if (bne & 0xFF000010) != 0x54000000 or (bne & 0xF) != 1:
            continue
        imm19 = (bne >> 5) & 0x7FFFF
        branch = 0x14000000 | (imm19 & 0x03FFFFFF)
        if bne == branch:
            continue
        struct.pack_into("<I", data, site - 4, branch)
        patched += 1
    return patched


def patch_unity_highmem(decoded: Path) -> None:
    libs = sorted(decoded.glob("lib/*/libunity.so"))
    if not libs:
        print("  warn: libunity.so not found; skipping high-mem patch")
        return
    for lib in libs:
        raw = bytearray(lib.read_bytes())
        n = patch_libunity_bytes(raw)
        if n:
            lib.write_bytes(raw)
            print(
                f"  patched Unity >16GB fatal skip in {lib.relative_to(decoded)} ({n} site(s))"
            )
        else:
            print(f"  warn: no Unity >16GB patch sites in {lib.relative_to(decoded)}")


if __name__ == "__main__":
    import sys
    import zipfile

    apk = Path(sys.argv[1])
    with zipfile.ZipFile(apk) as z:
        data = bytearray(z.read("lib/arm64-v8a/libunity.so"))
    print("patched", patch_libunity_bytes(data))
