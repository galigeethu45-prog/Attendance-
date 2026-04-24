#!/usr/bin/env python
"""
Add or update email addresses for users
Useful for testing password reset functionality
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 70)
print("USER EMAIL MANAGEMENT")
print("=" * 70)

# Show all users
print("\n📋 Current Users:")
print("-" * 70)

users = User.objects.all()
if not users.exists():
    print("❌ No users found in system")
    print("   Create users first before adding emails")
    exit(1)

for user in users:
    email_status = user.email if user.email else "❌ No email"
    print(f"  • {user.username} ({user.get_full_name() or 'No name'}) - {email_status}")

# Show users without email
users_without_email = User.objects.filter(email='') | User.objects.filter(email__isnull=True)
if users_without_email.exists():
    print(f"\n⚠️  {users_without_email.count()} users without email addresses")

# Add/Update email
print("\n" + "=" * 70)
print("ADD OR UPDATE EMAIL ADDRESS")
print("=" * 70)

username = input("\nEnter username to add/update email (or press Enter to exit): ").strip()

if username:
    try:
        user = User.objects.get(username=username)
        print(f"\n✓ Found user: {user.username}")
        
        if user.email:
            print(f"  Current email: {user.email}")
            update = input("  Update email? (y/n): ").strip().lower()
            if update != 'y':
                print("  Cancelled")
                exit(0)
        
        new_email = input("  Enter new email address: ").strip()
        
        if new_email:
            # Validate email format (basic)
            if '@' not in new_email or '.' not in new_email:
                print("  ❌ Invalid email format")
                exit(1)
            
            user.email = new_email
            user.save()
            
            print(f"\n✅ Email updated successfully!")
            print(f"  User: {user.username}")
            print(f"  Email: {user.email}")
            
            print("\n📝 Next Steps:")
            print("  1. Test password reset: http://127.0.0.1:8000/password-reset/")
            print(f"  2. Enter email: {user.email}")
            print("  3. Check email inbox for reset link")
        else:
            print("  ❌ Email cannot be empty")
            
    except User.DoesNotExist:
        print(f"\n❌ User '{username}' not found")
        print("   Available users:")
        for u in User.objects.all():
            print(f"   - {u.username}")
else:
    print("\n⏭️  Exited")

print()
