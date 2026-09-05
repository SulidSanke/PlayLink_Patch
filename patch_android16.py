#!/usr/bin/env python3
"""One-click PlayLink companion patcher for Android 16.

Put official APKs in originals/, run patch.bat. Does not ship Sony APKs.
"""
from __future__ import annotations

import re
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

ONCREATE_RE = re.compile(
    r"^\.method [^\n]*onCreate\(Landroid/os/Bundle;\)V$",
    re.M,
)

JNIBRIDGE_INVOKE_SIGNATURE = (
    ".method public final invoke("
    "Ljava/lang/Object;"
    "Ljava/lang/reflect/Method;"
    "[Ljava/lang/Object;"
    ")Ljava/lang/Object;"
)
JNIBRIDGE_SHIM_LABEL = ":playlink_service_connection_normal"
JNIBRIDGE_PATCH_POINT = "    :cond_0\n"
JNIBRIDGE_NATIVE_INVOKE = (
    "Lbitter/jnibridge/JNIBridge;->invoke("
    "JLjava/lang/Class;Ljava/lang/reflect/Method;[Ljava/lang/Object;"
    ")Ljava/lang/Object;"
)
JNIBRIDGE_SERVICE_CONNECTION_SHIM = """    # Newer Android versions may dispatch a three-argument ServiceConnection
    # callback that legacy Unity's native JNIBridge cannot resolve. Redirect it
    # through the original two-argument callback understood by the game.
    invoke-virtual {p2}, Ljava/lang/reflect/Method;->getDeclaringClass()Ljava/lang/Class;

    move-result-object v0

    const-class v4, Landroid/content/ServiceConnection;

    if-ne v0, v4, :playlink_service_connection_normal

    invoke-virtual {p2}, Ljava/lang/reflect/Method;->getName()Ljava/lang/String;

    move-result-object v0

    const-string v4, "onServiceConnected"

    invoke-virtual {v4, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :playlink_service_connection_normal

    invoke-virtual {p2}, Ljava/lang/reflect/Method;->getParameterTypes()[Ljava/lang/Class;

    move-result-object v0

    array-length v0, v0

    const/4 v4, 0x3

    if-ne v0, v4, :playlink_service_connection_normal

    check-cast p1, Landroid/content/ServiceConnection;

    const/4 v0, 0x0

    aget-object v4, p3, v0

    check-cast v4, Landroid/content/ComponentName;

    const/4 v0, 0x1

    aget-object v5, p3, v0

    check-cast v5, Landroid/os/IBinder;

    invoke-interface {p1, v4, v5}, Landroid/content/ServiceConnection;->onServiceConnected(Landroid/content/ComponentName;Landroid/os/IBinder;)V

    const/4 v0, 0x0

    monitor-exit v1

    goto :goto_0

    :playlink_service_connection_normal
"""


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


def safe_stem(name: str) -> str:
    out = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_")
    return out or "app"


def launcher_activity(decoded: Path) -> str | None:
    text = (decoded / "AndroidManifest.xml").read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"<activity\b", text, flags=re.I)
    for block in blocks[1:]:
        if "android.intent.action.MAIN" in block and "android.intent.category.LAUNCHER" in block:
            m = re.search(r'android:name="([^"]+)"', block)
            if m:
                name = m.group(1)
                if name.startswith("."):
                    pkg = re.search(r'package="([^"]+)"', text)
                    if pkg:
                        name = pkg.group(1) + name
                return name
    return None


def _insert_mic_call(method: str, cls: str) -> str:
    # onCreate often uses .locals > 16, so p0 is v16+ and needs /range.
    call = f"    invoke-direct/range {{p0 .. p0}}, {cls}->playlinkEnsureMic()V\n"
    lines = method.splitlines(keepends=True)
    out: list[str] = []
    inserted = False
    for line in lines:
        out.append(line)
        if not inserted and "invoke-super" in line:
            out.append("\n" + call + "\n")
            inserted = True
    if not inserted:
        joined = "".join(out)
        if ".prologue" in joined:
            return joined.replace(".prologue\n", ".prologue\n\n" + call + "\n", 1)
        return call + joined
    return "".join(out)


def _append_mic_helper(text: str, cls: str) -> str:
    helper = f"""
.method private playlinkEnsureMic()V
    .locals 3

    const-string v0, "android.permission.RECORD_AUDIO"

    invoke-virtual {{p0, v0}}, {cls}->checkSelfPermission(Ljava/lang/String;)I

    move-result v1

    if-eqz v1, :need_mic

    return-void

    :need_mic
    const/4 v1, 0x1

    new-array v1, v1, [Ljava/lang/String;

    const/4 v2, 0x0

    aput-object v0, v1, v2

    const/16 v2, 0x7e7

    invoke-virtual {{p0, v1, v2}}, {cls}->requestPermissions([Ljava/lang/String;I)V

    return-void
.end method
"""
    stripped = text.rstrip()
    if stripped.endswith(".end class"):
        return stripped[: -len(".end class")].rstrip() + "\n" + helper + "\n.end class\n"
    return stripped + "\n" + helper + "\n"


def _inject_mic_simple(smali: Path, cls: str) -> None:
    text = smali.read_text(encoding="utf-8")
    if "playlinkEnsureMic()V" in text:
        return
    match = ONCREATE_RE.search(text)
    if match:
        idx = match.start()
        rest = text[idx:]
        end = rest.find("\n.end method")
        if end < 0:
            print("  warn: onCreate has no .end method in", smali.name)
            return
        method = rest[:end]
        text = text[:idx] + _insert_mic_call(method, cls) + rest[end:]
    else:
        super_m = re.search(r"^\.super (L[^;]+;)", text, re.M)
        parent = super_m.group(1) if super_m else "Landroid/app/Activity;"
        added = f"""
.method protected onCreate(Landroid/os/Bundle;)V
    .locals 1

    invoke-super {{p0, p1}}, {parent}->onCreate(Landroid/os/Bundle;)V

    invoke-direct/range {{p0 .. p0}}, {cls}->playlinkEnsureMic()V

    return-void
.end method
"""
        stripped = text.rstrip()
        if stripped.endswith(".end class"):
            text = stripped[: -len(".end class")].rstrip() + "\n" + added + "\n.end class\n"
        else:
            text = stripped + added + "\n"
        print("  added onCreate to", smali.name)
    text = _append_mic_helper(text, cls)
    smali.write_text(text, encoding="utf-8")
    print("  requested RECORD_AUDIO from", smali.name)


def inject_runtime_mic_permission(decoded: Path) -> None:
    manifest = (decoded / "AndroidManifest.xml").read_text(encoding="utf-8", errors="replace")
    if "android.permission.RECORD_AUDIO" not in manifest:
        return
    act = launcher_activity(decoded)
    if not act:
        print("  warn: no launcher activity for mic patch")
        return
    rel = "/".join(act.split("."))
    hits = list(decoded.glob(f"smali*/{rel}.smali"))
    if not hits:
        print("  warn: launcher smali not found", act)
        return
    _inject_mic_simple(hits[0], "L" + act.replace(".", "/") + ";")


def wants_microphone(decoded: Path) -> bool:
    manifest = decoded / "AndroidManifest.xml"
    if not manifest.exists():
        return False
    return "android.permission.RECORD_AUDIO" in manifest.read_text(
        encoding="utf-8", errors="replace"
    )


def patch_legacy_unity_service_connection(decoded: Path) -> None:
    """Redirect the extended ServiceConnection callback for legacy Unity."""
    hits = sorted(decoded.glob("smali*/bitter/jnibridge/JNIBridge$a.smali"))
    if not hits:
        print("  warn: Unity JNIBridge$a.smali not found; skipping ServiceConnection shim")
        return
    if len(hits) != 1:
        print(
            f"  warn: expected one Unity JNIBridge$a.smali, found {len(hits)};"
            " skipping ServiceConnection shim"
        )
        return

    smali = hits[0]
    text = smali.read_text(encoding="utf-8")
    if JNIBRIDGE_SHIM_LABEL in text:
        print("  legacy Unity ServiceConnection shim already present")
        return
    if text.count(JNIBRIDGE_INVOKE_SIGNATURE) != 1:
        print("  warn: unsupported Unity JNIBridge InvocationHandler layout")
        return

    start = text.index(JNIBRIDGE_INVOKE_SIGNATURE)
    end = text.find(".end method", start)
    if end < 0:
        print("  warn: unsupported Unity JNIBridge InvocationHandler layout")
        return
    method = text[start:end]
    locals_match = re.search(r"^\s*\.locals\s+(\d+)\s*$", method, re.M)
    if not locals_match or int(locals_match.group(1)) < 6:
        print("  warn: Unity JNIBridge invoke method has unsupported registers")
        return
    if (
        method.count(JNIBRIDGE_PATCH_POINT) != 1
        or method.count(JNIBRIDGE_NATIVE_INVOKE) != 1
    ):
        print("  warn: unsupported Unity JNIBridge InvocationHandler patch point")
        return

    patched_method = method.replace(
        JNIBRIDGE_PATCH_POINT,
        JNIBRIDGE_PATCH_POINT + JNIBRIDGE_SERVICE_CONNECTION_SHIM,
        1,
    )
    smali.write_text(text[:start] + patched_method + text[end:], encoding="utf-8")
    print("  patched legacy Unity ServiceConnection callback")


def patch_one(apk: Path) -> Path:
    dest = WORK / safe_stem(apk.stem)
    if dest.exists():
        shutil.rmtree(dest)
    unity = is_unity(apk)
    decode_flags = () if unity else ("-s",)
    apktool("d", "-f", *decode_flags, "-o", str(dest), str(apk))
    patch_manifest(dest)
    if wants_microphone(dest):
        if not unity:
            apktool("d", "-f", "-o", str(dest), str(apk))
            patch_manifest(dest)
        inject_runtime_mic_permission(dest)
    if unity:
        patch_legacy_unity_service_connection(dest)
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
        raise SystemExit("Missing tools/apktool.jar")
    if not (HERE / "tools" / "uber-apk-signer.jar").exists():
        raise SystemExit("Missing tools/uber-apk-signer.jar")
    helper = HERE / "tools" / "libnoaslr.so"
    if not helper.exists():
        subprocess.run([sys.executable, str(HERE / "tools" / "gen_noaslr.py")], check=True)

    apks = find_apks()
    if not apks:
        print("No original APKs found.")
        print()
        print(f"Put the files in:\n  {ORIGINALS}")
        print()
        print("Expected games: Hidden Agenda, That's You!, Knowledge is Power, KiP Decades,")
        print("Chimparty, Frantics, SingStar Mic")
        print("Do not put already patched *-android16.apk here — originals only.")
        raise SystemExit(1)

    WORK.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    built: list[Path] = []
    for apk in apks:
        print("=" * 70)
        kind = "Unity wrap" if is_unity(apk) else "UE4/manifest"
        print("Patch", apk.name, f"({kind})")
        built.append(patch_one(apk))

    print("=" * 70)
    print("Done. Install from:")
    print(f"  {OUT}")
    for path in built:
        print(f"  - {path.name}")


if __name__ == "__main__":
    main()
