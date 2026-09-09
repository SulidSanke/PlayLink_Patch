package com.playstation.playlink;

import java.nio.ByteBuffer;

/** Copy ImageReader RGBA rows into an allocateDirect buffer without native HAL pointers. */
public final class SafeCopy {
    private SafeCopy() {}

    public static void copyRgba(
            ByteBuffer src, int width, int height, int rowStride, ByteBuffer dst) {
        if (src == null || dst == null || width <= 0 || height <= 0) {
            return;
        }
        int rowBytes = width * 4;
        if (rowStride < rowBytes) {
            rowStride = rowBytes;
        }
        byte[] row = new byte[rowBytes];
        int srcPos = src.position();
        dst.clear();
        for (int y = 0; y < height; y++) {
            src.position(srcPos + y * rowStride);
            src.get(row, 0, rowBytes);
            dst.put(row);
        }
        dst.rewind();
        src.position(srcPos);
    }
}
