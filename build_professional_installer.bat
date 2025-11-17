@echo off
REM ============================================
REM Video Manager - Professional Installer Build Script
REM ============================================

echo.
echo ============================================
echo Video Manager - Professional Build
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/6] Checking dependencies...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Check if all required packages are installed
echo Verifying required packages...
pip install -r requirements.txt --quiet

echo.
echo [2/6] Cleaning previous builds...
echo.

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "database\__pycache__" rmdir /s /q "database\__pycache__"
if exist "ui\__pycache__" rmdir /s /q "ui\__pycache__"
if exist "utils\__pycache__" rmdir /s /q "utils\__pycache__"
if exist "VideoManager_Setup.exe" del /q "VideoManager_Setup.exe"

echo.
echo [3/6] Building executable with PyInstaller...
echo.

REM Build with PyInstaller
pyinstaller --clean VideoManager.spec

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo [4/6] Verifying build...
echo.

if not exist "dist\VideoManager\VideoManager.exe" (
    echo ERROR: VideoManager.exe was not created
    pause
    exit /b 1
)

echo Build successful!
echo.

REM Check if NSIS is installed
echo [5/6] Checking for NSIS installer...
echo.

where makensis >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: NSIS is not installed or not in PATH
    echo.
    echo To create the installer, please:
    echo 1. Download NSIS from: https://nsis.sourceforge.io/Download
    echo 2. Install NSIS
    echo 3. Add NSIS to your PATH or run: makensis installer_setup.nsi
    echo.
    echo The executable is ready in: dist\VideoManager\
    echo.
    pause
    exit /b 0
)

echo [6/6] Creating installer with NSIS...
echo.

REM Create installer with NSIS
makensis installer_setup.nsi

if errorlevel 1 (
    echo.
    echo ERROR: NSIS installer creation failed
    pause
    exit /b 1
)

echo.
echo ============================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ============================================
echo.
echo Installer created: VideoManager_Setup.exe
echo Portable version: dist\VideoManager\
echo.
echo You can now distribute VideoManager_Setup.exe
echo.
pause
