#!/usr/bin/env python
"""
Organize Project Structure
Moves files into proper folders for clean structure
"""
import os
import shutil
from pathlib import Path

print("=" * 80)
print("PROJECT ORGANIZATION")
print("=" * 80)

# Define folder structure
folders = {
    'docs': 'Documentation files',
    'scripts': 'Utility scripts',
    'scripts/setup': 'Setup scripts',
    'scripts/test': 'Test scripts',
    'scripts/maintenance': 'Maintenance scripts',
}

# Create folders
print("\n📁 Creating folder structure...")
for folder, desc in folders.items():
    Path(folder).mkdir(parents=True, exist_ok=True)
    print(f"  ✓ {folder}/ - {desc}")

# Files to move
moves = {
    # Documentation to docs/
    'docs': [
        'START_HERE.md',
        'README.md',  # Will keep copy in root
        'QUICKSTART.md',
        'FEATURES.md',
        'DEPLOYMENT.md',
        'PROJECT_SUMMARY.md',
        'SYSTEM_STATUS_REPORT.md',
        'AUTO_CHECKOUT_SCHEDULER_GUIDE.md',
        'AUTO_CHECKOUT_QUICKSTART.md',
        'SETUP_AUTO_CHECKOUT_INSTRUCTIONS.md',
        'EMAIL_SETUP_COMPLETE_GUIDE.md',
        'EMAIL_VERIFICATION_STEPS.md',
        'EMAIL_CONNECTION_ISSUE_SOLUTION.md',
        'EMAIL_ISSUE_SUMMARY.md',
        'GMAIL_SMTP_SETUP.md',
        'OUTLOOK_SMTP_SETUP.md',
        'SETUP_EMAIL.md',
        'EMERGENCY_OVERRIDE_GUIDE.md',
        'EMERGENCY_OVERRIDE_SUMMARY.md',
        'FIXES_APPLIED_SUMMARY.md',
        'AUTO_CHECKOUT_FIXED.md',
    ],
    
    # Setup scripts to scripts/setup/
    'scripts/setup': [
        'setup_auto_checkout_task.bat',
        'setup_auto_checkout_no_admin.bat',
        'setup_auto_checkout.bat',
        'setup_auto_checkout.sh',
        'setup_auto_checkout_scheduler.ps1',
        'SETUP_GMAIL_EMAIL.bat',
        'setup_email_smtp.py',
        'setup_admin.bat',
        'setup_admin_hr.py',
        'setup_company_users.py',
        'SETUP_COMPANY.bat',
        'SETUP_MASTER_DATA_SYSTEM.bat',
        'QUICK_START_MASTER_DATA.bat',
        'setup.py',
        'create_hr_user.py',
        'quick_create_admin.py',
        'create_password_reset_templates.py',
    ],
    
    # Test scripts to scripts/test/
    'scripts/test': [
        'test_auto_checkout.bat',
        'test_break_system.py',
        'test_break_times.py',
        'test_break_logs_fix.py',
        'test_email_config.py',
        'test_emergency_override.py',
        'test_employee_details.py',
        'test_forgot_password.py',
        'test_halfday_logic.py',
        'test_late_arrival.bat',
        'test_login.py',
        'test_logout.py',
        'test_overtime_workflow.py',
        'test_profile_fix.py',
        'test_work_mode.py',
        'test_base_template.py',
        'check_break_logs.py',
        'check_employee_ids.py',
        'check_ip_detection.py',
        'check_users.py',
        'comprehensive_system_check.py',
        'diagnose_email_connection.py',
        'verify_email_setup.py',
        'verify_migration.py',
        'verify_system.py',
        'show_my_ip.py',
    ],
    
    # Maintenance scripts to scripts/maintenance/
    'scripts/maintenance': [
        'run_auto_checkout_now.py',
        'run_auto_checkout.bat',
        'remove_auto_checkout_task.bat',
        'fix_old_checkouts.py',
        'fix_admin_login.py',
        'fix_halfday_hours.py',
        'fix_late_arrivals.py',
        'fix_system_issues.py',
        'fix_yesterday_checkout.py',
        'FIX_BREAK_ERROR.bat',
        'FIX_LOGIN.bat',
        'apply_break_migration.py',
        'add_user_email.py',
        'reset_passwords.py',
        'update_profiles.py',
        'switch_to_gmail.py',
        'debug_login.py',
        'debug_template.py',
        'write_template.py',
    ],
}

# Files to DELETE (old/redundant documentation)
delete_files = [
    'ADMIN_HR_SETUP_GUIDE.txt',
    'AUTO_CHECKOUT_SETUP.txt',
    'BREAK_SYSTEM_SETUP.txt',
    'COMPLETE_MASTER_DATA_GUIDE.txt',
    'CSV_UPLOAD_GUIDE.txt',
    'DEPLOY_NOW.txt',
    'FINAL_DEPLOYMENT_GUIDE.txt',
    'FINAL_IMPLEMENTATION_GUIDE.txt',
    'FINAL_UI_IMPROVEMENTS.txt',
    'FIX_PRODUCTION_ERROR.txt',
    'GET_OFFICE_IP_GUIDE.txt',
    'GET_PUBLIC_IP_NOW.txt',
    'HR_ADMIN_USER_GUIDE.txt',
    'HR_DASHBOARD_ERROR_FIXED.txt',
    'LEAVE_BALANCE_FEATURE.txt',
    'READ_ME_FIRST.txt',
    'READ_THIS_EMAIL_FIX.md',
    'ROLE_MANAGEMENT_IMPLEMENTATION.txt',
    'SECURITY_IMPLEMENTATION_GUIDE.txt',
    'SWITCH_TO_MYSQL_GUIDE.txt',
    'UI_IMPROVEMENTS_APPLIED.txt',
    'URGENT_PRODUCTION_FIX.txt',
    'START_SYSTEM_NOW.bat',
    'main.py',  # Empty/unused file
]

# Move files
print("\n📦 Moving files...")
moved_count = 0
for dest_folder, files in moves.items():
    for filename in files:
        if os.path.exists(filename):
            try:
                dest_path = os.path.join(dest_folder, filename)
                shutil.move(filename, dest_path)
                print(f"  ✓ {filename} → {dest_folder}/")
                moved_count += 1
            except Exception as e:
                print(f"  ✗ {filename}: {e}")

# Delete redundant files
print("\n🗑️  Deleting redundant files...")
deleted_count = 0
for filename in delete_files:
    if os.path.exists(filename):
        try:
            os.remove(filename)
            print(f"  ✓ Deleted: {filename}")
            deleted_count += 1
        except Exception as e:
            print(f"  ✗ {filename}: {e}")

# Keep README.md in root (copy from docs if moved)
if os.path.exists('docs/README.md') and not os.path.exists('README.md'):
    shutil.copy('docs/README.md', 'README.md')
    print("\n  ✓ Kept README.md in root")

# Create a new clean README for root
print("\n📝 Creating clean root README...")

readme_content = """# AttendanceHub - Employee Attendance Management System

A comprehensive Django-based attendance management system with automatic checkout, break tracking, leave management, and HR dashboard.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database
```bash
python manage.py migrate
```

### 3. Create Admin User
```bash
python scripts/setup/setup_admin_hr.py
```

### 4. Run Server
```bash
python manage.py runserver
```

### 5. Setup Auto-Checkout (Optional)
```bash
# Windows
scripts/setup/setup_auto_checkout_no_admin.bat

# Linux
scripts/setup/setup_auto_checkout.sh
```

## 📚 Documentation

- **Quick Start**: `docs/QUICKSTART.md`
- **Features**: `docs/FEATURES.md`
- **Deployment**: `docs/DEPLOYMENT.md`
- **Full Docs**: `docs/` folder

## 🏗️ Project Structure

```
attendance-system/
├── attendance/          # Main Django app (backend)
├── core/               # Project settings (backend)
├── templates/          # HTML templates (frontend)
├── static/            # CSS, JS, images (frontend)
├── docs/              # Documentation
├── scripts/           # Utility scripts
│   ├── setup/        # Setup scripts
│   ├── test/         # Test scripts
│   └── maintenance/  # Maintenance scripts
├── manage.py          # Django management
└── requirements.txt   # Dependencies
```

## ✨ Features

- ✅ Automatic check-in/check-out
- ✅ Break management (Tea & Lunch)
- ✅ Leave request system
- ✅ HR dashboard with analytics
- ✅ Work mode (Office/Hybrid/WFH)
- ✅ Emergency override for network issues
- ✅ Auto-checkout at 7 PM
- ✅ Audit logging
- ✅ Master data management

## 🔧 Configuration

1. Copy `.env.example` to `.env`
2. Update database settings
3. Update email settings (optional)
4. Set your office IP address in `attendance/views.py`

## 📞 Support

For detailed documentation, see `docs/` folder.

## 📄 License

MIT License
"""

with open('README.md', 'w') as f:
    f.write(readme_content)

print("  ✓ Created clean README.md")

# Summary
print("\n" + "=" * 80)
print("ORGANIZATION COMPLETE")
print("=" * 80)
print(f"\n✅ Moved: {moved_count} files")
print(f"🗑️  Deleted: {deleted_count} redundant files")
print(f"📁 Created: {len(folders)} folders")

print("\n📂 New Structure:")
print("  ├── docs/              # All documentation")
print("  ├── scripts/")
print("  │   ├── setup/        # Setup scripts")
print("  │   ├── test/         # Test scripts")
print("  │   └── maintenance/  # Maintenance scripts")
print("  ├── attendance/        # Backend app")
print("  ├── core/             # Backend settings")
print("  ├── templates/        # Frontend templates")
print("  ├── static/           # Frontend assets")
print("  ├── manage.py")
print("  ├── requirements.txt")
print("  └── README.md")

print("\n✨ Project is now clean and professional!")
print("=" * 80)
print()
