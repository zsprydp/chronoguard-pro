@echo off
echo =============================================
echo ChronoGuard Pro Database Testing Suite
echo =============================================
echo.

echo Step 1: Initializing database...
python init_database.py
echo.

if errorlevel 1 (
    echo Database initialization failed!
    pause
    exit /b 1
)

echo Step 2: Testing database with real API calls...
echo.
python test_database.py

echo.
echo =============================================
echo Testing completed! 
echo =============================================
echo.
echo You can also:
echo - Visit API docs: http://localhost:7000/docs  
echo - View frontend: http://localhost:7500
echo - Check TESTING.md for manual test instructions
echo.
pause