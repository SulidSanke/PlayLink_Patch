package com.playstation.playlink;

import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.util.Log;
import android.util.Size;
import java.io.File;
import java.io.FileInputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

/**
 * Hybrid NatCam for Decades / Android 16.
 *
 * Real Camera2 only on character-select selfie UI. Rematch often starts
 * preview before PHOTO_TAKING is written — so we (1) clear the completed latch
 * on AVATAR_SELECTION / ENTERING_NAME and (2) upgrade an already-running fake
 * preview to real when {@link #enterProfileSelfie()} finally fires.
 */
public final class FakeNatCam {
    private static final String TAG = "Unity";
    static final String STAGE_PATH =
            "/data/data/com.playstation.kipdecades/playlink_stage";
    static final String AVATAR_STAGE_PATH =
            "/data/data/com.playstation.kipdecades/playlink_avatar_stage";

    static final int STAGE_ENTERING_NAME = 3;
    static final int STAGE_TAKING_PHOTO = 5;
    static final int AVATAR_SELECTION = 1;
    static final int AVATAR_PHOTO_TAKING = 2;

    private static final long MIN_PROFILE_SELFIE_MS = 30000L;
    private static final long FRAME_INTERVAL_MS = 50L;
    private static final long POLL_MS = 100L;

    static com.olokobayusuf.natcam.CameraDevice activeDevice;
    static com.olokobayusuf.natcam.CameraDevice.Callback callback;
    static ByteBuffer frameBuffer;
    static int width;
    static int height;
    static int lastRotation;
    static boolean running;
    static Runnable ticker;

    static volatile boolean profileSelfieActive;
    static volatile boolean profileSelfieCompleted;
    static int lastProfileStage = Integer.MIN_VALUE;
    static int lastAvatarStage = Integer.MIN_VALUE;
    static long realStartedAtMs;
    static boolean pollerStarted;
    static boolean upgrading;

    private FakeNatCam() {}

    public static boolean shouldUseFake() {
        ensurePoller();
        syncFromStageFiles();
        if (profileSelfieActive) {
            return false;
        }
        if (!profileSelfieCompleted) {
            return false;
        }
        return true;
    }

    public static void onProfileCreationStage(int stage) {
        if (stage == lastProfileStage) {
            return;
        }
        lastProfileStage = stage;
        if (stage == STAGE_ENTERING_NAME || stage == STAGE_TAKING_PHOTO) {
            // New profile flow / selfie — allow real again after a prior match.
            profileSelfieCompleted = false;
        }
        recompute();
    }

    public static void onAvatarScreenStage(int stage) {
        if (stage == lastAvatarStage) {
            return;
        }
        lastAvatarStage = stage;
        if (stage == AVATAR_SELECTION || stage == AVATAR_PHOTO_TAKING) {
            profileSelfieCompleted = false;
        }
        recompute();
    }

    static void recompute() {
        boolean wantReal =
                lastProfileStage == STAGE_TAKING_PHOTO
                        || lastAvatarStage == AVATAR_PHOTO_TAKING;
        if (wantReal) {
            if (!profileSelfieActive) {
                enterProfileSelfie();
            }
        } else if (profileSelfieActive) {
            leaveProfileSelfie();
        }
    }

    public static void enterProfileSelfie() {
        profileSelfieActive = true;
        profileSelfieCompleted = false;
        Log.i(TAG, "playlink: enterProfileSelfie");
        upgradeFakeToRealIfNeeded();
    }

    public static void leaveProfileSelfie() {
        profileSelfieActive = false;
        profileSelfieCompleted = true;
        Log.i(TAG, "playlink: leaveProfileSelfie");
    }

    /** If preview already opened as fake (race), tear it down and open real Camera2. */
    static void upgradeFakeToRealIfNeeded() {
        if (upgrading || !running) {
            return;
        }
        com.olokobayusuf.natcam.CameraDevice dev = activeDevice;
        com.olokobayusuf.natcam.CameraDevice.Callback cb = callback;
        int rot = lastRotation;
        if (dev == null || cb == null) {
            return;
        }
        upgrading = true;
        try {
            Log.i(TAG, "playlink: upgrading fake preview to real camera");
            stopAny();
            dev.startPreview(rot, cb);
        } catch (Throwable t) {
            Log.e(TAG, "playlink: upgrade to real failed", t);
        } finally {
            upgrading = false;
        }
    }

    static int readIntFile(String path) {
        File f = new File(path);
        if (!f.isFile() || f.length() < 4L) {
            return Integer.MIN_VALUE;
        }
        byte[] buf = new byte[4];
        FileInputStream in = null;
        try {
            in = new FileInputStream(f);
            if (in.read(buf) != 4) {
                return Integer.MIN_VALUE;
            }
        } catch (Throwable t) {
            return Integer.MIN_VALUE;
        } finally {
            if (in != null) {
                try {
                    in.close();
                } catch (Throwable ignored) {
                }
            }
        }
        return ByteBuffer.wrap(buf).order(ByteOrder.LITTLE_ENDIAN).getInt();
    }

    static void syncFromStageFiles() {
        int profile = readIntFile(STAGE_PATH);
        if (profile != Integer.MIN_VALUE) {
            onProfileCreationStage(profile);
        }
        int avatar = readIntFile(AVATAR_STAGE_PATH);
        if (avatar != Integer.MIN_VALUE) {
            onAvatarScreenStage(avatar);
        }
    }

    static void ensurePoller() {
        if (pollerStarted) {
            return;
        }
        pollerStarted = true;
        final Handler h = new Handler(Looper.getMainLooper());
        h.post(
                new Runnable() {
                    @Override
                    public void run() {
                        syncFromStageFiles();
                        h.postDelayed(this, POLL_MS);
                    }
                });
    }

    public static boolean isActive(com.olokobayusuf.natcam.CameraDevice device) {
        return running && activeDevice == device;
    }

    public static void noteRealStarted(
            com.olokobayusuf.natcam.CameraDevice device,
            com.olokobayusuf.natcam.CameraDevice.Callback delegate) {
        noteRealStarted();
    }

    public static void noteRealStarted() {
        syncFromStageFiles();
        realStartedAtMs = SystemClock.uptimeMillis();
    }

    public static void noteRealStopped() {
        syncFromStageFiles();
        if (realStartedAtMs <= 0L) {
            return;
        }
        long elapsed = SystemClock.uptimeMillis() - realStartedAtMs;
        realStartedAtMs = 0L;
        if (profileSelfieActive) {
            leaveProfileSelfie();
            return;
        }
        if (profileSelfieCompleted) {
            return;
        }
        if (elapsed >= MIN_PROFILE_SELFIE_MS) {
            Log.i(
                    TAG,
                    "playlink: arming NatCam fake after real session "
                            + elapsed
                            + "ms (duration fallback)");
            leaveProfileSelfie();
        }
    }

    public static void start(
            com.olokobayusuf.natcam.CameraDevice device,
            com.olokobayusuf.natcam.CameraDevice.Callback delegate) {
        start(device, delegate, 0);
    }

    public static void start(
            com.olokobayusuf.natcam.CameraDevice device,
            com.olokobayusuf.natcam.CameraDevice.Callback delegate,
            int rotation) {
        stopAny();
        if (device == null || delegate == null) {
            return;
        }

        lastRotation = rotation;
        Size size = device.getPreviewResolution();
        int w = size != null ? size.getWidth() : 640;
        int h = size != null ? size.getHeight() : 480;
        if (w < 1) {
            w = 640;
        }
        if (h < 1) {
            h = 480;
        }

        activeDevice = device;
        callback = delegate;
        width = w;
        height = h;
        frameBuffer = ByteBuffer.allocateDirect(w * h * 4).order(ByteOrder.nativeOrder());
        running = true;

        ticker =
                new Runnable() {
                    @Override
                    public void run() {
                        if (!running) {
                            return;
                        }
                        com.olokobayusuf.natcam.CameraDevice.Callback cb = callback;
                        ByteBuffer buf = frameBuffer;
                        if (cb != null && buf != null) {
                            try {
                                buf.rewind();
                                cb.onFrame(
                                        buf,
                                        0,
                                        width,
                                        height,
                                        SystemClock.elapsedRealtimeNanos());
                            } catch (Throwable t) {
                                Log.e(TAG, "playlink: fake onFrame threw", t);
                            }
                        }
                        if (!running) {
                            return;
                        }
                        Handler dh = com.olokobayusuf.natcam.CameraDevice.delegateHandler;
                        if (dh == null) {
                            return;
                        }
                        dh.postDelayed(this, FRAME_INTERVAL_MS);
                    }
                };

        Handler dh = com.olokobayusuf.natcam.CameraDevice.delegateHandler;
        if (dh == null) {
            dh = new Handler(Looper.getMainLooper());
        }
        dh.post(ticker);
        Log.i(
                TAG,
                "playlink: NatCam fake preview started "
                        + device.uniqueID()
                        + " "
                        + w
                        + "x"
                        + h);
    }

    public static void stop(com.olokobayusuf.natcam.CameraDevice device) {
        if (!running) {
            return;
        }
        if (device != null && activeDevice != device) {
            return;
        }
        stopAny();
    }

    public static void stopAny() {
        running = false;
        Handler dh = com.olokobayusuf.natcam.CameraDevice.delegateHandler;
        if (dh != null && ticker != null) {
            dh.removeCallbacks(ticker);
        }
        ticker = null;
        callback = null;
        frameBuffer = null;
        activeDevice = null;
    }
}
