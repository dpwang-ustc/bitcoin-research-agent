@echo off
REM Bitcoin Research Agent - 定时任务调度器启动脚本 (Windows)

echo ========================================
echo Bitcoin Research Agent Scheduler
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found!
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)

REM 检查环境变量
if "%OPENAI_API_KEY%"=="" (
    echo Warning: OPENAI_API_KEY not set!
    echo Please set it: set OPENAI_API_KEY=sk-...
    echo.
    pause
)

REM 安装依赖
echo Checking dependencies...
pip install schedule pyyaml --quiet

REM 启动调度器
echo.
echo Starting scheduler...
echo.
python src/scheduler/task_scheduler.py

pause

