@echo off
echo ========================================
echo Running Database Migration
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run migration
python manage.py migrate attendance

echo.
echo ========================================
echo Migration Complete!
echo ========================================
echo.
echo Press any key to exit...
pause > nul
