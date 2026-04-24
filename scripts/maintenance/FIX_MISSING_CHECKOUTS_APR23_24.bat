@echo off
REM Fix missing checkouts for April 23 and 24, 2026

echo ================================================================================
echo FIX MISSING CHECKOUTS - APRIL 23 & 24, 2026
echo ================================================================================
echo.
echo This will automatically checkout employees who forgot to checkout on:
echo   - April 23, 2026
echo   - April 24, 2026
echo.
echo Checkout time will be set to 7:00 PM IST
echo.
pause

cd /d "%~dp0..\.."
call venv\Scripts\activate.bat

python scripts/maintenance/fix_missing_checkouts_apr23_24.py

echo.
echo ================================================================================
echo DONE! Check the output above for results.
echo ================================================================================
echo.
pause
