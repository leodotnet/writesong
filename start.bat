@echo off
chcp 65001 >nul
title WriteSong - AI歌词与音乐创作平台

echo.
echo ========================================
echo    WriteSong - AI歌词与音乐创作平台
echo ========================================
echo.

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
echo 默认端口：3027
echo 访问地址：http://localhost:3027
echo.
echo 按 Ctrl+C 停止应用
echo.

:: 启动应用（默认端口3027）
python app.py

:: 如果应用异常退出，暂停显示错误信息
if errorlevel 1 (
    echo.
    echo 应用启动失败，请检查错误信息
    pause
) 