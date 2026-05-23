@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ================================================
echo     大昌阅读器 - 一键构建 Windows exe
echo ================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "BUILD_DIR=%TEMP%\dachang_reader_build_%RANDOM%"
set "APP_NAME=DACHANGReader"

echo [1/8] 创建构建目录...
if exist "%BUILD_DIR%" rd /s /q "%BUILD_DIR%"
mkdir "%BUILD_DIR%"
cd /d "%BUILD_DIR%"
echo 完成

echo.
echo [2/8] 下载Python 3.11.9（嵌入式版）...
if not exist "python-3.11.9-embed-amd64.zip" (
    echo 正在下载（约25MB）...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile 'python-3.11.9-embed-amd64.zip' -UseBasicParsing"
    if errorlevel 1 (
        echo 下载失败，请检查网络连接
        pause
        exit /b 1
    )
)
echo 下载完成，解压中...
powershell -Command "Expand-Archive -Force 'python-3.11.9-embed-amd64.zip' '.'"
echo 完成

echo.
echo [3/8] 启用pip支持（修改python311._pth）...
echo # > python311._pth
echo import site >> python311._pth
echo 完成

echo.
echo [4/8] 安装pip...
python.exe -m ensurepip --upgrade 2>&1
if errorlevel 1 (
    echo ensurepip失败，尝试备用方案...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py' -UseBasicParsing"
    python.exe get-pip.py --quiet
)
python.exe -m pip --version >nul 2>&1
if errorlevel 1 (
    echo pip安装失败！
    pause
    exit /b 1
)
echo pip安装成功

echo.
echo [5/8] 安装依赖库...
echo 安装PyQt5（较大，请等待约10-15分钟）...
python.exe -m pip install PyQt5==5.15.11 --quiet --no-cache-dir
if errorlevel 1 (
    echo PyQt5安装失败，尝试5.15.10版本...
    python.exe -m pip install PyQt5==5.15.10 --quiet --no-cache-dir
    if errorlevel 1 (
        echo PyQt5安装失败！
        pause
        exit /b 1
    )
)
echo PyQt5安装成功

echo 安装ebooklib和lxml...
python.exe -m pip install ebooklib lxml --quiet --no-cache-dir
if errorlevel 1 (
    echo ebooklib安装失败，继续...
)

echo 安装PyMuPDF...
python.exe -m pip install PyMuPDF --quiet --no-cache-dir
if errorlevel 1 (
    echo PyMuPDF安装失败，继续...
)

echo 安装PyInstaller...
python.exe -m pip install pyinstaller --quiet --no-cache-dir
if errorlevel 1 (
    echo PyInstaller安装失败！
    pause
    exit /b 1
)
echo 依赖安装完成

echo.
echo [6/8] 复制源代码...
copy /y "%SCRIPT_DIR%dachang_reader.py" "." >nul 2>&1
if errorlevel 1 (
    echo 源代码复制失败！
    pause
    exit /b 1
)
echo 完成

echo.
echo [7/8] 开始打包（约5-10分钟）...
echo 请耐心等待，这步需要几分钟...
python.exe -m PyInstaller --name=%APP_NAME% --onedir --windowed --clean --noconfirm --hidden-import=PyQt5 --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtGui --hidden-import=PyQt5.QtWidgets --hidden-import=ebooklib --hidden-import=ebooklib.epub --hidden-import=lxml --hidden-import=fitz dachang_reader.py

echo.
echo [8/8] 检查并复制结果...
if exist "dist\%APP_NAME%\%APP_NAME%.exe" (
    echo.
    echo ================================================
    echo     构建成功！
    echo ================================================
    echo.
    echo 正在复制程序到文件夹...

    copy "dist\%APP_NAME%\%APP_NAME%.exe" "%SCRIPT_DIR%" /y >nul 2>&1

    if not exist "%SCRIPT_DIR%%APP_NAME%" mkdir "%SCRIPT_DIR%%APP_NAME%"
    xcopy "dist\%APP_NAME%\*" "%SCRIPT_DIR%%APP_NAME%\" /e /y /q >nul 2>&1

    if not exist "%SCRIPT_DIR%books" mkdir "%SCRIPT_DIR%books"

    echo.
    echo exe已生成: %SCRIPT_DIR%%APP_NAME%.exe
    echo 程序目录: %SCRIPT_DIR%%APP_NAME%\
    echo.
    echo 即将打开文件夹...
    timeout /t 3 >nul
    explorer "%SCRIPT_DIR%"
) else (
    echo.
    echo ================================================
    echo     构建失败！
    echo ================================================
    echo.
    echo 请检查上方错误信息，或将错误截图发给我。
    echo.
    echo 按任意键退出...
    pause >nul
)