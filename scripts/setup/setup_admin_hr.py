"""
Complete Admin/HR Setup Script
Run this to create or update admin/HR users
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import EmployeeProfile

def create_superuser():
    """Create a Django superuser (admin)"""
    print("\n" + "=" * 60)
    print("CREATE SUPERUSER (ADMIN)")
    print("=" * 60)
    
    username = input("Enter username (e.g., admin): ").strip()
    if not username:
        print("❌ Username is required!")
        return
    
    if User.objects.filter(username=username).exists():
        print(f"❌ User '{username}' already exists!")
        return
    
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()
    
    if not password:
        print("❌ Password is required!")
        return
    
    # Create superuser
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    
    # Create profile
    EmployeeProfile.objects.create(
        user=user,
        employee_id=username,
        is_hr=True,
        profile_completed=True
    )
    
    print(f"\n✅ Superuser created successfully!")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"\n🔐 Login at: http://127.0.0.1:8000/login/")
    print(f"🔐 Admin panel: http://127.0.0.1:8000/admin/")

def create_hr_user():
    """Create an HR user (not superuser)"""
    print("\n" + "=" * 60)
    print("CREATE HR USER")
    print("=" * 60)
    
    employee_id = input("Enter Employee ID (e.g., HR001): ").strip()
    if not employee_id:
        print("❌ Employee ID is required!")
        return
    
    if User.objects.filter(username=employee_id).exists():
        print(f"❌ User with employee ID '{employee_id}' already exists!")
        return
    
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()
    full_name = input("Enter full name: ").strip()
    
    if not password:
        print("❌ Password is required!")
        return
    
    # Parse name
    first_name = full_name.split()[0] if full_name else ""
    last_name = " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else ""
    
    # Create user
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
    print(f"\n🔐 Login at: http://127.0.0.1:8000/login/")

def make_existing_user_hr():
    """Make an existing user an HR"""
    print("\n" + "=" * 60)
    print("MAKE EXISTING USER HR")
    print("=" * 60)
    
    # Show existing users
    users = User.objects.all()
    if not users.exists():
        print("❌ No users found in database!")
        return
    
    print("\nExisting users:")
    for i, user in enumerate(users, 1):
        hr_status = ""
        try:
            if user.employeeprofile.is_hr:
                hr_status = " [Already HR]"
        except EmployeeProfile.DoesNotExist:
            hr_status = " [No profile]"
        
        print(f"  {i}. {user.username} - {user.email}{hr_status}")
    
    username = input("\nEnter username to make HR: ").strip()
    
    try:
        user = User.objects.get(username=username)
        
        # Get or create profile
        profile, created = EmployeeProfile.objects.get_or_create(
            user=user,
            defaults={
                'employee_id': user.username,
                'is_hr': True,
                'profile_completed': True
            }
        )
        
        if not created:
            profile.is_hr = True
            profile.profile_completed = True
            profile.save()
        
        print(f"\n✅ User '{username}' is now an HR!")
        
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found!")

def list_all_users():
    """List all users and their status"""
    print("\n" + "=" * 60)
    print("ALL USERS IN DATABASE")
    print("=" * 60)
    
    users = User.objects.all()
    
    if not users.exists():
        print("\n❌ No users found in database")
        return
    
    for user in users:
        print(f"\n👤 {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Name: {user.get_full_name() or 'Not set'}")
        print(f"   Superuser: {'Yes' if user.is_superuser else 'No'}")
        
        try:
            profile = user.employeeprofile
            print(f"   Employee ID: {profile.employee_id}")
            print(f"   HR: {'Yes' if profile.is_hr else 'No'}")
            print(f"   Profile Complete: {'Yes' if profile.profile_completed else 'No'}")
        except EmployeeProfile.DoesNotExist:
            print(f"   ⚠️  No profile")

def main():
    print("\n" + "=" * 60)
    print("ADMIN/HR SETUP TOOL")
    print("=" * 60)
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Create Superuser (Admin)")
        print("2. Create HR User")
        print("3. Make Existing User HR")
        print("4. List All Users")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            create_superuser()
        elif choice == '2':
            create_hr_user()
        elif choice == '3':
            make_existing_user_hr()
        elif choice == '4':
            list_all_users()
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice!")

if __name__ == '__main__':
    main()
