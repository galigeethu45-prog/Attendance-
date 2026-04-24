"""
Fix missing checkouts for April 23 and 24, 2026
Run this once to fix the past records
"""
import os
import sys
import django
from datetime import datetime, time
import pytz

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from attendance.models import Attendance, AuditLog
from django.utils import timezone

def fix_missing_checkouts():
    local_tz = pytz.timezone('Asia/Kolkata')
    
    # Dates to fix
    dates_to_fix = [
        datetime(2026, 4, 23).date(),  # April 23, 2026
        datetime(2026, 4, 24).date(),  # April 24, 2026
    ]
    
    total_fixed = 0
    
    for date in dates_to_fix:
        print(f"\n{'='*60}")
        print(f"Fixing checkouts for: {date.strftime('%B %d, %Y')}")
        print(f"{'='*60}")
        
        # Find attendance records without checkout
        pending = Attendance.objects.filter(
            date=date,
            check_out__isnull=True,
            check_in__isnull=False
        )
        
        print(f"Found {pending.count()} pending checkout(s)")
        
        for attendance in pending:
            # Set checkout to 7 PM IST
            checkout_time = datetime.combine(date, time(19, 0, 0))
            checkout_time = local_tz.localize(checkout_time)
            
            attendance.check_out = checkout_time
            attendance.save()
            attendance.calculate_work_hours()
            
            # Log the fix
            AuditLog.objects.create(
                user=attendance.employee,
                action='check_out',
                description=f'Auto checked out at 7:00 PM IST (system - retroactive fix)',
                ip_address=None
            )
            
            print(f"✓ Fixed: {attendance.employee.username} - {attendance.employee.get_full_name() or 'No name'}")
            print(f"  Check-in: {attendance.check_in.strftime('%I:%M %p')}")
            print(f"  Check-out: {attendance.check_out.strftime('%I:%M %p')}")
            print(f"  Work hours: {attendance.get_work_hours_display()}")
            print(f"  Status: {attendance.get_status_display()}")
            
            total_fixed += 1
    
    print(f"\n{'='*60}")
    print(f"✓ COMPLETED: Fixed {total_fixed} checkout(s) across {len(dates_to_fix)} day(s)")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    fix_missing_checkouts()
