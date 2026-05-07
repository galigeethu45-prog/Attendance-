#!/bin/bash

# ============================================================================
# AUTO-CHECKOUT SETUP FOR EC2 (PRODUCTION)
# ============================================================================
# This script sets up auto-checkout to run at 7:00 PM IST every day
# ============================================================================

echo "=========================================="
echo "AUTO-CHECKOUT SETUP FOR EC2"
echo "=========================================="
echo ""

# Get the project directory (where manage.py is located)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo "Project directory: $PROJECT_DIR"
echo ""

# Get Python path (virtual environment or system Python)
if [ -d "$PROJECT_DIR/venv" ]; then
    PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
    echo "Using virtual environment: $PYTHON_PATH"
elif [ -d "$PROJECT_DIR/.venv" ]; then
    PYTHON_PATH="$PROJECT_DIR/.venv/bin/python"
    echo "Using virtual environment: $PYTHON_PATH"
else
    PYTHON_PATH=$(which python3)
    echo "Using system Python: $PYTHON_PATH"
fi

# Verify Python exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "ERROR: Python not found at $PYTHON_PATH"
    exit 1
fi

# Verify manage.py exists
if [ ! -f "$PROJECT_DIR/manage.py" ]; then
    echo "ERROR: manage.py not found in $PROJECT_DIR"
    exit 1
fi

echo ""
echo "=========================================="
echo "STEP 1: Create log directory"
echo "=========================================="

# Create log directory
sudo mkdir -p /var/log/attendance
sudo chown $USER:$USER /var/log/attendance
sudo chmod 755 /var/log/attendance
echo "✓ Log directory created: /var/log/attendance"

echo ""
echo "=========================================="
echo "STEP 2: Test auto-checkout command"
echo "=========================================="

# Test the command
echo "Testing command..."
cd "$PROJECT_DIR"
$PYTHON_PATH manage.py auto_checkout
echo ""

echo ""
echo "=========================================="
echo "STEP 3: Setup cron job"
echo "=========================================="

# Create cron job entry
CRON_COMMAND="0 19 * * * cd $PROJECT_DIR && $PYTHON_PATH manage.py auto_checkout >> /var/log/attendance/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "auto_checkout"; then
    echo "⚠ Cron job already exists. Removing old entry..."
    crontab -l 2>/dev/null | grep -v "auto_checkout" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

echo "✓ Cron job added successfully!"
echo ""
echo "Cron job details:"
echo "  Schedule: Every day at 7:00 PM IST (19:00)"
echo "  Command: $CRON_COMMAND"
echo ""

echo ""
echo "=========================================="
echo "STEP 4: Verify cron job"
echo "=========================================="

echo "Current crontab:"
crontab -l | grep "auto_checkout"
echo ""

echo ""
echo "=========================================="
echo "SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "✓ Auto-checkout will run every day at 7:00 PM IST"
echo "✓ Logs will be saved to:"
echo "  - Command log: /var/log/attendance/auto_checkout.log"
echo "  - Cron log: /var/log/attendance/cron.log"
echo ""
echo "To verify it's working:"
echo "  1. Check logs: tail -f /var/log/attendance/auto_checkout.log"
echo "  2. Check cron log: tail -f /var/log/attendance/cron.log"
echo "  3. Test manually: cd $PROJECT_DIR && $PYTHON_PATH manage.py auto_checkout"
echo ""
echo "To remove the cron job:"
echo "  crontab -e"
echo "  (Then delete the line containing 'auto_checkout')"
echo ""
echo "=========================================="
