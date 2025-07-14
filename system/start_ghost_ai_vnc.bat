@echo off
echo ========================================
echo    Ghost AI VNC Server Startup
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found, using system Python
)

REM Set environment variables (if not already set)
if "%DISCORD_TOKEN%"=="" (
    echo Warning: DISCORD_TOKEN not set
)
if "%ODDS_API_KEY%"=="" (
    echo Warning: ODDS_API_KEY not set
)

echo.
echo Starting Ghost AI deployment...
echo.

REM Run the deployment script
python vnc_deployment.py

echo.
echo Deployment complete!
echo Check logs/vnc_deployment.log for details
echo.
pause 