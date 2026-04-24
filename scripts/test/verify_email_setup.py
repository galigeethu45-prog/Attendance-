#!/usr/bin/env python
"""
Comprehensive Email Setup Verification
Tests email configuration and sends test emails
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.contrib.auth.models import User
import socket

print("=" * 80)
print("COMPREHENSIVE EMAIL SETUP VERIFICATION")
print("=" * 80)

# 1. Check Django Settings
print("\n📋 STEP 1: Django Email Settings")
print("-" * 80)
print(f"✓ EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"✓ EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"✓ EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"✓ EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"✓ EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
print(f"✓ EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"✓ EMAIL_HOST_PASSWORD: {'*' * 8 if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
print(f"✓ DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# Validate configuration
errors = []
warnings = []

if 'console' in settings.EMAIL_BACKEND.lower():
    warnings.append("Using console backend - emails won't be sent to real addresses")
elif 'smtp' not in settings.EMAIL_BACKEND.lower():
    errors.append(f"Unknown email backend: {settings.EMAIL_BACKEND}")

if not settings.EMAIL_HOST:
    errors.append("EMAIL_HOST is not set")

if not settings.EMAIL_HOST_USER:
    warnings.append("EMAIL_HOST_USER is not set")

if not settings.EMAIL_HOST_PASSWORD:
    warnings.append("EMAIL_HOST_PASSWORD is not set")

# Port validation
if settings.EMAIL_PORT == 465 and not getattr(settings, 'EMAIL_USE_SSL', False):
    errors.append("Port 465 requires EMAIL_USE_SSL=True")
elif settings.EMAIL_PORT == 587 and not settings.EMAIL_USE_TLS:
    warnings.append("Port 587 typically requires EMAIL_USE_TLS=True")

if getattr(settings, 'EMAIL_USE_SSL', False) and settings.EMAIL_USE_TLS:
    errors.append("Cannot use both EMAIL_USE_SSL and EMAIL_USE_TLS")

# 2. Network Connectivity Test
print("\n🌐 STEP 2: Network Connectivity Test")
print("-" * 80)

if settings.EMAIL_HOST and 'console' not in settings.EMAIL_BACKEND.lower():
    try:
        print(f"Testing connection to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((settings.EMAIL_HOST, settings.EMAIL_PORT))
        sock.close()
        
        if result == 0:
            print(f"✓ Successfully connected to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        else:
            errors.append(f"Cannot connect to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
            print(f"✗ Connection failed (error code: {result})")
    except Exception as e:
        errors.append(f"Network error: {str(e)}")
        print(f"✗ Connection test failed: {str(e)}")
else:
    print("⏭️  Skipped (console backend or no host configured)")

# 3. Display Errors and Warnings
if errors:
    print("\n❌ CONFIGURATION ERRORS:")
    print("-" * 80)
    for i, error in enumerate(errors, 1):
        print(f"{i}. {error}")

if warnings:
    print("\n⚠️  WARNINGS:")
    print("-" * 80)
    for i, warning in enumerate(warnings, 1):
        print(f"{i}. {warning}")

if errors:
    print("\n" + "=" * 80)
    print("❌ VERIFICATION FAILED - Fix errors above before testing email")
    print("=" * 80)
    sys.exit(1)

# 4. Send Test Email
print("\n📧 STEP 3: Send Test Email")
print("-" * 80)

test_email = input("Enter email address to send test email (or press Enter to skip): ").strip()

if test_email:
    print(f"\nSending test email to: {test_email}")
    print("Please wait...")
    
    try:
        # Send simple test email
        result = send_mail(
            subject='✅ AttendanceHub Email Test',
            message='''Hello!

This is a test email from your AttendanceHub system.

If you received this email, your email configuration is working correctly!

Configuration Details:
- Email Server: {host}
- Port: {port}
- Security: {security}
- From: {from_email}

Best regards,
AttendanceHub System
'''.format(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                security='SSL' if getattr(settings, 'EMAIL_USE_SSL', False) else ('TLS' if settings.EMAIL_USE_TLS else 'None'),
                from_email=settings.DEFAULT_FROM_EMAIL
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        if 'console' in settings.EMAIL_BACKEND.lower():
            print("\n✓ Email content printed above (console backend)")
            print("  Note: Email was NOT sent to real address")
        else:
            print("\n✅ EMAIL SENT SUCCESSFULLY!")
            print(f"  Check inbox: {test_email}")
            print("  Also check spam/junk folder")
            print(f"  Emails sent: {result}")
            
    except Exception as e:
        print(f"\n❌ FAILED TO SEND EMAIL")
        print(f"Error: {str(e)}")
        print("\n🔧 Troubleshooting:")
        
        error_str = str(e).lower()
        
        if 'authentication' in error_str or 'username' in error_str or 'password' in error_str:
            print("  • Authentication failed - check credentials")
            print("  • Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env")
            print("  • For Gmail: Use App Password (not regular password)")
            print("  • For company email: Verify password is correct")
            
        elif 'connection' in error_str or 'timeout' in error_str:
            print("  • Cannot connect to email server")
            print("  • Check EMAIL_HOST and EMAIL_PORT")
            print("  • Check firewall/network settings")
            print("  • Try different port (465 for SSL, 587 for TLS)")
            
        elif 'ssl' in error_str or 'tls' in error_str:
            print("  • SSL/TLS configuration issue")
            print("  • For port 465: Use EMAIL_USE_SSL=True, EMAIL_USE_TLS=False")
            print("  • For port 587: Use EMAIL_USE_TLS=True, EMAIL_USE_SSL=False")
            
        elif 'refused' in error_str:
            print("  • Connection refused by server")
            print("  • Check if email server allows SMTP connections")
            print("  • Verify port number is correct")
            
        else:
            print("  • Check all email settings in .env file")
            print("  • Verify email server is accessible")
            print("  • Contact email server administrator if needed")
        
        sys.exit(1)
else:
    print("⏭️  Skipped test email")

# 5. Check Users with Email
print("\n👥 STEP 4: Users with Email Addresses")
print("-" * 80)

users_with_email = User.objects.filter(email__isnull=False).exclude(email='')
if users_with_email.exists():
    print(f"✓ Found {users_with_email.count()} users with email addresses:")
    for user in users_with_email[:10]:
        print(f"  • {user.username}: {user.email}")
    
    if users_with_email.count() > 10:
        print(f"  ... and {users_with_email.count() - 10} more")
else:
    print("⚠️  No users with email addresses found")
    print("  Add email addresses to test password reset functionality")

# 6. Password Reset Test Instructions
print("\n🔐 STEP 5: Test Password Reset")
print("-" * 80)
print("To test password reset functionality:")
print("  1. Start Django server: python manage.py runserver")
print("  2. Go to: http://127.0.0.1:8000/password-reset/")
print("  3. Enter email address of a user")
print("  4. Check email inbox (or terminal if console backend)")
print("  5. Click reset link and set new password")

# Final Summary
print("\n" + "=" * 80)
if not errors and test_email:
    print("✅ EMAIL SETUP VERIFICATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\n📝 Next Steps:")
    print("  1. Check email inbox for test email")
    print("  2. Test password reset functionality")
    print("  3. Monitor Django logs for any email errors")
    
    if warnings:
        print("\n⚠️  Note: There are some warnings above - review them")
else:
    print("✅ EMAIL CONFIGURATION VERIFIED")
    print("=" * 80)
    
    if not test_email:
        print("\n📝 To complete verification:")
        print("  1. Run this script again and send test email")
        print("  2. Test password reset functionality")

print()
