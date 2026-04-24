# 🚀 Auto-Checkout Setup Instructions

## Two Options Available

---

## ✅ Option 1: No Admin Required (Recommended to Try First)

### File: `setup_auto_checkout_no_admin.bat`

**Just double-click it** - No admin rights needed!

### Pros:
- ✅ No admin password needed
- ✅ Quick and easy
- ✅ Works for most cases

### Cons:
- ⚠️ Only runs when you are logged in
- ⚠️ Won't run if computer is locked (in some cases)

### How to Use:
1. Double-click `setup_auto_checkout_no_admin.bat`
2. Press any key when prompted
3. Wait for "SUCCESS!" message
4. Done!

---

## ✅ Option 2: With Admin Rights (Most Reliable)

### File: `setup_auto_checkout_task.bat`

**Right-click → Run as administrator**

### Pros:
- ✅ Runs even when logged out
- ✅ Runs even when computer is locked
- ✅ Most reliable option
- ✅ Runs whether you're logged in or not

### Cons:
- ⚠️ Requires admin password

### How to Use:
1. **Right-click** on `setup_auto_checkout_task.bat`
2. Select **"Run as administrator"**
3. Enter admin password if prompted
4. Press any key when prompted
5. Wait for "SUCCESS!" message
6. Done!

---

## 🤔 Which One Should I Use?

### Try Option 1 First (No Admin)
- If you don't have admin rights
- If you're always logged in during work hours
- If you want quick setup

### Use Option 2 If (With Admin)
- Option 1 doesn't work
- You want it to run even when logged out
- You want the most reliable solution
- You have admin rights

---

## 📋 What Happens After Setup

### Both Options:
1. Creates a scheduled task in Windows
2. Task runs every day at 7:00 PM
3. Automatically checks out all employees
4. Calculates work hours
5. Logs the action

### Difference:
- **Option 1**: Runs when you're logged in
- **Option 2**: Runs always (even logged out)

---

## ✅ Verify Setup

After running either option:

1. Press `Win + R`
2. Type: `taskschd.msc`
3. Press Enter
4. Look for: **"AttendanceHub Auto-Checkout"**
5. Should show:
   - Status: **Ready**
   - Next Run: **Today at 7:00 PM**

---

## 🧪 Test It

### Test Immediately:
```cmd
schtasks /Run /TN "AttendanceHub Auto-Checkout"
```

Or double-click: `test_auto_checkout.bat`

---

## 🔧 Troubleshooting

### "Access Denied" Error

**Solution**: Use Option 2 (with admin rights)

### Task Created But Not Running

**Check 1**: Are you logged in at 7 PM?
- If using Option 1, you must be logged in
- If using Option 2, doesn't matter

**Check 2**: Is task enabled?
1. Open Task Scheduler
2. Find the task
3. Right-click → Enable

**Check 3**: Test manually
```cmd
schtasks /Run /TN "AttendanceHub Auto-Checkout"
```

---

## 📞 Quick Reference

| File | Admin Required? | Runs When Logged Out? |
|------|----------------|----------------------|
| `setup_auto_checkout_no_admin.bat` | ❌ No | ❌ No |
| `setup_auto_checkout_task.bat` | ✅ Yes | ✅ Yes |

---

## 💡 Recommendation

1. **Try Option 1 first** (no admin)
2. **If it works** - great, you're done!
3. **If it doesn't work** or you want more reliability - use Option 2 (with admin)

---

## ✅ Summary

**Easiest**: Double-click `setup_auto_checkout_no_admin.bat`  
**Most Reliable**: Right-click `setup_auto_checkout_task.bat` → Run as administrator  
**Test**: Double-click `test_auto_checkout.bat`  
**Remove**: Double-click `remove_auto_checkout_task.bat`

---

**Both options work! Choose what's convenient for you.** 🚀
