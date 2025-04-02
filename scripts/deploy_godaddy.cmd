@echo off
REM deploy_godaddy.cmd - Deploy the Research Agent to GoDaddy hosting

echo ===================================
echo Research Agent Deployment to GoDaddy
echo ===================================

REM Check if required environment variables are set
if not defined GODADDY_HOST (
    echo Error: GODADDY_HOST environment variable is not set.
    echo Please set the following environment variables:
    echo   GODADDY_HOST - The hostname for your GoDaddy server
    echo   GODADDY_USER - Your GoDaddy SSH username
    echo   GODADDY_PATH - The path to deploy the application on the server
    exit /b 1
)

if not defined GODADDY_USER (
    echo Error: GODADDY_USER environment variable is not set.
    exit /b 1
)

if not defined GODADDY_PATH (
    echo Error: GODADDY_PATH environment variable is not set.
    exit /b 1
)

REM Create deployment package
echo Creating deployment package...
if not exist "deploy" mkdir deploy
xcopy /E /Y /EXCLUDE:scripts\deploy_exclude.txt . deploy\

REM Create WSGI file if it doesn't exist
if not exist "deploy\wsgi.py" (
    echo Creating WSGI file...
    echo import os > deploy\wsgi.py
    echo from src.ui.app import app as application >> deploy\wsgi.py
    echo if __name__ == "__main__": >> deploy\wsgi.py
    echo     application.run^(^) >> deploy\wsgi.py
)

REM Create .htaccess file for Apache
echo Creating .htaccess file...
echo RewriteEngine On > deploy\.htaccess
echo RewriteCond %%{REQUEST_FILENAME} !-f >> deploy\.htaccess
echo RewriteRule ^(.*)$ /wsgi.py/$1 [QSA,L] >> deploy\.htaccess

REM Create requirements file for deployment
echo Creating deployment requirements...
echo flask>=2.0.0 > deploy\requirements.txt
echo python-dotenv>=1.0.0 >> deploy\requirements.txt
echo gunicorn>=20.1.0 >> deploy\requirements.txt
echo whitenoise>=6.0.0 >> deploy\requirements.txt
echo openai>=1.0.0 >> deploy\requirements.txt
echo requests>=2.28.0 >> deploy\requirements.txt
echo aiohttp>=3.8.0 >> deploy\requirements.txt
echo pydantic>=2.0.0 >> deploy\requirements.txt
echo duckduckgo-search>=3.0.0 >> deploy\requirements.txt
echo beautifulsoup4>=4.10.0 >> deploy\requirements.txt
echo rich>=13.0.0 >> deploy\requirements.txt
echo tqdm>=4.65.0 >> deploy\requirements.txt

REM Create deploy_exclude.txt if it doesn't exist
if not exist "scripts\deploy_exclude.txt" (
    echo Creating deployment exclusion list...
    echo .git\ > scripts\deploy_exclude.txt
    echo .github\ >> scripts\deploy_exclude.txt
    echo .vscode\ >> scripts\deploy_exclude.txt
    echo __pycache__\ >> scripts\deploy_exclude.txt
    echo venv\ >> scripts\deploy_exclude.txt
    echo tests\ >> scripts\deploy_exclude.txt
    echo .env >> scripts\deploy_exclude.txt
    echo .gitignore >> scripts\deploy_exclude.txt
    echo deploy\ >> scripts\deploy_exclude.txt
    echo *.pyc >> scripts\deploy_exclude.txt
)

REM Compress the deployment package
echo Compressing deployment package...
powershell Compress-Archive -Path deploy\* -DestinationPath deploy\research_agent.zip -Force

REM Upload to GoDaddy using SCP
echo Uploading to GoDaddy...
echo This will prompt for your password.
scp deploy\research_agent.zip %GODADDY_USER%@%GODADDY_HOST%:%GODADDY_PATH%

REM Execute remote commands to unpack and set up the application
echo Setting up the application on the server...
ssh %GODADDY_USER%@%GODADDY_HOST% "cd %GODADDY_PATH% && unzip -o research_agent.zip && pip install -r requirements.txt && touch tmp/restart.txt"

echo ===================================
echo Deployment completed!
echo ===================================
echo Your Research Agent should now be available at:
echo https://%GODADDY_HOST%/
echo 
echo If you encounter any issues, check the server logs at:
echo %GODADDY_PATH%/logs/error.log
echo ===================================

pause
