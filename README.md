# PlayLink companion — patch na Android 16

Oficjalne aplikacje PlayLink (That’s You!, Knowledge is Power, Decades, Hidden Agenda) padają na nowym Androidzie. Ten skrypt przerabia **Twoje** oryginalne APK tak, żeby działały (m.in. na Androidzie 16).

**Nie ma tu gotowych APK.** Wrzucasz oryginały, dostajesz spatchowane pliki u siebie na dysku.

## Co trzeba

- Windows
- [Java 17+](https://adoptium.net/)
- [Python 3](https://www.python.org/downloads/) (zaznacz *Add python.exe to PATH*)

## Jak użyć

1. Pobierz oryginalne APK (wersje: That’s You! **1.6**, KiP **1.5A**, Decades **1.4**, Hidden Agenda **1.07**). Nazwa pliku jest obojętna.
2. Wrzuć je do folderu `originals`.
3. Odpal `patch.bat`.
4. Zainstaluj wynik z folderu `out` (`*-android16.apk`).

Na PS5 wyszukiwanie konsoli („Graj”) zwykle nie działa — wpisz IP ręcznie. Gra zapamięta je na tym telefonie.

## Co wolno wrzucać do tego repo

Skrypty, `patch.bat`, `tools/` (apktool, signer, `libnoaslr.so`). **Żadnych `.apk`.**
