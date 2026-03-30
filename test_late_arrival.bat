@echo off
echo ============================================
echo Testing Late Arrival Detection
echo ============================================
echo.
echo This script will:
echo 1. Show current attendance records
echo 2. Fix any incorrect late arrival statuses
echo.
pause

cd /d "%~dp0"
call venv\Scripts\activate

echo.
echo Running fix script...
echo.
python fix_late_arrivals.py

echo.
echo ============================================
echo Done! Check the results above.
echo ============================================
echo.
echo You can now:
echo 1. Login to the system at http://127.0.0.1:8000/login/
echo 2. Check HR Dashboard to see late arrivals
echo.
pause
