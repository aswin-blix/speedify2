@echo off
setlocal
title Speedify Build

echo ============================================
echo   Speedify ^| Windows Installer Builder
echo ============================================
echo.

:: ── 1. Ensure dependencies ───────────────────────────────────────────────────
echo [1/4] Installing build dependencies...
pip install pyinstaller psutil --quiet --disable-pip-version-check
if errorlevel 1 (
    echo ERROR: pip install failed. Make sure Python is in PATH.
    pause & exit /b 1
)
echo       Done.
echo.

:: ── 2. Build the main app exe ────────────────────────────────────────────────
echo [2/4] Building speedify.exe...
pyinstaller speedify.spec --noconfirm --clean
if errorlevel 1 (
    echo ERROR: speedify build failed.
    pause & exit /b 1
)
if not exist "dist\speedify.exe" (
    echo ERROR: dist\speedify.exe not found after build.
    pause & exit /b 1
)
echo       Done: dist\speedify.exe
echo.

:: ── 3. Build the installer exe ───────────────────────────────────────────────
echo [3/4] Building Speedify-Setup.exe...
pyinstaller installer.spec --noconfirm --clean
if errorlevel 1 (
    echo ERROR: installer build failed.
    pause & exit /b 1
)
if not exist "dist\Speedify-Setup.exe" (
    echo ERROR: dist\Speedify-Setup.exe not found after build.
    pause & exit /b 1
)
echo       Done: dist\Speedify-Setup.exe
echo.

:: ── 4. Report ────────────────────────────────────────────────────────────────
echo [4/4] Build complete!
echo.
echo   App exe  : dist\speedify.exe
echo   Installer: dist\Speedify-Setup.exe  ^<-- share this file
echo.
echo Share "dist\Speedify-Setup.exe" with anyone running Windows.
echo They can double-click it to install Speedify.
echo.
pause
endlocal
