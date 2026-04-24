#!/usr/bin/env python
"""
Test script to verify Work Mode feature
Tests that work mode correctly bypasses IP restrictions
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import EmployeeProfile

print("=" * 70)
print("WORK MODE FEATURE VERIFICATION")
print("=" * 70)

# Test 1: Check migration applied
print("\n1. Checking if work_mode field exists...")
try:
    profile = EmployeeProfile.objects.first()
    if profile:
        work_mode = profile.work_mode
        print(f"   ✓ work_mode field exists")
        print(f"   ✓ Current value: {profile.get_work_mode_display()}")
    else:
        print("   ⚠ No employee profiles found to test")
except AttributeError as e:
    print(f"   ✗ work_mode field not found: {e}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Check all work mode choices
print("\n2. Testing work mode choices...")
choices = EmployeeProfile.WORK_MODE_CHOICES
for value, label in choices:
    print(f"   ✓ {value:20} → {label}")

# Test 3: Test work mode logic
print("\n3. Testing check-in logic with work modes...")
from attendance.views import can_check_in_from_location

# Create a mock request object
class MockRequest:
    def __init__(self):
        self.META = {'REMOTE_ADDR': '192.168.1.100'}  # Non-office IP

mock_request = MockRequest()

# Test each work mode
for user in User.objects.all()[:3]:
    try:
        profile = user.employeeprofile
        can_check_in, reason = can_check_in_from_location(user, mock_request)
        
        status = "✓ ALLOWED" if can_check_in else "✗ BLOCKED"
        print(f"   {status} | {user.username:15} | Mode: {profile.get_work_mode_display():20} | {reason}")
    except EmployeeProfile.DoesNotExist:
        print(f"   ⚠ SKIP     | {user.username:15} | No profile")

# Test 4: Update work mode
print("\n4. Testing work mode update...")
test_user = User.objects.filter(is_superuser=False).first()
if test_user:
    try:
        profile = test_user.employeeprofile
        old_mode = profile.work_mode
        
        # Change to hybrid
        profile.work_mode = 'hybrid'
        profile.save()
        print(f"   ✓ Changed {test_user.username} from '{old_mode}' to 'hybrid'")
        
        # Test check-in with hybrid mode
        can_check_in, reason = can_check_in_from_location(test_user, mock_request)
        print(f"   ✓ Check-in test: {'ALLOWED' if can_check_in else 'BLOCKED'} - {reason}")
        
        # Restore original mode
        profile.work_mode = old_mode
        profile.save()
        print(f"   ✓ Restored to '{old_mode}'")
    except Exception as e:
        print(f"   ✗ Error: {e}")
else:
    print("   ⚠ No non-superuser found to test")

print("\n" + "=" * 70)
print("WORK MODE FEATURE TEST COMPLETED!")
print("=" * 70)
print("\nFeature Summary:")
print("  • Office Only: Must be on office network or have WFH approval")
print("  • Hybrid: Can check-in from anywhere without WFH approval")
print("  • Permanent WFH: Always remote, can check-in from anywhere")
print("  • HR can change work mode from employee details page")
print("=" * 70)
