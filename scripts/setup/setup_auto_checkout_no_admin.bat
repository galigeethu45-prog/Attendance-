@echo off
REM ============================================================================
REM Setup Auto-Checkout Scheduled Task (No Admin Required)
REM Creates task for current user only
REM ============================================================================

echo ================================================================================
echo AUTO-CHECKOUT SCHEDULED TASK SETUP (No Admin)
echo ================================================================================
echo.
echo This will create a scheduled task that runs EVERY DAY at 7:00 PM
echo to automatically checkout all employees.
echo.
echo Task Details:
echo   - Name: AttendanceHub Auto-Checkout
echo   - Time: 7:00 PM (19:00) every day
echo   - Runs as: Current user (%USERNAME%)
echo   - No admin rights required
echo.
pause

REM Get current directory
set SCRIPT_DIR=%~dp0
set PYTHON_PATH=%SCRIPT_DIR%venv\Scripts\python.exe
set MANAGE_PATH=%SCRIPT_DIR%manage.py

echo.
echo Creating scheduled task...
echo.

REM Delete existing task if it exists
schtasks /Delete /TN "AttendanceHub Auto-Checkout" /F >nul 2>&1

REM Create new task (without /RL HIGHEST - no admin needed)
schtasks /Create ^
    /TN "AttendanceHub Auto-Checkout" ^
    /TR "\"%PYTHON_PATH%\" \"%MANAGE_PATH%\" auto_checkout" ^
    /SC DAILY ^
    /ST 19:00 ^
    /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================================
    echo SUCCESS! Auto-Checkout Task Created
    echo ================================================================================
    echo.
    echo Task Name: AttendanceHub Auto-Checkout
    echo Schedule: Every day at 7:00 PM
    echo Status: Enabled
    echo Runs as: %USERNAME%
    echo.
    echo The task will run automatically every day at 7 PM when you are logged in.
    echo.
    echo To verify the task:
    echo   1. Press Win+R
    echo   2. Type: taskschd.msc
    echo   3. Look for "AttendanceHub Auto-Checkout"
    echo.
    echo To test now:
    echo   schtasks /Run /TN "AttendanceHub Auto-Checkout"
    echo.
    echo ================================================================================
) else (
    echo.
    echo ================================================================================
    echo ERROR! Failed to create task
    echo ================================================================================
    echo.
    echo Error code: %ERRORLEVEL%
    echo.
    echo Possible solutions:
    echo   1. Try running as administrator (right-click, "Run as administrator")
    echo   2. Or use: setup_auto_checkout_task.bat (requires admin)
    echo.
    echo ================================================================================
)

echo.
pause
