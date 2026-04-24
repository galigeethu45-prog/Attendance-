#!/usr/bin/env python
"""
Check IP Detection and Network Validation
Helps diagnose why check-in is allowed or blocked
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import SystemSettings, EmployeeProfile
from attendance.views import get_client_ip, is_on_office_network, can_check_in_from_location
import socket

print("=" * 80)
print("IP DETECTION & NETWORK VALIDATION CHECK")
print("=" * 80)

# Get current IP
try:
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"\n🌐 Your Current IP Address: {local_ip}")
except:
    print("\n⚠️  Could not detect IP address")
    local_ip = "Unknown"

# Check allowed IPs from views.py
print("\n📋 Allowed Office IPs (from views.py):")
print("-" * 80)

# Read the ALLOWED_OFFICE_IPS from views.py
with open('attendance/views.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
    # Find the ALLOWED_OFFICE_IPS section
    start = content.find('ALLOWED_OFFICE_IPS = [')
    end = content.find(']', start) + 1
    
    if start != -1:
        allowed_ips_section = content[start:end]
        print(allowed_ips_section)
    else:
        print("Could not find ALLOWED_OFFICE_IPS in views.py")

# Check emergency override
print("\n🚨 Emergency Override Status:")
print("-" * 80)

settings = SystemSettings.get_settings()
print(f"Enabled: {settings.emergency_override_enabled}")
if settings.emergency_override_enabled:
    print(f"Reason: {settings.emergency_override_reason}")
    print(f"Enabled by: {settings.emergency_override_enabled_by}")
    print(f"Enabled at: {settings.emergency_override_enabled_at}")

# Test with each user
print("\n👥 User Check-in Validation:")
print("-" * 80)

users = User.objects.all()

for user in users:
    print(f"\n{user.username} ({user.get_full_name() or 'No name'}):")
    
    try:
        profile = user.employeeprofile
        print(f"  • Is HR: {profile.is_hr}")
        print(f"  • Work Mode: {profile.work_mode}")
    except EmployeeProfile.DoesNotExist:
        print(f"  • No profile")
    
    # Test check-in validation (without request, so IP check will fail)
    can_check_in, reason = can_check_in_from_location(user, request=None)
    
    print(f"  • Can check-in: {can_check_in}")
    print(f"  • Reason: {reason}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print("\n📝 To Fix IP Restrictions:")
print("1. Make sure localhost IPs (127.0.0.1, ::1) are COMMENTED OUT in views.py")
print("2. Only keep actual Regus office public IP in ALLOWED_OFFICE_IPS")
print("3. Restart Django server after changes")
print("4. Test from personal hotspot - should be BLOCKED")
print("5. Test from Regus WiFi - should be ALLOWED")

print("\n🔍 Current Status:")
if '127.0.0.1' in str(content[start:end]) and not '# \'127.0.0.1\'' in str(content[start:end]):
    print("⚠️  WARNING: Localhost (127.0.0.1) is ACTIVE in allowed IPs")
    print("   This allows check-in from anywhere when testing locally!")
    print("   COMMENT IT OUT for production use")
else:
    print("✅ Localhost IPs are commented out (correct for production)")

if settings.emergency_override_enabled:
    print("⚠️  WARNING: Emergency Override is ENABLED")
    print("   All employees can check-in from anywhere!")
    print("   Disable it if not needed")
else:
    print("✅ Emergency Override is disabled (normal restrictions active)")

print("\n" + "=" * 80)
print()
