#!/usr/bin/env python
"""
Script to fix yesterday's missing checkouts
Run this if auto-checkout didn't run yesterday
"""
import os
import django
import pytz
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from attendance.models import Attendance, AuditLog

def fix_yesterday_checkouts():
    """Fix missing checkouts for yesterday"""
    yesterday = (timezone.now() - timedelta(days=1)).date()
    local_tz = pytz.timezone('Asia/Kolkata')
    
    print(f"\n{'='*60}")
    print(f"Fixing Missing Checkouts for {yesterday}")
    print(f"{'='*60}\n")
    
    # Find attendance records from yesterday without checkout
    pending_checkouts = Attendance.objects.filter(
        date=yesterday,
        check_out__isnull=True,
        check_in__isnull=False
    )
    
    if not pending_checkouts.exists():
        print("✓ No missing checkouts found for yesterday")
        print(f"{'='*60}\n")
        return
    
    count = 0
    for attendance in pending_checkouts:
        # Set check_out to 7 PM IST of yesterday
        checkout_time = datetime.combine(
            yesterday,
            datetime.strptime('19:00', '%H:%M').time()
        )
        checkout_time = local_tz.localize(checkout_time)
        
        attendance.check_out = checkout_time
        attendance.save()
        attendance.calculate_work_hours()
        
        # Log the fix
        AuditLog.objects.create(
            user=attendance.employee,
            action='check_out',
            description=f'Auto checked out at 7:00 PM (manual fix for {yesterday})',
            ip_address=None
        )
        
        count += 1
        
        print(f"✓ Fixed: {attendance.employee.username}")
        print(f"  Employee ID: {attendance.employee.employeeprofile.employee_id}")
        print(f"  Check-in: {attendance.check_in.astimezone(local_tz).strftime('%I:%M %p')}")
        print(f"  Check-out: 07:00 PM (auto)")
        print(f"  Total Hours: {attendance.get_work_hours_display()}")
        print()
    
    print(f"{'='*60}")
    print(f"Summary: Fixed {count} missing checkout(s) for {yesterday}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    fix_yesterday_checkouts()
