@echo off
REM migrate_data.cmd - Migrate data from temp_data to external storage

echo ===================================
echo Migrating Research Agent Data
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

REM Run the migration script
python scripts/migrate_data.py

echo ===================================
echo Migration complete!
echo ===================================

pause
