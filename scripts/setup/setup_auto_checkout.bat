@echo off
echo ============================================
echo Auto Checkout Setup
echo ============================================
echo.
echo This will set up automatic checkout at 7 PM daily
echo.
echo IMPORTANT: Your computer must be ON at 7 PM for this to work!
echo.
pause

echo.
echo Setting up Windows Task Scheduler...
echo.

PowerShell -ExecutionPolicy Bypass -File "%~dp0setup_auto_checkout_scheduler.ps1"

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo The auto-checkout task is now scheduled to run at 7 PM daily.
echo.
echo To test it now, run:
echo   python manage.py auto_checkout
echo.
pause
