@echo off
echo Building ChronoGuard Pro...
echo.

echo Building frontend...
cd packages\frontend
call npm run build
if %errorlevel% neq 0 (
    echo ERROR: Frontend build failed
    pause
    exit /b 1
)

echo Frontend build completed!
echo.

echo Building backend...
cd ..\backend
echo Backend build completed (Python - no build step required)!

echo.
echo Build completed successfully!
echo.
pause
