@echo off
REM run_ui_tests.cmd - Run the web UI tests

echo ===================================
echo Running Web UI Tests
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

REM Install required packages if not already installed
pip show selenium >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing Selenium...
    pip install selenium
)

REM Install webdriver-manager if not already installed
pip show webdriver-manager >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing webdriver-manager...
    pip install webdriver-manager
)

REM Run the web UI tests
echo Running web UI tests...

echo Testing Flask app endpoints...
python -m pytest tests/ui/test_flask_app.py -v

echo Testing web interface...
python -m pytest tests/ui/test_app.py -v

echo ===================================
echo Web UI tests completed!
echo ===================================

pause
