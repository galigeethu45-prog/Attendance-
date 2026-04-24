@echo off
echo ========================================
echo COMPANY ATTENDANCE SYSTEM SETUP
echo ========================================
echo.
echo This will create:
echo   1. HR User (HR001 / hr123)
echo   2. Sample Employee (EMP001 / emp123)
echo.
echo Both use the SAME login page!
echo.
pause
echo.
call venv\Scripts\activate.bat
python setup_company_users.py
echo.
pause
