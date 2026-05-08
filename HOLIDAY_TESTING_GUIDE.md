# Holiday Calendar System - Testing Guide 🧪

## ✅ Server Status: RUNNING
Django server started successfully with **NO ERRORS**!

---

## 🎯 Quick Testing Steps

### 1. Employee Holiday Calendar View
**URL:** http://127.0.0.1:8000/attendance/holidays/

**What to test:**
- [ ] Calendar displays current month (May 2026)
- [ ] Sundays are highlighted in yellow with sun icon
- [ ] 2nd & 4th Saturdays are highlighted in blue
- [ ] Company holidays (if any in May) are shown
- [ ] Change month using dropdown (try different months)
- [ ] Change year using dropdown (try 2026)
- [ ] Upcoming holidays sidebar shows next 5 holidays
- [ ] All holidays list on right side shows holidays by type
- [ ] Today's date is highlighted with blue border
- [ ] Hover over holiday shows tooltip with details

**Expected Results:**
- Clean calendar grid layout
- Color-coded holidays
- Responsive design
- Smooth navigation

---

### 2. HR Holiday Management View
**URL:** http://127.0.0.1:8000/attendance/holidays/manage/

**What to test:**

#### A. View Existing Holidays
- [ ] See 6 cards showing holidays by type
- [ ] Weekly Offs card shows ~52 Sundays
- [ ] 2nd Saturdays card shows ~12 Saturdays
- [ ] 4th Saturdays card shows ~12 Saturdays
- [ ] Company Holidays card shows 14 holidays
- [ ] Summary stats at bottom show correct counts

#### B. Add New Holiday
- [ ] Fill in date (e.g., 2026-12-31)
- [ ] Enter name (e.g., "New Year's Eve")
- [ ] Select type (e.g., "Company Holiday")
- [ ] Add description (optional)
- [ ] Click "Add Holiday"
- [ ] See success message
- [ ] Page reloads with new holiday in list

#### C. Delete Holiday
- [ ] Find a holiday in any card
- [ ] Click red trash icon
- [ ] Confirm deletion
- [ ] See success message
- [ ] Holiday removed from list

#### D. Auto-Generate Holidays
- [ ] Select year (e.g., 2027)
- [ ] Click "Generate for 2027"
- [ ] Confirm action
- [ ] See success message showing count
- [ ] Page reloads with generated holidays

---

### 3. HR Dashboard Integration
**URL:** http://127.0.0.1:8000/attendance/hr-dashboard/

**What to test:**
- [ ] See "Holiday Calendar" tab (between Reports and Office Network)
- [ ] Click on Holiday Calendar tab
- [ ] See information about holiday system
- [ ] See 3 quick action cards:
  - View Calendar (links to employee view)
  - Add Holidays (links to HR management)
  - Auto-Generate (links to HR management)
- [ ] See holiday check-in policy explanation
- [ ] See "How Holiday System Works" section

---

### 4. Navbar Integration
**URL:** Any page when logged in

**What to test:**
- [ ] See "Holidays" link in navbar
- [ ] Located between "Overtime" and "Approvals" dropdown
- [ ] Has calendar icon
- [ ] Click opens employee holiday calendar
- [ ] Works from any page

---

### 5. Leave Calculation (Holiday Exclusion)
**URL:** http://127.0.0.1:8000/attendance/leave-request/

**Test Scenario:**
1. Submit leave request from **Monday to Friday** (5 days)
2. If **Wednesday is a holiday**, system should show **4 days** (not 5)
3. Holiday is automatically excluded from count

**What to test:**
- [ ] Create leave request spanning a Sunday
- [ ] Check total days shown (should exclude Sunday)
- [ ] Create leave request spanning 2nd/4th Saturday
- [ ] Check total days shown (should exclude Saturday)
- [ ] Create leave request spanning company holiday
- [ ] Check total days shown (should exclude holiday)

**Example:**
- Request: May 5 (Mon) to May 9 (Fri) = 5 days
- If May 7 (Wed) is a holiday = Shows **4 days**

---

### 6. Check-in Validation on Holiday
**URL:** http://127.0.0.1:8000/attendance/dashboard/

**Test Scenario A: Check-in on Sunday (without OT)**
1. Change system date to a Sunday (or wait for Sunday)
2. Try to check-in
3. Should see warning: "Today is a holiday (Sunday)"
4. Should still allow check-in
5. Attendance counted as normal working day

**Test Scenario B: Check-in on Holiday (with OT)**
1. Submit OT request for a holiday
2. HR approves OT
3. Try to check-in on that holiday
4. Should allow check-in without warning
5. Attendance counted as overtime

**What to test:**
- [ ] Check-in on Sunday shows holiday warning
- [ ] Check-in still allowed
- [ ] Check-in with approved OT works smoothly
- [ ] Check-in without OT shows warning but allows

---

## 🎨 Visual Checks

### Calendar Colors:
- 🌞 **Yellow** = Weekly Offs (Sundays)
- 📅 **Blue** = 2nd & 4th Saturdays
- 🚩 **Red** = National Holidays
- 🏢 **Green** = Company Holidays
- ⭐ **Blue** = Optional Holidays

### Icons:
- Sun icon = Weekly Off
- Calendar icon = Saturday
- Flag icon = National Holiday
- Building icon = Company Holiday
- Star icon = Optional Holiday

---

## 📊 Data Verification

### Check Database:
```bash
python manage.py shell
```

```python
from attendance.models import CompanyHoliday

# Count holidays by type
print("Sundays:", CompanyHoliday.objects.filter(holiday_type='weekly_off').count())
print("2nd Saturdays:", CompanyHoliday.objects.filter(holiday_type='second_saturday').count())
print("4th Saturdays:", CompanyHoliday.objects.filter(holiday_type='fourth_saturday').count())
print("Company:", CompanyHoliday.objects.filter(holiday_type='company').count())
print("Total:", CompanyHoliday.objects.count())

# Expected: 52 + 12 + 12 + 14 = 90 holidays for 2026
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Calendar not showing holidays
**Solution:** Check if holidays are in database for selected month/year

### Issue 2: Leave calculation not excluding holidays
**Solution:** Check `LeaveRequest.total_days` property in models.py

### Issue 3: Check-in validation not working
**Solution:** Check `check_in()` function in views.py

### Issue 4: AJAX not working (add/delete holiday)
**Solution:** Check browser console for JavaScript errors

### Issue 5: 404 on holiday URLs
**Solution:** Check `attendance/urls.py` has holiday routes

---

## ✅ Success Criteria

All features working if:
- ✅ Calendar displays with color-coded holidays
- ✅ HR can add/delete holidays
- ✅ Auto-generate creates Sundays + Saturdays
- ✅ Leave calculation excludes holidays
- ✅ Check-in validation works on holidays
- ✅ Navbar has Holidays link
- ✅ HR Dashboard has Holiday Calendar tab
- ✅ No errors in browser console
- ✅ No errors in Django server logs

---

## 🚀 Next Steps After Testing

1. **Test with real data:**
   - Add actual company holidays for 2026
   - Test leave requests spanning holidays
   - Test check-in on holidays

2. **User Acceptance Testing:**
   - Have HR test holiday management
   - Have employees test calendar view
   - Collect feedback

3. **Production Deployment:**
   - Backup database
   - Run migrations on production
   - Populate holidays for current year
   - Monitor for issues

---

## 📞 Support

If you encounter any issues:
1. Check Django server logs
2. Check browser console (F12)
3. Verify database has holidays
4. Check URL routing
5. Verify template syntax

---

**Status:** ✅ Ready for Testing
**Server:** Running at http://127.0.0.1:8000/
**Implementation:** 100% Complete
