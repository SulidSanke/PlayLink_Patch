package com.olokobayusuf.natcam;

import android.os.Handler;
import android.util.Size;
import java.nio.ByteBuffer;

/** Compile-time stubs mirroring NatCam APIs we call. */
public class CameraDevice {
    public static Handler delegateHandler;

    public String uniqueID() {
        return "0";
    }

    public Size getPreviewResolution() {
        return new Size(1280, 720);
    }

    public Size getPhotoResolution() {
        return new Size(1280, 720);
    }

    public void startPreview(int rotation, Callback delegate) {}

    public void stopPreview() {}

    public interface Callback {
        void onFrame(ByteBuffer pixelBuffer, int textureID, int width, int height, long timestamp);

        void onPhoto(ByteBuffer pixelBuffer, int width, int height);
    }
}
