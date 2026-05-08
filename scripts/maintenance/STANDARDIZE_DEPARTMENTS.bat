@echo off
echo ========================================
echo DEPARTMENT STANDARDIZATION SCRIPT
echo ========================================
echo.
echo This will standardize department names:
echo - Information Technology → IT
echo - Human Resources → HR
echo.
pause

python scripts\maintenance\standardize_departments.py

echo.
pause
