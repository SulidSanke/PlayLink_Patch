#!/usr/bin/env python3
"""Patch PlayLink companion APK manifests for modern Android."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parent
TOOLS = ROOT / "tools"
WORK = ROOT / "work"
OUT = ROOT / "patched"
ANDROID = "http://schemas.android.com/apk/res/android"
NS = {"android": ANDROID}

BROKEN = [
    ROOT / "Hidden Agenda 1.07.apk",
    ROOT / "KiP 1.5A.apk",
    ROOT / "KiP Decades 1.4.apk",
]


def q(name: str) -> str:
    return f"{{{ANDROID}}}{name}"


def apktool(*args: str) -> None:
    cmd = ["java", "-jar", str(TOOLS / "apktool.jar"), *args]
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True)


def decode(apk: Path) -> Path:
    dest = WORK / apk.stem
    if dest.exists():
        shutil.rmtree(dest)
    apktool("d", "-f", "-s", "-o", str(dest), str(apk))
    return dest


def ensure_permission(manifest: etree._Element, name: str, extra: dict[str, str] | None = None) -> None:
    for perm in manifest.findall("uses-permission"):
        if perm.get(q("name")) == name:
            if extra:
                for k, v in extra.items():
                    perm.set(q(k), v)
            return
    perm = etree.Element("uses-permission")
    perm.set(q("name"), name)
    if extra:
        for k, v in extra.items():
            perm.set(q(k), v)
    sdk = manifest.find("uses-sdk")
    insert_at = list(manifest).index(sdk) + 1 if sdk is not None else 0
    manifest.insert(insert_at, perm)


def set_exported_on_intent_activities(application: etree._Element) -> None:
    for activity in application.findall("activity"):
        if activity.find("intent-filter") is not None and activity.get(q("exported")) is None:
            activity.set(q("exported"), "true")
    for receiver in application.findall("receiver"):
        if receiver.find("intent-filter") is not None and receiver.get(q("exported")) is None:
            receiver.set(q("exported"), "true")
    for service in application.findall("service"):
        if service.find("intent-filter") is not None and service.get(q("exported")) is None:
            service.set(q("exported"), "true")


def patch_manifest(decoded: Path) -> None:
    etree.register_namespace("android", ANDROID)
    manifest_path = decoded / "AndroidManifest.xml"
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(manifest_path), parser)
    manifest = tree.getroot()

    pkg = manifest.get("package", "")
    sdk = manifest.find("uses-sdk")
    if sdk is None:
        sdk = etree.Element("uses-sdk")
        sdk.set(q("minSdkVersion"), "21")
        manifest.insert(0, sdk)
    sdk.set(q("targetSdkVersion"), "28")
    if not sdk.get(q("minSdkVersion")):
        sdk.set(q("minSdkVersion"), "21")

    ensure_permission(manifest, "android.permission.CHANGE_WIFI_MULTICAST_STATE")
    ensure_permission(manifest, "android.permission.ACCESS_WIFI_STATE")
    ensure_permission(manifest, "android.permission.INTERNET")
    ensure_permission(
        manifest,
        "android.permission.NEARBY_WIFI_DEVICES",
        extra={"usesPermissionFlags": "neverForLocation"},
    )

    application = manifest.find("application")
    if application is None:
        raise SystemExit(f"No <application> in {manifest_path}")

    application.set(q("usesCleartextTraffic"), "true")
    application.set(q("extractNativeLibs"), "true")
    application.set(q("requestLegacyExternalStorage"), "true")
    application.set(q("preserveLegacyExternalStorage"), "true")
    # Android 16: run 4KB-era native code on 16KB kernels without the warning dialog.
    # Integer 1 = enabled. The string "enabled" compiled to a bogus value with old aapt2.
    application.set(q("pageSizeCompat"), "enabled")

    has_apache = False
    for lib in application.findall("uses-library"):
        if lib.get(q("name")) == "org.apache.http.legacy":
            has_apache = True
            break
    if not has_apache:
        lib = etree.SubElement(application, "uses-library")
        lib.set(q("name"), "org.apache.http.legacy")
        lib.set(q("required"), "false")

    set_exported_on_intent_activities(application)

    # Hidden Agenda / UE4: data is already inside the APK as assets/main.obb.png.
    # Verifying/downloading Play Store OBB on a sideloaded app exits after splash.
    for meta in application.findall("meta-data"):
        name = meta.get(q("name"))
        if name == "com.epicgames.ue4.GameActivity.bVerifyOBBOnStartUp":
            meta.set(q("value"), "false")
        if name == "com.epicgames.ue4.GameActivity.bHasOBBFiles":
            meta.set(q("value"), "false")
        if name == "com.epicgames.ue4.GameActivity.bValidateTextureFormats":
            meta.set(q("value"), "false")

    tree.write(
        str(manifest_path),
        encoding="utf-8",
        xml_declaration=True,
        standalone=False,
    )
    yml_path = decoded / "apktool.yml"
    if yml_path.exists():
        text = yml_path.read_text(encoding="utf-8")
        text, n = re.subn(r"targetSdkVersion:\s*\d+", "targetSdkVersion: 28", text)
        yml_path.write_text(text, encoding="utf-8")
        if n:
            print("Patched apktool.yml targetSdkVersion -> 28")

    print(f"Patched manifest for {pkg}")


def restore_original_libs(decoded: Path, apk: Path) -> None:
    """Keep stock native libs so Android 16 can apply 16KB backcompat mode."""
    import zipfile

    lib_dir = decoded / "lib"
    if not lib_dir.exists():
        return
    with zipfile.ZipFile(apk) as z:
        for name in z.namelist():
            if name.startswith("lib/") and name.endswith(".so"):
                dest = decoded / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(z.read(name))
                print("  restored", name)


def build_and_sign(decoded: Path, apk: Path, out_dir: Path | None = None) -> Path:
    built_dir = decoded / "dist"
    apktool("b", str(decoded))
    unsigned = next(built_dir.glob("*.apk"))
    dest = out_dir or OUT
    dest.mkdir(exist_ok=True)
    cmd = [
        "java",
        "-jar",
        str(TOOLS / "uber-apk-signer.jar"),
        "--apks",
        str(unsigned),
        "--out",
        str(dest),
        "--allowResign",
    ]
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True)
    signed = [
        p
        for p in dest.glob("*.apk")
        if unsigned.stem in p.name and "signed" in p.name.lower()
    ]
    if not signed:
        raise SystemExit(f"Signed APK not found for {apk.name}")
    final = dest / f"{apk.stem}-android16.apk"
    chosen = max(signed, key=lambda p: p.stat().st_mtime)
    if chosen != final:
        if final.exists():
            final.unlink()
        chosen.replace(final)
    print("SIGNED:", final)
    return final


def main() -> None:
    WORK.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    for apk in BROKEN:
        print("=" * 70)
        print("Processing", apk.name)
        decoded = decode(apk)
        patch_manifest(decoded)
        build_and_sign(decoded, apk)


if __name__ == "__main__":
    try:
        from lxml import etree  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "lxml", "-q"], check=True)
    main()
