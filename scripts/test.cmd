@echo off
REM test.cmd - Run tests for the Research Agent

echo ===================================
echo Running Research Agent Tests
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

REM Run the tests
echo Running tests...
pytest tests -v
if %ERRORLEVEL% neq 0 (
    echo Tests failed.
    exit /b 1
)

echo ===================================
echo All tests passed successfully.
echo ===================================
