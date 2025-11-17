@echo off
REM Create portable package for Video Manager

echo.
echo ============================================
echo Creating Portable Package
echo ============================================
echo.

REM Check if dist folder exists
if not exist "dist\VideoManager\VideoManager.exe" (
    echo ERROR: Executable not found!
    echo Please run build_professional_installer.bat first
    pause
    exit /b 1
)

echo [1/3] Preparing portable package...

REM Create output directory
if not exist "portable_release" mkdir "portable_release"

echo [2/3] Copying files...

REM Copy the entire VideoManager folder
xcopy "dist\VideoManager" "portable_release\VideoManager\" /E /I /Y /Q

REM Create README for portable version
echo Creating portable README...
(
echo Video Manager - Portable Version
echo ================================
echo.
echo This is the portable version of Video Manager.
echo No installation required!
echo.
echo How to Use:
echo -----------
echo 1. Extract this folder to any location
echo 2. Run VideoManager.exe
echo 3. All data will be stored in the 'storage' subfolder
echo.
echo Features:
echo ---------
echo - No administrator privileges required
echo - Runs from USB drives, network shares, etc.
echo - All data stays in the application folder
echo - Easy to backup - just copy the entire folder
echo.
echo First Run:
echo ----------
echo - Database and storage folders are created automatically
echo - No configuration needed
echo - Ready to use immediately
echo.
echo System Requirements:
echo -------------------
echo - Windows 7 SP1 or later
echo - 4GB RAM minimum
echo - 500MB free disk space
echo.
echo Support:
echo --------
echo - Check app.log in storage folder for errors
echo - See README.md for full documentation
echo.
echo Version: 1.0.0
echo Build Date: November 16, 2025
) > "portable_release\VideoManager\README_PORTABLE.txt"

echo [3/3] Creating ZIP archive...

REM Create ZIP file using PowerShell
powershell -Command "Compress-Archive -Path 'portable_release\VideoManager' -DestinationPath 'VideoManager_Portable_v1.0.0.zip' -Force"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create ZIP file
    pause
    exit /b 1
)

REM Clean up temporary folder
rmdir /s /q "portable_release"

echo.
echo ============================================
echo PORTABLE PACKAGE CREATED SUCCESSFULLY!
echo ============================================
echo.
echo Package: VideoManager_Portable_v1.0.0.zip
echo.
echo Distribution:
echo - Share the ZIP file with users
echo - Users extract and run VideoManager.exe
echo - No installation required
echo.
pause
