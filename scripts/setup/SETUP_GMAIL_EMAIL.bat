@echo off
echo ================================================================================
echo GMAIL SMTP SETUP - QUICK START
echo ================================================================================
echo.
echo This will help you configure Gmail for sending emails.
echo.
echo BEFORE RUNNING THIS:
echo   1. Go to: https://myaccount.google.com/apppasswords
echo   2. Generate an App Password for Mail
echo   3. Copy the 16-character password
echo.
echo ================================================================================
echo.
pause

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
)

echo.
echo Running Gmail setup script...
echo.
python switch_to_gmail.py

echo.
echo ================================================================================
echo SETUP COMPLETED!
echo ================================================================================
echo.
echo NEXT STEPS:
echo   1. Restart Django server (Ctrl+C and run again)
echo   2. Test email: python verify_email_setup.py
echo   3. Test password reset: http://127.0.0.1:8000/password-reset/
echo.
pause
