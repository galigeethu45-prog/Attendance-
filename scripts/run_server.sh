#!/bin/bash

echo "========================================"
echo "  AttendanceHub - Starting Server"
echo "========================================"
echo ""

# Activate virtual environment
source venv/bin/activate

echo "Virtual environment activated!"
echo ""

# Check if migrations are needed
echo "Checking database..."
python manage.py migrate --check > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Running migrations..."
    python manage.py migrate
fi

echo ""
echo "========================================"
echo "  Server Starting..."
echo "========================================"
echo ""
echo "Access the application at:"
echo "  http://localhost:8000/"
echo ""
echo "Login Credentials:"
echo "  HR Admin: hr_admin / admin123"
echo "  Employee: employee1 / emp123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Start Django development server
python manage.py runserver
