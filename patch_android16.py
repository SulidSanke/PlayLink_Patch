#!/usr/bin/env python3
"""One-click PlayLink companion patcher for Android 16.

Put official APKs in originals/, run patch.bat. Does not ship Sony APKs.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import patch_playlink as pl

pl.ROOT = HERE
pl.TOOLS = HERE / "tools"
pl.WORK = HERE / "work-patch"
pl.OUT = HERE / "out"

from patch_noaslr_wrap import add_wrap, store_wrap_uncompressed
from patch_playlink import apktool, build_and_sign, patch_manifest, restore_original_libs

ORIGINALS = HERE / "originals"
OUT = HERE / "out"
WORK = HERE / "work-patch"

SKIP_NAME = ("-android16", "debugsigned", "wrapstored")


def ensure_lxml() -> None:
    try:
        import lxml  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "lxml", "-q"], check=True)


def is_unity(apk: Path) -> bool:
    with zipfile.ZipFile(apk) as z:
        return any(name.endswith("libil2cpp.so") for name in z.namelist())


def find_apks() -> list[Path]:
    ORIGINALS.mkdir(exist_ok=True)
    found: list[Path] = []
    for folder in (ORIGINALS, HERE):
        for apk in folder.glob("*.apk"):
            lower = apk.name.lower()
            if any(s in lower for s in SKIP_NAME):
                continue
            if apk.resolve() in {p.resolve() for p in found}:
                continue
            found.append(apk)
    found.sort(key=lambda p: p.name.lower())
    return found


def patch_one(apk: Path) -> Path:
    dest = WORK / apk.stem
    if dest.exists():
        shutil.rmtree(dest)
    apktool("d", "-f", "-s", "-o", str(dest), str(apk))
    patch_manifest(dest)
    unity = is_unity(apk)
    if unity:
        restore_original_libs(dest, apk)
        add_wrap(dest)
    signed = build_and_sign(dest, apk, OUT)
    if unity:
        signed = store_wrap_uncompressed(signed, OUT)
    for junk in OUT.glob("*.idsig"):
        junk.unlink(missing_ok=True)
    for junk in OUT.glob("*wrapstored*"):
        junk.unlink(missing_ok=True)
    return signed


def main() -> None:
    ensure_lxml()
    if not (HERE / "tools" / "apktool.jar").exists():
        raise SystemExit("Brak tools/apktool.jar")
    if not (HERE / "tools" / "uber-apk-signer.jar").exists():
        raise SystemExit("Brak tools/uber-apk-signer.jar")
    helper = HERE / "tools" / "libnoaslr.so"
    if not helper.exists():
        subprocess.run([sys.executable, str(HERE / "tools" / "gen_noaslr.py")], check=True)

    apks = find_apks()
    if not apks:
        print("Nie znaleziono oryginalnych APK.")
        print()
        print(f"Wrzuc pliki do:\n  {ORIGINALS}")
        print()
        print("Szukane gry: Hidden Agenda, That's You!, Knowledge is Power, KiP Decades")
        print("Nie wkladaj tu gotowych *-android16.apk — tylko oryginaly.")
        raise SystemExit(1)

    WORK.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    built: list[Path] = []
    for apk in apks:
        print("=" * 70)
        print("Patch", apk.name, "(Unity wrap)" if is_unity(apk) else "(UE4/manifest)")
        built.append(patch_one(apk))

    print("=" * 70)
    print("Gotowe. Zainstaluj z:")
    print(f"  {OUT}")
    for path in built:
        print(f"  - {path.name}")


if __name__ == "__main__":
    main()
