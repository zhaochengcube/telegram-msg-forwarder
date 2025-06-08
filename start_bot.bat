@echo off
chcp 65001 > nul
echo 正在启动 Telegram Bot...
echo.

REM 检查虚拟环境是否存在
if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\Activate.ps1" (
    echo 激活虚拟环境...
    powershell -ExecutionPolicy Bypass -File "venv\Scripts\Activate.ps1"
) else (
    echo 警告: 未找到虚拟环境，使用系统Python
)

echo 启动机器人...
python3 telegram_bot.py

echo.
echo 机器人已停止运行
pause 