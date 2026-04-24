#!/usr/bin/env python
"""
Quick Switch to Gmail SMTP
Interactive script to configure Gmail for email sending
"""
import os
import re

print("=" * 80)
print("SWITCH TO GMAIL SMTP - INTERACTIVE SETUP")
print("=" * 80)

print("""
📧 This script will help you configure Gmail SMTP for sending emails.

Why Gmail?
  ✓ More reliable than company email servers
  ✓ Works from any network (no firewall issues)
  ✓ Easy to set up with App Password
  ✓ Free for development/testing

Requirements:
  1. Gmail account
  2. 2-Step Verification enabled
  3. App Password generated

""")

# Step 1: Check if user has App Password
print("=" * 80)
print("STEP 1: Generate Gmail App Password")
print("=" * 80)
print("""
1. Go to: https://myaccount.google.com/security
2. Enable '2-Step Verification' (if not already enabled)
3. Go to: https://myaccount.google.com/apppasswords
4. Select 'Mail' and 'Windows Computer'
5. Click 'Generate'
6. Copy the 16-character password (e.g., 'abcd efgh ijkl mnop')

""")

has_app_password = input("Do you have the App Password ready? (y/n): ").strip().lower()

if has_app_password != 'y':
    print("\n⏭️  Please generate App Password first, then run this script again.")
    print("   URL: https://myaccount.google.com/apppasswords")
    exit(0)

# Step 2: Get Gmail credentials
print("\n" + "=" * 80)
print("STEP 2: Enter Gmail Credentials")
print("=" * 80)

gmail_address = input("\nEnter your Gmail address (e.g., yourname@gmail.com): ").strip()

# Validate email format
if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', gmail_address):
    print("❌ Invalid Gmail address format")
    print("   Must be: yourname@gmail.com")
    exit(1)

print("\nEnter your Gmail App Password (16 characters, spaces will be removed)")
app_password = input("App Password: ").strip().replace(' ', '')

if len(app_password) != 16:
    print(f"⚠️  Warning: App Password should be 16 characters (you entered {len(app_password)})")
    confirm = input("Continue anyway? (y/n): ").strip().lower()
    if confirm != 'y':
        exit(0)

# Step 3: Update .env file
print("\n" + "=" * 80)
print("STEP 3: Update .env File")
print("=" * 80)

env_file = '.env'

if not os.path.exists(env_file):
    print(f"❌ .env file not found: {env_file}")
    exit(1)

# Read current .env
with open(env_file, 'r') as f:
    env_content = f.read()

# Backup current .env
backup_file = '.env.backup'
with open(backup_file, 'w') as f:
    f.write(env_content)
print(f"✓ Backed up current .env to: {backup_file}")

# Update email settings
new_settings = f"""
# ============================================================================
# EMAIL CONFIGURATION - Gmail SMTP
# ============================================================================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_SSL=False
EMAIL_USE_TLS=True
EMAIL_HOST_USER={gmail_address}
EMAIL_HOST_PASSWORD={app_password}
DEFAULT_FROM_EMAIL={gmail_address}
"""

# Remove old email configuration section
lines = env_content.split('\n')
new_lines = []
skip_section = False

for line in lines:
    if '# ============================================================================' in line:
        if 'EMAIL CONFIGURATION' in lines[lines.index(line):lines.index(line)+2]:
            skip_section = True
            continue
    
    if skip_section:
        if line.startswith('EMAIL_') or line.startswith('DEFAULT_FROM_EMAIL'):
            continue
        elif line.strip() == '':
            skip_section = False
            continue
        else:
            skip_section = False
    
    if not skip_section:
        new_lines.append(line)

# Add new email configuration
env_content = '\n'.join(new_lines).rstrip() + '\n' + new_settings

# Write updated .env
with open(env_file, 'w') as f:
    f.write(env_content)

print(f"✓ Updated {env_file} with Gmail SMTP settings")

# Step 4: Verify configuration
print("\n" + "=" * 80)
print("STEP 4: Verify Configuration")
print("=" * 80)
print(f"""
✅ Gmail SMTP Configuration Applied!

Settings:
  • Email Host: smtp.gmail.com
  • Port: 587
  • Security: TLS
  • Username: {gmail_address}
  • Password: {'*' * len(app_password)}
  • From Email: {gmail_address}

""")

# Step 5: Next steps
print("=" * 80)
print("NEXT STEPS")
print("=" * 80)
print("""
1. RESTART Django Server (IMPORTANT!)
   • Stop current server: Press Ctrl+C in terminal
   • Start again: python manage.py runserver

2. Test Email Configuration
   • Run: python verify_email_setup.py
   • Enter your email to receive test email

3. Test Password Reset
   • Go to: http://127.0.0.1:8000/password-reset/
   • Enter email address
   • Check Gmail inbox for reset link

4. Check Spam Folder
   • If email not in inbox, check spam/junk folder
   • Mark as "Not Spam" if found there

""")

print("=" * 80)
print("✅ SETUP COMPLETED!")
print("=" * 80)
print("\n💡 Tip: If you want to revert to company email server:")
print(f"   1. Restore from backup: copy {backup_file} to {env_file}")
print("   2. Restart Django server")
print()
