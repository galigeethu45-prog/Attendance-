# ⚡ Auto-Checkout Quick Start

## 🎯 Goal
Automatically checkout all employees at 7 PM every day, **whether anyone is using the system or not**.

---

## ✅ Setup (30 Seconds)

### Step 1: Run Setup
1. **Right-click** `setup_auto_checkout_task.bat`
2. Click **"Run as administrator"**
3. Press any key
4. Wait for "SUCCESS!" message

### Step 2: Verify
1. Press `Win + R`
2. Type `taskschd.msc`
3. Look for **"AttendanceHub Auto-Checkout"**
4. Should show: Status = **Ready**, Next Run = **Today 7:00 PM**

**Done!** It will now run automatically every day at 7 PM.

---

## 🧪 Test It (Optional)

Double-click `test_auto_checkout.bat` to test immediately.

---

## 📋 What Happens

### Every Day at 7:00 PM
1. Windows Task Scheduler triggers automatically
2. Finds all employees without checkout
3. Sets checkout to 7:00 PM
4. Calculates work hours
5. Done!

### No User Action Needed
- ✅ Runs even if no one is logged in
- ✅ Runs even if system is idle
- ✅ Runs even if Django server is off
- ✅ Runs every single day

---

## 🔧 Troubleshooting

### Task Not Running?
```cmd
schtasks /Query /TN "AttendanceHub Auto-Checkout"
```
If not found, run setup again.

### Test Manually
```cmd
schtasks /Run /TN "AttendanceHub Auto-Checkout"
```

---

## 📞 Need Help?

Read full guide: `AUTO_CHECKOUT_SCHEDULER_GUIDE.md`

---

**That's it! Simple and automatic.** 🚀
