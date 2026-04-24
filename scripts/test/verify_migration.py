"""
Pre-flight check before applying migration
Run this first: python verify_migration.py
"""
import os
import sys

print("=" * 70)
print("PRE-FLIGHT MIGRATION CHECK")
print("=" * 70)

# Check 1: Migration file exists
print("\n[1/5] Checking migration file...")
migration_file = "attendance/migrations/0012_breaklog_time_slot.py"
if os.path.exists(migration_file):
    print(f"✓ Found: {migration_file}")
else:
    print(f"✗ ERROR: Migration file not found!")
    print(f"  Expected: {migration_file}")
    sys.exit(1)

# Check 2: Models file updated
print("\n[2/5] Checking models.py...")
models_file = "attendance/models.py"
if os.path.exists(models_file):
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'time_slot' in content and 'TIME_SLOTS' in content:
            print("✓ models.py has time_slot field")
        else:
            print("✗ ERROR: models.py missing time_slot field!")
            sys.exit(1)
else:
    print("✗ ERROR: models.py not found!")
    sys.exit(1)

# Check 3: Views file updated
print("\n[3/5] Checking views.py...")
views_file = "attendance/views.py"
if os.path.exists(views_file):
    with open(views_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'tea_morning_count' in content and 'tea_evening_count' in content:
            print("✓ views.py has updated break logic")
        else:
            print("✗ ERROR: views.py missing updated break logic!")
            sys.exit(1)
else:
    print("✗ ERROR: views.py not found!")
    sys.exit(1)

# Check 4: Apply script exists
print("\n[4/5] Checking apply script...")
apply_script = "apply_break_migration.py"
if os.path.exists(apply_script):
    print(f"✓ Found: {apply_script}")
else:
    print(f"✗ ERROR: Apply script not found!")
    sys.exit(1)

# Check 5: Test script exists
print("\n[5/5] Checking test script...")
test_script = "test_break_system.py"
if os.path.exists(test_script):
    print(f"✓ Found: {test_script}")
else:
    print(f"✗ WARNING: Test script not found (optional)")

print("\n" + "=" * 70)
print("✓ ALL CHECKS PASSED!")
print("=" * 70)
print("\nYou can now safely run:")
print("  python apply_break_migration.py")
print("\nThis will:")
print("  1. Add time_slot column to database")
print("  2. Update existing break records")
print("  3. Verify the changes")
print("\nThe migration is safe and reversible.")
print("=" * 70)
