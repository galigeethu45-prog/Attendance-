@echo off
echo ========================================
echo FIXING BREAK SYSTEM ERROR
echo ========================================
echo.

REM Check if venv exists
if exist "venv\Scripts\activate.bat" (
    echo [1/3] Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist "env\Scripts\activate.bat" (
    echo [1/3] Activating virtual environment...
    call env\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    echo Please activate your virtual environment manually and run:
    echo   python manage.py migrate
    pause
    exit /b 1
)

echo.
echo [2/3] Running database migration...
python manage.py migrate

echo.
echo [3/3] Checking if migration was successful...
python -c "from attendance.models import BreakLog; print('SUCCESS: Database updated!')"

echo.
echo ========================================
echo DONE! You can now refresh your browser.
echo ========================================
pause
