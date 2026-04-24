@echo off
REM ============================================================================
REM Test Auto-Checkout Command
REM Runs the auto-checkout command immediately to test it
REM ============================================================================

echo ================================================================================
echo TEST AUTO-CHECKOUT
echo ================================================================================
echo.
echo This will run the auto-checkout command RIGHT NOW to test it.
echo.
echo What it does:
echo   1. Finds all employees who checked in but didn't check out
echo   2. Sets their checkout time to 7:00 PM
echo   3. Calculates work hours
echo   4. Shows results
echo.
pause

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    echo.
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo.
    echo ERROR: Virtual environment not found!
    echo Please make sure venv folder exists.
    pause
    exit /b 1
)

echo.
echo Running auto-checkout command...
echo ================================================================================
echo.

python manage.py auto_checkout

echo.
echo ================================================================================
echo TEST COMPLETED
echo ================================================================================
echo.
echo Check the output above to see:
echo   - How many employees were auto-checked out
echo   - Their work hours
echo   - Any errors (if any)
echo.
echo If you see "Successfully auto checked out X employee(s)" - it's working!
echo.
pause
