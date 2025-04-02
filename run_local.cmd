@echo off
REM run_local.cmd - Run the Research Agent with local models via Ollama

echo ===================================
echo Research Agent (Local Models)
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

REM Check if Ollama is running
curl -s http://localhost:11434/api/version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Ollama is not running.
    echo Starting Ollama...
    start "" ollama serve
    
    REM Wait for Ollama to start
    echo Waiting for Ollama to start...
    timeout /t 5 /nobreak >nul
    
    REM Check again if Ollama is running
    curl -s http://localhost:11434/api/version >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo Failed to start Ollama.
        echo Please start Ollama manually and run this script again.
        pause
        exit /b 1
    )
)

REM Run the Research Agent with Ollama
python run_research.py --model ollama %*

echo ===================================
echo Research completed!
echo ===================================

pause
