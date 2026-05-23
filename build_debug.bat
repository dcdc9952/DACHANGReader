@echo off
chcp 65001 >nul
title DACHANG Reader Build - Debug Mode

echo ============================================
echo DACHANG Reader - Build Script (Debug Mode)
echo ============================================
echo.

echo [Step 1] Checking current directory...
cd
echo.
echo Press any key to continue...
pause >nul

echo [Step 2] Checking Python...
where python >nul 2>&1 && echo Python found || echo Python NOT found
echo.
echo Press any key to continue...
pause >nul

echo [Step 3] Checking for previous builds...
if exist "python-embed" (
    echo Found previous python-embed folder
) else (
    echo No previous build found
)
echo.
echo Press any key to continue...
pause >nul

echo [Step 4] Starting build process...
echo Downloading Python embedded version...
echo.

set PYTHON_ZIP=python-3.11.9-embed-amd64.zip
set PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip

echo URL: %PYTHON_URL%
echo File: %PYTHON_ZIP%
echo.

echo To run the FULL build, please use build_dachang_reader.bat instead.
echo This debug version stops here for testing.
echo.
echo Press any key to exit...
pause >nul
