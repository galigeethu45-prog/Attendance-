"""
Remove Today's Auto-Assigned Checkout
This script removes checkout for today's date only (keeps check-in)

Usage:
    python scripts/maintenance/remove_today_checkout.py
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from attendance.models import Attendance


def main():
    print("=" * 70)
    print("REMOVE TODAY'S AUTO-ASSIGNED CHECKOUT")
    print("=" * 70)
    print()
    print("This will remove checkout time for today only (keeps check-in)")
    print()
    print("=" * 70)
    print()
    
    today = timezone.now().date()
    print(f"Today's Date: {today.strftime('%Y-%m-%d')}")
    print()
    
    # Process employees one by one
    while True:
        print("Enter Employee ID (or 'done' to finish):")
        employee_id = input("> ").strip()
        
        if employee_id.lower() == 'done':
            break
        
        if not employee_id:
            continue
        
        print()
        print("=" * 70)
        print(f"PROCESSING: {employee_id}")
        print("=" * 70)
        
        # Find user by employee ID
        user = None
        try:
            from attendance.models import EmployeeProfile
            profile = EmployeeProfile.objects.get(employee_id=employee_id)
            user = profile.user
        except:
            try:
                # Try username as fallback
                user = User.objects.get(username=employee_id)
            except:
                print(f"❌ Employee '{employee_id}' not found")
                print()
                continue
        
        print(f"✓ Found: {user.get_full_name() or user.username} ({employee_id})")
        print()
        
        # Find today's attendance with checkout
        attendance = Attendance.objects.filter(
            employee=user,
            date=today,
            check_in__isnull=False,
            check_out__isnull=False
        ).first()
        
        if not attendance:
            print("✅ No checkout found for today")
            print()
            continue
        
        # Show current status
        print(f"Current Status:")
        print(f"  Check-in:  {attendance.check_in.strftime('%I:%M %p')}")
        print(f"  Check-out: {attendance.check_out.strftime('%I:%M %p')}")
        print(f"  Hours:     {attendance.hours_worked}h")
        print()
        
        # Confirm removal
        print("Remove today's checkout? (yes/no):")
        confirm = input("> ").strip().lower()
        
        if confirm in ['yes', 'y']:
            # Remove checkout but keep check-in
            attendance.check_out = None
            attendance.hours_worked = None
            attendance.work_hours = None
            attendance.save()
            
            print()
            print(f"✅ Checkout removed for {employee_id} on {today.strftime('%Y-%m-%d')}")
            print(f"   Check-in time preserved: {attendance.check_in.strftime('%I:%M %p')}")
        else:
            print("⏭️  Skipped")
        
        print()
        print("=" * 70)
        print()
    
    print()
    print("Done!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
