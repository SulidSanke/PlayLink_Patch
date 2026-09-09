# Changelog

All notable changes to the PlayLink companion patcher are listed here.

## Unreleased / current main

### Community pull requests

- **[#1](https://github.com/SulidSanke/PlayLink_Patch/pull/1)** — Fix legacy Unity `JNIBridge` / `ServiceConnection` crash on newer Android (three-argument `onServiceConnected`). Tested on Pixel 9a **Android 17**.
- **[#2](https://github.com/SulidSanke/PlayLink_Patch/pull/2)** — Document Linux patcher usage and required dependencies.

### Patcher

- Rename output APKs from `*-android16.apk` to `*-patched.apk`.
- **Knowledge is Power: Decades 1.4** — hybrid NatCam for Android 16+:
  - real Camera2 + GL preview only on character-select selfie (`PHOTO_TAKING` / profile photo stage);
  - black fake frames for mid-match NatCam FaceDetection blips (avoids feeding HAL buffers into Unity 2017);
  - rematch: clear latch on avatar selection / upgrade fake→real if preview started early;
  - ImageReader fast-path + `SafeCopy` for still photos;
  - skip Unity’s fatal “more that 16GB of memory” abort path in `libunity.so` (arm64).
- Unity wrap.sh + `libnoaslr.so` flow unchanged for IL2CPP games.
- SingStar Mic runtime microphone permission (earlier).
- Manifest / `targetSdkVersion` compatibility for older PlayLink APKs (earlier).

### Docs

- README: known issues (16GB / overlays / base KiP pending), PS5 IP, Linux notes.
- This changelog.
