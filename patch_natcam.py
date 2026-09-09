#!/usr/bin/env python3
"""Hybrid NatCam: real Camera2 only for character-select profile selfie.

1) Real NatCam with ImageReader fast-path + SafeCopy photos (live GL preview).
2) After character-select selfie ends, use black allocateDirect frames for all
   other startPreview calls (FaceDetection / Flip / mid-match) — no TTL.
3) Preferred gate: FakeNatCam.enterProfileSelfie/leaveProfileSelfie from IL2CPP
   (CHARACTER_SELECT_TAKING_PHOTO). Fallback: first real preview >=30s → leave.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAKE_DIR = HERE / "tools" / "fake_natcam"
SMALI_OUT = FAKE_DIR / "smali_out"

FRAME_METHOD = """\
.method public onImageAvailable(Landroid/media/ImageReader;)V
    .locals 8
    .param p1, "imageReader"    # Landroid/media/ImageReader;

    .prologue
    # playlink: skip HAL CPU copy — close image immediately so preview does not stall

    invoke-virtual {p1}, Landroid/media/ImageReader;->acquireLatestImage()Landroid/media/Image;

    move-result-object v7

    if-nez v7, :cond_0

    return-void

    :cond_0
    invoke-virtual {v7}, Landroid/media/Image;->getWidth()I

    move-result v3

    invoke-virtual {v7}, Landroid/media/Image;->getHeight()I

    move-result v4

    invoke-virtual {v7}, Landroid/media/Image;->getTimestamp()J

    move-result-wide v5

    invoke-virtual {v7}, Landroid/media/Image;->close()V

    iget-object v0, p0, Lcom/olokobayusuf/natcam/FrameRenderer$4;->this$0:Lcom/olokobayusuf/natcam/FrameRenderer;

    invoke-static {v0}, Lcom/olokobayusuf/natcam/FrameRenderer;->access$800(Lcom/olokobayusuf/natcam/FrameRenderer;)Landroid/os/Handler;

    move-result-object v0

    new-instance v1, Lcom/olokobayusuf/natcam/FrameRenderer$4$1;

    move-object v2, p0

    invoke-direct/range {v1 .. v6}, Lcom/olokobayusuf/natcam/FrameRenderer$4$1;-><init>(Lcom/olokobayusuf/natcam/FrameRenderer$4;IIJ)V

    invoke-virtual {v0, v1}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z

    return-void
.end method
"""

PHOTO_COPY_OLD = """\
    invoke-static {v9}, Lcom/olokobayusuf/natrender/Unmanaged;->baseAddress(Ljava/nio/ByteBuffer;)J

    move-result-wide v0

    iget-object v5, p0, Lcom/olokobayusuf/natcam/PhotoRenderer$3;->this$0:Lcom/olokobayusuf/natcam/PhotoRenderer;

    invoke-static {v5}, Lcom/olokobayusuf/natcam/PhotoRenderer;->access$400(Lcom/olokobayusuf/natcam/PhotoRenderer;)Ljava/nio/ByteBuffer;

    move-result-object v5

    invoke-static {v5}, Lcom/olokobayusuf/natrender/Unmanaged;->baseAddress(Ljava/nio/ByteBuffer;)J

    move-result-wide v5

    invoke-static/range {v0 .. v6}, Lcom/olokobayusuf/natrender/Unmanaged;->copyFrame(JIIIJ)V
"""

PHOTO_COPY_NEW = """\
    iget-object v5, p0, Lcom/olokobayusuf/natcam/PhotoRenderer$3;->this$0:Lcom/olokobayusuf/natcam/PhotoRenderer;

    invoke-static {v5}, Lcom/olokobayusuf/natcam/PhotoRenderer;->access$400(Lcom/olokobayusuf/natcam/PhotoRenderer;)Ljava/nio/ByteBuffer;

    move-result-object v5

    invoke-static {v9, v2, v3, v4, v5}, Lcom/playstation/playlink/SafeCopy;->copyRgba(Ljava/nio/ByteBuffer;IIILjava/nio/ByteBuffer;)V
"""

# Injected at the top of the original startPreview body (keeps real path intact).
START_PREVIEW_HEAD = """\
.method public startPreview(ILcom/olokobayusuf/natcam/CameraDevice$Callback;)V
    .locals 10
    .param p1, "rotation"    # I
    .param p2, "delegate"    # Lcom/olokobayusuf/natcam/CameraDevice$Callback;

    .prologue
    # playlink: fake unless character-select selfie stage (or pre-fallback)
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->shouldUseFake()Z

    move-result v0

    if-eqz v0, :cond_playlink_real

    invoke-static {p0, p2, p1}, Lcom/playstation/playlink/FakeNatCam;->start(Lcom/olokobayusuf/natcam/CameraDevice;Lcom/olokobayusuf/natcam/CameraDevice$Callback;I)V

    return-void

    :cond_playlink_real
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->noteRealStarted()V

"""

STOP_PREVIEW_HEAD = """\
.method public stopPreview()V
    .locals 5

    .prologue
    const/4 v4, 0x0

    # playlink: stop fake ticker, or note real session length for arming
    invoke-static {p0}, Lcom/playstation/playlink/FakeNatCam;->isActive(Lcom/olokobayusuf/natcam/CameraDevice;)Z

    move-result v1

    if-eqz v1, :cond_playlink_real_stop

    invoke-static {p0}, Lcom/playstation/playlink/FakeNatCam;->stop(Lcom/olokobayusuf/natcam/CameraDevice;)V

    return-void

    :cond_playlink_real_stop
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->noteRealStopped()V

"""

IS_RUNNING_PATCHED = """\
.method public isRunning()Z
    .locals 1

    .prologue
    invoke-static {p0}, Lcom/playstation/playlink/FakeNatCam;->isActive(Lcom/olokobayusuf/natcam/CameraDevice;)Z

    move-result v0

    if-eqz v0, :cond_orig

    const/4 v0, 0x1

    return v0

    :cond_orig
    iget-object v0, p0, Lcom/olokobayusuf/natcam/CameraDevice;->previewRenderer:Lcom/olokobayusuf/natcam/FrameRenderer;

    if-eqz v0, :cond_0

    const/4 v0, 0x1

    :goto_0
    return v0

    :cond_0
    const/4 v0, 0x0

    goto :goto_0
.end method
"""


def ensure_playlink_smali() -> Path:
    """Use committed smali under tools/fake_natcam/smali_out (rebuild only if missing)."""
    marker = SMALI_OUT / "com" / "playstation" / "playlink" / "FakeNatCam.smali"
    if not marker.exists():
        subprocess.run([sys.executable, str(FAKE_DIR / "build_smali.py")], check=True, cwd=str(HERE))
    if not marker.exists():
        raise SystemExit("FakeNatCam smali missing after build")
    safe = SMALI_OUT / "com" / "playstation" / "playlink" / "SafeCopy.smali"
    if not safe.exists():
        raise SystemExit("SafeCopy smali missing after build")
    return SMALI_OUT


def _replace_method(text: str, method_start: str, new_method: str) -> str:
    start = text.find(method_start)
    if start < 0:
        raise ValueError(f"method not found: {method_start[:60]}")
    end = text.find("\n.end method", start)
    if end < 0:
        raise ValueError("method end not found")
    end += len("\n.end method")
    return text[:start] + new_method + text[end:]


def _inject_after_prologue(text: str, method_start: str, head: str) -> str:
    """Replace method opening through first .prologue with hybrid head, keep rest."""
    start = text.find(method_start)
    if start < 0:
        raise ValueError(f"method not found: {method_start[:60]}")
    end = text.find("\n.end method", start)
    if end < 0:
        raise ValueError("method end not found")
    end += len("\n.end method")
    body = text[start:end]
    # Drop original signature + locals + params + prologue; keep from first real insn.
    # For startPreview original begins with eglGetCurrentContext after prologue.
    # For stopPreview original begins with :try_start_0 after const/4 v4.
    if "eglGetCurrentContext" in body:
        idx = body.find("invoke-static {}, Landroid/opengl/EGL14;->eglGetCurrentContext()")
        if idx < 0:
            raise ValueError("startPreview body marker missing")
        rest = body[idx:]
        # rest still includes through .end method — head already has signature;
        # strip trailing .end method from rest and from head composition
        if not rest.endswith(".end method"):
            raise ValueError("unexpected method tail")
        rest = rest[: -len(".end method")]
        return text[:start] + head + rest + ".end method" + text[end:]
    if ":try_start_0" in body:
        idx = body.find("    :try_start_0")
        if idx < 0:
            idx = body.find(":try_start_0")
        if idx < 0:
            raise ValueError("stopPreview try marker missing")
        rest = body[idx:]
        if not rest.endswith(".end method"):
            raise ValueError("unexpected method tail")
        rest = rest[: -len(".end method")]
        return text[:start] + head + rest + ".end method" + text[end:]
    raise ValueError("no injection marker in method")


def disable_natcam_preview(decoded: Path) -> None:
    devices = list(decoded.glob("smali*/com/olokobayusuf/natcam/CameraDevice.smali"))
    frames = list(decoded.glob("smali*/com/olokobayusuf/natcam/FrameRenderer$4.smali"))
    photos = list(decoded.glob("smali*/com/olokobayusuf/natcam/PhotoRenderer$3.smali"))
    if not devices and not frames and not photos:
        return

    built = ensure_playlink_smali()
    smali_roots = {
        next(p for p in path.parents if p.name.startswith("smali"))
        for path in devices + frames + photos
    }
    for smali_root in smali_roots:
        dest = smali_root / "com" / "playstation" / "playlink"
        dest.mkdir(parents=True, exist_ok=True)
        for src in (built / "com" / "playstation" / "playlink").glob("*.smali"):
            shutil.copy2(src, dest / src.name)

    for path in devices:
        text = path.read_text(encoding="utf-8")
        if "Lcom/playstation/playlink/FakeNatCam;->shouldUseFake()Z" in text:
            print(f"  hybrid NatCam already installed in {path.name}")
        else:
            text = _inject_after_prologue(
                text,
                ".method public startPreview(ILcom/olokobayusuf/natcam/CameraDevice$Callback;)V",
                START_PREVIEW_HEAD,
            )
            text = _inject_after_prologue(text, ".method public stopPreview()V", STOP_PREVIEW_HEAD)
            text = _replace_method(text, ".method public isRunning()Z", IS_RUNNING_PATCHED)
            path.write_text(text, encoding="utf-8")
            print(f"  installed hybrid NatCam in {path.relative_to(decoded)}")

    for path in frames:
        text = path.read_text(encoding="utf-8")
        if "playlink: skip HAL CPU copy" in text:
            print(f"  preview ImageReader already fast-path in {path.name}")
            continue
        text = _replace_method(
            text, ".method public onImageAvailable(Landroid/media/ImageReader;)V", FRAME_METHOD
        )
        path.write_text(text, encoding="utf-8")
        print(f"  fast-path preview ImageReader in {path.relative_to(decoded)}")

    for path in photos:
        text = path.read_text(encoding="utf-8")
        if "Lcom/playstation/playlink/SafeCopy;->copyRgba" in text:
            print(f"  photo copy already patched in {path.name}")
            continue
        if PHOTO_COPY_OLD not in text:
            raise SystemExit(f"photo copy pattern missing in {path}")
        path.write_text(text.replace(PHOTO_COPY_OLD, PHOTO_COPY_NEW, 1), encoding="utf-8")
        print(f"  patched photo copy in {path.relative_to(decoded)}")
