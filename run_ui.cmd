@echo off
REM run_ui.cmd - Run the Research Agent Web UI

echo ===================================
echo Research Agent Web UI
echo ===================================

REM Activate virtual environment if not already activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    if %ERRORLEVEL% neq 0 (
        echo Failed to activate virtual environment.
        echo Please run setup.cmd first.
        exit /b 1
    )
)

REM Install Flask if not already installed
pip show flask >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing Flask...
    pip install flask
)

REM Run the web UI
echo Starting web UI...
echo.
echo The web UI will be available at http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python -m src.ui.app

echo ===================================
echo Web UI stopped
echo ===================================

pause
