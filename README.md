# PlayLink companion — Android 16 patch

Official PlayLink apps (That’s You!, Knowledge is Power, Decades, Hidden Agenda) crash on current Android. This script patches **your** original APKs so they run again, including on Android 16.

**No APKs are included.** You supply the originals; patched files are written to your machine.

## Requirements

- Windows
- [Java 17+](https://adoptium.net/)
- [Python 3](https://www.python.org/downloads/) (tick *Add python.exe to PATH*)

## Usage

1. Get the original APKs (That’s You! **1.6**, KiP **1.5A**, Decades **1.4**, Hidden Agenda **1.07**). Filenames do not matter.
2. Put them in the `originals` folder.
3. Run `patch.bat`.
4. Install the results from `out` (`*-android16.apk`).

On PS5, console auto-discovery (Play) usually fails — enter the IP manually. The game remembers it on that phone.

## What belongs in this repo

Scripts, `patch.bat`, and `tools/` (apktool, signer, `libnoaslr.so`). **No `.apk` files.**
