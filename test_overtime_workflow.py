"""
Test script to verify overtime workflow
Run with: python test_overtime_workflow.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import Overtime, EmployeeProfile
from datetime import date

print("=" * 60)
print("OVERTIME WORKFLOW TEST")
print("=" * 60)

# Get test user
try:
    user = User.objects.get(username='employee1')
    print(f"\n✓ Found user: {user.username}")
except User.DoesNotExist:
    print("\n✗ User 'employee1' not found. Please create it first.")
    exit(1)

# Check profile
try:
    profile = user.employeeprofile
    print(f"✓ Profile exists: {profile.employee_id}")
    print(f"  - Is HR: {profile.is_hr}")
except EmployeeProfile.DoesNotExist:
    print("✗ Employee profile not found")
    exit(1)

# Check existing OT records
ot_count = Overtime.objects.filter(employee=user).count()
print(f"\n✓ Existing OT records: {ot_count}")

# Show recent OT records
print("\nRecent OT Records:")
print("-" * 60)
for ot in Overtime.objects.filter(employee=user).order_by('-date')[:5]:
    print(f"  ID: {ot.id}")
    print(f"  Date: {ot.date}")
    print(f"  Status: {ot.status}")
    print(f"  Reason: {ot.reason[:50] if ot.reason else 'N/A'}")
    print(f"  Start: {ot.start_time or 'Not started'}")
    print(f"  End: {ot.end_time or 'Not ended'}")
    print(f"  Hours: {ot.get_ot_hours_display()}")
    print("-" * 60)

# Test workflow states
print("\nWorkflow State Check:")
print("-" * 60)

# Pending requests
pending = Overtime.objects.filter(employee=user, status='pending').count()
print(f"  Pending requests: {pending}")

# Approved but not started
approved_not_started = Overtime.objects.filter(
    employee=user,
    status='approved',
    start_time__isnull=True
).count()
print(f"  Approved (not started): {approved_not_started}")

# Active (started but not ended)
active = Overtime.objects.filter(
    employee=user,
    status='approved',
    start_time__isnull=False,
    end_time__isnull=True
).count()
print(f"  Active sessions: {active}")

# Completed
completed = Overtime.objects.filter(employee=user, status='completed').count()
print(f"  Completed: {completed}")

# Rejected
rejected = Overtime.objects.filter(employee=user, status='rejected').count()
print(f"  Rejected: {rejected}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nIf you see this message, the database structure is correct.")
print("You can now access the overtime page at: http://127.0.0.1:8000/attendance/overtime/")
