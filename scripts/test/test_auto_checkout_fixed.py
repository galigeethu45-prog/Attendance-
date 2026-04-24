"""
Test the fixed auto-checkout command
This will verify the command works correctly
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from attendance.models import Attendance
from django.utils import timezone

def test_auto_checkout():
    print("\n" + "="*60)
    print("TESTING AUTO-CHECKOUT COMMAND")
    print("="*60 + "\n")
    
    # Get today's date
    today = timezone.now().date()
    
    # Check pending checkouts before running
    pending_before = Attendance.objects.filter(
        date=today,
        check_out__isnull=True,
        check_in__isnull=False
    ).count()
    
    print(f"Date: {today.strftime('%B %d, %Y')}")
    print(f"Pending checkouts BEFORE: {pending_before}")
    print("\n" + "-"*60)
    print("Running auto_checkout command...")
    print("-"*60 + "\n")
    
    # Run the command
    try:
        call_command('auto_checkout')
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return
    
    # Check pending checkouts after running
    pending_after = Attendance.objects.filter(
        date=today,
        check_out__isnull=True,
        check_in__isnull=False
    ).count()
    
    print("\n" + "-"*60)
    print("RESULTS:")
    print("-"*60)
    print(f"Pending checkouts AFTER: {pending_after}")
    print(f"Checkouts processed: {pending_before - pending_after}")
    
    if pending_after == 0:
        print("\n✓ SUCCESS: All employees checked out!")
    else:
        print(f"\n⚠ WARNING: {pending_after} employee(s) still not checked out")
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    test_auto_checkout()
