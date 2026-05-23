@echo off
setlocal enabledelayedexpansion
:: ============================================
:: DACHANG Reader Builder - Safe Version
:: NO Chinese characters in code
:: ============================================
set "LOG_FILE=%TEMP%\dachang_build.log"
echo %date% %time% - Build started > "%LOG_FILE%"
:: Request admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs -WorkingDirectory '%~dp0'"
    exit /b
)
:: Set paths (avoid special chars)
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "BUILD_DIR=%USERPROFILE%\Desktop\dachang_build_%RANDOM%"
set "APP_NAME=DACHANGReader"
echo ================================================
echo     DACHANG Reader Builder
echo ================================================
echo.
echo [1/8] Creating build directory...
echo %date% %time% - Creating build dir >> "%LOG_FILE%"
if exist "%BUILD_DIR%" rd /s /q "%BUILD_DIR%" 2>nul
mkdir "%BUILD_DIR%" 2>nul
if not exist "%BUILD_DIR%" (
    echo ERROR: Cannot create build directory
    pause
    exit /b 1
)
cd /d "%BUILD_DIR%"
if %errorlevel% neq 0 (
    echo ERROR: Cannot enter build directory
    pause
    exit /b 1
)
echo Build dir: %BUILD_DIR%
echo OK
echo.
echo [2/8] Downloading Python...
echo %date% %time% - Downloading Python >> "%LOG_FILE%"
set "PYTHON_ZIP=python-3.11.9-embed-amd64.zip"
if not exist "%PYTHON_ZIP%" (
    echo Downloading Python 3.11.9...

    set "DOWNLOAD_OK=0"

    echo Trying official source...
    powershell -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile '%PYTHON_ZIP%' -UseBasicParsing -TimeoutSec 30; exit 0 } catch { exit 1 }" >nul 2>&1
    if !errorlevel! equ 0 set "DOWNLOAD_OK=1"

    if "!DOWNLOAD_OK!"=="0" (
        echo Trying mirror 1...
        powershell -Command "$ProgressPreference='SilentlyContinue'; try { Invoke-WebRequest -Uri 'https://mirrors.tuna.tsinghua.edu.cn/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile '%PYTHON_ZIP%' -UseBasicParsing -TimeoutSec 30; exit 0 } catch { exit 1 }" >nul 2>&1
        if !errorlevel! equ 0 set "DOWNLOAD_OK=1"
    )

    if "!DOWNLOAD_OK!"=="0" (
        echo Trying mirror 2...
        powershell -Command "$ProgressPreference='SilentlyContinue'; try { Invoke-WebRequest -Uri 'https://mirrors.huaweicloud.com/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile '%PYTHON_ZIP%' -UseBasicParsing -TimeoutSec 30; exit 0 } catch { exit 1 }" >nul 2>&1
        if !errorlevel! equ 0 set "DOWNLOAD_OK=1"
    )

    if "!DOWNLOAD_OK!"=="0" (
        echo.
        echo DOWNLOAD FAILED!
        echo Please manually download from:
        echo https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip
        echo.
        echo Place the file in: %BUILD_DIR%
        echo Then press any key to continue...
        pause >nul
        if not exist "%PYTHON_ZIP%" (
            echo File not found! Aborting.
            pause
            exit /b 1
        )
    )
)
echo Extracting Python...
powershell -Command "Expand-Archive -Force '%PYTHON_ZIP%' '.'" >nul 2>&1
if %errorlevel% neq 0 (
    echo Extraction failed!
    pause
    exit /b 1
)
echo OK
echo.
echo [3/8] Configuring Python...
echo %date% %time% - Configuring Python >> "%LOG_FILE%"
echo # > python311._pth
echo import site >> python311._pth
echo python311.zip >> python311._pth
echo . >> python311._pth
echo OK
echo.
echo [4/8] Installing pip...
echo %date% %time% - Installing pip >> "%LOG_FILE%"
python.exe -c "import ensurepip; ensurepip.bootstrap()" >nul 2>&1
if %errorlevel% neq 0 (
    echo Downloading get-pip.py...
    powershell -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py' -UseBasicParsing" >nul 2>&1
    if exist "get-pip.py" (
        python.exe get-pip.py --no-warn-script-location >nul 2>&1
    )
)
python.exe -c "import pip" >nul 2>&1
if %errorlevel% neq 0 (
    echo pip installation failed!
    pause
    exit /b 1
)
echo OK
echo.
echo [5/8] Installing dependencies...
echo %date% %time% - Installing dependencies >> "%LOG_FILE%"
set "PIP_MIRROR=https://mirrors.aliyun.com/pypi/simple/"
echo Installing PyQt5 (large, may take 10-15 min)...
python.exe -m pip install PyQt5==5.15.9 -i %PIP_MIRROR% --quiet --no-cache-dir --default-timeout=100
if %errorlevel% neq 0 (
    echo PyQt5 5.15.9 failed, trying 5.15.6...
    python.exe -m pip install PyQt5==5.15.6 -i %PIP_MIRROR% --quiet --no-cache-dir --default-timeout=100
    if %errorlevel% neq 0 (
        echo PyQt5 installation failed!
        pause
        exit /b 1
    )
)
echo PyQt5 OK
echo Installing ebooklib...
python.exe -m pip install ebooklib lxml -i %PIP_MIRROR% --quiet --no-cache-dir
echo OK
echo Installing PyMuPDF...
python.exe -m pip install PyMuPDF -i %PIP_MIRROR% --quiet --no-cache-dir
echo OK
echo Installing PyInstaller...
python.exe -m pip install pyinstaller==6.6.0 -i %PIP_MIRROR% --quiet --no-cache-dir
if %errorlevel% neq 0 (
    echo PyInstaller installation failed!
    pause
    exit /b 1
)
echo OK
echo.
echo [6/8] Copying source code...
echo %date% %time% - Copying source >> "%LOG_FILE%"
cd /d "%SCRIPT_DIR%"
if not exist "%SCRIPT_DIR%\dachang_reader.py" (
    echo ERROR: dachang_reader.py not found!
    pause
    exit /b 1
)
copy "%SCRIPT_DIR%\dachang_reader.py" "%BUILD_DIR%\" >nul
if exist "%SCRIPT_DIR%\requirements.txt" (
    copy "%SCRIPT_DIR%\requirements.txt" "%BUILD_DIR%\" >nul
)
echo OK
echo.
echo [7/8] Building EXE...
echo %date% %time% - Building EXE >> "%LOG_FILE%"
cd /d "%BUILD_DIR%"
if exist "build" rd /s /q "build" 2>nul
if exist "dist" rd /s /q "dist" 2>nul
echo Building (5-10 minutes)...
python.exe -m PyInstaller --name %APP_NAME% --onefile --windowed --noconsole --hidden-import=PyQt5 --hidden-import=PyQt5.QtWidgets --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtGui --hidden-import=ebooklib --hidden-import=lxml --hidden-import=fitz dachang_reader.py
if %errorlevel% neq 0 (
    echo.
    echo BUILD FAILED!
    pause
    exit /b 1
)
if not exist "%BUILD_DIR%\dist\%APP_NAME%.exe" (
    echo Executable not found!
    pause
    exit /b 1
)
echo OK
echo.
echo [8/8] Copying to destination...
echo %date% %time% - Copying EXE >> "%LOG_FILE%"
copy "%BUILD_DIR%\dist\%APP_NAME%.exe" "%SCRIPT_DIR%\" >nul
if %errorlevel% neq 0 (
    echo Copy failed but file at: %BUILD_DIR%\dist\%APP_NAME%.exe
) else (
    echo File copied to: %SCRIPT_DIR%
)
echo.
echo ================================================
echo     BUILD COMPLETED
echo ================================================
echo.
echo Output: %SCRIPT_DIR%\%APP_NAME%.exe
echo Log: %LOG_FILE%
echo.
set /p "CLEAN=Delete temp files? (Y/N): "
if /i "!CLEAN!"=="Y" (
    rd /s /q "%BUILD_DIR%" 2>nul
    echo Cleaned
)
endlocal
pause
exit /b 0