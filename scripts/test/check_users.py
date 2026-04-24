"""
Script to check existing users and their profiles
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import EmployeeProfile

print("=" * 60)
print("EXISTING USERS IN DATABASE")
print("=" * 60)

users = User.objects.all()

if users.exists():
    for user in users:
        print(f"\n👤 Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Full Name: {user.get_full_name() or 'Not set'}")
        print(f"   Is Superuser: {user.is_superuser}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Active: {user.is_active}")
        
        try:
            profile = user.employeeprofile
            print(f"   Employee ID: {profile.employee_id}")
            print(f"   Is HR: {profile.is_hr}")
            print(f"   Profile Completed: {profile.profile_completed}")
            print(f"   Department: {profile.department or 'Not set'}")
        except EmployeeProfile.DoesNotExist:
            print(f"   ⚠️  No EmployeeProfile found")
else:
    print("\n❌ No users found in database")

print("\n" + "=" * 60)
print("HR USERS:")
print("=" * 60)

hr_profiles = EmployeeProfile.objects.filter(is_hr=True)
if hr_profiles.exists():
    for profile in hr_profiles:
        print(f"  ✓ {profile.employee_id}: {profile.user.get_full_name() or profile.user.username}")
else:
    print("  ❌ No HR users found")

print("\n" + "=" * 60)
