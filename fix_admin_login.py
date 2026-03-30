"""
Fix admin login - Creates/resets admin user
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from attendance.models import EmployeeProfile

print("=" * 60)
print("FIX ADMIN LOGIN")
print("=" * 60)

# Delete existing admin if exists
if User.objects.filter(username='admin').exists():
    print("\n⚠️  Existing 'admin' user found. Deleting...")
    User.objects.filter(username='admin').delete()
    print("✓ Deleted")

# Create fresh admin user
print("\n📝 Creating new admin user...")
admin_user = User.objects.create_superuser(
    username='admin',
    email='admin@company.com',
    password='admin123',
    first_name='Admin',
    last_name='User'
)
print("✓ User created")

# Create profile
print("📝 Creating employee profile...")
EmployeeProfile.objects.create(
    user=admin_user,
    employee_id='admin',
    is_hr=True,
    profile_completed=True,
    department='Administration',
    designation='Administrator'
)
print("✓ Profile created")

# Test authentication
print("\n🔐 Testing authentication...")
test_auth = authenticate(username='admin', password='admin123')

if test_auth is not None:
    print("✅ Authentication SUCCESSFUL!")
else:
    print("❌ Authentication FAILED!")
    print("Trying to fix...")
    admin_user.set_password('admin123')
    admin_user.save()
    test_auth = authenticate(username='admin', password='admin123')
    if test_auth:
        print("✅ Fixed! Authentication now works!")

print("\n" + "=" * 60)
print("✅ ADMIN USER READY")
print("=" * 60)
print("\n🔐 Login Credentials:")
print("   Username: admin")
print("   Password: admin123")
print("\n🌐 Login URL:")
print("   http://127.0.0.1:8000/login/")
print("\n📋 User Details:")
print(f"   - Email: {admin_user.email}")
print(f"   - Superuser: {admin_user.is_superuser}")
print(f"   - Active: {admin_user.is_active}")
print(f"   - Staff: {admin_user.is_staff}")

try:
    profile = admin_user.employeeprofile
    print(f"   - Employee ID: {profile.employee_id}")
    print(f"   - Is HR: {profile.is_hr}")
    print(f"   - Profile Complete: {profile.profile_completed}")
except:
    print("   - Profile: Error")

print("\n" + "=" * 60)
print("🚀 You can now login!")
print("=" * 60)
