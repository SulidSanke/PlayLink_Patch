.class public final Lcom/playstation/playlink/SafeCopy;
.super Ljava/lang/Object;
.source "SafeCopy.java"


# direct methods
.method private constructor <init>()V
    .registers 1

    .line 7
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static copyRgba(Ljava/nio/ByteBuffer;IIILjava/nio/ByteBuffer;)V
    .registers 10

    .line 11
    if-eqz p0, :cond_3d

    if-eqz p4, :cond_3d

    if-lez p1, :cond_3d

    if-gtz p2, :cond_9

    goto :goto_3d

    .line 14
    :cond_9
    mul-int/lit8 p1, p1, 0x4

    .line 15
    if-ge p3, p1, :cond_e

    .line 16
    move p3, p1

    .line 18
    :cond_e
    new-array v0, p1, [B

    .line 19
    invoke-virtual {p0}, Ljava/nio/ByteBuffer;->position()I

    move-result v1

    .line 20
    invoke-virtual {p4}, Ljava/nio/ByteBuffer;->clear()Ljava/nio/Buffer;

    move-result-object v2

    check-cast v2, Ljava/nio/ByteBuffer;

    .line 21
    const/4 v2, 0x0

    const/4 v3, 0x0

    :goto_1c
    if-ge v3, p2, :cond_30

    .line 22
    mul-int v4, v3, p3

    add-int/2addr v4, v1

    invoke-virtual {p0, v4}, Ljava/nio/ByteBuffer;->position(I)Ljava/nio/Buffer;

    move-result-object v4

    check-cast v4, Ljava/nio/ByteBuffer;

    .line 23
    invoke-virtual {p0, v0, v2, p1}, Ljava/nio/ByteBuffer;->get([BII)Ljava/nio/ByteBuffer;

    .line 24
    invoke-virtual {p4, v0}, Ljava/nio/ByteBuffer;->put([B)Ljava/nio/ByteBuffer;

    .line 21
    add-int/lit8 v3, v3, 0x1

    goto :goto_1c

    .line 26
    :cond_30
    invoke-virtual {p4}, Ljava/nio/ByteBuffer;->rewind()Ljava/nio/Buffer;

    move-result-object p1

    check-cast p1, Ljava/nio/ByteBuffer;

    .line 27
    invoke-virtual {p0, v1}, Ljava/nio/ByteBuffer;->position(I)Ljava/nio/Buffer;

    move-result-object p0

    check-cast p0, Ljava/nio/ByteBuffer;

    .line 28
    return-void

    .line 12
    :cond_3d
    :goto_3d
    return-void
.end method
