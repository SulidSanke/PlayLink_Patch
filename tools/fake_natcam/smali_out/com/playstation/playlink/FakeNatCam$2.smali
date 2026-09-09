.class Lcom/playstation/playlink/FakeNatCam$2;
.super Ljava/lang/Object;
.source "FakeNatCam.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/playstation/playlink/FakeNatCam;->start(Lcom/olokobayusuf/natcam/CameraDevice;Lcom/olokobayusuf/natcam/CameraDevice$Callback;I)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# direct methods
.method constructor <init>()V
    .registers 1

    .line 265
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 9

    .line 268
    sget-boolean v0, Lcom/playstation/playlink/FakeNatCam;->running:Z

    if-nez v0, :cond_5

    .line 269
    return-void

    .line 271
    :cond_5
    sget-object v1, Lcom/playstation/playlink/FakeNatCam;->callback:Lcom/olokobayusuf/natcam/CameraDevice$Callback;

    .line 272
    sget-object v2, Lcom/playstation/playlink/FakeNatCam;->frameBuffer:Ljava/nio/ByteBuffer;

    .line 273
    if-eqz v1, :cond_28

    if-eqz v2, :cond_28

    .line 275
    :try_start_d
    invoke-virtual {v2}, Ljava/nio/ByteBuffer;->rewind()Ljava/nio/Buffer;

    move-result-object v0

    check-cast v0, Ljava/nio/ByteBuffer;

    .line 276
    sget v4, Lcom/playstation/playlink/FakeNatCam;->width:I

    sget v5, Lcom/playstation/playlink/FakeNatCam;->height:I

    .line 281
    invoke-static {}, Landroid/os/SystemClock;->elapsedRealtimeNanos()J

    move-result-wide v6

    .line 276
    const/4 v3, 0x0

    invoke-interface/range {v1 .. v7}, Lcom/olokobayusuf/natcam/CameraDevice$Callback;->onFrame(Ljava/nio/ByteBuffer;IIIJ)V
    :try_end_1f
    .catchall {:try_start_d .. :try_end_1f} :catchall_20

    .line 284
    goto :goto_28

    .line 282
    :catchall_20
    move-exception v0

    .line 283
    const-string v1, "Unity"

    const-string v2, "playlink: fake onFrame threw"

    invoke-static {v1, v2, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 286
    :cond_28
    :goto_28
    sget-boolean v0, Lcom/playstation/playlink/FakeNatCam;->running:Z

    if-nez v0, :cond_2d

    .line 287
    return-void

    .line 289
    :cond_2d
    sget-object v0, Lcom/olokobayusuf/natcam/CameraDevice;->delegateHandler:Landroid/os/Handler;

    .line 290
    if-nez v0, :cond_32

    .line 291
    return-void

    .line 293
    :cond_32
    const-wide/16 v1, 0x32

    invoke-virtual {v0, p0, v1, v2}, Landroid/os/Handler;->postDelayed(Ljava/lang/Runnable;J)Z

    .line 294
    return-void
.end method
