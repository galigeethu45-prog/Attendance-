# Bulk Check-in Script - Feature Complete

## Overview
Management command script to bulk-assign missing check-ins and check-outs for employees who forgot to check in.

## File Location
`attendance/management/commands/bulk_checkin.py`

## Usage
```bash
python manage.py bulk_checkin <employee_id> --month <YYYY-MM>
```

### Example
```bash
python manage.py bulk_checkin AI0001 --month 2026-08
```

## Features

### 1. Complete Attendance Creation
- ✅ Creates both check-in (9:00 AM) AND check-out (7:00 PM) together
- ✅ Automatically calculates work hours (10 hours)
- ✅ Sets attendance status automatically based on work hours
- ✅ Creates complete attendance records in one go

### 2. Smart Date Filtering
- ✅ Skips weekends (Saturday & Sunday)
- ✅ Skips company holidays
- ✅ Skips days with approved leave requests
- ✅ Skips days where attendance already exists
- ✅ Only processes working days up to yesterday (excludes today)

### 3. No Audit Trail
- ✅ Does NOT create audit log entries (as per requirement)
- ✅ Bulk assignment doesn't clutter audit logs
- ✅ Clean operation for administrative fixes

### 4. Detailed Output
The script provides comprehensive feedback:

#### Header Information
- Employee details (ID, name, email)
- Month being processed
- Check-in and check-out times being assigned
- Warning about no audit trail

#### Processing Log
For each day in the month:
- `⏭️` Weekend/Holiday/Leave days (skipped with reason)
- `✓` Days with existing attendance
- `📋` Missing attendance days (will be created)

#### Confirmation Prompt
- Shows count of missing days
- Asks for user confirmation before creating records
- Allows cancellation

#### Creation Results
For each created record:
- ✅ Date, check-in time, check-out time
- Work hours calculated
- Final attendance status (present/half-day)

#### Summary Report
- Total days checked
- Breakdown by skip reason
- Successfully created count
- Error count (if any)

### 5. Example Output

```
================================================================================
BULK CHECK-IN/CHECK-OUT ASSIGNMENT
================================================================================
Check-in Time: 09:00 AM
Check-out Time: 07:00 PM
Month: August 2026 (2026-08-01 to 2026-08-16)
Note: No audit trail will be created

Processing Employee: AI0001
Name: John Doe
Email: john@example.com
--------------------------------------------------------------------------------

⏭️  2026-08-02 - Weekend (Skipped)
⏭️  2026-08-03 - Weekend (Skipped)
✓ 2026-08-04 - Attendance already exists
📋 2026-08-05 - Missing attendance (Will create)
⏭️  2026-08-15 - Holiday: Independence Day (Skipped)
📋 2026-08-16 - Missing attendance (Will create)

--------------------------------------------------------------------------------
Found 2 missing attendance day(s) to create

⚠️  CONFIRMATION REQUIRED
Create check-in records for 2 day(s)? (yes/no): yes

Creating attendance records with check-in and check-out...

✅ 2026-08-05 - Check-in: 09:00 AM, Check-out: 07:00 PM, Hours: 10h 0m, Status: present
✅ 2026-08-16 - Check-in: 09:00 AM, Check-out: 07:00 PM, Hours: 10h 0m, Status: present

================================================================================
SUMMARY
================================================================================
Employee: John Doe (AI0001)
Month: August 2026
Check-in Time: 09:00 AM
Check-out Time: 07:00 PM

Total days checked: 17
⏭️  Skipped (Weekends): 4
⏭️  Skipped (Holidays): 1
⏭️  Skipped (On Leave): 0
✓ Already exists: 10
✅ Successfully created (with check-in & check-out): 2

✓ Done!
```

## Technical Details

### Timing Logic
- **Check-in Time**: 9:00 AM (fixed)
- **Check-out Time**: 7:00 PM (fixed)
- **Total Hours**: Automatically calculated (typically 10 hours)
- **Status**: Auto-determined by `calculate_work_hours()` method

### Database Operations
1. Creates `Attendance` record with both check_in and check_out
2. Calls `attendance.calculate_work_hours()` to:
   - Calculate total work hours
   - Set attendance status (present/late/half-day)
3. Saves the complete record

### What Gets Saved
```python
Attendance {
    employee: User object
    date: Date being processed
    check_in: 9:00 AM on that date
    check_out: 7:00 PM on that date
    total_work_hours: 10.0 (calculated)
    status: 'present' (auto-determined)
}
```

## Key Requirements Met

1. ✅ **Ask for employee ID and month** - Command line arguments
2. ✅ **Find all missing check-ins** - Scans entire month for gaps
3. ✅ **Skip weekends, holidays, leaves** - Smart filtering
4. ✅ **Assign both check-in AND check-out** - Complete attendance records
5. ✅ **Calculate work hours automatically** - Uses model method
6. ✅ **Set attendance status correctly** - Based on hours worked
7. ✅ **No audit trail entries** - Clean bulk operation
8. ✅ **Safe operation** - Confirmation prompt before creating records

## User Corrections Applied

### From User Feedback:
> "when we run this script it will assign the check-in time for that day but what about the check-out time and total work hours calculation and attendance status for that day?"

**Solution**: Script now creates BOTH check-in and check-out simultaneously, ensuring:
- Complete attendance record
- Work hours calculated (9 AM to 7 PM = 10 hours)
- Status set correctly (typically 'present' for 10 hours)

> "i don't want this to be recorded in the audit trail"

**Solution**: Removed all `AuditLog.objects.create()` calls from the script

## Deployment Notes

### AWS Production Usage
1. SSH into production server
2. Activate virtual environment
3. Navigate to project directory
4. Run command:
   ```bash
   python manage.py bulk_checkin <EMPLOYEE_ID> --month <YYYY-MM>
   ```
5. Review the missing days list
6. Type `yes` to confirm and create records

### Error Handling
- Invalid employee ID → Error message, script exits
- Invalid month format → Error message with correct format
- Database errors → Individual date errors shown, continues processing

### Safety Features
- Only processes past dates (up to yesterday)
- Confirmation prompt before creating records
- Skips existing attendance (no duplicates)
- Error handling for each date individually

## Related Scripts
- `bulk_checkout.py` - Assigns only check-outs for existing check-ins
- `auto_checkout.py` - Scheduled task for daily auto-checkout

## Date: August 17, 2026
