#!/usr/bin/env python
"""
Interactive Email SMTP Setup
Helps you configure Gmail or Outlook SMTP
"""

print("=" * 70)
print("EMAIL SMTP CONFIGURATION WIZARD")
print("=" * 70)

print("\nThis wizard will help you set up real email sending.")
print("Choose your email provider:\n")
print("1. Gmail (Recommended - Most reliable)")
print("2. Outlook/Hotmail (Personal account)")
print("3. Office 365 (Business account - @arraafiinfotech.com)")
print("4. Keep console backend (Development only)")
print()

choice = input("Enter your choice (1-4): ").strip()

if choice == "1":
    print("\n" + "=" * 70)
    print("GMAIL SMTP SETUP")
    print("=" * 70)
    print("\n📋 Steps to complete:")
    print("1. Enable 2-Factor Authentication:")
    print("   → https://myaccount.google.com/security")
    print("\n2. Generate App Password:")
    print("   → https://myaccount.google.com/apppasswords")
    print("   → Select 'Mail' and 'Windows Computer'")
    print("   → Copy the 16-character password (remove spaces!)")
    print("\n3. Fill in the details below:")
    print()
    
    email = input("Enter your Gmail address: ").strip()
    password = input("Enter your App Password (16 chars, no spaces): ").strip().replace(" ", "")
    
    config = f"""
# Gmail SMTP Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER={email}
EMAIL_HOST_PASSWORD={password}
DEFAULT_FROM_EMAIL={email}
"""
    
    print("\n✅ Configuration generated!")
    print("\n📝 Add these lines to your .env file:")
    print(config)
    print("\n📖 For detailed instructions, see: GMAIL_SMTP_SETUP.md")

elif choice == "2":
    print("\n" + "=" * 70)
    print("OUTLOOK SMTP SETUP")
    print("=" * 70)
    print("\n📋 If you have 2FA enabled:")
    print("1. Go to: https://account.microsoft.com/security")
    print("2. Click 'Advanced security options'")
    print("3. Create an app password")
    print("4. Use that password below")
    print()
    
    email = input("Enter your Outlook email: ").strip()
    password = input("Enter your password (or app password if 2FA): ").strip()
    
    config = f"""
# Outlook SMTP Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER={email}
EMAIL_HOST_PASSWORD={password}
DEFAULT_FROM_EMAIL={email}
"""
    
    print("\n✅ Configuration generated!")
    print("\n📝 Add these lines to your .env file:")
    print(config)
    print("\n📖 For detailed instructions, see: OUTLOOK_SMTP_SETUP.md")

elif choice == "3":
    print("\n" + "=" * 70)
    print("OFFICE 365 BUSINESS SMTP SETUP")
    print("=" * 70)
    print("\n⚠️  You may need to contact your IT admin for:")
    print("   - SMTP server address")
    print("   - Port number")
    print("   - Authentication requirements")
    print()
    
    email = input("Enter your business email (@arraafiinfotech.com): ").strip()
    password = input("Enter your password: ").strip()
    
    config = f"""
# Office 365 Business SMTP Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER={email}
EMAIL_HOST_PASSWORD={password}
DEFAULT_FROM_EMAIL={email}
"""
    
    print("\n✅ Configuration generated!")
    print("\n📝 Add these lines to your .env file:")
    print(config)
    print("\n⚠️  If this doesn't work, try:")
    print("   - Port 25 instead of 587")
    print("   - Port 465 with EMAIL_USE_SSL=True")
    print("\n📖 For detailed instructions, see: OUTLOOK_SMTP_SETUP.md")

elif choice == "4":
    print("\n⚠️  Console backend keeps emails in terminal only.")
    print("This is NOT suitable for production!")
    print("\nNo changes needed - already configured.")

else:
    print("\n❌ Invalid choice!")
    exit(1)

print("\n" + "=" * 70)
print("NEXT STEPS")
print("=" * 70)
print("\n1. Open .env file")
print("2. Find the EMAIL CONFIGURATION section")
print("3. Uncomment and fill in the lines for your chosen provider")
print("4. Save the file")
print("5. Restart Django server (Ctrl+C then python manage.py runserver)")
print("6. Test with: python test_email_config.py")
print("\n✅ Done!")
