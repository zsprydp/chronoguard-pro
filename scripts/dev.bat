@echo off
echo Starting ChronoGuard Pro Development Environment...
echo.

echo Checking prerequisites...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo Prerequisites check passed!
echo.

echo Installing dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install root dependencies
    pause
    exit /b 1
)

cd packages\frontend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)

cd ..\backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)

echo Dependencies installed successfully!
echo.

echo Initializing database...
python init_database.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)

echo Database initialized successfully!
echo.

echo Starting development servers...
echo Backend will start on http://localhost:7000
echo Frontend will start on http://localhost:7501
echo.

cd ..\..
start "ChronoGuard Backend" cmd /k "cd packages\backend && python -m uvicorn app.db_main:app --reload --port 7000"
timeout /t 3 /nobreak >nul
start "ChronoGuard Frontend" cmd /k "cd packages\frontend && npm run dev -- --port 7501"

echo.
echo Development environment started!
echo Close this window to continue working.
echo.
pause
