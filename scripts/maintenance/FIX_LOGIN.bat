@echo off
echo ========================================
echo FIX ADMIN LOGIN
echo ========================================
echo.
echo This will:
echo 1. Delete existing admin user (if any)
echo 2. Create fresh admin user
echo 3. Set password to: admin123
echo 4. Test authentication
echo.
pause
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Running fix script...
python fix_admin_login.py
echo.
echo ========================================
echo DONE!
echo ========================================
echo.
echo Now try logging in:
echo   URL: http://127.0.0.1:8000/login/
echo   Username: admin
echo   Password: admin123
echo.
pause
