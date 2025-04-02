@echo off
REM setup.cmd - Environment setup script for Research Agent

echo ===================================
echo Research Agent Setup
echo ===================================

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment.
        echo Please ensure Python 3.8+ is installed and in your PATH.
        exit /b 1
    )
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment.
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install dependencies.
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please update the .env file with your API keys and configuration.
)

REM Create data directories
echo Creating data directories...
if not exist data mkdir data
if not exist data\.gitkeep type nul > data\.gitkeep

echo ===================================
echo Setup complete! 
echo ===================================
echo To activate the environment, run:
echo   call venv\Scripts\activate.bat
echo To run the research agent, run:
echo   scripts\run.cmd
echo ===================================
