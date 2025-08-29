@echo off
echo Stopping ChronoGuard Pro Development Environment...
echo.

echo Stopping all Node.js processes...
taskkill /f /im node.exe >nul 2>nul

echo Stopping all Python processes...
taskkill /f /im python.exe >nul 2>nul

echo Stopping Docker containers...
docker-compose down >nul 2>nul

echo.
echo All services stopped successfully!
echo.
pause
