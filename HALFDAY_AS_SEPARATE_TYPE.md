# Half Day Leave - Separate Leave Type Implementation

## Overview
Half Day Leave is now a **separate, independent leave type** with the following characteristics:
- Has its own entry in the Leave Type dropdown
- **Unlimited** - no annual limit
- **Tracked separately** - does not count against Sick/Casual/Earned leave balances
- Requires **flexible timing** selection (Morning, Afternoon, or Custom)
- Only applicable for **single-day leaves**

## Changes Made

### 1. Model Update (`attendance/models.py`)
Added 'halfday' as a new leave type:
```python
LEAVE_TYPES = [
    ('sick', 'Sick Leave'),
    ('casual', 'Casual Leave'),
    ('earned', 'Earned Leaves'),
    ('halfday', 'Half Day Leave'),  # NEW!
    ('menstrual', 'Menstrual Leave'),
    ('unpaid', 'Unpaid Leaves'),
]
```

### 2. Leave Request Form (`templates/leave_request.html`)
**Dropdown now includes:**
- Sick Leave
- Casual Leave
- Earned Leaves
- **Half Day Leave** ← NEW
- Menstrual Leave (if female)
- Unpaid Leaves

**Timing Fields:**
- Appear ONLY when "Half Day Leave" is selected AND single day is chosen
- **Required** when visible (employee must specify timing)
- Options:
  - Morning preset (9 AM - 1 PM)
  - Afternoon preset (2 PM - 6 PM)
  - Custom timing

### 3. Leave Balance Display

**In Leave Request Page:**
```
┌──────────────────────────────────────┐
│ Sick Leave:      4/6 used            │
│ Casual Leave:    2/6 used            │
│ Earned Leave:    5/6 used            │
│                                      │
│ ✅ Half Day Leave: 8 taken this year│
│    Unlimited - No effect on others   │
│                                      │
│ Menstrual Leave: 10/12 used          │
│ Unpaid Leave:    No limit            │
└──────────────────────────────────────┘
```

**In Employee Details Page (HR View):**
```
┌────────────────────────────────────────┐
│ Total Leaves: 11 days                  │
│ Half Days: [8]  Unpaid: [2 days]      │
│                                        │
│ ℹ️ Half Day leaves tracked separately  │
└────────────────────────────────────────┘
```

### 4. How It Works

#### Employee Flow:
1. Go to Leave Management
2. Select **"Half Day Leave"** from dropdown
3. Choose a **single date** (same start and end date)
4. **Timing fields appear automatically**
5. Select timing:
   - Click "Morning" button → Sets 9:00 AM - 1:00 PM
   - Click "Afternoon" button → Sets 2:00 PM - 6:00 PM
   - Or enter custom times manually
6. Enter reason and submit

#### Validation Rules:
- ✅ Half Day Leave can only be for a single day
- ✅ Start time must be before end time
- ✅ Timing fields are REQUIRED for half-day leaves
- ✅ If dates are different, timing fields hide and become optional

#### Approver View:
- Sees "Half Day Leave" as the type
- Sees timing badge: "9:00 AM - 1:00 PM"
- Can approve/reject like any other leave

## Key Differences from Other Leave Types

| Feature | Sick/Casual/Earned | Half Day Leave |
|---------|-------------------|----------------|
| Annual Limit | Yes (6 days each) | ❌ Unlimited |
| Counts Against Balance | Yes | ❌ No |
| Tracking | Part of main balance | Separate counter |
| Timing Required | No | ✅ Yes |
| Multi-day Allowed | Yes | ❌ Single day only |

## Business Logic

### Leave Balance Calculation:
```python
# For regular leaves (counted against limit)
sick_used = sum(total_days) for sick leaves
casual_used = sum(total_days) for casual leaves
earned_used = sum(total_days) for earned leaves

# For half-day (just count the number, no limit)
halfday_used = count() of half-day leaves  # Not total_days!

# Half-day does NOT reduce any leave balance
```

### Why Separate?
1. **Flexibility:** Employees can take half-days without worrying about leave balance
2. **Transparency:** HR can see exactly how many half-days were taken
3. **Fair Policy:** Doesn't penalize employees for minor absences
4. **Better Tracking:** Separate metric for attendance patterns

## Visual Indicators

### In Forms:
```
Leave Type: [Half Day Leave ▼]  ← Selected

Start Date: [2026-09-20]
End Date:   [2026-09-20]  ← Must be same

╔═══════════════════════════════╗
║ ⏰ Half-Day Timing (Required) ║  ← Auto-appears
║                               ║
║ Start Time: [09:00]           ║
║ End Time:   [13:00]           ║
║                               ║
║ [Morning] [Afternoon]         ║
╚═══════════════════════════════╝

Reason: [Doctor's appointment]

[Submit Request]
```

### In Approval Page:
```
┌─────────────────────────────────────┐
│ Leave Request                        │
├─────────────────────────────────────┤
│ Employee: John Doe                   │
│ Type: Half Day Leave 🕐             │  ← Distinct type
│ Date: Sep 20, 2026                   │
│ Timing: [9:00 AM - 1:00 PM] ⏰     │  ← Required info
│ Days: 1 day (0.5 effective)         │
│ Reason: Doctor's appointment         │
└─────────────────────────────────────┘
```

## Updated Documentation

### For Employees

**When to use Half Day Leave:**
- Medical appointments
- Personal errands
- Short family emergencies
- Bank visits
- Other brief absences

**Benefits:**
- ✅ Doesn't reduce your Sick/Casual/Earned leave balance
- ✅ Unlimited - use as many as needed
- ✅ Flexible timing - choose your hours
- ✅ Quick approval process

**How to Request:**
1. Select "Half Day Leave" from dropdown
2. Pick same date for start and end
3. Choose morning/afternoon/custom timing
4. Submit!

### For HR

**Half Day Leave Statistics:**
- Shown separately in employee details
- Not included in annual leave counts
- Tracked by count (number of half-days)
- Timing information always available

**Approval Considerations:**
- Verify timing makes sense for work requirements
- Check for patterns of excessive half-days
- Timing visible in all approval screens

## Testing Checklist

- [ ] "Half Day Leave" appears in dropdown
- [ ] Selecting it shows timing fields (single day only)
- [ ] Timing fields are REQUIRED when visible
- [ ] Morning preset sets 09:00 - 13:00
- [ ] Afternoon preset sets 14:00 - 18:00
- [ ] Custom timing can be entered
- [ ] Multi-day selection hides timing fields
- [ ] Leave balance shows half-day count separately
- [ ] Half-days NOT counted in Sick/Casual/Earned balances
- [ ] Approval page shows timing badge
- [ ] Employee details shows half-day count
- [ ] Cannot submit half-day without timing

## Database Note

No new migration needed - 'halfday' is just a new choice value in the existing `leave_type` field. The timing fields (half_day_start_time, half_day_end_time) already exist from previous migration.

## Summary

✅ **Half Day Leave is now:**
- A separate, distinct leave type
- Unlimited (no annual cap)
- Tracked independently
- Requires flexible timing
- Does not affect other leave balances

Perfect for short absences! 🎉
