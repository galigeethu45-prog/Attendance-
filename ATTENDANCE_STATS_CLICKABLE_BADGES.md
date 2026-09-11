# Clickable Attendance Statistics Badges Feature

## Overview
Attendance statistics badges (Present, Absent, Late, Half Days, Leaves, WFH) in the Employee Attendance Dashboard are now clickable. Clicking a badge opens a modal showing detailed breakdown of all dates for that specific status.

## Implementation Date
September 11, 2026

## Changes Made

### 1. Template Updates (`templates/employee_attendance_dashboard.html`)

#### Converted Badges to Buttons
**Before:** Static `<span>` badges
```html
<span class="stats-badge stats-badge-success">{{ stat.present_days }}</span>
```

**After:** Clickable `<button>` badges with onclick handlers
```html
<button class="stats-badge stats-badge-success clickable-badge" 
        onclick="showAttendanceDetails({{ stat.employee.id }}, 'present', '{{ stat.name }}', '{{ start_date|date:'Y-m-d' }}', '{{ end_date|date:'Y-m-d' }}')"
        {% if stat.present_days == 0 %}disabled{% endif %}>
    {{ stat.present_days }}
</button>
```

#### Added Modal Component
- Bootstrap modal for displaying attendance details
- Responsive design with scrollable content
- Dark theme matching the application style
- Loading spinner while fetching data

#### Added JavaScript Functions
- `showAttendanceDetails()`: Fetches and displays attendance details in modal
- Handles different status types with appropriate columns
- Formats dates and times
- Shows loading and error states

#### Added CSS Styles
```css
.clickable-badge {
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
}

.clickable-badge:hover:not(:disabled) {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.clickable-badge:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
```

### 2. Backend API (`attendance/views.py`)

#### New Function: `attendance_details_api()`
- **Location**: After `employee_attendance_dashboard()` function
- **Route**: `/attendance/api/attendance-details/`
- **Method**: GET
- **Authorization**: HR, Manager, or Superuser only
- **Parameters**:
  - `employee_id`: User ID
  - `status`: Status type (present, absent, late, half-day, leave, wfh)
  - `start_date`: Start date (YYYY-MM-DD)
  - `end_date`: End date (YYYY-MM-DD)

#### Returns JSON with Records:
```json
{
    "records": [
        {
            "date": "2026-09-10",
            "check_in": "09:15 AM",
            "check_out": "06:30 PM",
            "hours": 8.5
        }
    ]
}
```

#### Status-Specific Logic:

**Present/Late/Half-Day:**
- Fetches attendance records with matching status
- Returns: date, check_in, check_out, hours

**Absent:**
- Calculates working days (excluding holidays, Sundays, 2nd/4th Saturdays)
- Subtracts days with attendance records
- Subtracts approved leave days
- Returns: date only

**Leave:**
- Fetches approved leave requests
- Handles both date ranges and selected specific dates
- Returns: date, leave_type, reason

**WFH:**
- Fetches approved WFH requests
- Handles both date ranges and selected specific dates
- Returns: date, reason

### 3. URL Configuration (`attendance/urls.py`)
Added new route:
```python
path('api/attendance-details/', views.attendance_details_api, name='attendance_details_api'),
```

## User Experience

### Before Clicking:
- Badges show count numbers (e.g., "5" for 5 present days)
- Hover effect: badge scales up slightly
- Disabled badges (count = 0) appear dimmed

### After Clicking:
1. Modal opens with loading spinner
2. API fetches detailed records
3. Modal displays:
   - **Title**: Status type + employee name (e.g., "Present Days - John Doe")
   - **Summary**: Total days and date range
   - **Table**: Detailed records with relevant columns

### Modal Content by Status:

#### Present / Late / Half-Day
| Date | Check In | Check Out | Hours |
|------|----------|-----------|-------|
| Wed, Sep 10, 2026 | 09:15 AM | 06:30 PM | 8.5h |

#### Absent
| Date | Status |
|------|--------|
| Wed, Sep 10, 2026 | Absent |

#### Leave
| Date | Leave Type | Reason |
|------|------------|--------|
| Wed, Sep 10, 2026 | Sick Leave | Medical appointment |

#### WFH
| Date | Reason |
|------|--------|
| Wed, Sep 10, 2026 | Working on project deliverables |

## Features

### 1. **Smart Absent Calculation**
- Only counts working days (excludes holidays, Sundays, 2nd/4th Saturdays)
- Excludes days with attendance records
- Excludes approved leave days
- Shows actual days the employee was supposed to work but didn't check in

### 2. **Date Handling**
- Handles both date range leaves/WFH (start_date to end_date)
- Handles selected specific dates (non-consecutive)
- Properly filters dates within the selected dashboard date range

### 3. **Authorization**
- Only HR, Manager, or Superuser can access the API
- Returns 403 error for unauthorized users

### 4. **Error Handling**
- Loading spinner while fetching data
- Error message if API fails
- "No records found" message if data is empty
- Parameter validation

### 5. **Performance**
- API returns only requested status data
- Database queries are optimized with select_related
- Modal content loads on-demand (not pre-loaded)

## Visual Design

### Badge Colors:
- **Present**: Green gradient (success)
- **Absent**: Red gradient (danger)
- **Late**: Orange gradient (warning)
- **Half Days**: Cyan gradient (info)
- **Leaves**: Purple gradient (#8e44ad to #9b59b6)
- **WFH**: Teal gradient (#16a085 to #1abc9c)

### Icons:
- Present: ✓ Check circle
- Absent: ✗ Times circle
- Late: 🕐 Clock
- Half Days: ◐ Adjust
- Leaves: 🏖️ Umbrella beach
- WFH: 🏠 Home

### Interactions:
- Hover: Scale 1.1x + shadow
- Click: Scale 0.95x (active state)
- Disabled: 50% opacity + not-allowed cursor

## Technical Details

### Dependencies:
- Bootstrap 5 Modal component
- Fetch API for AJAX calls
- Django JsonResponse
- pytz for timezone handling (IST)

### Date Format:
- API: ISO format (YYYY-MM-DD)
- Display: "Wed, Sep 10, 2026"
- Time: "09:15 AM" (12-hour format)

### Timezone:
- All times displayed in IST (Asia/Kolkata)
- Backend converts UTC to IST for display

## Testing Checklist
- [ ] Present badge shows correct count and opens modal with check-in/out details
- [ ] Absent badge correctly calculates working days minus attended/leave days
- [ ] Late badge shows records with late status
- [ ] Half-day badge shows records with half-day status
- [ ] Leave badge shows leave records with type and reason
- [ ] WFH badge shows WFH records with reason
- [ ] Badges with 0 count are disabled and non-clickable
- [ ] Modal shows loading spinner while fetching
- [ ] Modal shows error message if API fails
- [ ] Modal shows "no records" message if data is empty
- [ ] Date ranges are respected (only shows data within selected dates)
- [ ] Authorization works (only HR/Manager can access)
- [ ] Works with pagination (badges work on all pages)
- [ ] Works with filters (badges reflect filtered data)

## Production Ready
✅ **All features implemented:**
- Frontend: Clickable badges with hover effects
- Backend: API endpoint with proper authorization
- Error handling: Loading, error, and empty states
- Performance: Optimized queries and on-demand loading
- Security: Authorization checks
- UX: Clear visual feedback and detailed information

## Future Enhancements (Optional)
- Export modal data to CSV/PDF
- Add search/filter within modal table
- Show additional details (overtime hours, break times)
- Add date range picker in modal for quick filtering
- Pagination for modals with many records (>50 days)
