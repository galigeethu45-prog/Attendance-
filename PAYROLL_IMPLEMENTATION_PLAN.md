# Payroll System - Implementation Plan

## Overview
Complete implementation of the Payroll Integration System based on SmartPunch 2.0 SRS specifications.

## Timeline: 3-4 weeks

---

## Phase 1: Database & Models (Week 1)

### Task 1.1: Create Payroll Models
**Files**: `attendance/models.py`

**Models to Create**:
1. **PayrollCycle** - Monthly payroll processing cycles
2. **PayrollEntry** - Individual employee salary calculations
3. **LeaveBalance** - Annual leave tracking per employee

**EmployeeProfile Extensions**:
- Add salary fields (base_salary, ot_rate)
- Add bank details (account_number, ifsc_code, bank_name)
- Add statutory fields (pan_number, pf_number, uan_number, esi_number)

### Task 1.2: Create Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Task 1.3: Admin Interface
Register models in `attendance/admin.py` for testing

---

## Phase 2: Payroll Calculation Engine (Week 1-2)

### Task 2.1: Salary Calculation Service
**File**: `attendance/payroll_calculator.py`

**Functions to Implement**:
```python
class PayrollCalculator:
    def calculate_working_days(start_date, end_date)
    def calculate_per_day_salary(base_salary, working_days)
    def get_attendance_summary(employee, start_date, end_date)
    def calculate_leave_deductions(employee, year)
    def calculate_ot_earnings(employee, start_date, end_date)
    def calculate_deductions(attendance_summary, per_day_salary)
    def calculate_net_salary(employee, month, year)
    def process_employee_payroll(employee, cycle)
```

**Calculation Logic**:
```
Working Days = Total days - Weekends - Holidays
Per Day Salary = Base Salary / Working Days

Deductions:
- Half Day = (Per Day / 2) × Half Days Count
- Absent = Per Day × Absent Days Count
- Unpaid Leave = Per Day × Unpaid Leaves

OT Earnings:
- OT Amount = OT Hours × OT Rate (approved only)

Net Salary = Base - Deductions + OT
```

### Task 2.2: Leave Policy Implementation
**Logic**:
- 18 paid leaves per year (6 sick + 6 casual + 6 earned)
- First 18 leaves = No deduction
- Beyond 18 leaves = Deduct per day salary

### Task 2.3: Mid-Month Joiner/Exit Proration
**Logic**:
- Calculate working days from join date to month end
- Prorate salary = (Base / Month Days) × Working Days

---

## Phase 3: Backend APIs (Week 2)

### Task 3.1: Create Payroll Views
**File**: `attendance/payroll_views.py`

**Views to Create**:
```python
# Payroll Processing
@hr_required
def process_payroll(request)  # POST - Process monthly payroll

@hr_required
def payroll_cycles_list(request)  # GET - List all cycles

@hr_required
def payroll_cycle_detail(request, cycle_id)  # GET - Cycle details

@hr_required
def finalize_payroll(request, cycle_id)  # PUT - Finalize

@hr_required
def export_payroll_csv(request, cycle_id)  # GET - Export

# Payroll Entries
@hr_required
def payroll_entries_list(request, cycle_id)  # GET - All entries

@hr_required
def payroll_entry_detail(request, entry_id)  # GET - Entry details

@hr_required
def adjust_payroll_entry(request, entry_id)  # PUT - Manual adjustment

@hr_required
def payroll_breakdown(request, entry_id)  # GET - Detailed breakdown

# Leave Balance
@hr_required
def leave_balance_view(request, employee_id, year)  # GET

@hr_required
def update_leave_balance(request, balance_id)  # PUT
```

### Task 3.2: URL Configuration
**File**: `attendance/urls.py`

Add payroll URL patterns

### Task 3.3: Permissions & Security
- Restrict all payroll APIs to HR/Admin only
- Add audit logging for all payroll operations

---

## Phase 4: Frontend UI (Week 2-3)

### Task 4.1: Payroll Dashboard
**File**: `templates/payroll_dashboard.html`

**Features**:
- List of all payroll cycles
- Status indicators (Draft/Finalized/Paid)
- "Process New Payroll" button
- Quick stats (Total employees, Total amount, etc.)

### Task 4.2: Process Payroll Page
**File**: `templates/process_payroll.html`

**Features**:
- Month/Year selector
- Date range selector
- "Calculate Salaries" button
- Progress indicator
- Summary after calculation

### Task 4.3: Review Payroll Page
**File**: `templates/review_payroll.html`

**Features**:
- Employee list with calculated salaries
- Columns: Name, Base, Working Days, Present, Absent, Deductions, OT, Net
- Color-coded anomalies
- Search & filter
- Click to view breakdown
- Manual adjustment form
- Finalize button

### Task 4.4: Payroll Entry Breakdown Modal
**Component**: Modal popup showing:
- Attendance details (present, absent, half, late days)
- Leave details (paid/unpaid)
- OT details (hours, rate, amount)
- Deduction breakdown
- Final calculation

### Task 4.5: Export & Reports
**Features**:
- CSV export button
- Bank transfer format (Employee ID, Name, Account, IFSC, Amount)
- Payslip generation (PDF - future)

---

## Phase 5: Employee Salary Management (Week 3)

### Task 5.1: Salary Configuration Page
**File**: `templates/employee_salary_config.html`

**Features**:
- Search employee
- View current salary details
- Edit base salary
- Edit OT rate
- Update bank details
- Update statutory numbers (PAN, PF, etc.)
- Audit trail of changes

### Task 5.2: Leave Balance Management
**File**: `templates/leave_balance_management.html`

**Features**:
- View all employees' leave balances
- Year-wise view
- Update allocations
- Adjust usage
- Carry forward logic (future)

---

## Phase 6: Testing & Validation (Week 3-4)

### Task 6.1: Unit Tests
**File**: `attendance/tests/test_payroll.py`

**Test Cases**:
- Test salary calculation logic
- Test leave deduction logic
- Test OT calculation
- Test proration for mid-month joiners
- Test manual adjustments
- Test finalization workflow

### Task 6.2: Integration Tests
- Test full payroll processing flow
- Test CSV export format
- Test audit logging
- Test permissions

### Task 6.3: UAT (User Acceptance Testing)
- HR team tests with sample data
- Verify calculations manually
- Test edge cases (0 days worked, all leaves, etc.)

---

## Phase 7: HR Dashboard Integration (Week 4)

### Task 7.1: Add Payroll Cards to HR Dashboard
**File**: `templates/hr_dashboard.html`

**New Cards**:
- "Process Payroll" card
- "Pending Payroll Reviews" count
- "Last Payroll Processed" info
- Quick link to payroll dashboard

### Task 7.2: Navigation Menu Updates
**File**: `templates/base.html`

Add payroll menu items for HR users

---

## Database Schema Summary

### PayrollCycle
```python
- id (PK)
- month (1-12)
- year (2024, 2025, etc.)
- start_date
- end_date
- status (draft/finalized/paid)
- total_employees
- total_gross_amount
- total_deductions
- total_net_amount
- processed_by (FK User)
- processed_at
- finalized_at
- notes
```

### PayrollEntry
```python
- id (PK)
- payroll_cycle (FK)
- employee (FK User)
- base_salary
- working_days
- present_days
- absent_days
- half_days
- late_days
- paid_leaves_taken
- unpaid_leaves_taken
- wfh_days
- ot_hours
- ot_rate
- ot_amount
- half_day_deduction
- absent_deduction
- unpaid_leave_deduction
- other_deductions
- total_deductions
- gross_salary
- tds_deduction (future)
- pf_deduction (future)
- esi_deduction (future)
- manual_adjustment
- adjustment_reason
- adjusted_by (FK User)
- adjusted_at
- net_salary
- payment_status
- payment_date
- payment_reference
```

### LeaveBalance
```python
- id (PK)
- employee (FK User)
- year
- sick_leaves_total (default: 6)
- casual_leaves_total (default: 6)
- earned_leaves_total (default: 6)
- sick_leaves_used
- casual_leaves_used
- earned_leaves_used
- total_leaves_allocated (18)
- total_leaves_used
- total_leaves_remaining
```

### EmployeeProfile Extensions
```python
- base_salary (Decimal)
- ot_rate (Decimal, default: 300)
- bank_account_number
- bank_ifsc_code
- bank_name
- pan_number
- pf_number
- uan_number
- esi_number
```

---

## Key Success Criteria

✅ 100% automated salary calculation  
✅ Process 100 employees in < 60 seconds  
✅ Zero calculation errors  
✅ Audit trail for all operations  
✅ HR-only access (no employee visibility)  
✅ CSV export for bank transfer  
✅ Manual adjustment capability  
✅ Leave policy enforcement (18 paid leaves)  

---

## Implementation Priority

### High Priority (MVP):
1. ✅ Database models & migrations
2. ✅ Salary calculation engine
3. ✅ Process payroll API
4. ✅ Review & finalize workflow
5. ✅ CSV export
6. ✅ Basic UI for processing

### Medium Priority:
7. ✅ Manual adjustments
8. ✅ Leave balance tracking
9. ✅ Salary configuration page
10. ✅ Detailed reports

### Low Priority (Future):
11. ⏳ PDF payslip generation
12. ⏳ TDS/PF/ESI deductions
13. ⏳ Form 16 generation
14. ⏳ Salary revision history
15. ⏳ Loan/advance deductions

---

## Next Steps

Ready to start implementation? Let's begin with:

1. **Create database models** (PayrollCycle, PayrollEntry, LeaveBalance)
2. **Extend EmployeeProfile** with salary fields
3. **Create migrations**
4. **Build salary calculation engine**

Shall we proceed with Step 1?

