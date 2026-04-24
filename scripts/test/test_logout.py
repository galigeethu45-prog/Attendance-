#!/usr/bin/env python
"""Test logout functionality"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

print("Testing logout functionality...")

# Create client
client = Client()

# Get a user
user = User.objects.first()
if not user:
    print("❌ No users found")
    exit(1)

print(f"Testing with user: {user.username}")

# Login
client.force_login(user)
print("✓ User logged in")

# Test logout
response = client.get('/logout/')

if response.status_code == 302:  # Redirect
    print(f"✓ Logout successful (redirected to: {response.url})")
    
    # Check if user is logged out
    response2 = client.get('/attendance/')
    if response2.status_code == 302:  # Should redirect to login
        print("✓ User is logged out (redirected to login)")
    else:
        print("⚠ User might still be logged in")
else:
    print(f"❌ Logout failed with status: {response.status_code}")

print("\n✅ Logout test completed!")
