.class public final Lcom/playstation/playlink/FakeNatCam;
.super Ljava/lang/Object;
.source "FakeNatCam.java"


# static fields
.field static final AVATAR_PHOTO_TAKING:I = 0x2

.field static final AVATAR_SELECTION:I = 0x1

.field static final AVATAR_STAGE_PATH:Ljava/lang/String; = "/data/data/com.playstation.kipdecades/playlink_avatar_stage"

.field private static final FRAME_INTERVAL_MS:J = 0x32L

.field private static final MIN_PROFILE_SELFIE_MS:J = 0x7530L

.field private static final POLL_MS:J = 0x64L

.field static final STAGE_ENTERING_NAME:I = 0x3

.field static final STAGE_PATH:Ljava/lang/String; = "/data/data/com.playstation.kipdecades/playlink_stage"

.field static final STAGE_TAKING_PHOTO:I = 0x5

.field private static final TAG:Ljava/lang/String; = "Unity"

.field static activeDevice:Lcom/olokobayusuf/natcam/CameraDevice;

.field static callback:Lcom/olokobayusuf/natcam/CameraDevice$Callback;

.field static frameBuffer:Ljava/nio/ByteBuffer;

.field static height:I

.field static lastAvatarStage:I

.field static lastProfileStage:I

.field static lastRotation:I

.field static pollerStarted:Z

.field static volatile profileSelfieActive:Z

.field static volatile profileSelfieCompleted:Z

.field static realStartedAtMs:J

.field static running:Z

.field static ticker:Ljava/lang/Runnable;

.field static upgrading:Z

.field static width:I


# direct methods
.method static constructor <clinit>()V
    .registers 1

    .line 48
    const/high16 v0, -0x80000000

    sput v0, Lcom/playstation/playlink/FakeNatCam;->lastProfileStage:I

    .line 49
    sput v0, Lcom/playstation/playlink/FakeNatCam;->lastAvatarStage:I

    return-void
.end method

.method private constructor <init>()V
    .registers 1

    .line 54
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static ensurePoller()V
    .registers 2

    .line 177
    sget-boolean v0, Lcom/playstation/playlink/FakeNatCam;->pollerStarted:Z

    if-eqz v0, :cond_5

    .line 178
    return-void

    .line 180
    :cond_5
    const/4 v0, 0x1

    sput-boolean v0, Lcom/playstation/playlink/FakeNatCam;->pollerStarted:Z

    .line 181
    new-instance v0, Landroid/os/Handler;

    invoke-static {}, Landroid/os/Looper;->getMainLooper()Landroid/os/Looper;

    move-result-object v1

    invoke-direct {v0, v1}, Landroid/os/Handler;-><init>(Landroid/os/Looper;)V

    .line 182
    new-instance v1, Lcom/playstation/playlink/FakeNatCam$1;

    invoke-direct {v1, v0}, Lcom/playstation/playlink/FakeNatCam$1;-><init>(Landroid/os/Handler;)V

    invoke-virtual {v0, v1}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z

    .line 190
    return-void
.end method

.method public static enterProfileSelfie()V
    .registers 2

    .line 105
    const/4 v0, 0x1

    sput-boolean v0, Lcom/playstation/playlink/FakeNatCam;->profileSelfieActive:Z

    .line 106
    const/4 v0, 0x0

    sput-boolean v0, Lcom/playstation/playlink/FakeNatCam;->profileSelfieCompleted:Z

    .line 107
    const-string v0, "Unity"

    const-string v1, "playlink: enterProfileSelfie"

    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 108
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->upgradeFakeToRealIfNeeded()V

    .line 109
    return-void
.end method

.method public static isActive(Lcom/olokobayusuf/natcam/CameraDevice;)Z
    .registers 2

    .line 193
    sget-boolean v0, Lcom/playstation/playlink/FakeNatCam;->running:Z

    if-eqz v0, :cond_a

    sget-object v0, Lcom/playstation/playlink/FakeNatCam;->activeDevice:Lcom/olokobayusuf/natcam/CameraDevice;

    if-ne v0, p0, :cond_a

    const/4 p0, 0x1

    goto :goto_b

    :cond_a
    const/4 p0, 0x0

    :goto_b
    return p0
.end method

.method public static leaveProfileSelfie()V
    .registers 2

    .line 112
    const/4 v0, 0x0

    sput-boolean v0, Lcom/playstation/playlink/FakeNatCam;->profileSelfieActive:Z

    .line 113
    const/4 v0, 0x1

    sput-boolean v0, Lcom/playstation/playlink/FakeNatCam;->profileSelfieCompleted:Z

    .line 114
    const-string v0, "Unity"

    const-string v1, "playlink: leaveProfileSelfie"

    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 115
    return-void
.end method

.method public static noteRealStarted()V
    .registers 2

    .line 203
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->syncFromStageFiles()V

    .line 204
    invoke-static {}, Landroid/os/SystemClock;->uptimeMillis()J

    move-result-wide v0

    sput-wide v0, Lcom/playstation/playlink/FakeNatCam;->realStartedAtMs:J

    .line 205
    return-void
.end method

.method public static noteRealStarted(Lcom/olokobayusuf/natcam/CameraDevice;Lcom/olokobayusuf/natcam/CameraDevice$Callback;)V
    .registers 2

    .line 199
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->noteRealStarted()V

    .line 200
    return-void
.end method

.method public static noteRealStopped()V
    .registers 6

    .line 208
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->syncFromStageFiles()V

    .line 209
    sget-wide v0, Lcom/playstation/playlink/FakeNatCam;->realStartedAtMs:J

    const-wide/16 v2, 0x0

    cmp-long v4, v0, v2

    if-gtz v4, :cond_c

    .line 210
    return-void

    .line 212
    :cond_c
    invoke-static {}, Landroid/os/SystemClock;->uptimeMillis()J

    move-result-wide v0

    sget-wide v4, Lcom/playstation/playlink/FakeNatCam;->realStartedAtMs:J

    sub-long/2addr v0, v4

    .line 213
    sput-wide v2, Lcom/playstation/playlink/FakeNatCam;->realStartedAtMs:J

    .line 214
    sget-boolean v2, Lcom/playstation/playlink/FakeNatCam;->profileSelfieActive:Z

    if-eqz v2, :cond_1d

    .line 215
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->leaveProfileSelfie()V

    .line 216
    return-void

    .line 218
    :cond_1d
    sget-boolean v2, Lcom/playstation/playlink/FakeNatCam;->profileSelfieCompleted:Z

    if-eqz v2, :cond_22

    .line 219
    return-void

    .line 221
    :cond_22
    const-wide/16 v2, 0x7530

    cmp-long v4, v0, v2

    if-ltz v4, :cond_49

    .line 222
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "playlink: arming NatCam fake after real session "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v0, v1}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, "ms (duration fallback)"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    const-string v1, "Unity"

    invoke-static {v1, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 227
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->leaveProfileSelfie()V

    .line 229
    :cond_49
    return-void
.end method

.method public static onAvatarScreenStage(I)V
    .registers 2

    .line 81
    sget v0, Lcom/playstation/playlink/FakeNatCam;->lastAvatarStage:I

    if-ne p0, v0, :cond_5

    .line 82
    return-void

    .line 84
    :cond_5
    sput p0, Lcom/playstation/playlink/FakeNatCam;->lastAvatarStage:I

    .line 85
    const/4 v0, 0x1

    if-eq p0, v0, :cond_d

    const/4 v0, 0x2

    if-ne p0, v0, :cond_10

    .line 86
    :cond_d
    const/4 p0, 0x0

    sput-boolean p0, Lcom/playstation/playlink/FakeNatCam;->profileSelfieCompleted:Z

    .line 88
    :cond_10
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->recompute()V

    .line 89
    return-void
.end method

.method public static onProfileCreationStage(I)V
    .registers 2

    .line 69
    sget v0, Lcom/playstation/playlink/FakeNatCam;->lastProfileStage:I

    if-ne p0, v0, :cond_5

    .line 70
    return-void

    .line 72
    :cond_5
    sput p0, Lcom/playstation/playlink/FakeNatCam;->lastProfileStage:I

    .line 73
    const/4 v0, 0x3

    if-eq p0, v0, :cond_d

    const/4 v0, 0x5

    if-ne p0, v0, :cond_10

    .line 75
    :cond_d
    const/4 p0, 0x0

    sput-boolean p0, Lcom/playstation/playlink/FakeNatCam;->profileSelfieCompleted:Z

    .line 77
    :cond_10
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->recompute()V

    .line 78
    return-void
.end method

.method static readIntFile(Ljava/lang/String;)I
    .registers 7

    .line 141
    new-instance v0, Ljava/io/File;

    invoke-direct {v0, p0}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    .line 142
    invoke-virtual {v0}, Ljava/io/File;->isFile()Z

    move-result p0

    const/high16 v1, -0x80000000

    if-eqz p0, :cond_53

    invoke-virtual {v0}, Ljava/io/File;->length()J

    move-result-wide v2

    const-wide/16 v4, 0x4

    cmp-long p0, v2, v4

    if-gez p0, :cond_18

    goto :goto_53

    .line 145
    :cond_18
    const/4 p0, 0x4

    new-array v2, p0, [B

    .line 146
    nop

    .line 148
    const/4 v3, 0x0

    :try_start_1d
    new-instance v4, Ljava/io/FileInputStream;

    invoke-direct {v4, v0}, Ljava/io/FileInputStream;-><init>(Ljava/io/File;)V
    :try_end_22
    .catchall {:try_start_1d .. :try_end_22} :catchall_49

    .line 149
    :try_start_22
    invoke-virtual {v4, v2}, Ljava/io/FileInputStream;->read([B)I

    move-result v0
    :try_end_26
    .catchall {:try_start_22 .. :try_end_26} :catchall_46

    if-eq v0, p0, :cond_30

    .line 150
    nop

    .line 155
    nop

    .line 157
    :try_start_2a
    invoke-virtual {v4}, Ljava/io/FileInputStream;->close()V
    :try_end_2d
    .catchall {:try_start_2a .. :try_end_2d} :catchall_2e

    .line 159
    goto :goto_2f

    .line 158
    :catchall_2e
    move-exception p0

    .line 150
    :goto_2f
    return v1

    .line 155
    :cond_30
    nop

    .line 157
    :try_start_31
    invoke-virtual {v4}, Ljava/io/FileInputStream;->close()V
    :try_end_34
    .catchall {:try_start_31 .. :try_end_34} :catchall_35

    .line 159
    :goto_34
    goto :goto_37

    .line 158
    :catchall_35
    move-exception p0

    goto :goto_34

    .line 162
    :goto_37
    invoke-static {v2}, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;

    move-result-object p0

    sget-object v0, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;

    invoke-virtual {p0, v0}, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;

    move-result-object p0

    invoke-virtual {p0}, Ljava/nio/ByteBuffer;->getInt()I

    move-result p0

    return p0

    .line 152
    :catchall_46
    move-exception p0

    move-object v3, v4

    goto :goto_4a

    :catchall_49
    move-exception p0

    .line 153
    :goto_4a
    nop

    .line 155
    if-eqz v3, :cond_52

    .line 157
    :try_start_4d
    invoke-virtual {v3}, Ljava/io/FileInputStream;->close()V
    :try_end_50
    .catchall {:try_start_4d .. :try_end_50} :catchall_51

    .line 159
    goto :goto_52

    .line 158
    :catchall_51
    move-exception p0

    .line 153
    :cond_52
    :goto_52
    return v1

    .line 143
    :cond_53
    :goto_53
    return v1
.end method

.method static recompute()V
    .registers 2

    .line 92
    sget v0, Lcom/playstation/playlink/FakeNatCam;->lastProfileStage:I

    const/4 v1, 0x5

    if-eq v0, v1, :cond_d

    sget v0, Lcom/playstation/playlink/FakeNatCam;->lastAvatarStage:I

    const/4 v1, 0x2

    if-ne v0, v1, :cond_b

    goto :goto_d

    :cond_b
    const/4 v0, 0x0

    goto :goto_e

    :cond_d
    :goto_d
    const/4 v0, 0x1

    .line 95
    :goto_e
    if-eqz v0, :cond_18

    .line 96
    sget-boolean v0, Lcom/playstation/playlink/FakeNatCam;->profileSelfieActive:Z

    if-nez v0, :cond_1f

    .line 97
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->enterProfileSelfie()V

    goto :goto_1f

    .line 99
    :cond_18
    sget-boolean v0, Lcom/playstation/playlink/FakeNatCam;->profileSelfieActive:Z

    if-eqz v0, :cond_1f

    .line 100
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->leaveProfileSelfie()V

    .line 102
    :cond_1f
    :goto_1f
    return-void
.end method

.method public static shouldUseFake()Z
    .registers 2

    .line 57
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->ensurePoller()V

    .line 58
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->syncFromStageFiles()V

    .line 59
    sget-boolean v0, Lcom/playstation/playlink/FakeNatCam;->profileSelfieActive:Z

    const/4 v1, 0x0

    if-eqz v0, :cond_c

    .line 60
    return v1

    .line 62
    :cond_c
    sget-boolean v0, Lcom/playstation/playlink/FakeNatCam;->profileSelfieCompleted:Z

    if-nez v0, :cond_11

    .line 63
    return v1

    .line 65
    :cond_11
    const/4 v0, 0x1

    return v0
.end method

.method public static start(Lcom/olokobayusuf/natcam/CameraDevice;Lcom/olokobayusuf/natcam/CameraDevice$Callback;)V
    .registers 3

    .line 234
    const/4 v0, 0x0

    invoke-static {p0, p1, v0}, Lcom/playstation/playlink/FakeNatCam;->start(Lcom/olokobayusuf/natcam/CameraDevice;Lcom/olokobayusuf/natcam/CameraDevice$Callback;I)V

    .line 235
    return-void
.end method

.method public static start(Lcom/olokobayusuf/natcam/CameraDevice;Lcom/olokobayusuf/natcam/CameraDevice$Callback;I)V
    .registers 7

    .line 241
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->stopAny()V

    .line 242
    if-eqz p0, :cond_95

    if-nez p1, :cond_9

    goto/16 :goto_95

    .line 246
    :cond_9
    sput p2, Lcom/playstation/playlink/FakeNatCam;->lastRotation:I

    .line 247
    invoke-virtual {p0}, Lcom/olokobayusuf/natcam/CameraDevice;->getPreviewResolution()Landroid/util/Size;

    move-result-object p2

    .line 248
    const/16 v0, 0x280

    if-eqz p2, :cond_18

    invoke-virtual {p2}, Landroid/util/Size;->getWidth()I

    move-result v1

    goto :goto_1a

    :cond_18
    const/16 v1, 0x280

    .line 249
    :goto_1a
    const/16 v2, 0x1e0

    if-eqz p2, :cond_23

    invoke-virtual {p2}, Landroid/util/Size;->getHeight()I

    move-result p2

    goto :goto_25

    :cond_23
    const/16 p2, 0x1e0

    .line 250
    :goto_25
    const/4 v3, 0x1

    if-ge v1, v3, :cond_29

    .line 251
    goto :goto_2a

    .line 250
    :cond_29
    move v0, v1

    .line 253
    :goto_2a
    if-ge p2, v3, :cond_2d

    .line 254
    goto :goto_2e

    .line 253
    :cond_2d
    move v2, p2

    .line 257
    :goto_2e
    sput-object p0, Lcom/playstation/playlink/FakeNatCam;->activeDevice:Lcom/olokobayusuf/natcam/CameraDevice;

    .line 258
    sput-object p1, Lcom/playstation/playlink/FakeNatCam;->callback:Lcom/olokobayusuf/natcam/CameraDevice$Callback;

    .line 259
    sput v0, Lcom/playstation/playlink/FakeNatCam;->width:I

    .line 260
    sput v2, Lcom/playstation/playlink/FakeNatCam;->height:I

    .line 261
    mul-int p1, v0, v2

    mul-int/lit8 p1, p1, 0x4

    invoke-static {p1}, Ljava/nio/ByteBuffer;->allocateDirect(I)Ljava/nio/ByteBuffer;

    move-result-object p1

    invoke-static {}, Ljava/nio/ByteOrder;->nativeOrder()Ljava/nio/ByteOrder;

    move-result-object p2

    invoke-virtual {p1, p2}, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;

    move-result-object p1

    sput-object p1, Lcom/playstation/playlink/FakeNatCam;->frameBuffer:Ljava/nio/ByteBuffer;

    .line 262
    sput-boolean v3, Lcom/playstation/playlink/FakeNatCam;->running:Z

    .line 264
    new-instance p1, Lcom/playstation/playlink/FakeNatCam$2;

    invoke-direct {p1}, Lcom/playstation/playlink/FakeNatCam$2;-><init>()V

    sput-object p1, Lcom/playstation/playlink/FakeNatCam;->ticker:Ljava/lang/Runnable;

    .line 297
    sget-object p1, Lcom/olokobayusuf/natcam/CameraDevice;->delegateHandler:Landroid/os/Handler;

    .line 298
    if-nez p1, :cond_5e

    .line 299
    new-instance p1, Landroid/os/Handler;

    invoke-static {}, Landroid/os/Looper;->getMainLooper()Landroid/os/Looper;

    move-result-object p2

    invoke-direct {p1, p2}, Landroid/os/Handler;-><init>(Landroid/os/Looper;)V

    .line 301
    :cond_5e
    sget-object p2, Lcom/playstation/playlink/FakeNatCam;->ticker:Ljava/lang/Runnable;

    invoke-virtual {p1, p2}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z

    .line 302
    nop

    .line 305
    invoke-virtual {p0}, Lcom/olokobayusuf/natcam/CameraDevice;->uniqueID()Ljava/lang/String;

    move-result-object p0

    new-instance p1, Ljava/lang/StringBuilder;

    invoke-direct {p1}, Ljava/lang/StringBuilder;-><init>()V

    const-string p2, "playlink: NatCam fake preview started "

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string p1, " "

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string p1, "x"

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    .line 302
    const-string p1, "Unity"

    invoke-static {p1, p0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 310
    return-void

    .line 243
    :cond_95
    :goto_95
    return-void
.end method

.method public static stop(Lcom/olokobayusuf/natcam/CameraDevice;)V
    .registers 2

    .line 313
    sget-boolean v0, Lcom/playstation/playlink/FakeNatCam;->running:Z

    if-nez v0, :cond_5

    .line 314
    return-void

    .line 316
    :cond_5
    if-eqz p0, :cond_c

    sget-object v0, Lcom/playstation/playlink/FakeNatCam;->activeDevice:Lcom/olokobayusuf/natcam/CameraDevice;

    if-eq v0, p0, :cond_c

    .line 317
    return-void

    .line 319
    :cond_c
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->stopAny()V

    .line 320
    return-void
.end method

.method public static stopAny()V
    .registers 2

    .line 323
    const/4 v0, 0x0

    sput-boolean v0, Lcom/playstation/playlink/FakeNatCam;->running:Z

    .line 324
    sget-object v0, Lcom/olokobayusuf/natcam/CameraDevice;->delegateHandler:Landroid/os/Handler;

    .line 325
    if-eqz v0, :cond_10

    sget-object v1, Lcom/playstation/playlink/FakeNatCam;->ticker:Ljava/lang/Runnable;

    if-eqz v1, :cond_10

    .line 326
    sget-object v1, Lcom/playstation/playlink/FakeNatCam;->ticker:Ljava/lang/Runnable;

    invoke-virtual {v0, v1}, Landroid/os/Handler;->removeCallbacks(Ljava/lang/Runnable;)V

    .line 328
    :cond_10
    const/4 v0, 0x0

    sput-object v0, Lcom/playstation/playlink/FakeNatCam;->ticker:Ljava/lang/Runnable;

    .line 329
    sput-object v0, Lcom/playstation/playlink/FakeNatCam;->callback:Lcom/olokobayusuf/natcam/CameraDevice$Callback;

    .line 330
    sput-object v0, Lcom/playstation/playlink/FakeNatCam;->frameBuffer:Ljava/nio/ByteBuffer;

    .line 331
    sput-object v0, Lcom/playstation/playlink/FakeNatCam;->activeDevice:Lcom/olokobayusuf/natcam/CameraDevice;

    .line 332
    return-void
.end method

.method static syncFromStageFiles()V
    .registers 2

    .line 166
    const-string v0, "/data/data/com.playstation.kipdecades/playlink_stage"

    invoke-static {v0}, Lcom/playstation/playlink/FakeNatCam;->readIntFile(Ljava/lang/String;)I

    move-result v0

    .line 167
    const/high16 v1, -0x80000000

    if-eq v0, v1, :cond_d

    .line 168
    invoke-static {v0}, Lcom/playstation/playlink/FakeNatCam;->onProfileCreationStage(I)V

    .line 170
    :cond_d
    const-string v0, "/data/data/com.playstation.kipdecades/playlink_avatar_stage"

    invoke-static {v0}, Lcom/playstation/playlink/FakeNatCam;->readIntFile(Ljava/lang/String;)I

    move-result v0

    .line 171
    if-eq v0, v1, :cond_18

    .line 172
    invoke-static {v0}, Lcom/playstation/playlink/FakeNatCam;->onAvatarScreenStage(I)V

    .line 174
    :cond_18
    return-void
.end method

.method static upgradeFakeToRealIfNeeded()V
    .registers 6

    .line 119
    const-string v0, "Unity"

    sget-boolean v1, Lcom/playstation/playlink/FakeNatCam;->upgrading:Z

    if-nez v1, :cond_35

    sget-boolean v1, Lcom/playstation/playlink/FakeNatCam;->running:Z

    if-nez v1, :cond_b

    goto :goto_35

    .line 122
    :cond_b
    sget-object v1, Lcom/playstation/playlink/FakeNatCam;->activeDevice:Lcom/olokobayusuf/natcam/CameraDevice;

    .line 123
    sget-object v2, Lcom/playstation/playlink/FakeNatCam;->callback:Lcom/olokobayusuf/natcam/CameraDevice$Callback;

    .line 124
    sget v3, Lcom/playstation/playlink/FakeNatCam;->lastRotation:I

    .line 125
    if-eqz v1, :cond_34

    if-nez v2, :cond_16

    goto :goto_34

    .line 128
    :cond_16
    const/4 v4, 0x1

    sput-boolean v4, Lcom/playstation/playlink/FakeNatCam;->upgrading:Z

    .line 130
    const/4 v4, 0x0

    :try_start_1a
    const-string v5, "playlink: upgrading fake preview to real camera"

    invoke-static {v0, v5}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 131
    invoke-static {}, Lcom/playstation/playlink/FakeNatCam;->stopAny()V

    .line 132
    invoke-virtual {v1, v3, v2}, Lcom/olokobayusuf/natcam/CameraDevice;->startPreview(ILcom/olokobayusuf/natcam/CameraDevice$Callback;)V
    :try_end_25
    .catchall {:try_start_1a .. :try_end_25} :catchall_26

    goto :goto_2c

    .line 133
    :catchall_26
    move-exception v1

    .line 134
    :try_start_27
    const-string v2, "playlink: upgrade to real failed"

    invoke-static {v0, v2, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    :try_end_2c
    .catchall {:try_start_27 .. :try_end_2c} :catchall_30

    .line 136
    :goto_2c
    sput-boolean v4, Lcom/playstation/playlink/FakeNatCam;->upgrading:Z

    .line 137
    nop

    .line 138
    return-void

    .line 136
    :catchall_30
    move-exception v0

    sput-boolean v4, Lcom/playstation/playlink/FakeNatCam;->upgrading:Z

    .line 137
    throw v0

    .line 126
    :cond_34
    :goto_34
    return-void

    .line 120
    :cond_35
    :goto_35
    return-void
.end method
