#!/usr/bin/env python
"""
Test Break Logs Fix
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from attendance.models import BreakLog
from django.utils import timezone
from datetime import timedelta

print("=" * 80)
print("BREAK LOGS FIX TEST")
print("=" * 80)

today = timezone.now().date()

# Test TODAY filter (new method)
print("\n📅 Testing TODAY filter:")
print("-" * 80)

today_start = timezone.datetime.combine(today, timezone.datetime.min.time())
today_end = timezone.datetime.combine(today, timezone.datetime.max.time())
today_start = timezone.make_aware(today_start)
today_end = timezone.make_aware(today_end)

print(f"Today Start: {today_start}")
print(f"Today End: {today_end}")

break_logs_today = BreakLog.objects.filter(break_start__range=(today_start, today_end))
print(f"\nBreak Logs Found: {break_logs_today.count()}")

for log in break_logs_today:
    print(f"  • {log.attendance.employee.username} - {log.break_type} - {log.break_start}")

# Test WEEK filter (new method)
print("\n📅 Testing WEEK filter:")
print("-" * 80)

week_start = today - timedelta(days=today.weekday())
week_start_dt = timezone.datetime.combine(week_start, timezone.datetime.min.time())
week_start_dt = timezone.make_aware(week_start_dt)

print(f"Week Start: {week_start_dt}")

break_logs_week = BreakLog.objects.filter(break_start__gte=week_start_dt)
print(f"\nBreak Logs Found: {break_logs_week.count()}")

for log in break_logs_week:
    print(f"  • {log.attendance.employee.username} - {log.break_type} - {log.break_start}")

# Test MONTH filter (new method)
print("\n📅 Testing MONTH filter:")
print("-" * 80)

month_start = today.replace(day=1)
month_start_dt = timezone.datetime.combine(month_start, timezone.datetime.min.time())
month_start_dt = timezone.make_aware(month_start_dt)

print(f"Month Start: {month_start_dt}")

break_logs_month = BreakLog.objects.filter(break_start__gte=month_start_dt)
print(f"\nBreak Logs Found: {break_logs_month.count()}")

for log in break_logs_month:
    print(f"  • {log.attendance.employee.username} - {log.break_type} - {log.break_start}")

# Test ALL TIME
print("\n📅 Testing ALL TIME filter:")
print("-" * 80)

break_logs_all = BreakLog.objects.all()
print(f"Break Logs Found: {break_logs_all.count()}")

for log in break_logs_all:
    print(f"  • {log.attendance.employee.username} - {log.break_type} - {log.break_start}")

print("\n" + "=" * 80)
print("✅ FIX VERIFICATION")
print("=" * 80)

if break_logs_today.count() > 0:
    print("✅ TODAY filter: WORKING")
else:
    print("❌ TODAY filter: NOT WORKING")

if break_logs_week.count() > 0:
    print("✅ WEEK filter: WORKING")
else:
    print("❌ WEEK filter: NOT WORKING")

if break_logs_month.count() > 0:
    print("✅ MONTH filter: WORKING")
else:
    print("❌ MONTH filter: NOT WORKING")

print("\n" + "=" * 80)
print()
