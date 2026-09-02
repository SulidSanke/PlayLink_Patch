@echo off
setlocal
cd /d "%~dp0"

where java >nul 2>nul
if errorlevel 1 (
  echo Java not found. Install JDK/JRE 17+ and try again.
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
  echo Python 3 not found. Install it from https://www.python.org/downloads/
  echo Enable "Add python.exe to PATH" during setup.
  pause
  exit /b 1
)

echo PlayLink Android 16 patcher
echo 1^) Put original APKs in the originals folder
echo 2^) This script writes *-android16.apk into out
echo.

%PY% patch_android16.py
set ERR=%ERRORLEVEL%
echo.
if not %ERR%==0 (
  echo Patch failed. Exit code: %ERR%
) else (
  echo Done.
)
pause
exit /b %ERR%
