#!/bin/bash
# Bitcoin Research Agent - 定时任务调度器启动脚本 (Linux/Mac)

echo "========================================"
echo "Bitcoin Research Agent Scheduler"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found!"
    echo "Please install Python 3.8+"
    exit 1
fi

# 检查环境变量
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY not set!"
    echo "Please set it: export OPENAI_API_KEY=sk-..."
    echo ""
fi

# 安装依赖
echo "Checking dependencies..."
pip3 install schedule pyyaml --quiet

# 启动调度器
echo ""
echo "Starting scheduler..."
echo ""
python3 src/scheduler/task_scheduler.py

# Make script executable: chmod +x start_scheduler.sh

