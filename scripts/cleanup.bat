@echo off
echo Cleaning up old directories...
echo.

echo Stopping all processes first...
taskkill /f /im node.exe >nul 2>nul
taskkill /f /im python.exe >nul 2>nul

echo Waiting for processes to stop...
timeout /t 3 /nobreak >nul

echo Removing old directories...
if exist "backend" (
    echo Removing backend directory...
    rmdir /s /q "backend" 2>nul
)

if exist "frontend" (
    echo Removing frontend directory...
    rmdir /s /q "frontend" 2>nul
)

if exist "ml" (
    echo Removing ml directory...
    rmdir /s /q "ml" 2>nul
)

echo.
echo Cleanup completed!
echo You can now safely use the new monorepo structure.
echo.
pause
