@echo off
echo ========================================
echo ADMIN/HR SETUP TOOL
echo ========================================
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Choose an option:
echo 1. Quick Create Admin (username: admin, password: admin123)
echo 2. Interactive Setup (custom credentials)
echo 3. Check Existing Users
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Creating admin user...
    python quick_create_admin.py
) else if "%choice%"=="2" (
    echo.
    python setup_admin_hr.py
) else if "%choice%"=="3" (
    echo.
    python check_users.py
) else (
    echo Invalid choice!
)

echo.
pause
