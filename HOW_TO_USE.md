# 🎯 How to Use AttendanceHub - Step by Step

## 🚀 Starting the Application

### Step 1: Start the Server
```bash
# Option 1: Double-click (Windows)
run_server.bat

# Option 2: Command line
.\venv\Scripts\activate
python manage.py runserver
```

### Step 2: Open Your Browser
Go to: **http://localhost:8000/**

You will see this beautiful login page:
```
┌─────────────────────────────────────┐
│                                     │
│         🕐 AttendanceHub            │
│     Sign in to your account         │
│                                     │
│   ┌─────────────────────────────┐  │
│   │ 👤 Username                 │  │
│   └─────────────────────────────┘  │
│   ┌─────────────────────────────┐  │
│   │ 🔒 Password                 │  │
│   └─────────────────────────────┘  │
│   ☐ Remember me                    │
│                                     │
│   ┌─────────────────────────────┐  │
│   │      🔐 Sign In             │  │
│   └─────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

---

## 👤 For Employees

### Login
1. **Username:** `employee1`
2. **Password:** `emp123`
3. Click **"Sign In"**

### Daily Workflow

#### Morning - Check In
```
1. After login, you'll see your dashboard
2. Look for the "Check In" card (green icon)
3. Click the "Check In" button
4. ✅ You're checked in! Time is recorded.
```

#### During Day - Take Breaks
```
Tea Break (15 minutes, max 2 per day):
1. Click "Tea" button in the "Take Break" card
2. Break timer starts
3. When done, click "End Break"

Lunch Break (45 minutes, max 1 per day):
1. Click "Lunch" button in the "Take Break" card
2. Break timer starts
3. When done, click "End Break"
```

#### Evening - Check Out
```
1. Click the "Check Out" button (red icon)
2. ✅ Your work hours are calculated automatically
3. View your total hours for the day
```

### View Your History
```
1. Click "History" in the navigation bar
2. See all your attendance records
3. Filter by month, year, or status
4. Click "Export CSV" to download
```

### Request Leave
```
1. Click "Leave" in the navigation bar
2. Fill in the form:
   - Leave Type: Sick/Casual/Vacation/Emergency
   - Start Date: Select date
   - End Date: Select date
   - Reason: Explain why
3. Click "Submit Request"
4. Wait for HR approval
5. Check notifications for status
```

### Update Profile
```
1. Click your username (top-right)
2. Select "Profile"
3. Update your information:
   - First Name
   - Last Name
   - Email
4. Click "Save Changes"
```

### Check Notifications
```
1. Click your username (top-right)
2. Select "Notifications"
3. See all alerts:
   - Break limit warnings
   - Leave approval/rejection
   - System messages
4. Click "Mark All as Read" to clear
```

### Logout
```
1. Click your username (top-right)
2. Click "Logout"
3. ✅ You're logged out safely
4. Redirected to login page
```

---

## 👔 For HR Managers

### Login
1. **Username:** `hr_admin`
2. **Password:** `admin123`
3. Click **"Sign In"**

### HR Dashboard
```
1. After login, click "HR Panel" in navigation
2. You'll see:
   - Total Employees
   - Present Today
   - Absent Today
   - Pending Leave Requests
```

### Monitor Today's Attendance
```
1. In HR Dashboard, view "Today's Attendance" tab
2. See all employees:
   - Name and Department
   - Check-in time
   - Check-out time
   - Work hours
   - Status (Present/Late/Absent)
   - Number of breaks taken
```

### Approve/Reject Leave Requests
```
1. Click "Leave Requests" tab
2. See all pending requests with:
   - Employee name
   - Leave type
   - Start and end dates
   - Number of days
   - Reason

To Approve:
1. Click green ✅ button
2. Employee gets notification

To Reject:
1. Click red ❌ button
2. Enter reason (optional)
3. Employee gets notification
```

### View Analytics
```
1. Click "Reports" tab
2. See two charts:
   
   Monthly Attendance Trend:
   - Line chart showing attendance over time
   - Last 7 days data
   
   Department Distribution:
   - Pie chart showing employees per department
   - Visual breakdown
```

### Generate Reports
```
1. Go to any employee's attendance history
2. Use filters to narrow down data
3. Click "Export CSV"
4. Open in Excel for further analysis
```

---

## 📊 Understanding the Dashboard

### Employee Dashboard Cards

**Check In Card (Green):**
- Shows if you've checked in
- Displays check-in time
- Button to check in

**Check Out Card (Red):**
- Shows if you've checked out
- Displays check-out time
- Button to check out

**Take Break Card (Blue):**
- Shows active break status
- Buttons for Tea and Lunch
- Shows remaining break count

**Work Hours Card (Purple):**
- Shows today's total work hours
- Updates after check-out
- Format: Xh Ym (e.g., 8h 45m)

### Statistics Cards

**This Month:**
- Total present days this month

**Total Hours:**
- Total work hours this month

**Late Arrivals:**
- Number of times late this month

**Notifications:**
- Unread notification count

---

## 🎨 Status Indicators

### Attendance Status
- ✅ **Present** (Green) - On time (before 9:30 AM)
- ⚠️ **Late** (Yellow) - After 9:30 AM
- 🔵 **Half-Day** (Blue) - Less than 4 hours
- ❌ **Absent** (Red) - No check-in

### Leave Status
- ⏳ **Pending** (Yellow) - Waiting for approval
- ✅ **Approved** (Green) - HR approved
- ❌ **Rejected** (Red) - HR rejected

---

## ⚠️ Important Rules

### Break Rules
```
Tea Break:
- Duration: 15 minutes allowed
- Frequency: Maximum 2 per day
- Exceeding: Warning notification sent

Lunch Break:
- Duration: 45 minutes allowed
- Frequency: Maximum 1 per day
- Exceeding: Warning notification sent
```

### Work Hours
```
Normal Day:
- Check-in before 9:30 AM = Present
- Check-in after 9:30 AM = Late
- Work less than 4 hours = Half-Day
- No check-in = Absent
```

### Leave Balance (Example)
```
Sick Leave: 12 days per year
Casual Leave: 15 days per year
Vacation: 20 days per year
```

---

## 🔔 Notifications You'll Receive

### Break Notifications
- "Tea break exceeded limit (20 mins)"
- "Lunch break exceeded limit (60 mins)"
- "You exceeded the allowed number of tea breaks today"

### Leave Notifications
- "Your Sick Leave request has been approved"
- "Your Casual Leave request has been rejected"
- "Leave request submitted successfully"

---

## 💡 Pro Tips

### For Employees:
1. ✅ Check in on time to avoid "Late" status
2. ✅ End breaks promptly to avoid warnings
3. ✅ Check notifications regularly
4. ✅ Request leaves in advance
5. ✅ Keep your profile updated

### For HR:
1. ✅ Review attendance daily
2. ✅ Process leave requests promptly
3. ✅ Check analytics weekly
4. ✅ Export reports for records
5. ✅ Monitor break violations

---

## 🐛 Troubleshooting

### Can't Login?
```
✓ Check username and password
✓ Make sure caps lock is off
✓ Try: employee1 / emp123
✓ Or: hr_admin / admin123
```

### Can't Check In?
```
✓ Make sure you're logged in
✓ Check if already checked in today
✓ Refresh the page
```

### Can't Take Break?
```
✓ Make sure you've checked in
✓ Check if already on a break
✓ Verify break limit not exceeded
✓ Check notifications for warnings
```

### Can't Check Out?
```
✓ Make sure you've checked in
✓ End any active breaks first
✓ Refresh the page
```

---

## 📱 Mobile Usage

The application is mobile-friendly!

```
On Mobile:
1. Open browser (Chrome/Safari)
2. Go to: http://localhost:8000/
3. Login normally
4. All features work on mobile
5. Cards stack vertically
6. Touch-friendly buttons
```

---

## 🎓 Common Scenarios

### Scenario 1: Normal Work Day
```
9:00 AM  → Check In
11:00 AM → Tea Break (15 min)
11:15 AM → End Break
1:00 PM  → Lunch Break (45 min)
1:45 PM  → End Break
4:00 PM  → Tea Break (15 min)
4:15 PM  → End Break
6:00 PM  → Check Out
Result: 8h 45m work hours, Present status
```

### Scenario 2: Late Arrival
```
10:00 AM → Check In (Late!)
1:00 PM  → Lunch Break
1:45 PM  → End Break
6:30 PM  → Check Out
Result: 8h 15m work hours, Late status
```

### Scenario 3: Half Day
```
9:00 AM  → Check In
12:00 PM → Check Out
Result: 3h 0m work hours, Half-Day status
```

### Scenario 4: Leave Request
```
Day 1: Submit leave request for next week
Day 2: HR reviews and approves
Day 3: Check notification for approval
Next Week: Leave is marked in system
```

---

## 🎉 You're Ready!

Now you know how to use AttendanceHub completely!

**Remember:**
- ✅ Check in daily
- ✅ Manage breaks properly
- ✅ Check out before leaving
- ✅ Request leaves in advance
- ✅ Check notifications regularly

**Need Help?**
- Check START_HERE.md
- Read QUICKSTART.md
- Review FEATURES.md

**Happy Tracking! 🚀**
