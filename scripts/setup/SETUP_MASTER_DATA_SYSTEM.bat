@echo off
echo ========================================
echo MASTER DATA SYSTEM SETUP
echo ========================================
echo.

echo [1/2] Running database migrations...
python manage.py migrate

echo.
echo [2/2] Verifying setup...
python -c "from attendance.models import EmployeeMasterData; print('SUCCESS: Master Data system ready!')"

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Start server: python manage.py runserver
echo 2. Login as HR/Admin
echo 3. Go to: http://127.0.0.1:8000/attendance/master-data/
echo 4. Add employee master data
echo.
pause
