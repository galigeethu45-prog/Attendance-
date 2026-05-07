# Phase 3: Major Features - IN PROGRESS

## Completed So Far ✅

### Database Models Updated

#### 1. Multi-Date Selection for Leave/WFH ✅
**Files Modified:**
- `attendance/models.py` - LeaveRequest model
- `attendance/models.py` - WFHRequest model

**Changes:**
- Added `selected_dates` JSONField to store non-consecutive dates
- Added `get_dates_list()` method to return all dates (selected or range)
- Updated `total_days` property to handle both modes
- Backward compatible with existing date range functionality

**Usage:**
- Date Range: Use `start_date` and `end_date` (existing behavior)
- Specific Dates: Use `selected_dates` JSON array: `["2026-05-21", "2026-05-25", "2026-05-30"]`

#### 2. Manager Role + Hierarchical Approval ✅
**Files Modified:**
- `attendance/models.py` - EmployeeProfile model
- `attendance/models.py` - LeaveRequest model
- `attendance/models.py` - WFHRequest model

**Changes:**
- Added 'manager' to ROLE_CHOICES in EmployeeProfile
- Added hierarchical approval fields to LeaveRequest:
  - `tl_comment`, `tl_approved`, `tl_approver`, `tl_approved_at`
  - `manager_comment`, `manager_approved`, `manager_approver`, `manager_approved_at`
- Added same fields to WFHRequest

**Approval Hierarchy:**
1. Team Leader → Comments (visible to Manager & HR)
2. Manager → Approves/Rejects (goes to HR for final decision)
3. HR → Final approval authority

#### 3. Onsite/Client Visit Feature ✅
**Files Created/Modified:**
- `attendance/models.py` - New OnsiteRequest model
- `attendance/admin.py` - OnsiteRequest admin registration

**New Model: OnsiteRequest**
- Visit types: Onsite (physical) or Online Meeting (from office)
- Fields: visit_date, client_name, location, purpose, expected_duration
- Hierarchical approval (Manager → HR)
- Actual check-in/check-out tracking
- Enables flexible break times during client meetings

#### 4. Migration Created ✅
**File:** `attendance/migrations/0021_add_multidate_manager_onsite.py`

**Includes:**
- Manager role addition
- Multi-date fields for Leave/WFH
- Hierarchical approval fields
- OnsiteRequest model creation
- Database indexes for performance

---

## Next Steps (To Complete Phase 3)

### 1. Update Views & Logic
- [ ] Modify leave_request view to handle multi-date selection
- [ ] Modify wfh_request view to handle multi-date selection
- [ ] Create hierarchical approval views (TL, Manager, HR)
- [ ] Create onsite request views (request, approval, tracking)
- [ ] Update break validation to allow flexible times for onsite visits
- [ ] Create employee attendance dashboard for HR

### 2. Update Templates
- [ ] Add multi-date picker to leave request form (calendar + manual entry)
- [ ] Add multi-date picker to WFH request form
- [ ] Create approval workflow UI showing TL → Manager → HR chain
- [ ] Create onsite request form
- [ ] Create onsite approval page
- [ ] Create employee attendance dashboard template
- [ ] Update break buttons to check for active onsite requests

### 3. Update Middleware/Helpers
- [ ] Modify `can_check_in_from_location()` to check for approved onsite requests
- [ ] Modify break time validation to allow flexible breaks for onsite/online meetings
- [ ] Add helper functions for hierarchical approval logic

### 4. Testing
- [ ] Test multi-date selection (calendar + manual)
- [ ] Test hierarchical approval workflow
- [ ] Test onsite request creation and approval
- [ ] Test flexible break times during client meetings
- [ ] Test employee attendance dashboard

---

## Database Migration Instructions

**IMPORTANT:** Run this migration on your server:

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Run migration
python manage.py migrate attendance

# Verify migration
python manage.py showmigrations attendance
```

**Expected Output:**
```
[X] 0020_systemsettings
[X] 0021_add_multidate_manager_onsite
```

---

## Features Summary

| Feature | Status | Database | Views | Templates |
|---------|--------|----------|-------|-----------|
| Multi-date Leave/WFH | ✅ Models | ⏳ Pending | ⏳ Pending |
| Manager Role | ✅ Models | ⏳ Pending | ⏳ Pending |
| Hierarchical Approval | ✅ Models | ⏳ Pending | ⏳ Pending |
| Onsite Requests | ✅ Models | ⏳ Pending | ⏳ Pending |
| Flexible Breaks | ⏳ Pending | ⏳ Pending | ⏳ Pending |
| Attendance Dashboard | ⏳ Pending | ⏳ Pending | ⏳ Pending |

---

**Status: Database models complete, views and templates in progress**
