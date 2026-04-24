@echo off
REM UNDO the early auto-checkouts from April 24, 2026

echo ================================================================================
echo UNDO EARLY AUTO-CHECKOUTS - APRIL 24, 2026
echo ================================================================================
echo.
echo This will REMOVE the checkouts that were set at 2:09 PM today.
echo Employees will be able to check out properly at end of day.
echo.
echo WARNING: This will affect all employees who were auto-checked out today.
echo.
pause

cd /d "%~dp0..\.."
call venv\Scripts\activate.bat

python scripts/maintenance/UNDO_auto_checkout_apr24.py

echo.
echo ================================================================================
echo DONE! Employees can now check out normally.
echo ================================================================================
echo.
pause
