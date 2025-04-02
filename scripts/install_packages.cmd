@echo off
REM install_packages.cmd - Install required packages for the Research Agent

echo ===================================
echo Installing Required Packages
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

REM Install core dependencies
echo Installing core dependencies...
pip install openai>=1.0.0 python-dotenv>=1.0.0 requests>=2.28.0 aiohttp>=3.8.0 pydantic>=2.0.0

REM Install web search dependencies
echo Installing web search dependencies...
pip install duckduckgo-search>=3.0.0 google-api-python-client>=2.0.0 beautifulsoup4>=4.10.0

REM Install testing dependencies
echo Installing testing dependencies...
pip install pytest>=7.0.0 pytest-asyncio>=0.21.0 pytest-cov>=4.1.0 anyio>=4.0.0

echo ===================================
echo Package installation complete!
echo ===================================
