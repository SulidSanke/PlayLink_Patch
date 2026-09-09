#!/usr/bin/env python3
"""Patch libil2cpp.so so FakeNatCam sees character-select selfie UI.

Writes little-endian int32 values:

  playlink_stage        ← PartyGameSetupController.RecordProfileCreationStageChanged
                          (CHARACTER_SELECT_TAKING_PHOTO = 5)

  playlink_avatar_stage ← ProfileAvatarPortraitPhotoAreaView.RefreshView
                          (eProfileAvatarScreenStage.PHOTO_TAKING = 2)

Rematch / continue often skips profile-creation stage 5 but still refreshes
the avatar photo UI with PHOTO_TAKING — that is the rematch gate.
"""
from __future__ import annotations

import struct
from pathlib import Path

GOT_OPEN = 0x16CB1C8
GOT_WRITE = 0x16CB6E0
GOT_CLOSE = 0x16CB158

# Must stay within RX LOAD file gap before 0x152d000
CAVE_BASE = 0x152C650
LOAD1_FILE_OFF = 0x152D000


def u32(x: int) -> bytes:
    return struct.pack("<I", x & 0xFFFFFFFF)


def stp_pre(rt: int, rt2: int, rn: int, imm_bytes: int) -> int:
    imm7 = (imm_bytes // 8) & 0x7F
    return 0xA9800000 | (imm7 << 15) | (rt2 << 10) | (rn << 5) | rt


def stp_so(rt: int, rt2: int, rn: int, imm_bytes: int) -> int:
    imm7 = (imm_bytes // 8) & 0x7F
    return 0xA9000000 | (imm7 << 15) | (rt2 << 10) | (rn << 5) | rt


def ldp_so(rt: int, rt2: int, rn: int, imm_bytes: int) -> int:
    imm7 = (imm_bytes // 8) & 0x7F
    return 0xA9400000 | (imm7 << 15) | (rt2 << 10) | (rn << 5) | rt


def ldp_post(rt: int, rt2: int, rn: int, imm_bytes: int) -> int:
    imm7 = (imm_bytes // 8) & 0x7F
    return 0xA8C00000 | (imm7 << 15) | (rt2 << 10) | (rn << 5) | rt


def str_w(rt: int, rn: int, byte_off: int) -> int:
    return 0xB9000000 | ((byte_off // 4) << 10) | (rn << 5) | rt


def ldr_w(rt: int, rn: int, byte_off: int) -> int:
    return 0xB9400000 | ((byte_off // 4) << 10) | (rn << 5) | rt


def adrp(rd: int, pc: int, target: int) -> int:
    imm = ((target & ~0xFFF) - (pc & ~0xFFF)) >> 12
    if imm < -(1 << 20) or imm >= (1 << 20):
        raise ValueError(f"ADRP out of range: {imm}")
    return 0x90000000 | ((imm & 3) << 29) | (((imm >> 2) & 0x7FFFF) << 5) | rd


def ldr_x_uoff(rt: int, rn: int, byte_off: int) -> int:
    return 0xF9400000 | ((byte_off // 8) << 10) | (rn << 5) | rt


def add_imm(rd: int, rn: int, imm: int) -> int:
    return 0x91000000 | (imm << 10) | (rn << 5) | rd


def adr(rd: int, pc: int, target: int) -> int:
    imm = target - pc
    if imm < 0 or imm >= (1 << 20):
        raise ValueError(f"ADR out of range: {imm}")
    return 0x10000000 | ((imm & 3) << 29) | (((imm >> 2) & 0x7FFFF) << 5) | rd


def movz_w(rd: int, imm16: int) -> int:
    return 0x52800000 | ((imm16 & 0xFFFF) << 5) | rd


def b_off(pc: int, target: int) -> int:
    return 0x14000000 | (((target - pc) // 4) & 0x3FFFFFF)


def tbnz_w(rt: int, bit: int, pc: int, target: int) -> int:
    return 0x37000000 | (bit << 19) | ((((target - pc) // 4) & 0x3FFF) << 5) | rt


def build_write_cave(cave_va: int, path: bytes, orig_first: int, cont_va: int) -> bytes:
    """Trampoline: save regs, write w1 as int32 to path, restore, orig insn, b cont."""
    path_off = 0xC0
    path_va = cave_va + path_off
    code: list[int] = []
    sp = 31

    def pc() -> int:
        return cave_va + 4 * len(code)

    code.append(stp_pre(0, 1, sp, -0x60))
    code.append(stp_so(2, 3, sp, 0x10))
    code.append(stp_so(4, 5, sp, 0x20))
    code.append(stp_so(6, 7, sp, 0x30))
    code.append(stp_so(8, 30, sp, 0x40))
    code.append(str_w(1, sp, 0x50))

    code.append(adr(0, pc(), path_va))
    code.append(movz_w(1, 0x241))  # O_WRONLY|O_CREAT|O_TRUNC
    code.append(movz_w(2, 0x180))  # 0600
    code.append(adrp(16, pc(), GOT_OPEN))
    code.append(ldr_x_uoff(16, 16, GOT_OPEN & 0xFFF))
    code.append(0xD63F0200)

    tbnz_i = len(code)
    code.append(0)

    code.append(str_w(0, sp, 0x54))
    code.append(ldr_w(0, sp, 0x54))
    code.append(add_imm(1, sp, 0x50))
    code.append(movz_w(2, 4))
    code.append(adrp(16, pc(), GOT_WRITE))
    code.append(ldr_x_uoff(16, 16, GOT_WRITE & 0xFFF))
    code.append(0xD63F0200)

    code.append(ldr_w(0, sp, 0x54))
    code.append(adrp(16, pc(), GOT_CLOSE))
    code.append(ldr_x_uoff(16, 16, GOT_CLOSE & 0xFFF))
    code.append(0xD63F0200)

    restore_pc = pc()
    code[tbnz_i] = tbnz_w(0, 31, cave_va + 4 * tbnz_i, restore_pc)

    code.append(ldp_so(8, 30, sp, 0x40))
    code.append(ldp_so(6, 7, sp, 0x30))
    code.append(ldp_so(4, 5, sp, 0x20))
    code.append(ldp_so(2, 3, sp, 0x10))
    code.append(ldp_post(0, 1, sp, 0x60))
    code.append(orig_first)
    code.append(b_off(pc(), cont_va))

    raw = b"".join(u32(w) for w in code)
    if len(raw) > path_off:
        raise SystemExit(f"cave too large: {len(raw)}")
    raw = raw + bytes(path_off - len(raw)) + path
    if len(raw) % 16:
        raw += bytes(16 - (len(raw) % 16))
    return raw


HOOKS = [
    {
        "name": "RecordProfileCreationStageChanged",
        "va": 0x7063DC,
        "orig": 0xA9BE4FF4,  # stp x20, x19, [sp, #-0x20]!
        "path": b"/data/data/com.playstation.kipdecades/playlink_stage\0",
        "cave": CAVE_BASE,
    },
    {
        "name": "ProfileAvatarPortraitPhotoAreaView.RefreshView",
        "va": 0x5A39A4,
        "orig": 0xA9BC5FF8,  # stp x24, x23, [sp, #-0x40]!
        "path": b"/data/data/com.playstation.kipdecades/playlink_avatar_stage\0",
        "cave": CAVE_BASE + 0x100,
    },
]


def patch_elf(data: bytearray) -> None:
    e_phoff = struct.unpack_from("<Q", data, 32)[0]
    e_phentsize = struct.unpack_from("<H", data, 54)[0]
    e_phnum = struct.unpack_from("<H", data, 56)[0]

    built = []
    for h in HOOKS:
        cave = build_write_cave(h["cave"], h["path"], h["orig"], h["va"] + 4)
        built.append((h, cave))

    end_needed = max(h["cave"] + len(cave) for h, cave in built)

    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        p_type, p_flags = struct.unpack_from("<II", data, off)
        p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from(
            "<QQQQQQ", data, off + 8
        )
        if p_type == 1 and p_flags == 5:
            if end_needed > p_offset + p_filesz:
                new_sz = end_needed - p_offset
                if p_offset + new_sz > LOAD1_FILE_OFF:
                    raise SystemExit("caves overflow into next LOAD")
                struct.pack_into("<QQ", data, off + 8 + 24, new_sz, max(p_memsz, new_sz))
                print(f"  extended RX LOAD filesz/memsz to 0x{new_sz:x}")
            break
    else:
        raise SystemExit("RX LOAD not found")

    if len(data) < LOAD1_FILE_OFF:
        raise SystemExit("unexpected libil2cpp layout")

    for h, cave in built:
        data[h["cave"] : h["cave"] + len(cave)] = cave
        hook = b_off(h["va"], h["cave"])
        cur = struct.unpack_from("<I", data, h["va"])[0]
        if cur == h["orig"]:
            struct.pack_into("<I", data, h["va"], hook)
            print(f"  hooked {h['name']} @ 0x{h['va']:x} -> cave 0x{h['cave']:x}")
        elif cur == hook:
            print(f"  {h['name']} already hooked")
        else:
            raise SystemExit(f"{h['name']}: unexpected insn {cur:08x}")


def patch_file(path: Path) -> None:
    data = bytearray(path.read_bytes())
    patch_elf(data)
    path.write_bytes(data)
    print(f"  patched {path}")


def patch_apk_lib(decoded_apk: Path) -> bool:
    lib = decoded_apk / "lib" / "arm64-v8a" / "libil2cpp.so"
    if not lib.exists():
        print("  no arm64 libil2cpp.so — skip profile-stage gate")
        return False
    blob = lib.read_bytes()
    marker = b"playlink_avatar_stage"
    h0 = HOOKS[0]
    hook0 = b_off(h0["va"], h0["cave"])
    if marker in blob and struct.unpack_from("<I", blob, h0["va"])[0] == hook0:
        # ensure second hook present too
        h1 = HOOKS[1]
        hook1 = b_off(h1["va"], h1["cave"])
        if struct.unpack_from("<I", blob, h1["va"])[0] == hook1:
            print("  profile/avatar stage gates already in libil2cpp.so")
            return True
    patch_file(lib)
    return True


if __name__ == "__main__":
    import sys

    target = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path(__file__).resolve().parent / "tools" / "il2cpp_dump" / "libil2cpp.so"
    )
    if "il2cpp_dump" in str(target) and target.name == "libil2cpp.so":
        out = target.with_name("libil2cpp.patched.so")
        out.write_bytes(target.read_bytes())
        patch_file(out)
    else:
        patch_file(target)
