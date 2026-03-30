"""
Script to create an HR user or make an existing user HR
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import EmployeeProfile

print("=" * 50)
print("HR USER SETUP")
print("=" * 50)

# Option 1: Create new HR user
print("\nOption 1: Create New HR User")
print("-" * 50)
employee_id = input("Enter Employee ID (e.g., HR001): ").strip()
email = input("Enter Email: ").strip()
password = input("Enter Password: ").strip()
full_name = input("Enter Full Name: ").strip()

if employee_id and email and password:
    # Check if user exists
    if User.objects.filter(username=employee_id).exists():
        print(f"\n❌ User with employee ID '{employee_id}' already exists!")
        user = User.objects.get(username=employee_id)
        make_hr = input("Make this user HR? (yes/no): ").strip().lower()
        if make_hr == 'yes':
            try:
                profile = user.employeeprofile
                profile.is_hr = True
                profile.profile_completed = True
                profile.save()
                print(f"✅ User '{employee_id}' is now an HR!")
            except EmployeeProfile.DoesNotExist:
                EmployeeProfile.objects.create(
                    user=user,
                    employee_id=employee_id,
                    is_hr=True,
                    profile_completed=True
                )
                print(f"✅ Created profile and made '{employee_id}' an HR!")
    else:
        # Create new user
        first_name = full_name.split()[0] if full_name else ""
        last_name = " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else ""
        
        user = User.objects.create_user(
            username=employee_id,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create HR profile
        EmployeeProfile.objects.create(
            user=user,
            employee_id=employee_id,
            is_hr=True,
            profile_completed=True
        )
        
        print(f"\n✅ HR user created successfully!")
        print(f"   Employee ID: {employee_id}")
        print(f"   Email: {email}")
        print(f"   Name: {full_name}")
        print(f"   Password: {password}")
        print(f"\n🔐 You can now login with these credentials")
else:
    print("\n❌ All fields are required!")

print("\n" + "=" * 50)
print("EXISTING HR USERS:")
print("=" * 50)
hr_profiles = EmployeeProfile.objects.filter(is_hr=True)
if hr_profiles.exists():
    for profile in hr_profiles:
        print(f"  - {profile.employee_id}: {profile.user.get_full_name() or profile.user.username}")
else:
    print("  No HR users found")

print("\n" + "=" * 50)
