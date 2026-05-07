# Auto-Checkout Setup Guide for EC2 (Production)

## Overview

This guide provides a **permanent, foolproof solution** for auto-checkout at 7:00 PM IST on EC2 servers.

---

## Quick Setup (Recommended)

### Step 1: Run the Setup Script

```bash
cd /path/to/your/project
bash scripts/setup/setup_auto_checkout_ec2.sh
```

This script will:
- ✅ Create log directories
- ✅ Test the auto-checkout command
- ✅ Setup cron job for 7:00 PM IST daily
- ✅ Verify everything is working

### Step 2: Verify Setup

```bash
bash scripts/test/diagnose_auto_checkout.sh
```

This will check:
- Python environment
- Django installation
- Database connection
- Cron job configuration
- Log files
- Command execution

---

## Manual Setup (If Script Fails)

### 1. Create Log Directory

```bash
sudo mkdir -p /var/log/attendance
sudo chown $USER:$USER /var/log/attendance
sudo chmod 755 /var/log/attendance
```

### 2. Test the Command

```bash
cd /path/to/your/project
python manage.py auto_checkout
```

**Expected output:**
- If before 7 PM: "STOPPED: Auto checkout only runs at or after 7:00 PM IST"
- If after 7 PM: List of employees checked out

### 3. Setup Cron Job

Edit crontab:
```bash
crontab -e
```

Add this line (replace paths with your actual paths):
```
0 19 * * * cd /path/to/your/project && /path/to/python manage.py auto_checkout >> /var/log/attendance/cron.log 2>&1
```

**Example:**
```
0 19 * * * cd /home/ubuntu/attendance-system && /home/ubuntu/attendance-system/venv/bin/python manage.py auto_checkout >> /var/log/attendance/cron.log 2>&1
```

### 4. Verify Cron Job

```bash
crontab -l | grep auto_checkout
```

---

## Troubleshooting

### Problem 1: Cron Job Not Running

**Check if cron service is running:**
```bash
sudo systemctl status cron
```

**If not running, start it:**
```bash
sudo systemctl start cron
sudo systemctl enable cron
```

**Check cron logs:**
```bash
sudo tail -f /var/log/syslog | grep CRON
```

### Problem 2: Command Runs But Doesn't Checkout

**Check command logs:**
```bash
tail -f /var/log/attendance/auto_checkout.log
```

**Check cron logs:**
```bash
tail -f /var/log/attendance/cron.log
```

**Common issues:**
- **Wrong timezone:** Server time might not be IST
- **Database connection:** Check if Django can connect to database
- **Permissions:** Check if user has write access to database

### Problem 3: No Logs Generated

**Check if log directory exists:**
```bash
ls -la /var/log/attendance/
```

**Check permissions:**
```bash
sudo chown $USER:$USER /var/log/attendance
sudo chmod 755 /var/log/attendance
```

### Problem 4: Python/Django Not Found

**Check Python path in cron:**
```bash
which python3
# or
which python
```

**Use absolute paths in crontab:**
```
0 19 * * * cd /full/path/to/project && /full/path/to/python manage.py auto_checkout >> /var/log/attendance/cron.log 2>&1
```

---

## Verification Steps

### 1. Check Pending Checkouts

```bash
python manage.py shell
```

```python
from attendance.models import Attendance
from django.utils import timezone

today = timezone.now().date()
pending = Attendance.objects.filter(
    date=today,
    check_out__isnull=True,
    check_in__isnull=False
)

print(f"Pending checkouts: {pending.count()}")
for att in pending:
    print(f"  - {att.employee.username} checked in at {att.check_in}")
```

### 2. Manual Test at 7 PM

Wait until 7:00 PM IST, then run:
```bash
cd /path/to/your/project
python manage.py auto_checkout
```

### 3. Check Audit Logs

```bash
python manage.py shell
```

```python
from attendance.models import AuditLog
from django.utils import timezone

today = timezone.now().date()
auto_checkouts = AuditLog.objects.filter(
    action='check_out',
    description__contains='Auto checked out',
    timestamp__date=today
)

print(f"Auto checkouts today: {auto_checkouts.count()}")
for log in auto_checkouts:
    print(f"  - {log.user.username} at {log.timestamp}")
```

---

## Understanding the Cron Schedule

```
0 19 * * *
│ │  │ │ │
│ │  │ │ └─── Day of week (0-7, Sunday=0 or 7)
│ │  │ └───── Month (1-12)
│ │  └─────── Day of month (1-31)
│ └────────── Hour (0-23)
└──────────── Minute (0-59)
```

**0 19 * * *** means:
- Minute: 0 (at the start of the hour)
- Hour: 19 (7 PM in 24-hour format)
- Day of month: * (every day)
- Month: * (every month)
- Day of week: * (every day of the week)

**Result:** Runs every day at 7:00 PM

---

## Alternative: Using systemd Timer (More Reliable)

If cron is unreliable, use systemd timer:

### 1. Create Service File

```bash
sudo nano /etc/systemd/system/attendance-auto-checkout.service
```

```ini
[Unit]
Description=Attendance Auto Checkout
After=network.target

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/python manage.py auto_checkout
StandardOutput=append:/var/log/attendance/auto_checkout.log
StandardError=append:/var/log/attendance/auto_checkout.log

[Install]
WantedBy=multi-user.target
```

### 2. Create Timer File

```bash
sudo nano /etc/systemd/system/attendance-auto-checkout.timer
```

```ini
[Unit]
Description=Run Attendance Auto Checkout Daily at 7 PM IST
Requires=attendance-auto-checkout.service

[Timer]
OnCalendar=*-*-* 19:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

### 3. Enable and Start Timer

```bash
sudo systemctl daemon-reload
sudo systemctl enable attendance-auto-checkout.timer
sudo systemctl start attendance-auto-checkout.timer
```

### 4. Check Timer Status

```bash
sudo systemctl status attendance-auto-checkout.timer
sudo systemctl list-timers | grep attendance
```

---

## Monitoring

### Real-time Log Monitoring

```bash
# Watch command log
tail -f /var/log/attendance/auto_checkout.log

# Watch cron log
tail -f /var/log/attendance/cron.log

# Watch both
tail -f /var/log/attendance/*.log
```

### Daily Check Script

Create a script to check if auto-checkout ran yesterday:

```bash
#!/bin/bash
# scripts/test/check_yesterday_checkout.sh

python manage.py shell << EOF
from attendance.models import AuditLog
from django.utils import timezone
from datetime import timedelta

yesterday = timezone.now().date() - timedelta(days=1)
auto_checkouts = AuditLog.objects.filter(
    action='check_out',
    description__contains='Auto checked out',
    timestamp__date=yesterday
)

if auto_checkouts.exists():
    print(f"✓ Auto-checkout ran yesterday ({yesterday})")
    print(f"  Checked out {auto_checkouts.count()} employees")
else:
    print(f"✗ Auto-checkout DID NOT run yesterday ({yesterday})")
    print("  Check logs: /var/log/attendance/")
EOF
```

---

## Support

If auto-checkout still doesn't work after following this guide:

1. Run diagnostic script: `bash scripts/test/diagnose_auto_checkout.sh`
2. Check all logs in `/var/log/attendance/`
3. Verify server timezone: `timedatectl`
4. Check if Django can access database
5. Try systemd timer instead of cron

---

## Summary

✅ **Setup:** Run `bash scripts/setup/setup_auto_checkout_ec2.sh`  
✅ **Verify:** Run `bash scripts/test/diagnose_auto_checkout.sh`  
✅ **Monitor:** Check `/var/log/attendance/auto_checkout.log`  
✅ **Test:** Run `python manage.py auto_checkout` after 7 PM  

**The auto-checkout will now run reliably every day at 7:00 PM IST!**
