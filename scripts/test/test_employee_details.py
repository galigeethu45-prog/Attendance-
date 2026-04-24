#!/usr/bin/env python
"""
Test employee details page
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Create test client
client = Client()

# Get admin user
admin = User.objects.filter(is_superuser=True).first()
if not admin:
    print("❌ No admin user found")
    exit(1)

# Login
client.force_login(admin)

# Get first non-admin user
employee = User.objects.filter(is_superuser=False).first()
if not employee:
    print("❌ No employee found")
    exit(1)

print(f"Testing employee details for: {employee.username}")

# Access employee details page
response = client.get(f'/attendance/employee/{employee.id}/details/')

print(f"\nStatus Code: {response.status_code}")
print(f"Content Length: {len(response.content)} bytes")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    if len(content) < 100:
        print(f"\n❌ BLANK PAGE - Content too short!")
        print(f"Content: {content}")
    elif 'Employee Details' in content:
        print(f"✅ Page loaded successfully!")
        print(f"✅ Contains 'Employee Details' heading")
    else:
        print(f"⚠️  Page loaded but may have issues")
        print(f"First 500 chars: {content[:500]}")
elif response.status_code == 302:
    print(f"⚠️  Redirected to: {response.url}")
else:
    print(f"❌ Error status code: {response.status_code}")
    print(f"Content: {response.content.decode('utf-8')[:500]}")
