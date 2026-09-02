@echo off
setlocal
cd /d "%~dp0"

where java >nul 2>nul
if errorlevel 1 (
  echo Brak Java. Zainstaluj JDK/JRE 17+ i sprobuj ponownie.
  echo https://adoptium.net/
  pause
  exit /b 1
)

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
  where python >nul 2>nul && set "PY=python"
)
if not defined PY (
  echo Brak Pythona 3. Zainstaluj z https://www.python.org/downloads/
  echo Przy instalacji zaznacz "Add python.exe to PATH".
  pause
  exit /b 1
)

echo PlayLink Android 16 patcher
echo 1^) Wrzuc oryginalne APK do folderu originals
echo 2^) Ten skrypt zrobi *-android16.apk w folderze out
echo.

%PY% patch_android16.py
set ERR=%ERRORLEVEL%
echo.
if not %ERR%==0 (
  echo Patch nie wyszedl. Kod: %ERR%
) else (
  echo Gotowe.
)
pause
exit /b %ERR%
