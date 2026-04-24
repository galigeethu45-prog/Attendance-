#!/usr/bin/env python
"""
Test email configuration
Helps diagnose email sending issues
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

print("=" * 70)
print("EMAIL CONFIGURATION TEST")
print("=" * 70)

# Show current configuration
print("\n📧 Current Email Settings:")
print(f"   Backend: {settings.EMAIL_BACKEND}")
print(f"   Host: {settings.EMAIL_HOST}")
print(f"   Port: {settings.EMAIL_PORT}")
print(f"   Use TLS: {settings.EMAIL_USE_TLS}")
print(f"   Use SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
print(f"   From Email: {settings.DEFAULT_FROM_EMAIL}")

if settings.EMAIL_HOST_USER:
    print(f"   Username: {settings.EMAIL_HOST_USER}")
    print(f"   Password: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'Not set'}")
else:
    print(f"   Username: Not configured")
    print(f"   Password: Not configured")

# Check backend type
if 'console' in settings.EMAIL_BACKEND.lower():
    print("\n⚠️  WARNING: Using CONSOLE backend")
    print("   Emails will be printed to terminal, not sent to real addresses")
    print("   To send real emails, update EMAIL_BACKEND in .env file")
    print("\n   See SETUP_EMAIL.md for configuration instructions")
elif 'smtp' in settings.EMAIL_BACKEND.lower():
    print("\n✓ Using SMTP backend - will send real emails")
else:
    print(f"\n⚠️  Unknown backend: {settings.EMAIL_BACKEND}")

# Ask if user wants to send test email
print("\n" + "=" * 70)
test_email = input("Enter email address to send test email (or press Enter to skip): ").strip()

if test_email:
    print(f"\n📤 Sending test email to: {test_email}")
    
    try:
        send_mail(
            subject='Test Email from AttendanceHub',
            message='This is a test email from your AttendanceHub system.\n\nIf you received this, your email configuration is working correctly!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        if 'console' in settings.EMAIL_BACKEND.lower():
            print("\n✓ Email printed above (console backend)")
            print("   Check the terminal output for the email content")
        else:
            print("\n✓ Email sent successfully!")
            print(f"   Check inbox: {test_email}")
            print("   Also check spam/junk folder")
            
    except Exception as e:
        print(f"\n❌ Failed to send email!")
        print(f"   Error: {str(e)}")
        print("\n🔧 Troubleshooting:")
        
        if 'authentication' in str(e).lower():
            print("   - Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD")
            print("   - For Gmail: Use App Password, not regular password")
            print("   - See SETUP_EMAIL.md for instructions")
        elif 'connection' in str(e).lower():
            print("   - Check EMAIL_HOST and EMAIL_PORT")
            print("   - Check firewall settings")
            print("   - Try different port (587 or 465)")
        else:
            print("   - Check all email settings in .env file")
            print("   - See SETUP_EMAIL.md for configuration guide")
else:
    print("\n⏭️  Skipped test email")

# Test password reset email
print("\n" + "=" * 70)
print("PASSWORD RESET EMAIL TEST")
print("=" * 70)

users = User.objects.filter(email__isnull=False).exclude(email='')
if users.exists():
    print(f"\n✓ Found {users.count()} users with email addresses:")
    for user in users[:5]:
        print(f"   - {user.username}: {user.email}")
    
    print("\n💡 To test password reset:")
    print("   1. Go to: http://127.0.0.1:8000/password-reset/")
    print("   2. Enter one of the email addresses above")
    print("   3. Check email inbox (or terminal if using console backend)")
else:
    print("\n⚠️  No users with email addresses found")
    print("   Add email addresses to user accounts to test password reset")

print("\n" + "=" * 70)
print("TEST COMPLETED")
print("=" * 70)

if 'console' in settings.EMAIL_BACKEND.lower():
    print("\n📝 Next Steps:")
    print("   1. Read SETUP_EMAIL.md for email configuration")
    print("   2. Update .env file with SMTP settings")
    print("   3. Restart Django server")
    print("   4. Run this test again")
else:
    print("\n✅ Email configuration looks good!")
    print("   If you didn't receive the test email:")
    print("   - Check spam/junk folder")
    print("   - Verify email address is correct")
    print("   - Check terminal for error messages")
