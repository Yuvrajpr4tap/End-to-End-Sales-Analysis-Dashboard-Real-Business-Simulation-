@echo off
REM Quick-start script for Streamlit dashboard

echo.
echo ========================================
echo   Sales Intelligence Dashboard
echo   Streamlit Web Application
echo ========================================
echo.

REM Navigate to project directory
cd /d D:\DA

REM Install dependencies if needed
echo Installing dependencies...
pip install -q -r requirements.txt

echo.
echo ========================================
echo   Starting Dashboard... 
echo ========================================
echo.
echo 🎉 Dashboard will open in your browser
echo    Local URL: http://localhost:8501
echo    Press CTRL+C to stop
echo.

REM Run Streamlit app
streamlit run app.py

pause
