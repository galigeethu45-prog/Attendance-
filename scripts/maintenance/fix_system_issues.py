#!/usr/bin/env python
"""
Fix System Issues
Addresses warnings found in system check
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import EmployeeProfile, Attendance
from django.utils import timezone
from datetime import datetime, time as dt_time

print("=" * 80)
print("SYSTEM ISSUES FIX")
print("=" * 80)

# Issue 1: No HR users
print("\n🔧 FIX 1: Create/Assign HR User")
print("-" * 80)

users = User.objects.all()
if not users.exists():
    print("❌ No users in system. Please create users first.")
else:
    print(f"Found {users.count()} users:")
    for i, user in enumerate(users, 1):
        profile = getattr(user, 'employeeprofile', None)
        is_hr = profile.is_hr if profile else False
        print(f"{i}. {user.username} - HR: {is_hr}")
    
    # Check if any HR exists
    hr_count = EmployeeProfile.objects.filter(is_hr=True).count()
    
    if hr_count == 0:
        print("\n⚠️  No HR users found. Let's create one!")
        
        choice = input("\nMake a user HR? Enter username (or press Enter to skip): ").strip()
        
        if choice:
            try:
                user = User.objects.get(username=choice)
                profile, created = EmployeeProfile.objects.get_or_create(user=user)
                profile.is_hr = True
                profile.save()
                
                print(f"\n✅ {user.username} is now an HR user!")
                print(f"   Name: {user.get_full_name() or 'Not set'}")
                print(f"   Email: {user.email or 'Not set'}")
            except User.DoesNotExist:
                print(f"\n❌ User '{choice}' not found")
        else:
            print("\n⏭️  Skipped HR user creation")
    else:
        print(f"\n✓ {hr_count} HR user(s) already exist")

# Issue 2: Old attendance records without checkout
print("\n🔧 FIX 2: Auto-Checkout Old Attendance Records")
print("-" * 80)

today = timezone.now().date()
old_open_attendance = Attendance.objects.filter(
    date__lt=today,
    check_out__isnull=True
)

if not old_open_attendance.exists():
    print("✓ No old open attendance records found")
else:
    print(f"Found {old_open_attendance.count()} old records without checkout:")
    
    for attendance in old_open_attendance:
        print(f"  • {attendance.employee.username} - {attendance.date}")
    
    fix = input("\nAuto-checkout these records at 7 PM? (y/n): ").strip().lower()
    
    if fix == 'y':
        count = 0
        for attendance in old_open_attendance:
            # Set checkout to 7 PM of that day
            checkout_time = datetime.combine(
                attendance.date,
                dt_time(19, 0)  # 7 PM
            )
            checkout_time = timezone.make_aware(checkout_time)
            
            attendance.check_out = checkout_time
            attendance.calculate_work_hours()
            attendance.save()
            
            count += 1
            print(f"  ✓ Auto-checked out: {attendance.employee.username} - {attendance.date}")
        
        print(f"\n✅ Auto-checked out {count} records")
    else:
        print("\n⏭️  Skipped auto-checkout")

# Issue 3: Users without email
print("\n🔧 FIX 3: Add Email Addresses")
print("-" * 80)

users_without_email = User.objects.filter(email='') | User.objects.filter(email__isnull=True)

if not users_without_email.exists():
    print("✓ All users have email addresses")
else:
    print(f"Found {users_without_email.count()} users without email:")
    
    for user in users_without_email:
        print(f"  • {user.username}")
    
    add_emails = input("\nAdd email addresses? (y/n): ").strip().lower()
    
    if add_emails == 'y':
        for user in users_without_email:
            email = input(f"  Email for {user.username}: ").strip()
            if email and '@' in email:
                user.email = email
                user.save()
                print(f"    ✓ Added: {email}")
            else:
                print(f"    ⏭️  Skipped")
        
        print("\n✅ Email addresses updated")
    else:
        print("\n⏭️  Skipped email addition")

# Summary
print("\n" + "=" * 80)
print("FIX COMPLETED")
print("=" * 80)

print("\n📝 Next Steps:")
print("1. Run: python comprehensive_system_check.py (to verify fixes)")
print("2. Test HR dashboard access")
print("3. Test all features")
print()
