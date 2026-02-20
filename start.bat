@echo off
echo === Price List Lookup ===

:: Kill any existing server on port 5000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do (
    echo Stopping existing server (PID %%a)...
    taskkill /PID %%a /F >nul 2>&1
)

:: Create venv if it doesn't exist
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment. Is Python installed?
        echo Download Python from https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

:: Activate venv
call .venv\Scripts\activate.bat

:: Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet

:: Open browser after a short delay, then start server
echo.
echo Starting server at http://localhost:5000
echo Press Ctrl+C to stop.
echo.
start "" http://localhost:5000
python app.py
