@echo off
REM Quick setup script for LinkedIn Engagement Automation (Windows)

echo ==================================
echo LinkedIn Engagement Automation
echo Setup Script
echo ==================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)
echo [OK] Python found
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo X Failed to create virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo X Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install chromium
if errorlevel 1 (
    echo X Failed to install Playwright browsers
    pause
    exit /b 1
)
echo [OK] Playwright browsers installed
echo.

REM Create .env from example
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo [OK] .env file created
    echo [!] Please edit .env and add your credentials
) else (
    echo [i] .env file already exists
)
echo.

REM Create data directory
echo Creating data directory...
if not exist data mkdir data
echo [OK] Data directory created
echo.

echo ==================================
echo Setup Complete!
echo ==================================
echo.
echo Next steps:
echo 1. Edit .env and add your LinkedIn credentials and API keys
echo 2. Edit config.yaml and add profiles to track
echo 3. Run: python main.py check
echo 4. Run: python main.py run
echo.
echo For more information, see README.md
echo.
pause
