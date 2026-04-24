#!/usr/bin/env python
"""
Script to fix attendance records and recalculate late arrival status
based on local timezone (Asia/Kolkata)
"""
import os
import django
import pytz
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from attendance.models import Attendance
from django.contrib.auth.models import User

def fix_late_arrivals():
    """Fix attendance records for today - recalculate status based on local time"""
    today = timezone.now().date()
    local_tz = pytz.timezone('Asia/Kolkata')
    
    # Get all attendance records for today with check-in
    today_attendance = Attendance.objects.filter(
        date=today,
        check_in__isnull=False
    )
    
    print(f"\n{'='*60}")
    print(f"Fixing Late Arrival Detection for {today}")
    print(f"{'='*60}\n")
    
    fixed_count = 0
    for attendance in today_attendance:
        # Convert check-in time to local timezone
        check_in_local = attendance.check_in.astimezone(local_tz)
        check_in_time = check_in_local.time()
        
        # Determine correct status (9:30 AM IST cutoff)
        old_status = attendance.status
        if check_in_time.hour > 9 or (check_in_time.hour == 9 and check_in_time.minute > 30):
            new_status = 'late'
        else:
            new_status = 'present'
        
        # Update if status changed
        if old_status != new_status:
            attendance.status = new_status
            attendance.save()
            fixed_count += 1
            
            print(f"✓ Fixed: {attendance.employee.username}")
            print(f"  Employee ID: {attendance.employee.employeeprofile.employee_id}")
            print(f"  Check-in (UTC): {attendance.check_in.strftime('%I:%M %p')}")
            print(f"  Check-in (IST): {check_in_time.strftime('%I:%M %p')}")
            print(f"  Status: {old_status} → {new_status}")
            print()
        else:
            print(f"○ No change: {attendance.employee.username} - Status: {old_status}")
            print(f"  Check-in (IST): {check_in_time.strftime('%I:%M %p')}")
            print()
    
    print(f"{'='*60}")
    print(f"Summary: Fixed {fixed_count} out of {today_attendance.count()} records")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    fix_late_arrivals()
