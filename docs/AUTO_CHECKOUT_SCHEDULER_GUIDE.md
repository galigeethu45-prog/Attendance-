# 🕐 Auto-Checkout Scheduler Setup Guide

## Overview

This guide will help you set up **automatic checkout at 7 PM every day** using Windows Task Scheduler. The task will run **automatically** whether anyone is using the system or not.

---

## ✅ Quick Setup (2 Minutes)

### Step 1: Run Setup Script

1. **Right-click** on `setup_auto_checkout_task.bat`
2. Select **"Run as administrator"**
3. Press any key when prompted
4. Wait for "SUCCESS!" message

**That's it!** The task is now scheduled and will run every day at 7 PM automatically.

---

## 🔍 Verify Setup

### Check Task Scheduler

1. Press `Win + R`
2. Type `taskschd.msc` and press Enter
3. Look for **"AttendanceHub Auto-Checkout"** in the task list
4. Should show:
   - Status: **Ready**
   - Next Run Time: **Today at 7:00 PM** (or tomorrow if after 7 PM)
   - Last Run Result: **(Not yet run)** or **Success (0x0)**

---

## 🧪 Test It Now (Optional)

### Manual Test

Run this command to test immediately:
```cmd
schtasks /Run /TN "AttendanceHub Auto-Checkout"
```

Or use the test script:
```cmd
test_auto_checkout.bat
```

This will:
1. Run the auto-checkout command immediately
2. Show which employees were checked out
3. Display work hours calculated

---

## 📋 How It Works

### Every Day at 7:00 PM

1. **Windows Task Scheduler** triggers the task
2. **Python script** runs: `python manage.py auto_checkout`
3. **Script checks** for employees without checkout
4. **Auto-checks out** everyone at 7:00 PM
5. **Calculates** work hours
6. **Logs** the action in audit trail

### No User Interaction Needed

- ✅ Runs even if no one is logged in
- ✅ Runs even if computer is locked
- ✅ Runs even if Django server is not running
- ✅ Runs even if no one is using the system
- ✅ Runs every single day automatically

---

## 🔧 Troubleshooting

### Task Not Running?

**Check 1: Task Exists**
```cmd
schtasks /Query /TN "AttendanceHub Auto-Checkout"
```
Should show task details. If not found, run setup script again.

**Check 2: Task is Enabled**
1. Open Task Scheduler
2. Find "AttendanceHub Auto-Checkout"
3. Right-click → **Enable** (if disabled)

**Check 3: Correct Time**
1. Open Task Scheduler
2. Double-click the task
3. Go to **Triggers** tab
4. Should show: **Daily at 7:00 PM**

**Check 4: Python Path**
1. Open Task Scheduler
2. Double-click the task
3. Go to **Actions** tab
4. Should show path to your venv Python

### Task Runs But Doesn't Work?

**Check 1: Django Server**
- Task runs independently of Django server
- Django server does NOT need to be running
- Task connects directly to database

**Check 2: Database Connection**
- Check `.env` file has correct database settings
- Test database connection:
  ```cmd
  python manage.py shell -c "from attendance.models import Attendance; print('DB OK')"
  ```

**Check 3: Permissions**
- Task must run with your user account
- Or run as SYSTEM with database access

### View Task History

1. Open Task Scheduler
2. Find "AttendanceHub Auto-Checkout"
3. Click **History** tab (bottom)
4. Look for recent runs and any errors

---

## 📊 Manual Commands

### Run Auto-Checkout Now
```cmd
python manage.py auto_checkout
```

### Check Pending Checkouts
```cmd
python manage.py shell -c "from attendance.models import Attendance; from django.utils import timezone; pending = Attendance.objects.filter(date=timezone.now().date(), check_out__isnull=True, check_in__isnull=False); print(f'Pending: {pending.count()}')"
```

### Fix Old Pending Checkouts
```cmd
python fix_old_checkouts.py
```

---

## 🔄 Modify Schedule

### Change Time

To run at different time (e.g., 8 PM):

1. Open Task Scheduler
2. Double-click "AttendanceHub Auto-Checkout"
3. Go to **Triggers** tab
4. Double-click the trigger
5. Change time to **20:00** (8 PM)
6. Click **OK**

### Run Multiple Times Per Day

To run at 7 PM and 9 PM:

1. Open Task Scheduler
2. Double-click "AttendanceHub Auto-Checkout"
3. Go to **Triggers** tab
4. Click **New**
5. Set time to **21:00** (9 PM)
6. Click **OK**

---

## 🗑️ Remove Task

### If You Want to Disable

**Option 1: Disable (Keep but don't run)**
```cmd
schtasks /Change /TN "AttendanceHub Auto-Checkout" /DISABLE
```

**Option 2: Delete (Remove completely)**
```cmd
schtasks /Delete /TN "AttendanceHub Auto-Checkout" /F
```

---

## 📝 Task Details

### Task Configuration

| Setting | Value |
|---------|-------|
| Name | AttendanceHub Auto-Checkout |
| Trigger | Daily at 7:00 PM |
| Action | Run Python command |
| Command | `python manage.py auto_checkout` |
| Run As | Your user account |
| Run Level | Highest privileges |
| Run whether user is logged on or not | Yes |

### What Gets Executed

```cmd
"C:\Users\HP\OneDrive\Desktop\Attendance Website\venv\Scripts\python.exe" 
"C:\Users\HP\OneDrive\Desktop\Attendance Website\manage.py" 
auto_checkout
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Task appears in Task Scheduler
- [ ] Task status is "Ready"
- [ ] Next run time shows today/tomorrow at 7:00 PM
- [ ] Task trigger is set to Daily at 19:00
- [ ] Task action points to correct Python and manage.py
- [ ] Manual test run works: `schtasks /Run /TN "AttendanceHub Auto-Checkout"`
- [ ] Check audit logs show auto-checkout entries

---

## 🎯 Expected Behavior

### Before 7 PM
- Employees can check in/out normally
- No auto-checkout happens
- Manual checkout works as usual

### At 7:00 PM Sharp
- Task Scheduler triggers
- Script runs automatically
- Finds all employees without checkout
- Sets checkout to 7:00 PM
- Calculates work hours
- Logs action in audit trail

### After 7 PM
- All employees from today are checked out
- Work hours calculated
- Attendance records complete
- Ready for next day

---

## 📞 Support

### Common Questions

**Q: Does Django server need to be running?**
A: No, the task runs independently and connects directly to the database.

**Q: What if computer is off at 7 PM?**
A: Task will run when computer starts next time (if configured).

**Q: Can I run it multiple times?**
A: Yes, script is safe to run multiple times. Won't duplicate checkouts.

**Q: What if someone already checked out?**
A: Script only affects employees without checkout. Won't change existing checkouts.

**Q: Can I see what happened?**
A: Yes, check audit logs in Django admin or HR dashboard.

---

## 🚀 Production Deployment

### For Production Server

1. **Run setup script** on production server
2. **Verify task** is created
3. **Test manually** first time
4. **Monitor** for first few days
5. **Check audit logs** daily

### For Multiple Servers

- Set up task on each server
- Or use one server as "scheduler"
- Ensure database is accessible

---

## 📄 Files

### Setup Files
- `setup_auto_checkout_task.bat` - Creates scheduled task
- `test_auto_checkout.bat` - Test task manually
- `remove_auto_checkout_task.bat` - Remove task

### Command Files
- `attendance/management/commands/auto_checkout.py` - The actual command
- `fix_old_checkouts.py` - Fix old pending records

### Documentation
- `AUTO_CHECKOUT_SCHEDULER_GUIDE.md` - This file
- `AUTO_CHECKOUT_SETUP.txt` - Quick reference

---

## ✅ Summary

**Setup:** Run `setup_auto_checkout_task.bat` as administrator  
**Runs:** Every day at 7:00 PM automatically  
**Action:** Auto-checkout all employees without checkout  
**Result:** Complete attendance records every day  
**Maintenance:** None required - fully automatic  

---

**Status:** ✅ Ready to Use  
**Requirement:** Windows Task Scheduler (built-in)  
**Dependencies:** Python, Django, Database access
