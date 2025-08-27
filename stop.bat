@echo off
REM ChronoGuard Pro Stop Script
REM Location: C:\Projects\chronoguard-pro

echo ============================================
echo  ChronoGuard Pro - Stopping Services
echo ============================================
echo.

REM Change to project directory
cd /d "C:\Projects\chronoguard-pro"

REM Check if Docker is available and containers are running
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Stopping Docker containers...
    docker-compose down
    
    if %errorlevel% equ 0 (
        echo [SUCCESS] All Docker services stopped successfully.
    ) else (
        echo [WARNING] Some containers may not have stopped cleanly.
    )
) else (
    echo [INFO] Docker not available - attempting to stop manual processes...
    
    REM Kill any Python processes running uvicorn
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq ChronoGuard Backend*" 2>nul
    
    REM Kill any Node processes
    taskkill /F /IM node.exe /FI "WINDOWTITLE eq ChronoGuard Frontend*" 2>nul
    
    echo [INFO] Attempted to stop manual processes.
)

echo.
echo All services have been stopped.
echo.
pause