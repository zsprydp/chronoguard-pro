@echo off
echo =============================================
echo Starting ChronoGuard Pro Database API
echo =============================================
echo.

echo Initializing database...
python init_database.py
echo.

if errorlevel 1 (
    echo Database initialization failed!
    pause
    exit /b 1
)

echo Starting API server with database backend...
echo Visit: http://localhost:7000/docs for API documentation
echo.
python -m uvicorn db_main:app --reload --port 7000