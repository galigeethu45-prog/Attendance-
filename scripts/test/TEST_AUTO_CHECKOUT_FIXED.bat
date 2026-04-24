@echo off
REM Test the fixed auto-checkout command

echo ================================================================================
echo TEST AUTO-CHECKOUT COMMAND (FIXED VERSION)
echo ================================================================================
echo.
echo This will test if the auto-checkout command works correctly.
echo.
pause

cd /d "%~dp0..\.."
call venv\Scripts\activate.bat

python scripts/test/test_auto_checkout_fixed.py

echo.
pause
