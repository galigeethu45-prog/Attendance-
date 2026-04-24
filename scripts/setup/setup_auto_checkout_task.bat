@echo off
REM ============================================================================
REM Setup Auto-Checkout Scheduled Task for Windows
REM Runs every day at 7:00 PM automatically
REM ============================================================================

echo ================================================================================
echo AUTO-CHECKOUT SCHEDULED TASK SETUP
echo ================================================================================
echo.
echo This will create a Windows Task Scheduler task that runs EVERY DAY at 7:00 PM
echo to automatically checkout all employees who forgot to checkout.
echo.
echo Task Details:
echo   - Name: AttendanceHub Auto-Checkout
echo   - Time: 7:00 PM (19:00) every day
echo   - Action: Run auto_checkout command
echo   - Runs: Whether user is logged in or not
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

REM Create new task
schtasks /Create ^
    /TN "AttendanceHub Auto-Checkout" ^
    /TR "\"%PYTHON_PATH%\" \"%MANAGE_PATH%\" auto_checkout" ^
    /SC DAILY ^
    /ST 19:00 ^
    /RU "%USERNAME%" ^
    /RL HIGHEST ^
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
    echo.
    echo The task will run automatically every day at 7 PM, even if:
    echo   - No one is using the system
    echo   - Computer is locked
    echo   - You are logged out
    echo.
    echo To verify the task was created:
    echo   1. Open Task Scheduler (taskschd.msc)
    echo   2. Look for "AttendanceHub Auto-Checkout"
    echo.
    echo To test the task manually:
    echo   schtasks /Run /TN "AttendanceHub Auto-Checkout"
    echo.
    echo ================================================================================
) else (
    echo.
    echo ================================================================================
    echo ERROR! Failed to create task
    echo ================================================================================
    echo.
    echo Please run this script as Administrator:
    echo   1. Right-click on this file
    echo   2. Select "Run as administrator"
    echo.
    echo ================================================================================
)

echo.
pause
