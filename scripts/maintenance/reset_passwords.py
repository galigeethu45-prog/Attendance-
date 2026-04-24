"""
Reset passwords for testing
Run: python reset_passwords.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

# Reset Admin password
admin = User.objects.get(username='admin')
admin.set_password('admin123')
admin.save()
print(f"✅ Admin password reset")
print(f"   Username: {admin.username}")
print(f"   Email: {admin.email}")
print(f"   Password: admin123")

# Reset Employee password
employee = User.objects.get(username='AI0021')
employee.set_password('employee123')
employee.save()
print(f"\n✅ Employee password reset")
print(f"   Username: {employee.username}")
print(f"   Email: {employee.email}")
print(f"   Password: employee123")

print("\n" + "="*50)
print("CREDENTIALS FOR LOGIN:")
print("="*50)
print("\n🔑 ADMIN/HR LOGIN:")
print("   Email: admin@arraafiinfotech.com")
print("   Password: admin123")
print("\n🔑 EMPLOYEE LOGIN:")
print("   Email: giri.g@arraafiinfotech.com")
print("   Password: employee123")
print("="*50)
