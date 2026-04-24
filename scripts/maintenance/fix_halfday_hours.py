"""
Script to fix existing half-day attendance records
This will cap work hours at 3.75 for all half-day records
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from attendance.models import Attendance

# Get all half-day records
halfday_records = Attendance.objects.filter(status='half-day')

print(f"Found {halfday_records.count()} half-day records")

updated_count = 0
for record in halfday_records:
    if record.total_work_hours > 3.75:
        old_hours = record.total_work_hours
        record.total_work_hours = 3.75
        record.save()
        print(f"Updated {record.employee.username} on {record.date}: {old_hours}h -> 3.75h")
        updated_count += 1

print(f"\nUpdated {updated_count} records")
print("Done!")
