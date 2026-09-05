# PlayLink companion — Android 16 patch

Official PlayLink apps crash on current Android. This script patches **your** original APKs so they run again, including on Android 16.

**No APKs are included.** You supply the originals; patched files are written to your machine.

## Requirements

- [Java 17+](https://adoptium.net/)
- [Python 3](https://www.python.org/downloads/)

On Windows, tick *Add python.exe to PATH* during Python installation.

The Python patcher also works on Linux; Fedora 44 has been tested with OpenJDK
25 and Python 3.14. On Fedora, install the supporting packages with:

```bash
sudo dnf install git python3 python3-lxml
```

Install an available OpenJDK 17 or newer package separately, then verify the
runtime before patching:

```bash
java -version
python3 --version
```

`android-tools` is optional and only needed when installing or testing the
result over ADB.

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
3. Run `patch.bat` on Windows, or run the Python patcher directly on Linux:
   ```bash
   python3 patch_android16.py
   ```
4. Install the results from `out` (`*-android16.apk`).

### Linux example

```bash
git clone https://github.com/SulidSanke/PlayLink_Patch.git
cd PlayLink_Patch

mkdir -p originals
cp /path/to/app.apk originals/

python3 patch_android16.py

ls -lh out/
```

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
