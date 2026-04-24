@echo off
REM Auto Checkout Script - Runs at 7 PM daily
REM This script automatically checks out employees who forgot to check out

cd /d "%~dp0"
call venv\Scripts\activate

echo ============================================
echo Running Auto Checkout at %date% %time%
echo ============================================

python manage.py auto_checkout

echo.
echo ============================================
echo Auto Checkout Complete
echo ============================================

REM Uncomment the line below if you want to see the output
REM pause
