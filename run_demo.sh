#!/bin/bash
# Bitcoin Research Agent - Public Demo Launcher (Linux/Mac)
# ===========================================================

echo ""
echo "========================================"
echo "Bitcoin Research Agent - Public Demo"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.12+ from https://www.python.org/"
    exit 1
fi

echo "[INFO] Python detected..."
echo ""

# Check if dependencies are installed
echo "[INFO] Checking dependencies..."
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "[WARN] Streamlit not found. Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies"
        exit 1
    fi
fi

echo "[INFO] Dependencies OK"
echo ""

# Load environment variables (optional)
if [ -f .env ]; then
    echo "[INFO] Loading environment variables from .env"
    export $(grep -v '^#' .env | xargs)
fi

# Launch demo
echo "========================================"
echo "Launching Bitcoin Research Agent Demo..."
echo "========================================"
echo ""
echo "Demo will be available at:"
echo "  Local:    http://localhost:8501"
echo "  Network:  http://$(hostname -I | awk '{print $1}'):8501"
echo ""
echo "Press Ctrl+C to stop the demo"
echo ""

streamlit run src/demo/demo_app.py --server.headless true --server.port 8501

