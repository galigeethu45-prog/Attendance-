@echo off
echo ========================================
echo   AttendanceHub - Starting Server
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Virtual environment activated!
echo.

REM Check if migrations are needed
echo Checking database...
python manage.py migrate --check >nul 2>&1
if errorlevel 1 (
    echo Running migrations...
    python manage.py migrate
)

echo.
echo ========================================
echo   Server Starting...
echo ========================================
echo.
echo Access the application at:
echo   http://localhost:8000/
echo.
echo Login Credentials:
echo   HR Admin: hr_admin / admin123
echo   Employee: employee1 / emp123
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start Django development server
python manage.py runserver

pause
