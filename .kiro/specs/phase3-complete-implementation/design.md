# Phase 3 Complete Implementation - Technical Design

## Overview

This design document provides practical implementation details for Phase 3 features. The database models are already in place (migration 0021), so this focuses on views, templates, and JavaScript integration.

**Core Features:**
1. Multi-date selection for Leave/WFH requests
2. Hierarchical approval workflow (TL → Manager → HR)
3. Onsite/client visit requests with flexible breaks
4. Employee attendance dashboard for HR
5. Manager role with HR-level access

**Technology Stack:**
- Backend: Django views (attendance/views.py)
- Frontend: Bootstrap 5 + Flatpickr.js for date picking
- Database: SQLite (models already migrated)
- Timezone: Asia/Kolkata (IST)

## Architecture

### Component Structure

```
attendance/
├── views.py (add new views)
├── urls.py (add new routes)
├── models.py (already complete)
└── migrations/0021_*.py (already applied)

templates/
├── leave_request.html (update)
├── wfh_request.html (update)
├── onsite_request.html (new)
├── onsite_approval.html (new)
├── hr_dashboard.html (update)
└── employee_attendance_dashboard.html (new)

static/
├── js/
│   ├── flatpickr.min.js (add if not present)
│   └── multi-date-picker.js (new)
└── css/
    └── flatpickr.min.css (add if not present)
```

### Request Flow

**Leave/WFH Request Flow:**
```
Employee submits → TL comments → Manager approves/rejects → HR final decision
```

**Onsite Request Flow:**
```
Employee submits → Manager approves/rejects → HR final decision
```

## Components and Interfaces

### 1. Multi-Date Selection Component

**Implementation Approach:**
- Use Flatpickr.js with `mode: "multiple"` for calendar selection
- Add hidden textarea for manual comma-separated entry
- Sync both inputs via JavaScript

**HTML Structure (for leave_request.html and wfh_request.html):**
```html
<!-- Date Selection Mode Toggle -->
<div class="mb-3">
    <label class="form-label">Selection Mode</label>
    <select id="dateSelectionMode" class="form-select">
        <option value="range">Date Range (Consecutive Days)</option>
        <option value="specific">Specific Dates (Non-consecutive)</option>
    </select>
</div>

<!-- Date Range Fields (existing) -->
<div id="dateRangeFields">
    <div class="mb-3">
        <label for="start_date" class="form-label">Start Date</label>
        <input type="date" class="form-control" id="start_date" name="start_date">
    </div>
    <div class="mb-3">
        <label for="end_date" class="form-label">End Date</label>
        <input type="date" class="form-control" id="end_date" name="end_date">
    </div>
</div>

<!-- Specific Dates Fields (new) -->
<div id="specificDatesFields" style="display: none;">
    <div class="mb-3">
        <label for="calendar_picker" class="form-label">Select Dates (Calendar)</label>
        <input type="text" id="calendar_picker" class="form-control" placeholder="Click to select dates">
    </div>
    <div class="mb-3">
        <label for="manual_dates" class="form-label">Or Enter Manually (comma-separated)</label>
        <textarea id="manual_dates" class="form-control" rows="2" 
                  placeholder="2026-05-21, 2026-05-25, 2026-05-30"></textarea>
        <small class="text-muted">Format: YYYY-MM-DD, YYYY-MM-DD</small>
    </div>
    <input type="hidden" id="selected_dates" name="selected_dates">
</div>
```

**JavaScript (multi-date-picker.js):**
```javascript
// Initialize Flatpickr
const picker = flatpickr("#calendar_picker", {
    mode: "multiple",
    dateFormat: "Y-m-d",
    minDate: "today",
    onChange: function(selectedDates, dateStr) {
        // Sync to hidden field
        const dates = selectedDates.map(d => formatDate(d));
        document.getElementById('selected_dates').value = JSON.stringify(dates);
        // Sync to manual textarea
        document.getElementById('manual_dates').value = dates.join(', ');
    }
});

// Manual entry sync
document.getElementById('manual_dates').addEventListener('blur', function() {
    const manualDates = this.value.split(',').map(d => d.trim()).filter(d => d);
    document.getElementById('selected_dates').value = JSON.stringify(manualDates);
    // Update calendar picker
    picker.setDate(manualDates);
});

// Mode toggle
document.getElementById('dateSelectionMode').addEventListener('change', function() {
    if (this.value === 'specific') {
        document.getElementById('dateRangeFields').style.display = 'none';
        document.getElementById('specificDatesFields').style.display = 'block';
        // Clear range fields
        document.getElementById('start_date').value = '';
        document.getElementById('end_date').value = '';
    } else {
        document.getElementById('dateRangeFields').style.display = 'block';
        document.getElementById('specificDatesFields').style.display = 'none';
        // Clear specific dates
        document.getElementById('selected_dates').value = '';
    }
});
```

### 2. Hierarchical Approval Views

**View Structure:**

```python
# attendance/views.py

@login_required
def leave_approval(request):
    """
    Hierarchical approval view - shows different requests based on role
    """
    user_profile = request.user.employeeprofile
    
    if user_profile.role == 'team_leader':
        # TL sees all pending requests (no comments yet)
        pending_requests = LeaveRequest.objects.filter(
            status='pending',
            tl_comment__isnull=True
        ).order_by('-created_at')
        
    elif user_profile.role == 'manager':
        # Manager sees requests with TL comments
        pending_requests = LeaveRequest.objects.filter(
            status='pending',
            tl_comment__isnull=False,
            manager_approved=False
        ).order_by('-created_at')
        
    elif user_profile.is_hr:
        # HR sees manager-approved requests
        pending_requests = LeaveRequest.objects.filter(
            status='pending',
            manager_approved=True
        ).order_by('-created_at')
    else:
        pending_requests = []
    
    return render(request, 'leave_approval.html', {
        'pending_requests': pending_requests,
        'user_role': user_profile.role
    })

@login_required
def leave_action(request, leave_id, action):
    """
    Handle TL comment, Manager approval/rejection, HR final decision
    """
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    user_profile = request.user.employeeprofile
    comment = request.POST.get('comment', '')
    
    if user_profile.role == 'team_leader':
        # TL adds comment
        leave_request.tl_comment = comment
        leave_request.tl_approver = request.user
        leave_request.tl_approved_at = timezone.now()
        leave_request.save()
        
        # Notify manager
        managers = User.objects.filter(employeeprofile__role='manager')
        for manager in managers:
            Notification.objects.create(
                employee=manager,
                message=f"Leave request from {leave_request.employee.get_full_name()} has TL comments"
            )
        
        log_action(request.user, 'leave_comment', f'TL commented on leave request', request)
        messages.success(request, 'Comment added successfully')
        
    elif user_profile.role == 'manager':
        if action == 'approve':
            leave_request.manager_approved = True
            leave_request.manager_comment = comment
            leave_request.manager_approver = request.user
            leave_request.manager_approved_at = timezone.now()
            leave_request.save()
            
            # Notify HR
            hr_users = User.objects.filter(employeeprofile__is_hr=True)
            for hr in hr_users:
                Notification.objects.create(
                    employee=hr,
                    message=f"Leave request from {leave_request.employee.get_full_name()} approved by manager"
                )
            
            log_action(request.user, 'leave_approve', f'Manager approved leave request', request)
            messages.success(request, 'Leave request approved and sent to HR')
            
        elif action == 'reject':
            leave_request.status = 'rejected'
            leave_request.manager_comment = comment
            leave_request.manager_approver = request.user
            leave_request.save()
            
            # Notify employee
            Notification.objects.create(
                employee=leave_request.employee,
                message=f"Your leave request has been rejected by manager"
            )
            
            log_action(request.user, 'leave_reject', f'Manager rejected leave request', request)
            messages.success(request, 'Leave request rejected')
            
    elif user_profile.is_hr:
        if action == 'approve':
            leave_request.status = 'approved'
            leave_request.hr_comment = comment
            leave_request.save()
            
            # Notify employee
            Notification.objects.create(
                employee=leave_request.employee,
                message=f"Your leave request has been approved by HR"
            )
            
            log_action(request.user, 'leave_approve', f'HR approved leave request', request)
            messages.success(request, 'Leave request approved')
            
        elif action == 'reject':
            leave_request.status = 'rejected'
            leave_request.hr_comment = comment
            leave_request.save()
            
            # Notify employee and manager
            Notification.objects.create(
                employee=leave_request.employee,
                message=f"Your leave request has been rejected by HR"
            )
            if leave_request.manager_approver:
                Notification.objects.create(
                    employee=leave_request.manager_approver,
                    message=f"Leave request you approved was rejected by HR"
                )
            
            log_action(request.user, 'leave_reject', f'HR rejected leave request', request)
            messages.success(request, 'Leave request rejected')
    
    return redirect('leave_approval')
```

**Template Structure (leave_approval.html):**
```html
<div class="card glass-card">
    <div class="card-header">
        <h5>
            {% if user_role == 'team_leader' %}
                Pending Leave Requests (Add Comments)
            {% elif user_role == 'manager' %}
                Leave Requests with TL Comments (Approve/Reject)
            {% else %}
                Manager-Approved Leave Requests (Final Decision)
            {% endif %}
        </h5>
    </div>
    <div class="card-body">
        <table class="table">
            <thead>
                <tr>
                    <th>Employee</th>
                    <th>Type</th>
                    <th>Dates</th>
                    <th>Reason</th>
                    {% if user_role != 'team_leader' %}
                    <th>TL Comment</th>
                    {% endif %}
                    {% if user_role == 'hr' %}
                    <th>Manager Decision</th>
                    {% endif %}
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for leave in pending_requests %}
                <tr>
                    <td>{{ leave.employee.get_full_name }}</td>
                    <td>{{ leave.get_leave_type_display }}</td>
                    <td>
                        {% if leave.selected_dates %}
                            {{ leave.selected_dates|length }} days (specific dates)
                        {% else %}
                            {{ leave.start_date }} to {{ leave.end_date }}
                        {% endif %}
                    </td>
                    <td>{{ leave.reason|truncatewords:10 }}</td>
                    {% if user_role != 'team_leader' %}
                    <td>{{ leave.tl_comment|default:"No comment" }}</td>
                    {% endif %}
                    {% if user_role == 'hr' %}
                    <td>
                        <span class="badge bg-success">Approved by {{ leave.manager_approver.get_full_name }}</span>
                        <br><small>{{ leave.manager_comment }}</small>
                    </td>
                    {% endif %}
                    <td>
                        <button class="btn btn-sm btn-primary" 
                                onclick="showActionModal({{ leave.id }}, '{{ user_role }}')">
                            {% if user_role == 'team_leader' %}
                                Add Comment
                            {% else %}
                                Approve/Reject
                            {% endif %}
                        </button>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- Action Modal -->
<div class="modal fade" id="actionModal">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Leave Request Action</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form method="post" id="actionForm">
                {% csrf_token %}
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Comment</label>
                        <textarea name="comment" class="form-control" rows="3" required></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    {% if user_role == 'team_leader' %}
                        <button type="submit" class="btn btn-primary">Submit Comment</button>
                    {% else %}
                        <button type="submit" name="action" value="reject" class="btn btn-danger">Reject</button>
                        <button type="submit" name="action" value="approve" class="btn btn-success">Approve</button>
                    {% endif %}
                </div>
            </form>
        </div>
    </div>
</div>
```

### 3. Onsite Request Feature

**Views:**

```python
@login_required
def onsite_request(request):
    """Employee submits onsite/client visit request"""
    if request.method == 'POST':
        visit_type = request.POST.get('visit_type')
        visit_date = request.POST.get('visit_date')
        client_name = request.POST.get('client_name')
        location = request.POST.get('location')
        purpose = request.POST.get('purpose')
        expected_duration = request.POST.get('expected_duration')
        
        # Validate future date
        from datetime import datetime
        visit_date_obj = datetime.strptime(visit_date, '%Y-%m-%d').date()
        if visit_date_obj < timezone.now().date():
            messages.error(request, 'Visit date must be in the future')
            return redirect('onsite_request')
        
        # Create request
        onsite_req = OnsiteRequest.objects.create(
            employee=request.user,
            visit_type=visit_type,
            visit_date=visit_date_obj,
            client_name=client_name,
            location=location,
            purpose=purpose,
            expected_duration=expected_duration,
            status='pending'
        )
        
        # Notify manager
        managers = User.objects.filter(employeeprofile__role='manager')
        for manager in managers:
            Notification.objects.create(
                employee=manager,
                message=f"Onsite request from {request.user.get_full_name()} for {visit_date}"
            )
        
        log_action(request.user, 'onsite_request', f'Requested onsite visit for {visit_date}', request)
        messages.success(request, 'Onsite request submitted successfully')
        return redirect('onsite_request')
    
    # Get user's requests
    my_requests = OnsiteRequest.objects.filter(employee=request.user).order_by('-visit_date')
    
    return render(request, 'onsite_request.html', {
        'my_requests': my_requests
    })

@login_required
def onsite_approval(request):
    """Manager and HR approve onsite requests"""
    user_profile = request.user.employeeprofile
    
    if user_profile.role == 'manager':
        # Manager sees pending requests
        pending_requests = OnsiteRequest.objects.filter(
            status='pending',
            manager_approved=False
        ).order_by('-visit_date')
        
    elif user_profile.is_hr:
        # HR sees manager-approved requests
        pending_requests = OnsiteRequest.objects.filter(
            status='pending',
            manager_approved=True
        ).order_by('-visit_date')
    else:
        pending_requests = []
    
    return render(request, 'onsite_approval.html', {
        'pending_requests': pending_requests,
        'user_role': user_profile.role
    })

@login_required
def onsite_check_in(request, request_id):
    """Employee checks in for onsite visit"""
    onsite_req = get_object_or_404(OnsiteRequest, id=request_id, employee=request.user)
    
    if onsite_req.status != 'approved':
        messages.error(request, 'Only approved onsite requests can be checked in')
        return redirect('dashboard')
    
    if onsite_req.actual_check_in:
        messages.info(request, 'Already checked in for this onsite visit')
        return redirect('dashboard')
    
    onsite_req.actual_check_in = timezone.now()
    onsite_req.save()
    
    log_action(request.user, 'onsite_checkin', f'Checked in for onsite visit to {onsite_req.client_name}', request)
    messages.success(request, f'Checked in for onsite visit to {onsite_req.client_name}')
    
    return redirect('dashboard')

@login_required
def onsite_check_out(request, request_id):
    """Employee checks out from onsite visit"""
    onsite_req = get_object_or_404(OnsiteRequest, id=request_id, employee=request.user)
    
    if not onsite_req.actual_check_in:
        messages.error(request, 'Must check in before checking out')
        return redirect('dashboard')
    
    if onsite_req.actual_check_out:
        messages.info(request, 'Already checked out from this onsite visit')
        return redirect('dashboard')
    
    onsite_req.actual_check_out = timezone.now()
    onsite_req.save()
    
    # Calculate duration
    duration = onsite_req.actual_check_out - onsite_req.actual_check_in
    hours = duration.total_seconds() / 3600
    
    log_action(request.user, 'onsite_checkout', f'Checked out from onsite visit - Duration: {hours:.2f}h', request)
    messages.success(request, f'Checked out from onsite visit. Duration: {hours:.2f} hours')
    
    return redirect('dashboard')
```

### 4. Flexible Break Logic

**Modify start_break() in views.py:**

```python
@login_required
def start_break(request, break_type):
    if request.method == 'POST':
        # ... existing validation code ...
        
        # Check for active approved onsite request
        today = timezone.now().date()
        active_onsite = OnsiteRequest.objects.filter(
            employee=request.user,
            visit_date=today,
            status='approved'
        ).first()
        
        # If onsite request exists, bypass time window validation
        if active_onsite:
            # Still enforce 5 PM cutoff
            import pytz
            local_tz = pytz.timezone('Asia/Kolkata')
            current_time = timezone.now().astimezone(local_tz).time()
            if current_time.hour >= 17:
                messages.error(request, 'Breaks are not allowed after 5:00 PM.')
                return redirect('dashboard')
            
            # Check count limits only
            if break_type == 'tea':
                tea_count = BreakLog.objects.filter(
                    attendance=attendance,
                    break_type='tea'
                ).count()
                if tea_count >= 2:
                    messages.error(request, 'You have already taken 2 tea breaks today.')
                    return redirect('dashboard')
            elif break_type == 'lunch':
                lunch_count = BreakLog.objects.filter(
                    attendance=attendance,
                    break_type='lunch'
                ).count()
                if lunch_count >= 1:
                    messages.error(request, 'You have already taken your lunch break today.')
                    return redirect('dashboard')
            
            # Create break with flexible time
            BreakLog.objects.create(
                attendance=attendance,
                break_type=break_type,
                time_slot='flexible',  # Special marker
                break_start=timezone.now()
            )
            
            log_action(request.user, 'break_start', 
                      f'Started {break_type} break (flexible - onsite visit)', request)
            messages.success(request, f'{break_type.title()} break started (flexible time - onsite visit)')
            return redirect('dashboard')
        
        # ... existing time window validation code ...
```

### 5. Employee Attendance Dashboard

**View:**

```python
@login_required
def employee_attendance_dashboard(request):
    """HR dashboard showing individual employee statistics"""
    if not request.user.employeeprofile.is_hr:
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    # Filters
    employee_id = request.GET.get('employee')
    department = request.GET.get('department')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Base query
    attendance_query = Attendance.objects.select_related('employee', 'employee__employeeprofile')
    
    # Apply filters
    if employee_id:
        attendance_query = attendance_query.filter(employee__employeeprofile__employee_id=employee_id)
    if department:
        attendance_query = attendance_query.filter(employee__employeeprofile__department=department)
    if start_date:
        attendance_query = attendance_query.filter(date__gte=start_date)
    if end_date:
        attendance_query = attendance_query.filter(date__lte=end_date)
    
    # Calculate statistics per employee
    from django.db.models import Count, Sum, Q
    employee_stats = {}
    
    for attendance in attendance_query:
        emp_id = attendance.employee.employeeprofile.employee_id
        if emp_id not in employee_stats:
            employee_stats[emp_id] = {
                'employee': attendance.employee,
                'present_days': 0,
                'absent_days': 0,
                'late_arrivals': 0,
                'half_days': 0,
                'total_hours': 0
            }
        
        if attendance.status == 'present':
            employee_stats[emp_id]['present_days'] += 1
        elif attendance.status == 'absent':
            employee_stats[emp_id]['absent_days'] += 1
        elif attendance.status in ['late', 'half-day']:
            employee_stats[emp_id]['late_arrivals'] += 1
            if attendance.status == 'half-day':
                employee_stats[emp_id]['half_days'] += 1
        
        employee_stats[emp_id]['total_hours'] += attendance.total_work_hours
    
    # Get all departments for filter
    departments = EmployeeProfile.objects.values_list('department', flat=True).distinct()
    
    # CSV export
    if request.GET.get('export') == 'csv':
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance_stats.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Employee ID', 'Name', 'Department', 'Present Days', 
                        'Absent Days', 'Late Arrivals', 'Half Days', 'Total Hours'])
        
        for emp_id, stats in employee_stats.items():
            emp = stats['employee']
            writer.writerow([
                emp.employeeprofile.employee_id,
                emp.get_full_name(),
                emp.employeeprofile.department,
                stats['present_days'],
                stats['absent_days'],
                stats['late_arrivals'],
                stats['half_days'],
                f"{stats['total_hours']:.2f}"
            ])
        
        return response
    
    return render(request, 'employee_attendance_dashboard.html', {
        'employee_stats': employee_stats,
        'departments': departments,
        'filters': {
            'employee': employee_id,
            'department': department,
            'start_date': start_date,
            'end_date': end_date
        }
    })
```

## Data Models

All models are already defined in `attendance/models.py` and migrated (migration 0021). Key fields:

**LeaveRequest:**
- `selected_dates`: JSONField for non-consecutive dates
- `tl_comment`, `tl_approved`, `tl_approver`, `tl_approved_at`
- `manager_comment`, `manager_approved`, `manager_approver`, `manager_approved_at`

**WFHRequest:**
- `selected_dates`: JSONField for non-consecutive dates
- `tl_comment`, `tl_approved`, `tl_approver`, `tl_approved_at`
- `manager_comment`, `manager_approved`, `manager_approver`, `manager_approved_at`

**OnsiteRequest:**
- `visit_type`, `visit_date`, `client_name`, `location`, `purpose`, `expected_duration`
- `manager_comment`, `manager_approved`, `manager_approver`, `manager_approved_at`
- `actual_check_in`, `actual_check_out`

**EmployeeProfile:**
- `role`: Choices include 'team_leader', 'manager'
- `is_hr`: Boolean flag (set to True for managers)

## Error Handling

**Validation Strategy:**
1. Client-side: JavaScript validation for date formats and selections
2. Server-side: Django form validation in views
3. Database: Model-level constraints

**Error Messages:**
- Display inline with form fields using Bootstrap alerts
- Use Django messages framework for success/error feedback
- Log all errors to audit log for debugging

**Common Error Scenarios:**
- Invalid date format → "Please enter dates in YYYY-MM-DD format"
- Past dates → "Dates must be in the future"
- Missing required fields → "This field is required"
- Overlapping requests → "You already have a request for these dates"
- Unauthorized access → "Access denied - insufficient permissions"

## Testing Strategy

**Unit Tests:**
- Test multi-date selection parsing and validation
- Test hierarchical approval state transitions
- Test flexible break time logic
- Test attendance statistics calculations

**Integration Tests:**
- Test complete approval workflow (TL → Manager → HR)
- Test onsite request with flexible breaks
- Test CSV export functionality

**Manual Testing Checklist:**
1. Multi-date picker works in both calendar and manual modes
2. Approval workflow shows correct requests per role
3. Onsite requests enable flexible breaks
4. Dashboard statistics are accurate
5. Mobile access restrictions work correctly
6. All notifications are sent correctly
7. Audit logs capture all actions

## URL Routes

Add to `attendance/urls.py`:

```python
urlpatterns = [
    # ... existing routes ...
    
    # Leave approval
    path('leave/approval/', views.leave_approval, name='leave_approval'),
    path('leave/action/<int:leave_id>/<str:action>/', views.leave_action, name='leave_action'),
    
    # WFH approval
    path('wfh/approval/', views.wfh_approval, name='wfh_approval'),
    path('wfh/action/<int:wfh_id>/<str:action>/', views.wfh_action, name='wfh_action'),
    
    # Onsite requests
    path('onsite/request/', views.onsite_request, name='onsite_request'),
    path('onsite/approval/', views.onsite_approval, name='onsite_approval'),
    path('onsite/action/<int:onsite_id>/<str:action>/', views.onsite_action, name='onsite_action'),
    path('onsite/check-in/<int:request_id>/', views.onsite_check_in, name='onsite_check_in'),
    path('onsite/check-out/<int:request_id>/', views.onsite_check_out, name='onsite_check_out'),
    
    # Employee dashboard
    path('dashboard/employees/', views.employee_attendance_dashboard, name='employee_attendance_dashboard'),
]
```

## Implementation Notes

**Priority Order:**
1. Multi-date selection (affects both leave and WFH)
2. Hierarchical approval views (core workflow)
3. Onsite requests (new feature)
4. Flexible breaks (depends on onsite)
5. Employee dashboard (reporting)

**Dependencies:**
- Flatpickr.js: Add via CDN or npm install
- Bootstrap 5: Already in project
- Django timezone: Already configured for Asia/Kolkata

**Backward Compatibility:**
- All existing leave/WFH requests work without selected_dates
- Model methods handle both date ranges and selected dates
- No data migration required

**Performance Considerations:**
- Use select_related() for employee queries
- Use prefetch_related() for related objects
- Add database indexes on frequently queried fields (already in migration 0021)
- Cache department list for filters

**Security:**
- Role-based access control on all views
- CSRF protection on all forms
- Input validation on all user inputs
- Audit logging for all actions
