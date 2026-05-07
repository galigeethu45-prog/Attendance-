#!/bin/bash

# ============================================================================
# AUTO-CHECKOUT DIAGNOSTIC SCRIPT
# ============================================================================
# This script helps diagnose why auto-checkout is not working
# ============================================================================

echo "=========================================="
echo "AUTO-CHECKOUT DIAGNOSTIC"
echo "=========================================="
echo ""

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "1. Checking project directory..."
echo "   Project dir: $PROJECT_DIR"
if [ -f "$PROJECT_DIR/manage.py" ]; then
    echo "   ✓ manage.py found"
else
    echo "   ✗ manage.py NOT found"
    exit 1
fi
echo ""

echo "2. Checking Python environment..."
if [ -d "$PROJECT_DIR/venv" ]; then
    PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
    echo "   ✓ Virtual environment found: venv/"
elif [ -d "$PROJECT_DIR/.venv" ]; then
    PYTHON_PATH="$PROJECT_DIR/.venv/bin/python"
    echo "   ✓ Virtual environment found: .venv/"
else
    PYTHON_PATH=$(which python3)
    echo "   ⚠ Using system Python: $PYTHON_PATH"
fi

if [ -f "$PYTHON_PATH" ]; then
    echo "   ✓ Python found: $PYTHON_PATH"
    $PYTHON_PATH --version
else
    echo "   ✗ Python NOT found at $PYTHON_PATH"
    exit 1
fi
echo ""

echo "3. Checking Django installation..."
cd "$PROJECT_DIR"
if $PYTHON_PATH -c "import django; print(f'Django version: {django.get_version()}')" 2>/dev/null; then
    echo "   ✓ Django is installed"
else
    echo "   ✗ Django is NOT installed"
    exit 1
fi
echo ""

echo "4. Checking database connection..."
if $PYTHON_PATH manage.py check --database default 2>/dev/null; then
    echo "   ✓ Database connection OK"
else
    echo "   ✗ Database connection FAILED"
    echo "   Run: $PYTHON_PATH manage.py check"
    exit 1
fi
echo ""

echo "5. Checking auto_checkout command..."
if $PYTHON_PATH manage.py help auto_checkout >/dev/null 2>&1; then
    echo "   ✓ auto_checkout command exists"
else
    echo "   ✗ auto_checkout command NOT found"
    exit 1
fi
echo ""

echo "6. Checking cron job..."
if crontab -l 2>/dev/null | grep -q "auto_checkout"; then
    echo "   ✓ Cron job exists:"
    crontab -l | grep "auto_checkout"
else
    echo "   ✗ Cron job NOT found"
    echo "   Run setup script: bash scripts/setup/setup_auto_checkout_ec2.sh"
fi
echo ""

echo "7. Checking log directory..."
if [ -d "/var/log/attendance" ]; then
    echo "   ✓ Log directory exists: /var/log/attendance"
    echo "   Permissions:"
    ls -ld /var/log/attendance
else
    echo "   ✗ Log directory NOT found: /var/log/attendance"
    echo "   Creating..."
    sudo mkdir -p /var/log/attendance
    sudo chown $USER:$USER /var/log/attendance
    sudo chmod 755 /var/log/attendance
    echo "   ✓ Created"
fi
echo ""

echo "8. Checking recent logs..."
if [ -f "/var/log/attendance/auto_checkout.log" ]; then
    echo "   ✓ Command log exists"
    echo "   Last 10 lines:"
    tail -10 /var/log/attendance/auto_checkout.log
else
    echo "   ⚠ No command log found yet"
fi
echo ""

if [ -f "/var/log/attendance/cron.log" ]; then
    echo "   ✓ Cron log exists"
    echo "   Last 10 lines:"
    tail -10 /var/log/attendance/cron.log
else
    echo "   ⚠ No cron log found yet"
fi
echo ""

echo "9. Checking current time..."
echo "   Server time: $(date)"
echo "   IST time: $(TZ='Asia/Kolkata' date)"
echo ""

echo "10. Testing auto_checkout command NOW..."
echo "    (This will show if command works, but won't checkout if before 7 PM)"
cd "$PROJECT_DIR"
$PYTHON_PATH manage.py auto_checkout
echo ""

echo "=========================================="
echo "DIAGNOSTIC COMPLETE"
echo "=========================================="
echo ""
echo "If everything shows ✓ but auto-checkout still doesn't work:"
echo ""
echo "1. Check if cron service is running:"
echo "   sudo systemctl status cron"
echo ""
echo "2. Check system logs:"
echo "   sudo tail -f /var/log/syslog | grep CRON"
echo ""
echo "3. Manually test at 7 PM:"
echo "   cd $PROJECT_DIR && $PYTHON_PATH manage.py auto_checkout"
echo ""
echo "4. Check database for pending checkouts:"
echo "   $PYTHON_PATH manage.py shell"
echo "   >>> from attendance.models import Attendance"
echo "   >>> from django.utils import timezone"
echo "   >>> today = timezone.now().date()"
echo "   >>> Attendance.objects.filter(date=today, check_out__isnull=True, check_in__isnull=False)"
echo ""
echo "=========================================="
