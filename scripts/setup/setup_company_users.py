"""
Setup Company Users - Creates HR and regular employees
This is how your company should set up users
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import EmployeeProfile

print("=" * 70)
print("COMPANY ATTENDANCE SYSTEM - USER SETUP")
print("=" * 70)

# Example 1: Create HR User
print("\n📋 Creating HR User...")
print("-" * 70)

hr_email = "hr@company.com"
hr_employee_id = "HR001"

if User.objects.filter(username=hr_employee_id).exists():
    print(f"⚠️  HR user {hr_employee_id} already exists")
    hr_user = User.objects.get(username=hr_employee_id)
else:
    hr_user = User.objects.create_user(
        username=hr_employee_id,
        email=hr_email,
        password='hr123',  # Change this!
        first_name='HR',
        last_name='Manager'
    )
    print(f"✅ Created HR user: {hr_employee_id}")

# Create/Update HR Profile
profile, created = EmployeeProfile.objects.get_or_create(
    user=hr_user,
    defaults={
        'employee_id': hr_employee_id,
        'is_hr': True,
        'profile_completed': True,
        'department': 'Human Resources',
        'designation': 'HR Manager'
    }
)

if not created:
    profile.is_hr = True
    profile.profile_completed = True
    profile.save()
    print(f"✅ Updated {hr_employee_id} to HR")
else:
    print(f"✅ Created HR profile for {hr_employee_id}")

print(f"\n🔐 HR Login Credentials:")
print(f"   Employee ID: {hr_employee_id}")
print(f"   Password: hr123")
print(f"   Email: {hr_email}")

# Example 2: Create Regular Employee
print("\n📋 Creating Regular Employee...")
print("-" * 70)

emp_email = "employee@company.com"
emp_employee_id = "EMP001"

if User.objects.filter(username=emp_employee_id).exists():
    print(f"⚠️  Employee {emp_employee_id} already exists")
    emp_user = User.objects.get(username=emp_employee_id)
else:
    emp_user = User.objects.create_user(
        username=emp_employee_id,
        email=emp_email,
        password='emp123',  # Change this!
        first_name='John',
        last_name='Doe'
    )
    print(f"✅ Created employee: {emp_employee_id}")

# Create/Update Employee Profile
profile, created = EmployeeProfile.objects.get_or_create(
    user=emp_user,
    defaults={
        'employee_id': emp_employee_id,
        'is_hr': False,
        'profile_completed': True,
        'department': 'Engineering',
        'designation': 'Software Developer'
    }
)

if not created:
    profile.profile_completed = True
    profile.save()
    print(f"✅ Updated profile for {emp_employee_id}")
else:
    print(f"✅ Created profile for {emp_employee_id}")

print(f"\n🔐 Employee Login Credentials:")
print(f"   Employee ID: {emp_employee_id}")
print(f"   Password: emp123")
print(f"   Email: {emp_email}")

# Summary
print("\n" + "=" * 70)
print("✅ SETUP COMPLETE - HOW IT WORKS")
print("=" * 70)

print("\n🌐 SINGLE LOGIN PAGE FOR EVERYONE:")
print("   URL: http://127.0.0.1:8000/login/")

print("\n👥 WHEN HR LOGS IN (HR001 / hr123):")
print("   ✓ Goes to dashboard")
print("   ✓ Sees 'HR Panel' link in navigation")
print("   ✓ Sees 'OT Approval' link in navigation")
print("   ✓ Can approve leave requests")
print("   ✓ Can view all employee attendance")

print("\n👤 WHEN EMPLOYEE LOGS IN (EMP001 / emp123):")
print("   ✓ Goes to dashboard")
print("   ✓ Sees only their own attendance")
print("   ✓ Can check in/out")
print("   ✓ Can request leave")
print("   ✓ NO HR Panel link (hidden)")

print("\n📝 TO ADD MORE USERS:")
print("   1. Employees register at: http://127.0.0.1:8000/register/")
print("   2. Or HR creates them in admin panel")
print("   3. To make someone HR: Run this script and modify the code")

print("\n" + "=" * 70)
print("🚀 READY TO USE!")
print("=" * 70)

# Show all users
print("\n📊 ALL USERS IN SYSTEM:")
print("-" * 70)
users = User.objects.all()
for user in users:
    try:
        profile = user.employeeprofile
        role = "HR" if profile.is_hr else "Employee"
        print(f"   {user.username:15} | {user.email:25} | {role}")
    except:
        print(f"   {user.username:15} | {user.email:25} | No Profile")

print("\n" + "=" * 70)
