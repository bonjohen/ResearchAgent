@echo off
REM setup_ollama.cmd - Set up Ollama for the Research Agent

echo ===================================
echo Setting up Ollama
echo ===================================

REM Check if Ollama is installed
where ollama >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Ollama is not installed or not in PATH.
    echo Please install Ollama from https://ollama.ai/download
    echo After installation, run this script again.
    pause
    exit /b 1
)

echo Ollama is installed.

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

echo Ollama is running.

REM Pull the Llama3 7B model
echo Pulling Llama3 7B model...
ollama pull llama3:7b

echo ===================================
echo Ollama setup complete!
echo ===================================
echo.
echo You can now use the Research Agent with Ollama by running:
echo run.cmd --model ollama
echo.
pause
