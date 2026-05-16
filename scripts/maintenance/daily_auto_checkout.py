"""
Daily Auto-Checkout Script
Runs automatically at midnight IST to assign 7 PM checkout to all employees
who forgot to check out the previous day.

This script is designed to run via cron job.
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
from attendance.models import Attendance, LeaveRequest, WFHRequest, AuditLog, BreakLog


def log_message(message):
    """Log message with timestamp"""
    timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")


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


def assign_checkout(attendance, checkout_time, admin_user):
    """Assign checkout time to attendance record"""
    # Combine date with checkout time
    checkout_datetime = timezone.make_aware(
        datetime.combine(attendance.date, checkout_time)
    )
    
    # Update attendance
    attendance.check_out = checkout_datetime
    
    # Calculate hours worked
    if attendance.check_in:
        time_diff = checkout_datetime - attendance.check_in
        hours = time_diff.total_seconds() / 3600
        attendance.hours_worked = round(hours, 2)
    
    # Calculate total break time
    breaks = BreakLog.objects.filter(
        attendance=attendance,
        break_start__isnull=False,
        break_end__isnull=False
    )
    
    total_break_minutes = 0
    for break_log in breaks:
        break_duration = break_log.break_end - break_log.break_start
        total_break_minutes += break_duration.total_seconds() / 60
    
    attendance.total_break_time = int(total_break_minutes)
    
    # Calculate work hours (total hours - break hours)
    if attendance.hours_worked and attendance.total_break_time:
        break_hours = attendance.total_break_time / 60
        attendance.work_hours = round(attendance.hours_worked - break_hours, 2)
    else:
        attendance.work_hours = attendance.hours_worked
    
    attendance.save()
    
    # Create audit log
    AuditLog.objects.create(
        user=admin_user,
        action='check_out',
        description=f'Daily auto-checkout: Assigned {checkout_time.strftime("%I:%M %p")} for {attendance.employee.username} on {attendance.date}',
        ip_address='127.0.0.1',
        target_user=attendance.employee
    )
    
    return True


def main():
    log_message("=" * 70)
    log_message("DAILY AUTO-CHECKOUT SCRIPT STARTED")
    log_message("=" * 70)
    
    # Get yesterday's date (we run at midnight, so process previous day)
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    log_message(f"Processing date: {yesterday.strftime('%Y-%m-%d')}")
    
    # Get admin user for audit log
    admin_user = None
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.filter(employeeprofile__is_hr=True).first()
    except:
        pass
    
    if not admin_user:
        admin_user = User.objects.first()
    
    log_message(f"Audit log user: {admin_user.username if admin_user else 'None'}")
    
    # Default checkout time
    checkout_time = time(19, 0)  # 7:00 PM
    log_message(f"Default checkout time: {checkout_time.strftime('%I:%M %p')}")
    
    # Find all missing checkouts for yesterday
    missing_checkouts = Attendance.objects.filter(
        date=yesterday,
        check_in__isnull=False,
        check_out__isnull=True
    ).select_related('employee')
    
    total_found = missing_checkouts.count()
    log_message(f"Found {total_found} missing checkout(s) for {yesterday.strftime('%Y-%m-%d')}")
    
    if total_found == 0:
        log_message("No missing checkouts found. Exiting.")
        log_message("=" * 70)
        return
    
    # Process each missing checkout
    total_processed = 0
    total_skipped = 0
    
    for attendance in missing_checkouts:
        employee = attendance.employee
        employee_name = employee.get_full_name() or employee.username
        
        # Check if on leave or WFH
        on_leave, reason = check_leave_or_wfh(employee, yesterday)
        
        if on_leave:
            log_message(f"⏭️  SKIPPED: {employee_name} - {reason}")
            total_skipped += 1
            continue
        
        # Assign checkout
        try:
            assign_checkout(attendance, checkout_time, admin_user)
            check_in_time = attendance.check_in.strftime('%I:%M %p')
            log_message(f"✅ PROCESSED: {employee_name} - Check-in: {check_in_time}, Assigned checkout: 07:00 PM")
            total_processed += 1
        except Exception as e:
            log_message(f"❌ ERROR: {employee_name} - {str(e)}")
            total_skipped += 1
    
    # Summary
    log_message("=" * 70)
    log_message("SUMMARY")
    log_message("=" * 70)
    log_message(f"Date processed: {yesterday.strftime('%Y-%m-%d')}")
    log_message(f"Total found: {total_found}")
    log_message(f"Successfully processed: {total_processed}")
    log_message(f"Skipped (leave/WFH/errors): {total_skipped}")
    log_message("=" * 70)
    log_message("DAILY AUTO-CHECKOUT SCRIPT COMPLETED")
    log_message("=" * 70)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log_message(f"FATAL ERROR: {str(e)}")
        import traceback
        log_message(traceback.format_exc())
        sys.exit(1)
