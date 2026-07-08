# Dynamic Approval Logic for Leave & WFH - Problem Statement & Solution

## Current Issue

When an employee has overlapping Leave and WFH approvals, the system doesn't properly prioritize them. 

### Example Scenario:
- Employee has approved **WFH from 01/07/2026 to 20/07/2026**
- On **11/07/2026**, employee also has an approved **Leave**
- **Current Behavior**: System still shows the employee as "On WFH" on 11/07/2026
- **Expected Behavior**: System should show "On Leave" for 11/07/2026 since Leave takes priority over WFH

## Root Cause Analysis

### Current Logic Issues:

1. **In `has_approved_wfh_today()` function** (views.py:117):
   - Only checks if WFH is approved for today
   - **Does NOT check if there's an approved Leave for today**
   - Returns True even if employee has Leave on the same day

2. **In `can_check_in_from_location()` function** (views.py:134):
   - Uses `has_approved_wfh_today()` to allow remote check-in
   - Should also check for Leave first
   - **Does NOT prioritize Leave over WFH**

3. **In Dashboard/HR Reports**:
   - Shows employee as "On WFH" without checking for conflicting Leave
   - May show both statuses leading to confusion

4. **No Priority System**:
   - Currently treats WFH and Leave as independent
   - Should implement priority: **Leave > WFH > Office**

## Solution Design

### 1. Create New Helper Function: `get_employee_status_today(user)`

**Purpose**: Get the actual work status for today considering all approvals with proper priority

**Returns**: 
```python
{
    'status': 'on_leave' | 'on_wfh' | 'on_onsite' | 'office',
    'type': 'leave' | 'wfh' | 'onsite' | None,
    'reason': 'Casual Leave' | 'WFH (Approved)' | 'Onsite Visit',
    'details': {} # Request object details
}
```

**Logic (Priority Order)**:
```
if employee has APPROVED Leave for today:
    return 'on_leave'
else if employee has APPROVED WFH for today:
    return 'on_wfh'
else if employee has APPROVED Onsite for today:
    return 'on_onsite'
else:
    return 'office'
```

### 2. Create New Helper Function: `get_employee_status_for_date(user, date)`

**Purpose**: Get work status for any specific date (used for reports, history, etc.)

**Returns**: Same as `get_employee_status_today()` but for any date

### 3. Update Existing Functions

**A. Update `has_approved_wfh_today()` to check Leave first**:
```python
def has_approved_wfh_today(user):
    today = get_local_today()
    
    # Check if on Leave (takes priority)
    if LeaveRequest.objects.filter(...).exists():
        return False  # Not on WFH, on Leave instead
    
    # Check if on WFH
    return WFHRequest.objects.filter(...).exists()
```

**B. Update `can_check_in_from_location()` to use new status function**:
```python
status_info = get_employee_status_today(user)
if status_info['status'] == 'on_leave':
    return (False, "Employee is on approved Leave today")
elif status_info['status'] == 'on_wfh':
    return (True, "Approved WFH - Can work from anywhere")
```

### 4. Update Display Logic

**In Dashboard** - Show employee's actual status for today with priority:
- If on Leave: "On Leave (Casual Leave)"
- If on WFH (and not on Leave): "On WFH (Approved)"
- If on Onsite (and not on Leave/WFH): "On Onsite Visit"
- Otherwise: "Office"

**In HR Reports** - Column `Status` should show:
- "On Leave" (if approved Leave exists for that date)
- "On WFH" (if only approved WFH exists, no Leave)
- "On Onsite" (if only approved Onsite visit exists, no Leave/WFH)
- Regular status otherwise

**In Attendance History** - Similar display logic

### 5. Update Export/Report Functions

**CSV Exports** should:
- Check Leave first, then WFH, then Onsite
- Export actual status based on priority
- Column "Status" reflects correct priority

## Files to Modify

### Backend (views.py):
1. ✅ Add `get_employee_status_today(user)` function
2. ✅ Add `get_employee_status_for_date(user, date)` function
3. ✅ Update `has_approved_wfh_today(user)` to check Leave first
4. ✅ Update `can_check_in_from_location()` to use new status logic
5. ✅ Update dashboard context to show correct status
6. ✅ Update HR report generation to use new status

### Frontend (templates):
1. ✅ Update dashboard to display correct status
2. ✅ Update HR dashboard stats
3. ✅ Update employee details page
4. ✅ Update attendance history display

### Reports/APIs:
1. ✅ Update `export_attendance_csv()` to use correct status
2. ✅ Update `employee_attendance_dashboard()` to show correct status
3. ✅ Update bulk checkout API to skip Leave (which it already does correctly)

## Implementation Priority

**Phase 1 (Critical)**:
- Add status functions with priority logic
- Update `has_approved_wfh_today()` 
- Update `can_check_in_from_location()`

**Phase 2 (Important)**:
- Update dashboard display
- Update HR reports
- Update attendance history

**Phase 3 (Enhancement)**:
- Update exports
- Update APIs
- UI improvements

## Testing Checklist

### Scenario 1: WFH > Leave Conflict
- [ ] Create WFH from 01/07 to 20/07 (approved)
- [ ] Create Leave on 11/07 (approved)
- [ ] Check dashboard - should show "On Leave" for 11/07
- [ ] Check HR reports - should show "On Leave"
- [ ] Verify check-in restricted (on Leave, can't check-in)

### Scenario 2: WFH Only
- [ ] Create WFH from 01/07 to 20/07 (approved)
- [ ] No Leave
- [ ] Check dashboard - should show "On WFH"
- [ ] Verify check-in allowed from anywhere

### Scenario 3: Leave Only  
- [ ] Create Leave on 15/07 (approved)
- [ ] No WFH
- [ ] Check dashboard - should show "On Leave"
- [ ] Verify check-in restricted

### Scenario 4: Multiple Leaves  
- [ ] Create Leave 01/07-05/07 (approved)
- [ ] Create Leave 15/07-18/07 (approved)
- [ ] Create WFH 01/07-20/07 (approved)
- [ ] On 02/07 - should show "On Leave"
- [ ] On 10/07 - should show "On WFH"
- [ ] On 16/07 - should show "On Leave"

### Scenario 5: Onsite Priority
- [ ] Create WFH 01/07-20/07 (approved)
- [ ] Create Onsite on 11/07 (approved)
- [ ] On 11/07 - should show "On Onsite" or "On Leave"? (Clarify priority)

## Priority Order (To Confirm)

Current assumption: **Leave > Onsite > WFH > Office**

But we should verify:
- Does Onsite take priority over Leave? (Employee might need to go to onsite instead of leave)
- Or does Leave take priority? (Employee already approved leave, onsite shouldn't override)

**Recommendation**: Leave > WFH > Onsite > Office
(Employee's Leave is sacred - shouldn't be overridden by onsite visits)

## Success Criteria

1. ✅ No conflicts between Leave and WFH status display
2. ✅ Priority order is clear and consistent  
3. ✅ All reports show correct status
4. ✅ Check-in/check-out respects Leave priority
5. ✅ No ambiguous status messages
6. ✅ HR can clearly see actual employee status in reports
