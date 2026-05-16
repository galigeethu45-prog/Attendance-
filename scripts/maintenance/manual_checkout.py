"""
Manual Checkout Script - Bulk Missing Checkouts
Assigns 7 PM checkout to ALL missing checkouts for a specific employee

Usage:
    python scripts/maintenance/manual_checkout.py

Features:
- Finds ALL missing checkouts for an employee (past dates up to today)
- Assigns 7 PM checkout automatically
- Skips employees on leave/WFH
- Creates audit log entries
- No override of existing checkouts
"""

import os
import sys
import django
from datetime import datetime, time, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from attendance.models import Attendance, LeaveRequest, WFHRequest, AuditLog


def check_leave_or_wfh(user, date):
    """Check if user has approved leave or WFH for the date"""
    # Check leave
    leave = LeaveRequest.objects.filter(
        employee=user,
        status='approved',
        start_date__lte=date,
        end_date__gte=date
    ).first()
    
    if leave:
        return True, f"On {leave.get_leave_type_display()} leave"
    
    # Check WFH
    wfh = WFHRequest.objects.filter(
        employee=user,
        status='approved',
        start_date__lte=date,
        end_date__gte=date
    ).first()
    
    if wfh:
        return True, "On approved WFH"
    
    return False, None


def find_missing_checkouts(user):
    """Find all attendance records without checkout for the user"""
    today = timezone.now().date()
    
    # Get all attendance records with check-in but no check-out (excluding today)
    missing = Attendance.objects.filter(
        employee=user,
        check_in__isnull=False,
        check_out__isnull=True,
        date__lt=today  # Changed from __lte to __lt to exclude today
    ).order_by('date')
    
    return missing


def assign_checkout(attendance, checkout_time, admin_user):
    """Assign checkout time to attendance record"""
    # Combine date with checkout time
    checkout_datetime = timezone.make_aware(
        datetime.combine(attendance.date, checkout_time)
    )
    
    # Update attendance
    attendance.check_out = checkout_datetime
    
    # Calculate work hours using the model's method
    attendance.calculate_work_hours()
    attendance.save()
    
    # Create audit log
    AuditLog.objects.create(
        user=admin_user,
        action='check_out',
        description=f'Manual bulk checkout: Assigned {checkout_time.strftime("%I:%M %p")} for {attendance.employee.username} on {attendance.date}',
        ip_address='127.0.0.1',
        target_user=attendance.employee
    )
    
    return True


def main():
    print("=" * 70)
    print("BULK MISSING CHECKOUT ASSIGNMENT")
    print("=" * 70)
    print()
    print("This script will find ALL missing checkouts for an employee")
    print("and assign 7:00 PM checkout time to all of them.")
    print()
    print("=" * 70)
    print()
    
    # Get admin user (use current Windows user or default)
    import getpass
    current_user = getpass.getuser()
    
    # Try to find admin user
    admin_user = None
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.filter(employeeprofile__is_hr=True).first()
    except:
        pass
    
    if not admin_user:
        print("⚠️  Warning: No admin user found for audit log")
        admin_user = User.objects.first()  # Use any user as fallback
    
    print(f"📝 Audit log will use: {admin_user.username}")
    print()
    
    # Default checkout time
    checkout_time = time(19, 0)  # 7:00 PM
    print(f"⏰ Default Checkout Time: {checkout_time.strftime('%I:%M %p')}")
    print()
    print("=" * 70)
    print()
    
    # Process employees one by one
    total_processed = 0
    total_skipped = 0
    
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
        
        # Find all missing checkouts
        missing_records = find_missing_checkouts(user)
        
        if not missing_records:
            print("✅ No missing checkouts found!")
            print()
            continue
        
        print(f"📋 Found {missing_records.count()} missing checkout(s):")
        print()
        
        # Show all missing checkouts
        records_to_process = []
        for attendance in missing_records:
            # Check if on leave or WFH
            on_leave, reason = check_leave_or_wfh(user, attendance.date)
            
            if on_leave:
                print(f"  ⏭️  {attendance.date.strftime('%Y-%m-%d')} - Skipped ({reason})")
                total_skipped += 1
            else:
                check_in_time = attendance.check_in.strftime('%I:%M %p')
                print(f"  ✓ {attendance.date.strftime('%Y-%m-%d')} - Check-in: {check_in_time}")
                records_to_process.append(attendance)
        
        print()
        
        if not records_to_process:
            print("⚠️  All records skipped (on leave/WFH)")
            print()
            continue
        
        # Confirm bulk assignment
        print(f"Assign 7:00 PM checkout to {len(records_to_process)} record(s)? (yes/no):")
        confirm = input("> ").strip().lower()
        
        if confirm in ['yes', 'y']:
            print()
            print("Processing...")
            success_count = 0
            
            for attendance in records_to_process:
                try:
                    assign_checkout(attendance, checkout_time, admin_user)
                    print(f"  ✅ {attendance.date.strftime('%Y-%m-%d')} - Checkout assigned")
                    success_count += 1
                    total_processed += 1
                except Exception as e:
                    print(f"  ❌ {attendance.date.strftime('%Y-%m-%d')} - Error: {str(e)}")
                    total_skipped += 1
            
            print()
            print(f"✅ Successfully assigned {success_count} checkout(s) for {employee_id}")
        else:
            print("⏭️  Skipped by user")
            total_skipped += len(records_to_process)
        
        print()
        print("=" * 70)
        print()
    
    # Summary
    print()
    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"✅ Total checkouts assigned: {total_processed}")
    print(f"⏭️  Total skipped: {total_skipped}")
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
