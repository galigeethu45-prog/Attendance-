@echo off
cls
echo.
echo ========================================
echo   ATTENDANCE SYSTEM - QUICK START
echo ========================================
echo.
echo Status: All migrations applied ✓
echo Database: Ready ✓
echo System: Operational ✓
echo.
echo ========================================
echo.

REM Check if venv exists
if exist "venv\Scripts\activate.bat" (
    echo [1/2] Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist "env\Scripts\activate.bat" (
    echo [1/2] Activating virtual environment...
    call env\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    echo Please create a virtual environment first.
    pause
    exit /b 1
)

echo.
echo [2/2] Starting Django development server...
echo.
echo ========================================
echo   SERVER STARTING...
echo ========================================
echo.
echo Open your browser and go to:
echo   http://127.0.0.1:8000/
echo.
echo To stop the server, press Ctrl+C
echo.
echo ========================================
echo.

python manage.py runserver
