@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ================================================
echo     大昌阅读器 - 一键构建 Windows exe
echo ================================================
echo.
echo 构建过程约需20-35分钟（首次需要下载Python）
echo.

set "SCRIPT_DIR=%~dp0"
set "BUILD_DIR=%TEMP%\dachang_reader_build_%RANDOM%"
set "APP_NAME=DACHANGReader"

echo [1/7] 创建构建目录...
if exist "%BUILD_DIR%" rd /s /q "%BUILD_DIR%"
mkdir "%BUILD_DIR%"
cd /d "%BUILD_DIR%"

echo [2/7] 下载Python 3.11.9（嵌入式版）...
if not exist "python-3.11.9-embed-amd64.zip" (
    echo 正在下载（约25MB）...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile 'python-3.11.9-embed-amd64.zip' -UseBasicParsing"
)
echo 下载完成，解压中...
powershell -Command "Expand-Archive -Force 'python-3.11.9-embed-amd64.zip' '.'"

echo [3/7] 启用pip（嵌入式Python需要修改配置）...
echo. > python311._pth
echo Uncomment to enable site-packages: >> python311._pth
echo import site >> python311._pth

echo [4/7] 下载pip...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py' -UseBasicParsing"

echo [5/7] 安装pip和依赖...
python.exe get-pip.py pip --quiet
if errorlevel 1 (
    echo pip安装失败，尝试备用方案...
    python.exe -m ensurepip --upgrade
    python.exe -m pip install --upgrade pip --quiet
)
python.exe -m pip install --upgrade pip --quiet
echo 安装PyQt5（较大，请等待约10分钟）...
python.exe -m pip install PyQt5==5.15.11 --quiet --no-cache-dir
if errorlevel 1 (
    echo PyQt5安装失败，尝试安装更小的版本...
    python.exe -m pip install PyQt5==5.15.10 --quiet --no-cache-dir
)
echo 安装PyInstaller...
python.exe -m pip install pyinstaller --quiet --no-cache-dir

echo [6/7] 复制源代码并开始打包（约5-10分钟）...
copy /y "%SCRIPT_DIR%dachang_reader.py" "." >nul 2>&1

echo 开始打包，这步需要几分钟，请耐心等待...
python.exe -m PyInstaller --name=%APP_NAME% --onedir --windowed --clean --noconfirm dachang_reader.py 2>nul

echo [7/7] 检查并复制结果...
if exist "dist\%APP_NAME%\%APP_NAME%.exe" (
    echo.
    echo ================================================
    echo     构建成功！
    echo ================================================
    echo.
    echo 正在复制程序到文件夹...
    copy "dist\%APP_NAME%\%APP_NAME%.exe" "%SCRIPT_DIR%" /y >nul 2>&1
    
    echo 复制支持文件...
    xcopy "dist\%APP_NAME%\*" "%SCRIPT_DIR%%APP_NAME%\" /e /y /q >nul 2>&1
    
    echo 创建书籍存储文件夹...
    if not exist "%SCRIPT_DIR%books" mkdir "%SCRIPT_DIR%books"
    
    echo.
    echo exe已生成: %SCRIPT_DIR%%APP_NAME%.exe
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
    echo 常见问题：
    echo   1. 网络连接失败 - 请确保网络正常
    echo   2. 杀毒软件拦截 - 请允许相关程序运行
    echo   3. 磁盘空间不足 - 需至少5GB可用空间
    echo.
    echo 按任意键退出...
    pause >nul
)