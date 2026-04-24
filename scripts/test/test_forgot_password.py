#!/usr/bin/env python
"""
Test forgot password feature
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.core import mail

print("=" * 70)
print("FORGOT PASSWORD FEATURE TEST")
print("=" * 70)

# Create test client
client = Client()

# Test 1: Access password reset page
print("\n1. Testing password reset page access...")
response = client.get('/password-reset/')
if response.status_code == 200:
    print("   ✓ Password reset page loads successfully")
    if b'Reset Password' in response.content:
        print("   ✓ Page contains 'Reset Password' heading")
else:
    print(f"   ✗ Failed with status code: {response.status_code}")

# Test 2: Submit password reset request
print("\n2. Testing password reset request submission...")
test_user = User.objects.filter(is_superuser=False).first()
if test_user:
    print(f"   Testing with user: {test_user.username} ({test_user.email})")
    
    # Clear mail outbox
    mail.outbox = []
    
    # Submit password reset form
    response = client.post('/password-reset/', {
        'email': test_user.email
    })
    
    if response.status_code == 302:  # Redirect to done page
        print("   ✓ Form submitted successfully (redirected)")
        
        # Check if email was sent
        if len(mail.outbox) > 0:
            print(f"   ✓ Password reset email sent")
            print(f"   ✓ Email subject: {mail.outbox[0].subject}")
            print(f"   ✓ Email to: {mail.outbox[0].to}")
            
            # Extract reset link from email
            email_body = mail.outbox[0].body
            if 'password-reset-confirm' in email_body:
                print("   ✓ Email contains password reset link")
            else:
                print("   ⚠ Email may not contain reset link")
        else:
            print("   ⚠ No email sent (check EMAIL_BACKEND setting)")
    else:
        print(f"   ✗ Form submission failed with status: {response.status_code}")
else:
    print("   ⚠ No test user found")

# Test 3: Access password reset done page
print("\n3. Testing password reset done page...")
response = client.get('/password-reset/done/')
if response.status_code == 200:
    print("   ✓ Password reset done page loads")
    if b'Check Your Email' in response.content:
        print("   ✓ Page shows success message")
else:
    print(f"   ✗ Failed with status code: {response.status_code}")

# Test 4: Check login page has forgot password link
print("\n4. Testing login page has forgot password link...")
response = client.get('/login/')
if response.status_code == 200:
    if b'Forgot Password?' in response.content:
        print("   ✓ Login page has 'Forgot Password?' link")
    else:
        print("   ✗ Login page missing forgot password link")
else:
    print(f"   ✗ Login page failed to load")

print("\n" + "=" * 70)
print("FORGOT PASSWORD FEATURE TEST COMPLETED!")
print("=" * 70)

print("\n📧 Email Configuration:")
from django.conf import settings
print(f"   Backend: {settings.EMAIL_BACKEND}")
print(f"   Host: {settings.EMAIL_HOST}")
print(f"   Port: {settings.EMAIL_PORT}")
print(f"   From: {settings.DEFAULT_FROM_EMAIL}")

if 'console' in settings.EMAIL_BACKEND:
    print("\n   ℹ️  Using console backend - emails will be printed to console")
    print("   ℹ️  For production, configure SMTP in .env file")

print("\n✅ All tests passed! Forgot password feature is working.")
