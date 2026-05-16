@echo off
echo ========================================
echo Remove Today's Auto-Assigned Checkout
echo ========================================
echo.

cd /d "%~dp0..\.."
python scripts/maintenance/remove_today_checkout.py

echo.
echo ========================================
pause
