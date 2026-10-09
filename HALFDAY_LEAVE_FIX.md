# Half-Day Leave "Invalid leave type" Error Fix

## Issue
When submitting a half-day leave request, the system showed error: **"Invalid leave type"**

## Root Cause
In `attendance/views.py` → `leave_request()` function:
- Line 1257: The validation only allowed: `['sick', 'casual', 'earned', 'menstrual', 'unpaid']`
- **'halfday' was missing** from the valid types list
- This caused all half-day leave submissions to be rejected

## Fix Applied

### 1. Added 'halfday' to Valid Types
**Before:**
```python
valid_types = ['sick', 'casual', 'earned', 'menstrual', 'unpaid']
```

**After:**
```python
valid_types = ['sick', 'casual', 'earned', 'menstrual', 'unpaid', 'halfday']
```

### 2. Made Timing Fields Required for Half-Day Type
Enhanced validation to require start_time and end_time for halfday leaves:

```python
# For halfday leave type, timing fields are REQUIRED
if leave_type == 'halfday':
    if not half_day_start_time or not half_day_end_time:
        messages.error(request, 'Half-day leave requires start time and end time.')
        return redirect('leave_request')
```

## Testing
1. Go to Leave Management
2. Select "Half Day Leave" from dropdown
3. Choose same start and end date (single day)
4. Select timing (e.g., Morning 09:00 - 13:00)
5. Enter reason
6. Submit

**Expected Result:** ✅ Leave request submitted successfully!

## Files Modified
- `attendance/views.py` (leave_request function, lines 1257 and 1343-1380)

## Date: September 23, 2026
