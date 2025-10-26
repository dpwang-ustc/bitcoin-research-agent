@echo off
REM Bitcoin Research Agent - Public Demo Launcher (Windows)
REM ========================================================

echo.
echo ========================================
echo Bitcoin Research Agent - Public Demo
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.12+ from https://www.python.org/
    pause
    exit /b 1
)

echo [INFO] Python detected...
echo.

REM Check if dependencies are installed
echo [INFO] Checking dependencies...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo [WARN] Streamlit not found. Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [INFO] Dependencies OK
echo.

REM Set environment variables (optional)
if exist .env (
    echo [INFO] Loading environment variables from .env
    for /f "tokens=*" %%i in (.env) do set %%i
)

REM Launch demo
echo ========================================
echo Launching Bitcoin Research Agent Demo...
echo ========================================
echo.
echo Demo will be available at:
echo   Local:    http://localhost:8501
echo   Network:  http://your-ip:8501
echo.
echo Press Ctrl+C to stop the demo
echo.

streamlit run src/demo/demo_app.py --server.headless true --server.port 8501

pause

