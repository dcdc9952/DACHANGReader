@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ================================================
echo     DACHANG Reader - Build Windows EXE
echo ================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "BUILD_DIR=%TEMP%\dachang_reader_build_%RANDOM%"
set "APP_NAME=DACHANGReader"

echo [1/8] Creating build directory...
if exist "%BUILD_DIR%" rd /s /q "%BUILD_DIR%"
mkdir "%BUILD_DIR%"
cd /d "%BUILD_DIR%"
echo Done

echo.
echo [2/8] Downloading Python 3.11.9 (embedded)...
if not exist "python-3.11.9-embed-amd64.zip" (
    echo Downloading (~25MB)...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile 'python-3.11.9-embed-amd64.zip' -UseBasicParsing"
    if errorlevel 1 (
        echo Download failed! Check network connection.
        pause
        exit /b 1
    )
)
echo Extracting...
powershell -Command "Expand-Archive -Force 'python-3.11.9-embed-amd64.zip' '.'"
echo Done

echo.
echo [3/8] Enabling pip support (modify python311._pth)...
echo # > python311._pth
echo import site >> python311._pth
echo Done

echo.
echo [4/8] Installing pip...
python.exe -m ensurepip --upgrade 2>&1
if errorlevel 1 (
    echo ensurepip failed, trying alternative...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py' -UseBasicParsing"
    python.exe get-pip.py --quiet
)
python.exe -m pip --version >nul 2>&1
if errorlevel 1 (
    echo pip installation failed!
    pause
    exit /b 1
)
echo pip installed successfully

echo.
echo [5/8] Installing dependencies...
echo Installing PyQt5 (large, wait ~10-15 min)...
python.exe -m pip install PyQt5==5.15.11 --quiet --no-cache-dir
if errorlevel 1 (
    echo PyQt5 failed, trying 5.15.10...
    python.exe -m pip install PyQt5==5.15.10 --quiet --no-cache-dir
    if errorlevel 1 (
        echo PyQt5 installation failed!
        pause
        exit /b 1
    )
)
echo PyQt5 installed

echo Installing ebooklib and lxml...
python.exe -m pip install ebooklib lxml --quiet --no-cache-dir
if errorlevel 1 (
    echo ebooklib installation failed, continuing...
)

echo Installing PyMuPDF...
python.exe -m pip install PyMuPDF --quiet --no-cache-dir
if errorlevel 1 (
    echo PyMuPDF installation failed, continuing...
)

echo Installing PyInstaller...
python.exe -m pip install pyinstaller --quiet --no-cache-dir
if errorlevel 1 (
    echo PyInstaller installation failed!
    pause
    exit /b 1
)
echo Dependencies installed

echo.
echo [6/8] Copying source code...
if not exist "%SCRIPT_DIR%DACHANGReader" mkdir "%SCRIPT_DIR%DACHANGReader"
copy "%SCRIPT_DIR%dachang_reader.py" "%BUILD_DIR%\"
copy "%SCRIPT_DIR%requirements.txt" "%BUILD_DIR%\"
echo Done

echo.
echo [7/8] Building EXE with PyInstaller...
cd /d "%BUILD_DIR%"
echo Building (this takes 5-10 minutes)...
python.exe -m PyInstaller --name %APP_NAME% --onefile --windowed --disable-console --add-data "python311;python311" --hidden-import=PyQt5 --hidden-import=PyQt5.QtWidgets --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtGui --hidden-import=ebooklib --hidden-import=lxml --hidden-import=fitz dachang_reader.py
if errorlevel 1 (
    echo.
    echo BUILD FAILED! Check error messages above.
    pause
    exit /b 1
)
echo Build complete

echo.
echo [8/8] Copying EXE to script folder...
copy "%BUILD_DIR%\dist\%APP_NAME%.exe" "%SCRIPT_DIR%"
if errorlevel 1 (
    echo Copy failed, trying alternative path...
    copy "%BUILD_DIR%\dist\DACHANGReader.exe" "%SCRIPT_DIR%"
)
echo.
echo ================================================
echo     BUILD SUCCESS!
echo     DACHANGReader.exe has been created!
echo ================================================
echo.
echo To run: Double-click DACHANGReader.exe
echo.

endlocal
pause