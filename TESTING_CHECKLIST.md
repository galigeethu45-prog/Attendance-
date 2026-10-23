# URGENT FIXES - TESTING CHECKLIST

**Date:** October 23, 2026  
**Tester:** _______________  
**Browser:** _______________  

---

## Pre-Testing Setup

- [ ] Server is running (`python manage.py runserver`)
- [ ] Browser cache cleared (Ctrl+Shift+Delete)
- [ ] Test users available:
  - [ ] HR user
  - [ ] Team Leader user
  - [ ] Regular employee user

---

## Fix #1: Name Consistency Testing

### Test Case 1.1: Leave Approval Page
- [ ] Login as HR
- [ ] Navigate to: Approvals → Leave Approval
- [ ] Check employee names in request cards
- [ ] Expected: All names in Title Case (e.g., "John Doe")
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 1.2: WFH Approval Page
- [ ] Navigate to: Approvals → WFH Approval
- [ ] Check employee names in request cards
- [ ] Expected: All names in Title Case
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 1.3: Onsite Approval Page
- [ ] Navigate to: Approvals → Onsite Approval
- [ ] Check employee names in request cards
- [ ] Expected: All names in Title Case
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 1.4: Overtime Approval Page
- [ ] Navigate to: HR Panel → Overtime Approval
- [ ] Check employee names in overtime cards
- [ ] Expected: All names in Title Case
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 1.5: Master Data List
- [ ] Navigate to: HR Panel → Master Data
- [ ] Check employee names in table
- [ ] Expected: All names in Title Case
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 1.6: HR Dashboard
- [ ] Navigate to: HR Dashboard
- [ ] Check Today's Attendance section
- [ ] Check Employee Profiles tab
- [ ] Expected: All names in Title Case
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 1.7: Employee Dashboard
- [ ] Logout and login as regular employee
- [ ] Check welcome message at top
- [ ] Expected: "Welcome, Your Name!" in Title Case
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

---

## Fix #2: Blank Page Testing

### Test Case 2.1: Few Requests (Control)
- [ ] Login as Team Leader
- [ ] Navigate to: Approvals → Leave Approval
- [ ] Click "All Requests" tab
- [ ] Expected: All cards visible
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 2.2: Many Requests (20+)
- [ ] Create 20+ test leave requests (if not available)
- [ ] Navigate to: Approvals → Leave Approval
- [ ] Click "All Requests" tab
- [ ] Expected: All cards display, no blank space
- [ ] Scroll down to see all requests
- [ ] Expected: Smooth scrolling, no cutoff
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 2.3: Approved Requests
- [ ] Click "Approved" tab
- [ ] Expected: All approved cards visible
- [ ] Scroll through list
- [ ] Expected: No blank areas
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 2.4: WFH Requests
- [ ] Navigate to: Approvals → WFH Approval
- [ ] Click "All Requests"
- [ ] Expected: All cards visible, scrollable
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

---

## Fix #3: Table Overlap Testing

### Test Case 3.1: Normal Content
- [ ] Login as HR
- [ ] Navigate to: Master Data Management
- [ ] Observe Email and Department columns
- [ ] Expected: Columns properly separated
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 3.2: Long Email Address
- [ ] Find or add employee with long email (25+ chars)
- [ ] Example: `very.long.email.address@company.com`
- [ ] Expected: Email wraps within column, no overlap
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 3.3: Long Department Name
- [ ] Find or add employee with long department (20+ chars)
- [ ] Example: `Information Technology Department`
- [ ] Expected: Department wraps within column
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 3.4: Both Long
- [ ] Find employee with both long email AND department
- [ ] Expected: Both columns wrap properly, no overlap
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 3.5: Responsive (Mobile)
- [ ] Resize browser to mobile width (375px)
- [ ] Check table scrolling
- [ ] Expected: Table scrolls horizontally if needed
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

---

## Fix #4: Daily Insights Testing

### Test Case 4.1: Access Daily Insights
- [ ] Login as HR
- [ ] Click "HR Panel" in navigation
- [ ] Click "HR Dashboard" from dropdown
- [ ] Click "Reports" tab
- [ ] Expected: Daily Insights section at top
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 4.2: Stat Cards Display
- [ ] Verify all 8 stat cards are visible:
  - [ ] Total Employees (blue icon)
  - [ ] Present Today (green icon)
  - [ ] Absent Today (red icon)
  - [ ] Late Arrivals (yellow icon)
  - [ ] On Leave (cyan icon)
  - [ ] Work From Home (purple icon)
  - [ ] Onsite/Client (pink icon)
  - [ ] Half Day (yellow icon)
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 4.3: Data Accuracy
- [ ] Count manually: Total employees = _____
- [ ] Check card shows: _____
- [ ] Expected: Numbers match
- [ ] Repeat for Present Today
- [ ] Expected: Numbers match
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 4.4: Percentages
- [ ] Check "Present Today" percentage
- [ ] Formula: (Present / Total) × 100
- [ ] Expected: Correct percentage shown
- [ ] Check "Absent Today" percentage
- [ ] Expected: Correct percentage shown
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 4.5: Animations
- [ ] Refresh page (F5)
- [ ] Observe stat cards loading
- [ ] Expected: Cards fade in sequentially (0.1s delays)
- [ ] Expected: Smooth animation, no flicker
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 4.6: Charts Below
- [ ] Scroll down in Reports tab
- [ ] Expected: Monthly Attendance chart visible
- [ ] Expected: Department-wise chart visible
- [ ] Expected: Charts still functional
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

### Test Case 4.7: Responsive Design
- [ ] Resize browser to tablet (768px)
- [ ] Expected: Cards stack 2 per row
- [ ] Resize to mobile (375px)
- [ ] Expected: Cards stack 1 per row
- [ ] Result: ✅ Pass / ❌ Fail
- [ ] Notes: _______________

---

## Cross-Browser Testing

### Chrome
- [ ] All fixes work in Chrome
- [ ] Version: _____
- [ ] Result: ✅ Pass / ❌ Fail

### Firefox
- [ ] All fixes work in Firefox
- [ ] Version: _____
- [ ] Result: ✅ Pass / ❌ Fail

### Edge
- [ ] All fixes work in Edge
- [ ] Version: _____
- [ ] Result: ✅ Pass / ❌ Fail

### Safari (if available)
- [ ] All fixes work in Safari
- [ ] Version: _____
- [ ] Result: ✅ Pass / ❌ Fail

---

## Performance Testing

### Page Load Speed
- [ ] HR Dashboard loads < 2 seconds
- [ ] Reports tab loads < 1 second
- [ ] Master Data table loads < 2 seconds
- [ ] Result: ✅ Pass / ❌ Fail

### Memory Usage
- [ ] Open Chrome DevTools → Performance
- [ ] Record page interaction
- [ ] Expected: No memory leaks
- [ ] Expected: Smooth 60fps animations
- [ ] Result: ✅ Pass / ❌ Fail

---

## Edge Cases

### Test Case E1: Empty Data
- [ ] Navigate to Reports tab with 0 employees
- [ ] Expected: Shows "0" in all cards, no errors
- [ ] Result: ✅ Pass / ❌ Fail

### Test Case E2: All Absent
- [ ] Scenario: No one checked in today
- [ ] Expected: Present = 0, Absent = Total
- [ ] Result: ✅ Pass / ❌ Fail

### Test Case E3: Special Characters in Name
- [ ] Add employee: "O'Connor, Jr."
- [ ] Expected: Title case: "O'connor, Jr."
- [ ] Result: ✅ Pass / ❌ Fail

### Test Case E4: Very Long Name
- [ ] Add employee with 40+ character name
- [ ] Expected: Name wraps or truncates gracefully
- [ ] Result: ✅ Pass / ❌ Fail

---

## Regression Testing

### Check Existing Features Still Work
- [ ] Check-in/Check-out functionality
- [ ] Leave request submission
- [ ] WFH request submission
- [ ] Approval workflows (TL → Manager → HR)
- [ ] Master data CRUD operations
- [ ] Export to CSV
- [ ] User management
- [ ] Holiday calendar
- [ ] Team management
- [ ] Result: ✅ Pass / ❌ Fail

---

## Final Sign-Off

### Summary
- Total Tests: _____
- Passed: _____
- Failed: _____
- Pass Rate: _____%

### Issues Found
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

### Recommendations
_______________________________________________
_______________________________________________
_______________________________________________

### Approval
- [ ] All critical fixes working
- [ ] No major bugs found
- [ ] Ready for production deployment

**Tested By:** _____________________  
**Date:** _____________________  
**Signature:** _____________________

---

**If any test fails, document the issue and notify the development team immediately.**

