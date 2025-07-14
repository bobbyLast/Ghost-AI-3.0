@echo off
echo.
echo ========================================
echo    GHOST AI 3.0 PRODUCTION SYSTEM
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate.bat
    echo Then: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check environment variables
if "%ODDS_API_KEY%"=="" (
    echo WARNING: ODDS_API_KEY not set
    echo Discord features will be disabled
    echo.
)

if "%DISCORD_TOKEN%"=="" (
    echo WARNING: DISCORD_TOKEN not set
    echo Discord features will be disabled
    echo.
)

echo Starting Ghost AI 3.0 Production System...
echo.
echo Features:
echo - 24/7 Autonomous Operation
echo - Daily Picks Generation (9 AM)
echo - Health Monitoring
echo - Performance Tracking
echo - Discord Integration (if token provided)
echo.
echo Press Ctrl+C to stop the system
echo.

REM Start the production system
python start_production.py

echo.
echo Production system stopped.
pause 