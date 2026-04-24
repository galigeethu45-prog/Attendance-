"""
Script to apply break time_slot migration and update existing records
Run this with: python apply_break_migration.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from attendance.models import BreakLog
import pytz

print("=" * 70)
print("APPLYING BREAK TIME_SLOT MIGRATION")
print("=" * 70)

# Step 1: Apply migration
print("\n[1/3] Applying database migration...")
try:
    call_command('migrate', 'attendance', '0012')
    print("✓ Migration applied successfully!")
except Exception as e:
    print(f"✗ Migration error: {e}")
    print("\nTrying to apply all migrations...")
    try:
        call_command('migrate')
        print("✓ All migrations applied!")
    except Exception as e2:
        print(f"✗ Error: {e2}")
        exit(1)

# Step 2: Update existing break records
print("\n[2/3] Updating existing break records...")
local_tz = pytz.timezone('Asia/Kolkata')

breaks_without_slot = BreakLog.objects.filter(time_slot__isnull=True)
count = breaks_without_slot.count()

if count == 0:
    print("✓ No records to update - all breaks have time_slot set")
else:
    print(f"Found {count} break records without time_slot")
    updated = 0
    
    for break_log in breaks_without_slot:
        if break_log.break_start:
            # Determine time slot based on break start time
            break_time = break_log.break_start.astimezone(local_tz)
            hour = break_time.hour
            
            if break_log.break_type == 'tea':
                if 10 <= hour < 11:
                    break_log.time_slot = 'morning'
                elif 16 <= hour < 17:
                    break_log.time_slot = 'evening'
                else:
                    # Default to morning for ambiguous cases
                    break_log.time_slot = 'morning'
            elif break_log.break_type == 'lunch':
                break_log.time_slot = 'afternoon'
            
            break_log.save()
            updated += 1
        else:
            # No start time, set default
            break_log.time_slot = 'morning' if break_log.break_type == 'tea' else 'afternoon'
            break_log.save()
            updated += 1
    
    print(f"✓ Updated {updated} break records with time_slot")

# Step 3: Verify
print("\n[3/3] Verifying changes...")
total_breaks = BreakLog.objects.count()
breaks_with_slot = BreakLog.objects.exclude(time_slot__isnull=True).count()
breaks_without_slot = BreakLog.objects.filter(time_slot__isnull=True).count()

print(f"Total break records: {total_breaks}")
print(f"With time_slot: {breaks_with_slot}")
print(f"Without time_slot: {breaks_without_slot}")

if breaks_without_slot == 0:
    print("\n✓ SUCCESS! All break records have time_slot set")
else:
    print(f"\n⚠ Warning: {breaks_without_slot} records still without time_slot")

print("\n" + "=" * 70)
print("MIGRATION COMPLETE")
print("=" * 70)
print("\nYou can now:")
print("1. Restart your Django development server")
print("2. Test the break functionality")
print("3. Morning tea (10-11 AM) and evening tea (4-4:45 PM) are separate")
print("4. Lunch break (1-1:45 PM) is independent")
print("=" * 70)
