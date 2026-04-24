@echo off
cls
echo.
echo ========================================
echo   MASTER DATA SYSTEM - QUICK START
echo ========================================
echo.
echo This will set up the Master Data system
echo.
pause

echo.
echo [Step 1/2] Running database migration...
python manage.py migrate
if errorlevel 1 (
    echo.
    echo ERROR: Migration failed!
    echo Please check if Django is installed and database is accessible.
    pause
    exit /b 1
)

echo.
echo [Step 2/2] Verifying installation...
python -c "from attendance.models import EmployeeMasterData; print('✓ EmployeeMasterData model loaded successfully')"
if errorlevel 1 (
    echo.
    echo ERROR: Model verification failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✓ SETUP COMPLETE!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Start server:
echo    python manage.py runserver
echo.
echo 2. Login as HR/Admin
echo.
echo 3. Go to Master Data:
echo    http://127.0.0.1:8000/attendance/master-data/
echo.
echo 4. Add employee master data
echo.
echo 5. Test employee registration
echo.
echo.
echo For detailed instructions, see:
echo    COMPLETE_MASTER_DATA_GUIDE.txt
echo.
echo ========================================
pause
