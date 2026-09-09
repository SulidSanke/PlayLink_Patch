#!/usr/bin/env python3
"""Compile FakeNatCam.java to smali under tools/fake_natcam/smali_out."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SDK = Path.home() / "AppData/Local/Android/Sdk"
ANDROID_JAR = SDK / "platforms" / "android-35" / "android.jar"
if not ANDROID_JAR.exists():
    ANDROID_JAR = SDK / "platforms" / "android-36" / "android.jar"
BUILD_TOOLS = sorted((SDK / "build-tools").glob("*"), reverse=True)[0]
D8 = BUILD_TOOLS / "d8.bat"
APKTOOL = ROOT / "tools" / "apktool.jar"


def main() -> None:
    if not ANDROID_JAR.exists():
        raise SystemExit(f"missing android.jar: {ANDROID_JAR}")
    if not D8.exists():
        raise SystemExit(f"missing d8: {D8}")

    src = HERE / "src"
    stubs = HERE / "stubs"
    classes = HERE / "classes"
    dexdir = HERE / "dex"
    smali_out = HERE / "smali_out"
    for p in (classes, dexdir, smali_out):
        if p.exists():
            shutil.rmtree(p)
        p.mkdir(parents=True)

    java_files = list(src.rglob("*.java")) + list(stubs.rglob("*.java"))
    subprocess.run(
        [
            "javac",
            "-encoding",
            "UTF-8",
            "--release",
            "17",
            "-classpath",
            str(ANDROID_JAR),
            "-d",
            str(classes),
            *[str(f) for f in java_files],
        ],
        check=True,
    )

    # Only package our FakeNatCam (not the stubs) into the dex.
    playlink_classes = list((classes / "com" / "playstation" / "playlink").rglob("*.class"))
    subprocess.run(
        [str(D8), "--lib", str(ANDROID_JAR), "--output", str(dexdir), *[str(c) for c in playlink_classes]],
        check=True,
        shell=False,
    )

    dex = dexdir / "classes.dex"
    baksmali = ROOT / "tools" / "baksmali.jar"
    if not baksmali.exists():
        raise SystemExit(f"missing {baksmali}")
    subprocess.run(
        ["java", "-jar", str(baksmali), "d", str(dex), "-o", str(smali_out)],
        check=True,
    )
    print(f"Wrote smali to {smali_out}")
    for p in sorted(smali_out.rglob("*.smali")):
        print(" ", p.relative_to(smali_out))


if __name__ == "__main__":
    main()
