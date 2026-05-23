@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================
echo     大昌阅读器 - 一键构建 Windows exe
echo ================================================
echo.
echo 构建过程约需15-25分钟（首次需要下载约25MB）
echo.

set PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip
set GETPIP_URL=https://bootstrap.pypa.io/get-pip.py
set BUILD_DIR=%TEMP%\dachang_reader_build
set APP_DIR=%~dp0
set APP_NAME=DACHANGReader

echo [1/6] 准备构建目录...
if exist "%BUILD_DIR%" rd /s /q "%BUILD_DIR%"
mkdir "%BUILD_DIR%"
cd /d "%BUILD_DIR%"

echo [2/6] 下载Python 3.11.9 嵌入式版...
if not exist "python-3.11.9-embed-amd64.zip" (
    echo 正在下载（约25MB）...
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile 'python-3.11.9-embed-amd64.zip' -UseBasicParsing"
)
echo 解压中...
powershell -Command "Expand-Archive -Force 'python-3.11.9-embed-amd64.zip' '.'"

echo [3/6] 下载pip安装脚本...
powershell -Command "Invoke-WebRequest -Uri '%GETPIP_URL%' -OutFile 'get-pip.py' -UseBasicParsing"

echo [4/6] 安装pip...
python.exe get-pip.py pip

echo [5/6] 安装PyQt5和PyInstaller（这步最久，请等待）...
echo 开始安装PyQt5（较大，请耐心等待约10分钟）...
python.exe -m pip install PyQt5==5.15.11 -q
echo 开始安装PyInstaller...
python.exe -m pip install pyinstaller -q

echo [6/6] 复制源代码并构建exe...
copy /y "%APP_DIR%dachang_reader.py" "." >nul
echo 开始打包（约5分钟）...
python.exe -m PyInstaller --name=%APP_NAME% --onedir --windowed --clean dachang_reader.py

if exist "dist\%APP_NAME%\%APP_NAME%.exe" (
    echo.
    echo ================================================
    echo     构建成功！
    echo ================================================
    echo.
    echo 正在复制程序到文件夹...
    copy "dist\%APP_NAME%\*" "%APP_DIR%" /y >nul
    
    echo 创建书籍存储文件夹...
    if not exist "%APP_DIR%books" mkdir "%APP_DIR%books"
    
    echo.
    echo exe已生成: %APP_DIR%%APP_NAME%.exe
    echo.
    echo 即将打开文件夹...
    timeout /t 3
    explorer "%APP_DIR%"
) else (
    echo.
    echo 构建失败，请检查上方错误信息
    pause
)