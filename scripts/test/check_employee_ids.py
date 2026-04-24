"""
Check all employee IDs in the system
Run with: venv\Scripts\python check_employee_ids.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import EmployeeProfile

print("=" * 70)
print("EMPLOYEE ID CHECK")
print("=" * 70)

print("\n1. All Users (username):")
print("-" * 70)
for user in User.objects.all().order_by('username'):
    has_profile = hasattr(user, 'employeeprofile')
    profile_id = user.employeeprofile.employee_id if has_profile else 'N/A'
    print(f"  Username: {user.username:15} | Email: {user.email:30} | Profile ID: {profile_id}")

print("\n2. All Employee Profiles (employee_id):")
print("-" * 70)
for profile in EmployeeProfile.objects.all().order_by('employee_id'):
    emp_id = profile.employee_id if profile.employee_id else '(None)'
    print(f"  Employee ID: {emp_id:15} | Username: {profile.user.username:15} | Email: {profile.user.email}")

print("\n3. Profiles with NULL employee_id:")
print("-" * 70)
null_profiles = EmployeeProfile.objects.filter(employee_id__isnull=True)
print(f"  Count: {null_profiles.count()}")
for profile in null_profiles:
    print(f"  - User: {profile.user.username} | Email: {profile.user.email}")

print("\n4. Duplicate Check:")
print("-" * 70)
from django.db.models import Count
duplicates = EmployeeProfile.objects.values('employee_id').annotate(
    count=Count('employee_id')
).filter(count__gt=1)

if duplicates.exists():
    print("  WARNING: Duplicate employee IDs found!")
    for dup in duplicates:
        if dup['employee_id']:
            print(f"  - {dup['employee_id']}: {dup['count']} times")
else:
    print("  ✓ No duplicates found")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Total Users: {User.objects.count()}")
print(f"Total Profiles: {EmployeeProfile.objects.count()}")
print(f"Profiles with NULL employee_id: {EmployeeProfile.objects.filter(employee_id__isnull=True).count()}")
print("=" * 70)
