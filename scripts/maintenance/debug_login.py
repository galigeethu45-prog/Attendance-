"""
Debug script to check login issues
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from attendance.models import EmployeeProfile

print("=" * 60)
print("LOGIN DEBUG TOOL")
print("=" * 60)

# Check if admin user exists
print("\n1. Checking if 'admin' user exists...")
try:
    admin_user = User.objects.get(username='admin')
    print(f"   ✓ User 'admin' found")
    print(f"   - Email: {admin_user.email}")
    print(f"   - Is Active: {admin_user.is_active}")
    print(f"   - Is Superuser: {admin_user.is_superuser}")
    print(f"   - Is Staff: {admin_user.is_staff}")
    
    # Check profile
    try:
        profile = admin_user.employeeprofile
        print(f"   - Has Profile: Yes")
        print(f"   - Employee ID: {profile.employee_id}")
        print(f"   - Is HR: {profile.is_hr}")
        print(f"   - Profile Completed: {profile.profile_completed}")
    except EmployeeProfile.DoesNotExist:
        print(f"   - Has Profile: No")
        print(f"   ⚠️  Creating profile...")
        EmployeeProfile.objects.create(
            user=admin_user,
            employee_id='admin',
            is_hr=True,
            profile_completed=True
        )
        print(f"   ✓ Profile created")
    
except User.DoesNotExist:
    print(f"   ✗ User 'admin' NOT found")
    print(f"   Creating admin user...")
    
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@company.com',
        password='admin123'
    )
    
    EmployeeProfile.objects.create(
        user=admin_user,
        employee_id='admin',
        is_hr=True,
        profile_completed=True
    )
    
    print(f"   ✓ Admin user created")

# Test authentication
print("\n2. Testing authentication with 'admin' / 'admin123'...")
test_user = authenticate(username='admin', password='admin123')

if test_user is not None:
    print(f"   ✓ Authentication SUCCESSFUL")
    print(f"   - User: {test_user.username}")
    print(f"   - Active: {test_user.is_active}")
else:
    print(f"   ✗ Authentication FAILED")
    print(f"   Resetting password to 'admin123'...")
    
    admin_user = User.objects.get(username='admin')
    admin_user.set_password('admin123')
    admin_user.save()
    
    print(f"   ✓ Password reset")
    
    # Test again
    test_user = authenticate(username='admin', password='admin123')
    if test_user:
        print(f"   ✓ Authentication now works!")
    else:
        print(f"   ✗ Still failing - check Django settings")

# List all users
print("\n3. All users in database:")
users = User.objects.all()
for user in users:
    status = "✓" if user.is_active else "✗"
    hr_status = ""
    try:
        if user.employeeprofile.is_hr:
            hr_status = " [HR]"
    except:
        pass
    print(f"   {status} {user.username} - {user.email}{hr_status}")

print("\n" + "=" * 60)
print("READY TO LOGIN")
print("=" * 60)
print("\nCredentials:")
print("  Username: admin")
print("  Password: admin123")
print("\nURL: http://127.0.0.1:8000/login/")
print("=" * 60)
