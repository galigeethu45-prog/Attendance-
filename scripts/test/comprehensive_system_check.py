#!/usr/bin/env python
"""
Comprehensive System Health Check
Verifies all features and identifies any issues
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import (
    EmployeeProfile, Attendance, BreakLog, LeaveRequest, 
    Notification, Overtime, WFHRequest, AuditLog, EmployeeMasterData
)
from django.utils import timezone
from django.conf import settings
from django.db.models import Q

print("=" * 80)
print("COMPREHENSIVE SYSTEM HEALTH CHECK")
print("=" * 80)

# Track issues
issues = []
warnings = []
successes = []

# 1. Database Models Check
print("\n📊 STEP 1: Database Models Check")
print("-" * 80)

models_to_check = [
    ('User', User),
    ('EmployeeProfile', EmployeeProfile),
    ('Attendance', Attendance),
    ('BreakLog', BreakLog),
    ('LeaveRequest', LeaveRequest),
    ('Notification', Notification),
    ('Overtime', Overtime),
    ('WFHRequest', WFHRequest),
    ('AuditLog', AuditLog),
    ('EmployeeMasterData', EmployeeMasterData),
]

for model_name, model_class in models_to_check:
    try:
        count = model_class.objects.count()
        print(f"✓ {model_name}: {count} records")
        successes.append(f"{model_name} model working")
    except Exception as e:
        print(f"✗ {model_name}: ERROR - {str(e)}")
        issues.append(f"{model_name} model error: {str(e)}")

# 2. User Accounts Check
print("\n👥 STEP 2: User Accounts Check")
print("-" * 80)

users = User.objects.all()
if users.count() == 0:
    print("✗ No users found in system")
    issues.append("No users in system")
else:
    print(f"✓ Total users: {users.count()}")
    
    # Check for HR users
    hr_users = User.objects.filter(employeeprofile__is_hr=True)
    if hr_users.count() == 0:
        print("⚠️  No HR users found")
        warnings.append("No HR users configured")
    else:
        print(f"✓ HR users: {hr_users.count()}")
        for hr in hr_users:
            print(f"  • {hr.username} - {hr.get_full_name()}")
    
    # Check for regular employees
    employees = User.objects.filter(employeeprofile__is_hr=False)
    print(f"✓ Regular employees: {employees.count()}")
    
    # Check users without profiles
    users_without_profile = User.objects.filter(employeeprofile__isnull=True)
    if users_without_profile.count() > 0:
        print(f"⚠️  Users without EmployeeProfile: {users_without_profile.count()}")
        for user in users_without_profile:
            print(f"  • {user.username}")
        warnings.append(f"{users_without_profile.count()} users without profiles")

# 3. Email Configuration Check
print("\n📧 STEP 3: Email Configuration Check")
print("-" * 80)

print(f"Backend: {settings.EMAIL_BACKEND}")
if 'console' in settings.EMAIL_BACKEND.lower():
    print("⚠️  Using console backend - emails won't be sent")
    warnings.append("Email backend is console (not sending real emails)")
elif 'smtp' in settings.EMAIL_BACKEND.lower():
    print(f"✓ Using SMTP backend")
    print(f"  Host: {settings.EMAIL_HOST}")
    print(f"  Port: {settings.EMAIL_PORT}")
    print(f"  User: {settings.EMAIL_HOST_USER or 'Not configured'}")
    
    if not settings.EMAIL_HOST_USER:
        warnings.append("EMAIL_HOST_USER not configured")
    if not settings.EMAIL_HOST_PASSWORD:
        warnings.append("EMAIL_HOST_PASSWORD not configured")

# 4. Static Files Check
print("\n📁 STEP 4: Static Files Check")
print("-" * 80)

static_dir = settings.BASE_DIR / 'static'
if static_dir.exists():
    print(f"✓ Static directory exists: {static_dir}")
    
    # Check for key files
    css_file = static_dir / 'css' / 'style.css'
    js_file = static_dir / 'js' / 'main.js'
    
    if css_file.exists():
        print(f"✓ CSS file exists: {css_file.stat().st_size} bytes")
    else:
        print(f"✗ CSS file missing: {css_file}")
        issues.append("CSS file missing")
    
    if js_file.exists():
        print(f"✓ JS file exists: {js_file.stat().st_size} bytes")
    else:
        print(f"✗ JS file missing: {js_file}")
        issues.append("JS file missing")
else:
    print(f"✗ Static directory not found: {static_dir}")
    issues.append("Static directory missing")

# 5. Templates Check
print("\n📄 STEP 5: Templates Check")
print("-" * 80)

templates_dir = settings.BASE_DIR / 'templates'
if templates_dir.exists():
    print(f"✓ Templates directory exists: {templates_dir}")
    
    required_templates = [
        'base.html',
        'login.html',
        'dashboard.html',
        'attendance_history.html',
        'leave_request.html',
        'hr_dashboard.html',
        'profile.html',
    ]
    
    for template in required_templates:
        template_path = templates_dir / template
        if template_path.exists():
            print(f"✓ {template}")
        else:
            print(f"✗ {template} missing")
            issues.append(f"Template missing: {template}")
else:
    print(f"✗ Templates directory not found: {templates_dir}")
    issues.append("Templates directory missing")

# 6. Settings Check
print("\n⚙️  STEP 6: Django Settings Check")
print("-" * 80)

print(f"DEBUG: {settings.DEBUG}")
if settings.DEBUG:
    warnings.append("DEBUG mode is ON - should be OFF in production")

print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
if settings.ALLOWED_HOSTS == ['*']:
    warnings.append("ALLOWED_HOSTS is '*' - should be specific domains in production")

print(f"SECRET_KEY: {'*' * 20} (hidden)")
if 'django-insecure' in settings.SECRET_KEY:
    warnings.append("Using default SECRET_KEY - should be changed in production")

print(f"TIME_ZONE: {settings.TIME_ZONE}")
if settings.TIME_ZONE != 'Asia/Kolkata':
    warnings.append(f"TIME_ZONE is {settings.TIME_ZONE}, expected Asia/Kolkata")

print(f"DATABASE: {settings.DATABASES['default']['ENGINE']}")

# 7. Feature Availability Check
print("\n✨ STEP 7: Feature Availability Check")
print("-" * 80)

features = {
    'Attendance': Attendance,
    'BreakLog': BreakLog,
    'LeaveRequest': LeaveRequest,
    'Notification': Notification,
    'Overtime': Overtime,
    'WFHRequest': WFHRequest,
    'AuditLog': AuditLog,
    'EmployeeMasterData': EmployeeMasterData,
}

for feature_name, model_class in features.items():
    count = model_class.objects.count()
    if count > 0:
        print(f"✓ {feature_name}: {count} records")
    else:
        print(f"⚠️  {feature_name}: No data (feature available but unused)")

# 8. Recent Activity Check
print("\n📈 STEP 8: Recent Activity Check")
print("-" * 80)

today = timezone.now().date()
yesterday = today - timezone.timedelta(days=1)

today_attendance = Attendance.objects.filter(date=today).count()
yesterday_attendance = Attendance.objects.filter(date=yesterday).count()

print(f"Today's attendance records: {today_attendance}")
print(f"Yesterday's attendance records: {yesterday_attendance}")

recent_leaves = LeaveRequest.objects.filter(
    created_at__gte=timezone.now() - timezone.timedelta(days=7)
).count()
print(f"Leave requests (last 7 days): {recent_leaves}")

pending_leaves = LeaveRequest.objects.filter(status='pending').count()
print(f"Pending leave requests: {pending_leaves}")

# 9. Data Integrity Check
print("\n🔍 STEP 9: Data Integrity Check")
print("-" * 80)

# Check for attendance without check-out (older than today)
old_open_attendance = Attendance.objects.filter(
    date__lt=today,
    check_out__isnull=True
).count()

if old_open_attendance > 0:
    print(f"⚠️  {old_open_attendance} old attendance records without check-out")
    warnings.append(f"{old_open_attendance} old records need auto-checkout")
else:
    print("✓ No old open attendance records")

# Check for breaks without end time
open_breaks = BreakLog.objects.filter(break_end__isnull=True).count()
if open_breaks > 0:
    print(f"⚠️  {open_breaks} breaks without end time")
    warnings.append(f"{open_breaks} breaks need to be closed")
else:
    print("✓ No open breaks")

# Check for users with email
users_with_email = User.objects.filter(email__isnull=False).exclude(email='').count()
users_without_email = User.objects.filter(Q(email__isnull=True) | Q(email='')).count()

print(f"✓ Users with email: {users_with_email}")
if users_without_email > 0:
    print(f"⚠️  Users without email: {users_without_email}")
    warnings.append(f"{users_without_email} users need email addresses")

# 10. Security Check
print("\n🔐 STEP 10: Security Check")
print("-" * 80)

if settings.DEBUG:
    print("⚠️  DEBUG mode is ON")
    print("   → Should be OFF in production")
else:
    print("✓ DEBUG mode is OFF")

if settings.SESSION_COOKIE_SECURE:
    print("✓ SESSION_COOKIE_SECURE is ON")
else:
    print("⚠️  SESSION_COOKIE_SECURE is OFF")
    if not settings.DEBUG:
        warnings.append("SESSION_COOKIE_SECURE should be ON in production")

if settings.CSRF_COOKIE_SECURE:
    print("✓ CSRF_COOKIE_SECURE is ON")
else:
    print("⚠️  CSRF_COOKIE_SECURE is OFF")
    if not settings.DEBUG:
        warnings.append("CSRF_COOKIE_SECURE should be ON in production")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"\n✅ Successes: {len(successes)}")
print(f"⚠️  Warnings: {len(warnings)}")
print(f"❌ Issues: {len(issues)}")

if issues:
    print("\n❌ CRITICAL ISSUES:")
    print("-" * 80)
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")

if warnings:
    print("\n⚠️  WARNINGS:")
    print("-" * 80)
    for i, warning in enumerate(warnings, 1):
        print(f"{i}. {warning}")

# Overall Status
print("\n" + "=" * 80)
if issues:
    print("❌ SYSTEM STATUS: ISSUES FOUND - Fix critical issues above")
elif warnings:
    print("⚠️  SYSTEM STATUS: WORKING WITH WARNINGS - Review warnings above")
else:
    print("✅ SYSTEM STATUS: ALL CHECKS PASSED - System is healthy!")
print("=" * 80)

# Recommendations
print("\n📝 RECOMMENDATIONS:")
print("-" * 80)

if not issues and not warnings:
    print("✓ System is in excellent condition!")
    print("✓ All features are working properly")
    print("✓ Ready for production deployment")
else:
    if issues:
        print("1. Fix critical issues immediately")
    if warnings:
        print("2. Review and address warnings")
    if 'Email' in str(warnings):
        print("3. Configure email settings for notifications")
    if users_without_email > 0:
        print("4. Add email addresses to user accounts")
    if old_open_attendance > 0:
        print("5. Run auto-checkout for old records")

print("\n" + "=" * 80)
print("CHECK COMPLETED")
print("=" * 80)
print()
