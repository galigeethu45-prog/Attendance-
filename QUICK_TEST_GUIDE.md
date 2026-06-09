# Quick Test Guide - Bulk Checkout Feature

## 🚀 Quick Start (5 Minutes)

### Step 1: Verify Server is Running
Your local server should be running at: http://127.0.0.1:8000/

### Step 2: Login
- Username: `admin` (or any HR user)
- This user is a **superuser** so they have full access

### Step 3: Navigate to Feature
1. Click **"HR"** in the navigation menu
2. Go to **"Office Network"** tab
3. Scroll down to **"Bulk Checkout Assignment"** section

### Step 4: Test Authentication (IMPORTANT)
1. Click the **"Test Auth"** button
2. You should see:
   ```
   User: admin
   Authenticated: true
   Superuser: true
   Employee ID: null
   Is HR: false
   Role: employee
   ```
3. ✅ If you see `Superuser: true`, the feature will work!

### Step 5: Use the Feature

#### Option A: Test with "All Employees"
1. Click **"Assign Missing Checkouts"** button
2. Click **"All Employees"**
3. You'll see a preview of all missing checkouts
4. Click **"Assign 7 PM Checkout"**
5. View results!

#### Option B: Test with "Specific Employee"
1. Click **"Assign Missing Checkouts"** button
2. Click **"Specific Employees"**
3. Select an employee from the dropdown
4. Click **"Continue"**
5. Review their missing checkouts
6. Click **"Assign 7 PM Checkout"**
7. View results!

## 🔍 What to Check

### Expected Behavior
- ✅ Modal opens smoothly
- ✅ Dropdown shows employee IDs (e.g., "AI0021 - John Doe")
- ✅ Preview shows missing checkouts
- ✅ Only shows dates BEFORE today
- ✅ Shows status for each record
- ✅ Results display assignment success

### Common Issues (All Fixed!)

❌ **"Error fetching missing checkouts: HTTP Error 403"**
✅ **FIXED**: Superusers now have access

❌ **Dropdown showing empty values**
✅ **FIXED**: Filters out employees without employee_id

❌ **Modal doesn't open**
✅ **FIXED**: All JavaScript functions complete

## 🎯 What Should Happen

When you click **"Assign 7 PM Checkout"**:

1. System checks each attendance record
2. For each missing checkout:
   - ✅ Assigns 7:00 PM as checkout time
   - ⏭️ Skips if employee is on Leave
   - ⏭️ Skips if employee is on WFH
3. Creates audit log for each assignment
4. Shows results with counts

## 🐛 Troubleshooting

### If you get 403 Forbidden:
- Click "Test Auth" button
- Check if `Superuser: true` or `Is HR: true`
- If both are false, you need HR permissions

### If dropdown is empty:
- Make sure employees have employee_id values
- Check database: `python manage.py shell -c "from attendance.models import EmployeeProfile; print([p.employee_id for p in EmployeeProfile.objects.all()])"`

### If server errors:
- Check server logs in terminal
- Look for DEBUG messages
- Server will show which user is accessing

## 📊 Test Data

If you don't have test data, create some:
1. Login as employee
2. Check-in without checking out
3. Wait until next day
4. Then use bulk checkout as HR

## ✅ Success Indicators

You know it's working when:
- ✅ Modal opens without errors
- ✅ Dropdown shows employee names
- ✅ Preview displays correctly
- ✅ Assignment completes successfully
- ✅ Results show assigned count
- ✅ Audit logs created (check in Audit Logs tab)

## 🎉 Feature is Complete When:

- [x] You can select "All Employees" and see preview
- [x] You can select specific employee from dropdown
- [x] Preview shows only past dates (not today)
- [x] Assignment creates 7 PM checkouts
- [x] Employees on leave/WFH are skipped
- [x] Results display correctly
- [x] No JavaScript errors in console
- [x] No Python errors in server log

## 🔗 Next Steps

Once local testing is complete:

1. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add bulk checkout assignment feature"
   git push origin main
   ```

2. **Deploy to AWS**
   ```bash
   ssh your-aws-server
   cd /path/to/project
   git pull origin main
   sudo systemctl restart gunicorn
   ```

3. **Test on Production**
   - Login as HR user
   - Test the feature
   - Verify audit logs

---

**Ready to Test!** 🚀

Just refresh your browser and try the steps above.
