"""
Test script to verify half-day logic
"""

import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from attendance.models import Attendance
from django.contrib.auth.models import User

# Get a test user
user = User.objects.first()
print(f"Testing with user: {user.username}")

# Create a test attendance record for today
today = timezone.now().date()

# Delete existing record for today if any
Attendance.objects.filter(employee=user, date=today).delete()

# Simulate late check-in (10:02 AM)
import pytz
local_tz = pytz.timezone('Asia/Kolkata')
check_in_time = timezone.now().replace(hour=10, minute=2, second=0, microsecond=0)

attendance = Attendance.objects.create(
    employee=user,
    date=today,
    check_in=check_in_time,
    status='half-day'  # Marked as half-day due to late arrival
)

print(f"\nCreated attendance record:")
print(f"  Check-in: {check_in_time.astimezone(local_tz).strftime('%I:%M %p')}")
print(f"  Status: {attendance.status}")

# Simulate check-out after 8 hours of work
check_out_time = check_in_time + timedelta(hours=8)
attendance.check_out = check_out_time
attendance.save()

print(f"  Check-out: {check_out_time.astimezone(local_tz).strftime('%I:%M %p')}")
print(f"  Actual work time: 8 hours")

# Calculate work hours
attendance.calculate_work_hours()

print(f"\nAfter calculate_work_hours():")
print(f"  Total work hours: {attendance.total_work_hours}")
print(f"  Status: {attendance.status}")
print(f"  Display: {attendance.get_work_hours_display()}")

if attendance.total_work_hours == 3.75:
    print("\n✅ SUCCESS: Hours capped at 3.75 for half-day!")
else:
    print(f"\n❌ FAILED: Expected 3.75 hours, got {attendance.total_work_hours}")

# Cleanup
attendance.delete()
print("\nTest record deleted.")
