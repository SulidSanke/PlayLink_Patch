# PlayLink companion — Android 16 patch

Official PlayLink apps crash on current Android. This script patches **your** original APKs so they run again, including on Android 16.

**No APKs are included.** You supply the originals; patched files are written to your machine.

## Requirements

- Windows
- [Java 17+](https://adoptium.net/)
- [Python 3](https://www.python.org/downloads/) (tick *Add python.exe to PATH*)

## Usage

1. Get the original APKs. Filenames do not matter. Known-good versions:
   - That’s You! **1.6**
   - Knowledge is Power **1.5A**
   - Knowledge is Power: Decades **1.4**
   - Hidden Agenda **1.07**
   - Chimparty **1.2**
   - Frantics **1.8**
   - SingStar Mic **3.9**
2. Put them in the `originals` folder.
3. Run `patch.bat`.
4. Install the results from `out` (`*-android16.apk`).

## Connecting on PS5

PS5 does not answer PlayLink auto-discovery. **Play / Search will not find the console.** Use a manual IP instead. The Unity games remember it after you type it once.

Phone and PS5 must be on the **same Wi‑Fi**.

### Find the PS5 IP address

1. On the PS5, open **Settings** (gear in the top-right).
2. Open **Network**.
3. Open **Connection Status** (sometimes listed as **View Connection Status**).
4. Read **IP Address** — four numbers, e.g. `192.168.1.20`.

Paste that address into the IP / server field in the phone app, then connect.

Hidden Agenda uses multicast, not that IP box. SingStar Mic uses Sony’s own discovery screen; if search fails, the console IP from the steps above is still what you need on the same network.

SingStar Mic needs the **Microphone** permission. Allow it on first launch. If you already connected and saw “Mic unavailable”, grant Microphone in Android settings (Apps → SingStar Mic → Permissions) and connect again.

## What belongs in this repo

Scripts, `patch.bat`, and `tools/` (apktool, signer, `libnoaslr.so`). **No `.apk` files.**
