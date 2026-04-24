@echo off
REM ============================================================================
REM Remove Auto-Checkout Scheduled Task
REM ============================================================================

echo ================================================================================
echo REMOVE AUTO-CHECKOUT SCHEDULED TASK
echo ================================================================================
echo.
echo This will REMOVE the auto-checkout scheduled task from Windows Task Scheduler.
echo.
echo WARNING: After removal, auto-checkout will NOT run automatically at 7 PM.
echo You will need to run setup_auto_checkout_task.bat again to re-enable it.
echo.
pause

echo.
echo Removing scheduled task...
echo.

schtasks /Delete /TN "AttendanceHub Auto-Checkout" /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================================
    echo SUCCESS! Task Removed
    echo ================================================================================
    echo.
    echo The auto-checkout scheduled task has been removed.
    echo.
    echo To re-enable automatic checkout:
    echo   Run: setup_auto_checkout_task.bat
    echo.
) else (
    echo.
    echo ================================================================================
    echo ERROR or Task Not Found
    echo ================================================================================
    echo.
    echo The task may not exist or you may need administrator privileges.
    echo.
)

echo.
pause
