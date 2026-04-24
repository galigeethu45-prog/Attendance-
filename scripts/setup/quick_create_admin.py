"""
Quick script to create admin user with default credentials
Username: admin
Password: admin123
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import EmployeeProfile

# Check if admin exists
if User.objects.filter(username='admin').exists():
    print("❌ Admin user already exists!")
    print("   Username: admin")
    print("   Try logging in with your password")
    
    # Make sure they have HR access
    user = User.objects.get(username='admin')
    try:
        profile = user.employeeprofile
        if not profile.is_hr:
            profile.is_hr = True
            profile.profile_completed = True
            profile.save()
            print("✅ Updated admin to have HR access")
    except EmployeeProfile.DoesNotExist:
        EmployeeProfile.objects.create(
            user=user,
            employee_id='admin',
            is_hr=True,
            profile_completed=True
        )
        print("✅ Created profile with HR access for admin")
else:
    # Create admin superuser
    user = User.objects.create_superuser(
        username='admin',
        email='admin@company.com',
        password='admin123'
    )
    
    # Create profile
    EmployeeProfile.objects.create(
        user=user,
        employee_id='admin',
        is_hr=True,
        profile_completed=True
    )
    
    print("=" * 60)
    print("✅ ADMIN USER CREATED SUCCESSFULLY!")
    print("=" * 60)
    print("\n🔐 Login Credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n🌐 Login URL: http://127.0.0.1:8000/login/")
    print("🔧 Admin Panel: http://127.0.0.1:8000/admin/")
    print("\n⚠️  IMPORTANT: Change the password after first login!")
    print("=" * 60)
