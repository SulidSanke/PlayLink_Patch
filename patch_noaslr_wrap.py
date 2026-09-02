#!/usr/bin/env python3
"""Add wrap.sh + no-ASLR helper to Unity PlayLink APKs and rebuild."""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from lxml import etree

from patch_playlink import (
    ANDROID,
    OUT,
    ROOT,
    TOOLS,
    WORK,
    build_and_sign,
    q,
    restore_original_libs,
)

WRAP_SH = """#!/system/bin/sh
log -p i -t playlink-wrap "invoked argc=$#"
HERE="$(cd "$(dirname "$0")" && pwd)"
HELPER="$HERE/libnoaslr.so"
chmod 755 "$HELPER" 2>/dev/null
if [ -x "$HELPER" ]; then
  log -p i -t playlink-wrap "exec helper $HELPER"
  exec "$HELPER" "$@"
fi
log -p i -t playlink-wrap "helper missing, passthrough"
exec "$@"
"""

APKS = [
    ROOT / "KiP 1.5A.apk",
    ROOT / "KiP Decades 1.4.apk",
]


def store_wrap_uncompressed(apk: Path, out_dir: Path | None = None) -> Path:
    """apktool/aapt2 compress wrap.sh; Android ignores compressed wrap scripts."""
    dest = out_dir or apk.parent
    tmp = dest / (apk.stem + "-wrapstored.apk")
    keep = {"lib/arm64-v8a/wrap.sh", "lib/arm64-v8a/libnoaslr.so"}
    if tmp.exists():
        tmp.unlink()
    with zipfile.ZipFile(apk, "r") as zin, zipfile.ZipFile(tmp, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename in keep:
                info = zipfile.ZipInfo(filename=item.filename, date_time=item.date_time)
                info.compress_type = zipfile.ZIP_STORED
                info.create_system = item.create_system
                info.external_attr = item.external_attr
                zout.writestr(info, data)
            else:
                zout.writestr(item, data)
    import subprocess

    cmd = [
        "java",
        "-jar",
        str(TOOLS / "uber-apk-signer.jar"),
        "--apks",
        str(tmp),
        "--out",
        str(dest),
        "--allowResign",
    ]
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True)
    signed = max(
        (p for p in dest.glob("*.apk") if tmp.stem in p.name and "signed" in p.name.lower()),
        key=lambda p: p.stat().st_mtime,
    )
    final = apk
    if signed != final:
        if final.exists():
            final.unlink()
        signed.replace(final)
    tmp.unlink(missing_ok=True)
    leftover = dest / f"{tmp.stem}-aligned-debugSigned.apk"
    leftover.unlink(missing_ok=True)
    print("STORED wrap.sh in", final)
    return final


def add_wrap(decoded: Path) -> None:
    lib = decoded / "lib" / "arm64-v8a"
    lib.mkdir(parents=True, exist_ok=True)
    helper = TOOLS / "libnoaslr.so"
    if not helper.exists():
        raise SystemExit("Run tools/gen_noaslr.py first")
    shutil.copy2(helper, lib / "libnoaslr.so")
    (lib / "wrap.sh").write_bytes(WRAP_SH.encode("ascii").replace(b"\r\n", b"\n"))
    print("Wrote wrap.sh + libnoaslr.so in", lib)

    etree.register_namespace("android", ANDROID)
    manifest_path = decoded / "AndroidManifest.xml"
    tree = etree.parse(str(manifest_path))
    application = tree.getroot().find("application")
    if application is None:
        raise SystemExit("No <application>")
    application.set(q("debuggable"), "true")
    application.set(q("extractNativeLibs"), "true")
    tree.write(str(manifest_path), encoding="utf-8", xml_declaration=True, standalone=False)

    yml_path = decoded / "apktool.yml"
    text = yml_path.read_text(encoding="utf-8")
    if "wrap.sh" not in text:
        text = text.replace("doNotCompress:\n", "doNotCompress:\n- wrap.sh\n", 1)
        yml_path.write_text(text, encoding="utf-8")


def main() -> None:
    for apk in APKS:
        print("=" * 70)
        print("Wrapping", apk.name)
        decoded = WORK / apk.stem
        if not decoded.exists():
            raise SystemExit(f"Missing decoded tree: {decoded}")
        (decoded / "lib").mkdir(exist_ok=True)
        restore_original_libs(decoded, apk)
        add_wrap(decoded)
        signed = build_and_sign(decoded, apk)
        store_wrap_uncompressed(signed)


if __name__ == "__main__":
    main()
