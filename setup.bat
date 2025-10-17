@echo off
REM Setup script for Windows

echo ========================================
echo LLM Code Deployment System - Setup
echo ========================================
echo.

REM Check Node.js
echo [1/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    exit /b 1
)
echo ✓ Node.js found

REM Check Python
echo [2/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python from https://python.org/
    exit /b 1
)
echo ✓ Python found

REM Install Node.js dependencies
echo [3/6] Installing Node.js dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: npm install failed
    exit /b 1
)
echo ✓ Node.js dependencies installed

REM Install Python dependencies
echo [4/6] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed
    exit /b 1
)
echo ✓ Python dependencies installed

REM Install Playwright browsers
echo [5/6] Installing Playwright browsers...
python -m playwright install chromium
if errorlevel 1 (
    echo WARNING: Playwright browser installation may have failed
)
echo ✓ Playwright setup complete

REM Setup environment file
echo [6/6] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo ✓ Created .env file from template
    echo.
    echo IMPORTANT: Please edit .env file with your credentials:
    echo   - STUDENT_EMAIL
    echo   - STUDENT_SECRET
    echo   - GITHUB_TOKEN
    echo   - GITHUB_USERNAME
    echo   - OPENAI_API_KEY or ANTHROPIC_API_KEY
) else (
    echo ✓ .env file already exists
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Edit .env with your credentials
echo   2. Initialize database: python scripts/instructor/init_db.py
echo   3. Start student API: npm start
echo.
echo For detailed instructions, see QUICKSTART.md
echo.

pause
