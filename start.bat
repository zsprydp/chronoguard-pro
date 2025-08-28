@echo off
REM ChronoGuard Pro Startup Script
REM Location: C:\Projects\chronoguard-pro
REM Repository: https://github.com/zsprydp/chronoguard-pro

echo ============================================
echo  ChronoGuard Pro - AI Appointment Platform
echo ============================================
echo.
echo Repository: https://github.com/zsprydp/chronoguard-pro
echo Local Path: C:\Projects\chronoguard-pro
echo.
echo Starting ChronoGuard Pro services...
echo.

REM Change to project directory
cd /d "C:\Projects\chronoguard-pro"

REM First try manual setup (more reliable for development)
echo [INFO] Starting in development mode...
echo.
echo [WARNING] This requires:
echo  - Python 3.10+ installed
echo  - Node.js 18+ installed
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ and try again.
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo Please install Node.js 18+ and try again.
    pause
    exit /b 1
)

echo [INFO] Both Python and Node.js detected!
echo.

REM Copy environment file if it doesn't exist
if not exist .env (
    echo [INFO] Creating .env file from template...
    copy .env.example .env >nul
)

REM Install backend dependencies if needed
if not exist "backend\venv" (
    echo [INFO] Setting up Python virtual environment...
    cd backend
    python -m venv venv
    cd ..
)

REM Install frontend dependencies if needed
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd frontend
    npm install
    cd ..
)

echo [INFO] Initializing database...
cd backend
python init_database.py
if %errorlevel% neq 0 (
    echo [ERROR] Database initialization failed!
    pause
    exit /b 1
)
cd ..

echo [INFO] Starting backend server with database (port 7000)...
start "ChronoGuard Backend" cmd /k "cd /d C:\Projects\chronoguard-pro\backend && python -m uvicorn app.db_main:app --reload --port 7000"

echo [INFO] Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul

echo [INFO] Starting frontend server (port 7501)...
start "ChronoGuard Frontend" cmd /k "cd /d C:\Projects\chronoguard-pro\frontend && npm run dev -- --port 7501"

echo.
echo ============================================
echo  ChronoGuard Pro is starting up!
echo ============================================
echo.
echo Access Points:
echo  Frontend Dashboard: http://localhost:7501
echo  Backend API:        http://localhost:7000
echo  API Documentation:  http://localhost:7000/docs
echo.
echo Demo Login Credentials:
echo  Email: demo@chronoguard.com
echo  Password: demo123
echo.
echo Both servers are starting in separate command windows.
echo Wait 30-60 seconds for all services to be ready.
echo.
echo Database: SQLite (ready to use, no setup required)
echo Full database integration with real data persistence.
echo.
echo To stop: Close the command windows or run stop.bat
echo.
pause