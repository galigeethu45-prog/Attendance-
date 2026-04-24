"""
Script to update existing employee profiles to set profile_completed=True
Run this once to update all existing employees
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from attendance.models import EmployeeProfile

# Update all existing profiles
updated = EmployeeProfile.objects.filter(profile_completed=False).update(profile_completed=True)
print(f"Updated {updated} employee profile(s) to profile_completed=True")

# Show all profiles
profiles = EmployeeProfile.objects.all()
print(f"\nTotal profiles: {profiles.count()}")
for profile in profiles:
    print(f"- {profile.employee_id}: {profile.user.username} (completed: {profile.profile_completed})")
