@echo off
echo ==========================================
echo   Bitcoin Research Agent Dashboard
echo ==========================================
echo.
echo Starting Streamlit dashboard...
echo.
streamlit run src/dashboard/app.py --server.port 8501

