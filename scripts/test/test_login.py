import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

print("="*60)
print("TESTING LOGIN CREDENTIALS")
print("="*60)

# Test admin
print("\n1. Testing ADMIN login...")
admin = authenticate(username='admin', password='admin123')
if admin:
    print(f"   ✅ SUCCESS - Admin can login")
    print(f"   Username: admin")
    print(f"   Password: admin123")
else:
    print(f"   ❌ FAILED - Admin authentication failed")

# Test employee
print("\n2. Testing EMPLOYEE login...")
emp = authenticate(username='AI0021', password='employee123')
if emp:
    print(f"   ✅ SUCCESS - Employee can login")
    print(f"   Username: AI0021")
    print(f"   Password: employee123")
else:
    print(f"   ❌ FAILED - Employee authentication failed")

print("\n" + "="*60)
print("LOGIN INSTRUCTIONS:")
print("="*60)
print("\n🔑 On the login page, enter:")
print("\nFor ADMIN:")
print("   Employee ID: admin")
print("   Password: admin123")
print("\nFor EMPLOYEE:")
print("   Employee ID: AI0021")
print("   Password: employee123")
print("\n⚠️  Use 'Employee ID' field, NOT email!")
print("="*60)
