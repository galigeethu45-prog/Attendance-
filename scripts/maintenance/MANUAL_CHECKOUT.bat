@echo off
echo ========================================
echo Manual Checkout Script
echo ========================================
echo.
echo This script will help you assign checkout
echo times for employees who forgot to check out.
echo.
echo Press any key to continue...
pause > nul

cd /d "%~dp0..\.."
call venv\Scripts\activate.bat
python scripts/maintenance/manual_checkout.py

echo.
echo Press any key to exit...
pause > nul
