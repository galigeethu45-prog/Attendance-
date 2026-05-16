# Manual Checkout Script - Usage Guide

## Purpose
Manually assign checkout time (default 7:00 PM) for employees who forgot to check out.

## Features
✅ **Interactive** - Asks for employee IDs one by one  
✅ **Safe** - Only checks out employees who checked in  
✅ **Smart** - Automatically skips employees on leave/WFH  
✅ **Audit Trail** - Creates audit log entries  
✅ **No Override** - Won't change existing checkout times  
✅ **No Notifications** - Silent operation  

## How to Use

### Method 1: Double-click the batch file (Windows)
1. Navigate to `scripts/maintenance/`
2. Double-click `MANUAL_CHECKOUT.bat`
3. Follow the prompts

### Method 2: Command line
```bash
# Activate virtual environment
venv\Scripts\activate

# Run script
python scripts/maintenance/manual_checkout.py
```

## Step-by-Step Example

### Step 1: Enter your username (for audit log)
```
Enter your username (for audit log):
> admin
```

### Step 2: Enter date (or press Enter for today)
```
Enter date (YYYY-MM-DD) or press Enter for today:
> 2026-05-15
📅 Target Date: May 15, 2026
```
*Press Enter to use today's date*

### Step 3: Enter checkout time (or press Enter for 7 PM)
```
Enter checkout time (HH:MM in 24-hour format) or press Enter for 7:00 PM:
> 19:00
⏰ Checkout Time: 07:00 PM
```
*Press Enter to use default 7:00 PM*

### Step 4: Enter employee IDs one by one
```
Enter Employee ID (or 'done' to finish):
> AI0001

Processing: AI0001
----------------------------------------
✓ Employee: John Doe
  Employee ID: AI0001
  Check-in: 09:15 AM
  Will checkout at: 07:00 PM
  Hours worked: 9.75 hours

Assign checkout? (yes/no):
> yes
✅ Checkout assigned successfully!

Enter Employee ID (or 'done' to finish):
> AI0002

Processing: AI0002
----------------------------------------
⚠️  Skipped: On Casual Leave leave

Enter Employee ID (or 'done' to finish):
> done
```

### Step 5: View summary
```
============================================================
SUMMARY
============================================================
✅ Successfully checked out: 1 employee(s)
⏭️  Skipped: 1 employee(s)

Done!
```

## What Gets Skipped Automatically

The script will automatically skip:
- ❌ Employees not found
- ❌ Employees with no check-in record
- ❌ Employees already checked out
- ❌ Employees on approved leave
- ❌ Employees on approved WFH

## Safety Features

1. **Confirmation Required** - Asks "yes/no" before each checkout
2. **No Overrides** - Won't change existing checkout times
3. **Audit Logging** - Every action is logged with your username
4. **Leave/WFH Check** - Automatically skips employees on leave/WFH

## Audit Log

Every checkout assignment creates an audit log entry:
- **User**: Your username
- **Action**: manual_checkout
- **Details**: "Manually assigned checkout at 07:00 PM for john on 2026-05-15"
- **Target User**: The employee who was checked out

You can view audit logs in the HR Dashboard.

## Tips

1. **Prepare a list** - Have employee IDs ready before running
2. **Check date** - Make sure you're using the correct date
3. **Verify first** - The script shows details before confirming
4. **Type 'done'** - When finished entering employee IDs
5. **Cancel anytime** - Press Ctrl+C to exit

## Common Use Cases

### Case 1: Single employee forgot to checkout today
```
Date: [Press Enter for today]
Time: [Press Enter for 7 PM]
Employee ID: AI0001
Confirm: yes
Employee ID: done
```

### Case 2: Multiple employees forgot yesterday
```
Date: 2026-05-14
Time: [Press Enter for 7 PM]
Employee ID: AI0001
Confirm: yes
Employee ID: AI0002
Confirm: yes
Employee ID: AI0003
Confirm: yes
Employee ID: done
```

### Case 3: Custom checkout time
```
Date: [Press Enter for today]
Time: 18:30
Employee ID: AI0001
Confirm: yes
Employee ID: done
```

## Troubleshooting

### "Employee not found"
- Check the employee ID is correct
- Try using username instead of employee ID

### "No check-in record"
- Employee didn't check in that day
- Check the date is correct

### "Already checked out"
- Employee already has a checkout time
- Script won't override existing checkouts

### "On leave/WFH"
- Employee has approved leave or WFH
- Script automatically skips them (this is correct behavior)

## Important Notes

⚠️ **This script is for manual corrections only**  
⚠️ **Use responsibly - all actions are logged**  
⚠️ **Cannot undo - checkout times are permanent**  
⚠️ **Backup database before bulk operations**  

## Need Help?

If you encounter issues:
1. Check the employee ID is correct
2. Verify the date format (YYYY-MM-DD)
3. Ensure virtual environment is activated
4. Check database connection is working
