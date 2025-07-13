@echo off
chcp 65001 >nul
title WriteSong - AI歌词与音乐创作平台

echo.
echo ========================================
echo    WriteSong - AI歌词与音乐创作平台
echo ========================================
echo.

:: 设置默认参数
set DEFAULT_PORT=3027
set DEFAULT_HOST=0.0.0.0

:: 检查命令行参数
if "%1"=="" (
    set PORT=%DEFAULT_PORT%
) else (
    set PORT=%1
)

if "%2"=="" (
    set HOST=%DEFAULT_HOST%
) else (
    set HOST=%2
)

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python 3.8+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查虚拟环境是否存在
if not exist "venv\Scripts\activate.bat" (
    echo 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo 错误：创建虚拟环境失败
        pause
        exit /b 1
    )
)

:: 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

:: 安装依赖
echo 检查并安装依赖...
pip install -r requirements.txt

:: 运行数据库迁移
echo 运行数据库迁移...
python migrate_db.py
python migrate_music_api.py

:: 启动应用
echo.
echo 启动WriteSong应用...
echo 主机: %HOST%
echo 端口: %PORT%
echo 访问地址: http://localhost:%PORT%
echo.
echo 使用说明:
echo   start_advanced.bat [端口] [主机]
echo   例如: start_advanced.bat 8080 127.0.0.1
echo.
echo 按 Ctrl+C 停止应用
echo.

:: 启动应用
python app.py --port %PORT% --host %HOST%

:: 如果应用异常退出，暂停显示错误信息
if errorlevel 1 (
    echo.
    echo 应用启动失败，请检查错误信息
    pause
) 