#!/usr/bin/env python
"""
Fix old pending checkouts (for past dates)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from attendance.models import Attendance, AuditLog
from django.utils import timezone
import pytz
from datetime import time as dt_time, timedelta

print("=" * 80)
print("FIX OLD PENDING CHECKOUTS")
print("=" * 80)

local_tz = pytz.timezone('Asia/Kolkata')
today = timezone.now().date()

# Find all old pending checkouts (before today)
old_pending = Attendance.objects.filter(
    date__lt=today,
    check_out__isnull=True,
    check_in__isnull=False
).order_by('date')

print(f"\nOld Pending Checkouts: {old_pending.count()}")

if not old_pending.exists():
    print("\n✅ No old pending checkouts found")
    print("=" * 80)
    exit(0)

print("\nPending Checkouts by Date:")
print("-" * 80)

for att in old_pending:
    check_in_local = att.check_in.astimezone(local_tz)
    print(f"  • {att.date} - {att.employee.username} - Checked in at {check_in_local.strftime('%I:%M %p')}")

# Confirm
print("\n" + "=" * 80)
confirm = input("Auto-checkout all at 7:00 PM of their respective dates? (y/n): ").strip().lower()

if confirm != 'y':
    print("\n❌ Cancelled")
    exit(0)

print("\nProcessing...")
print("-" * 80)

count = 0
for attendance in old_pending:
    # Set checkout to 7 PM of that date
    checkout_datetime = timezone.datetime.combine(
        attendance.date,
        dt_time(19, 0)  # 7:00 PM
    )
    checkout_datetime = local_tz.localize(checkout_datetime)
    
    attendance.check_out = checkout_datetime
    attendance.calculate_work_hours()
    attendance.save()
    
    # Log it
    AuditLog.objects.create(
        user=attendance.employee,
        action='check_out',
        description=f'Auto checked out at 7:00 PM (old record fix for {attendance.date})',
        ip_address=None
    )
    
    count += 1
    print(f"✅ {attendance.date} - {attendance.employee.username} - Work Hours: {attendance.get_work_hours_display()}")

print("\n" + "=" * 80)
print(f"✅ Successfully fixed {count} old checkout(s)")
print("=" * 80)
print()
