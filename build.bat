@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   QuickKeys - Windows Build Script
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Download from https://www.python.org/downloads/
    exit /b 1
)

:: Display Python version
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo [INFO] Using %%v

:: Check if we are in the QuickKeys directory
if not exist "main.py" (
    echo [ERROR] main.py not found. Run this script from the QuickKeys directory.
    exit /b 1
)

if not exist "quickkeys.spec" (
    echo [ERROR] quickkeys.spec not found. Run this script from the QuickKeys directory.
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

:: Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip --quiet

:: Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    exit /b 1
)

:: Install PyInstaller
echo [INFO] Installing PyInstaller...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install PyInstaller.
    exit /b 1
)

:: Clean previous builds
echo [INFO] Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

:: Build
echo [INFO] Building QuickKeys...
echo.
pyinstaller quickkeys.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed. Check the output above for details.
    exit /b 1
)

:: Verify output
if exist "dist\QuickKeys.exe" (
    echo.
    echo ============================================================
    echo   Build successful!
    echo   Output: dist\QuickKeys.exe
    echo ============================================================
    for %%f in (dist\QuickKeys.exe) do echo   Size: %%~zf bytes
) else (
    echo.
    echo [ERROR] Build completed but QuickKeys.exe not found in dist\
    exit /b 1
)

:: Deactivate virtual environment
call deactivate

endlocal
