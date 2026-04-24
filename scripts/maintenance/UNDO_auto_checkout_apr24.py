"""
UNDO the auto-checkouts that happened at 2:09 PM on April 24, 2026
This will remove the checkout times so employees can check out properly at end of day
"""
import os
import sys
import django
from datetime import datetime
import pytz

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from attendance.models import Attendance, AuditLog
from django.utils import timezone

def undo_early_checkouts():
    local_tz = pytz.timezone('Asia/Kolkata')
    today = datetime(2026, 4, 24).date()
    
    print("\n" + "="*70)
    print("UNDO EARLY AUTO-CHECKOUTS - APRIL 24, 2026")
    print("="*70)
    print(f"\nRemoving checkouts that happened at 2:09 PM (should be 7:00 PM)")
    print(f"Date: {today.strftime('%B %d, %Y')}\n")
    
    # Find all attendance records for today that have checkout at 7 PM
    # (These were set by the auto-checkout script)
    early_checkouts = Attendance.objects.filter(
        date=today,
        check_out__isnull=False
    )
    
    print(f"Found {early_checkouts.count()} checkout(s) to review\n")
    
    count = 0
    for attendance in early_checkouts:
        # Check if checkout was set to 7 PM (auto-checkout time)
        checkout_time = attendance.check_out.astimezone(local_tz)
        
        # If checkout is at 7:00 PM, it was likely set by auto-checkout
        if checkout_time.hour == 19 and checkout_time.minute == 0:
            print(f"Removing checkout for: {attendance.employee.username} - {attendance.employee.get_full_name() or 'No name'}")
            print(f"  Check-in: {attendance.check_in.strftime('%I:%M %p')}")
            print(f"  Check-out (removing): {attendance.check_out.strftime('%I:%M %p')}")
            
            # Remove checkout
            attendance.check_out = None
            attendance.total_work_hours = 0
            attendance.save()
            
            # Log the undo action
            AuditLog.objects.create(
                user=attendance.employee,
                action='check_out',
                description=f'Checkout removed - was set incorrectly at 2:09 PM (should run at 7 PM)',
                ip_address=None
            )
            
            count += 1
            print(f"  ✓ Checkout removed - employee can now check out properly\n")
    
    print("="*70)
    print(f"✓ COMPLETED: Removed {count} early checkout(s)")
    print(f"Employees can now check out normally at end of day")
    print("="*70 + "\n")

if __name__ == '__main__':
    confirm = input("This will remove all checkouts for April 24, 2026. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        undo_early_checkouts()
    else:
        print("Cancelled.")
