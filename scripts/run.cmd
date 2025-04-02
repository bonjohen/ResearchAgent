@echo off
REM run.cmd - Run the Research Agent

echo ===================================
echo Research Agent
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

REM Run the research agent
echo Starting Research Agent...
python run_research.py %*
if %ERRORLEVEL% neq 0 (
    echo Research Agent exited with an error.
    exit /b 1
)

echo ===================================
echo Research Agent completed successfully.
echo ===================================
