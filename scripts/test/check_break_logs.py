#!/usr/bin/env python
"""
Check Break Logs Data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from attendance.models import BreakLog, Attendance
from django.utils import timezone
from datetime import timedelta

print("=" * 80)
print("BREAK LOGS CHECK")
print("=" * 80)

# Check all break logs
break_logs = BreakLog.objects.all()
print(f"\nTotal Break Logs: {break_logs.count()}")

if break_logs.exists():
    print("\nBreak Log Details:")
    print("-" * 80)
    
    for log in break_logs:
        print(f"\nBreak Log ID: {log.id}")
        print(f"  Attendance ID: {log.attendance.id}")
        print(f"  Employee: {log.attendance.employee.username}")
        
        try:
            emp_id = log.attendance.employee.employeeprofile.employee_id
            print(f"  Employee ID: {emp_id}")
        except:
            print(f"  Employee ID: No profile or no employee_id")
        
        print(f"  Break Type: {log.break_type}")
        print(f"  Start: {log.break_start}")
        print(f"  End: {log.break_end}")
        print(f"  Duration: {log.duration_minutes} min")
        
        # Check if it matches today's filter
        today = timezone.now().date()
        break_date = log.break_start.date()
        print(f"  Date: {break_date}")
        print(f"  Is Today: {break_date == today}")
        
        # Check if it matches week filter
        week_start = today - timedelta(days=today.weekday())
        print(f"  Is This Week: {break_date >= week_start}")

# Check today's attendance
print("\n" + "=" * 80)
print("TODAY'S ATTENDANCE")
print("=" * 80)

today = timezone.now().date()
today_attendance = Attendance.objects.filter(date=today)

print(f"\nTotal Attendance Today: {today_attendance.count()}")

for att in today_attendance:
    print(f"\n{att.employee.username}:")
    print(f"  Check-in: {att.check_in}")
    print(f"  Check-out: {att.check_out}")
    
    breaks = BreakLog.objects.filter(attendance=att)
    print(f"  Breaks: {breaks.count()}")
    
    for brk in breaks:
        print(f"    - {brk.break_type}: {brk.break_start} to {brk.break_end}")

# Test the query from HR dashboard
print("\n" + "=" * 80)
print("HR DASHBOARD QUERY TEST")
print("=" * 80)

# Default filter (week)
week_start = today - timedelta(days=today.weekday())
break_logs_week = BreakLog.objects.select_related(
    'attendance__employee__employeeprofile'
).filter(break_start__date__gte=week_start).order_by('-break_start')

print(f"\nBreak Logs (This Week): {break_logs_week.count()}")

# Today filter
break_logs_today = BreakLog.objects.select_related(
    'attendance__employee__employeeprofile'
).filter(break_start__date=today).order_by('-break_start')

print(f"Break Logs (Today): {break_logs_today.count()}")

# All time
break_logs_all = BreakLog.objects.select_related(
    'attendance__employee__employeeprofile'
).order_by('-break_start')

print(f"Break Logs (All Time): {break_logs_all.count()}")

print("\n" + "=" * 80)
print()
