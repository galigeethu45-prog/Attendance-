#!/usr/bin/env python
"""
Manually run auto-checkout for today
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from attendance.models import Attendance, AuditLog
from django.utils import timezone
import pytz
from datetime import time as dt_time

print("=" * 80)
print("MANUAL AUTO-CHECKOUT")
print("=" * 80)

local_tz = pytz.timezone('Asia/Kolkata')
now = timezone.now().astimezone(local_tz)
today = now.date()

print(f"\nCurrent Time: {now.strftime('%Y-%m-%d %I:%M %p IST')}")
print(f"Today's Date: {today}")

# Find pending checkouts
pending_checkouts = Attendance.objects.filter(
    date=today,
    check_out__isnull=True,
    check_in__isnull=False
)

print(f"\nPending Checkouts: {pending_checkouts.count()}")

if not pending_checkouts.exists():
    print("\n✅ No pending checkouts found")
    print("=" * 80)
    exit(0)

print("\nEmployees to auto-checkout:")
print("-" * 80)

for att in pending_checkouts:
    print(f"  • {att.employee.username} - Checked in at {att.check_in.astimezone(local_tz).strftime('%I:%M %p')}")

# Confirm
confirm = input("\nAuto-checkout all at 7:00 PM? (y/n): ").strip().lower()

if confirm != 'y':
    print("\n❌ Cancelled")
    exit(0)

# Set checkout to 7 PM
checkout_datetime = timezone.datetime.combine(
    today,
    dt_time(19, 0)  # 7:00 PM
)
checkout_datetime = local_tz.localize(checkout_datetime)

print(f"\nCheckout Time: {checkout_datetime.strftime('%Y-%m-%d %I:%M %p IST')}")
print("\nProcessing...")
print("-" * 80)

count = 0
for attendance in pending_checkouts:
    attendance.check_out = checkout_datetime
    attendance.calculate_work_hours()
    attendance.save()
    
    # Log it
    AuditLog.objects.create(
        user=attendance.employee,
        action='check_out',
        description='Auto checked out at 7:00 PM (manual trigger)',
        ip_address=None
    )
    
    count += 1
    print(f"✅ {attendance.employee.username} - Work Hours: {attendance.get_work_hours_display()}")

print("\n" + "=" * 80)
print(f"✅ Successfully auto-checked out {count} employee(s)")
print("=" * 80)
print()
