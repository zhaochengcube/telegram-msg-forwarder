#!/bin/bash

echo "正在启动 Telegram Bot..."
echo

# 检查虚拟环境是否存在并激活
if [ -d "venv" ]; then
    echo "激活虚拟环境 (venv)..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "激活虚拟环境 (.venv)..."
    source .venv/bin/activate
elif [ -d "env" ]; then
    echo "激活虚拟环境 (env)..."
    source env/bin/activate
else
    echo "警告: 未找到虚拟环境，使用系统Python"
fi

# 检查Python命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "错误: 未找到Python"
    exit 1
fi

echo "启动机器人..."
$PYTHON_CMD telegram_bot.py

echo
echo "机器人已停止运行"
read -p "按Enter键继续..."