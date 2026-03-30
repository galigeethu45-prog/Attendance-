#!/usr/bin/env python
"""
Verification script to check system status
"""
import os
import django
import pytz
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from attendance.models import Attendance, EmployeeProfile
from django.contrib.auth.models import User

def verify_system():
    """Verify system configuration and current state"""
    print("\n" + "="*60)
    print("ATTENDANCE SYSTEM VERIFICATION")
    print("="*60 + "\n")
    
    # 1. Check timezone settings
    from django.conf import settings
    print("1. TIMEZONE CONFIGURATION:")
    print(f"   TIME_ZONE: {settings.TIME_ZONE}")
    print(f"   USE_TZ: {settings.USE_TZ}")
    print(f"   Current UTC time: {timezone.now().strftime('%Y-%m-%d %I:%M %p')}")
    
    local_tz = pytz.timezone('Asia/Kolkata')
    local_time = timezone.now().astimezone(local_tz)
    print(f"   Current IST time: {local_time.strftime('%Y-%m-%d %I:%M %p')}")
    print()
    
    # 2. Check users
    print("2. USER ACCOUNTS:")
    users = User.objects.all()
    for user in users:
        try:
            profile = user.employeeprofile
            print(f"   ✓ {user.username} (ID: {profile.employee_id})")
            print(f"     - Email: {user.email}")
            print(f"     - Is HR: {profile.is_hr}")
            print(f"     - Is Superuser: {user.is_superuser}")
        except EmployeeProfile.DoesNotExist:
            print(f"   ✗ {user.username} - No profile")
        print()
    
    # 3. Check today's attendance
    today = timezone.now().date()
    print(f"3. TODAY'S ATTENDANCE ({today}):")
    today_attendance = Attendance.objects.filter(date=today)
    
    if today_attendance.exists():
        for att in today_attendance:
            check_in_local = att.check_in.astimezone(local_tz) if att.check_in else None
            check_out_local = att.check_out.astimezone(local_tz) if att.check_out else None
            
            print(f"   Employee: {att.employee.username}")
            if check_in_local:
                print(f"   Check-in (IST): {check_in_local.strftime('%I:%M %p')}")
            else:
                print(f"   Check-in: Not checked in")
            
            if check_out_local:
                print(f"   Check-out (IST): {check_out_local.strftime('%I:%M %p')}")
            else:
                print(f"   Check-out: Not checked out")
            
            print(f"   Status: {att.status.upper()}")
            print(f"   Work Hours: {att.get_work_hours_display()}")
            print()
    else:
        print("   No attendance records for today")
        print()
    
    # 4. Check Attendance model status choices
    print("4. ATTENDANCE STATUS CHOICES:")
    from attendance.models import Attendance as AttendanceModel
    for choice in AttendanceModel._meta.get_field('status').choices:
        print(f"   - {choice[0]}: {choice[1]}")
    print()
    
    # 5. Check if pytz is installed
    print("5. DEPENDENCIES:")
    try:
        import pytz as pytz_module
        print(f"   ✓ pytz installed (version: {pytz_module.__version__})")
    except ImportError:
        print(f"   ✗ pytz NOT installed")
    
    try:
        import django
        print(f"   ✓ Django installed (version: {django.__version__})")
    except ImportError:
        print(f"   ✗ Django NOT installed")
    print()
    
    print("="*60)
    print("VERIFICATION COMPLETE")
    print("="*60 + "\n")

if __name__ == '__main__':
    verify_system()
