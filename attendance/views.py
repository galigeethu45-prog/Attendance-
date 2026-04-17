from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import datetime, timedelta, time as dt_time
from .models import Attendance, BreakLog, Notification, BREAK_RULES, LeaveRequest, EmployeeProfile, Overtime, AuditLog, WFHRequest, EmployeeMasterData
from django.contrib.auth.models import User


# =========================
# NETWORK DETECTION & WFH VALIDATION
# =========================
def get_wifi_ssid():
    """
    Detect current WiFi SSID
    Returns: SSID string or None if not connected to WiFi
    """
    # WiFi SSID detection doesn't work on web servers
    # This function is deprecated - use IP-based checking instead
    return None


def get_client_ip(request):
    """
    Get the real client IP address from request
    Handles proxy/load balancer scenarios (AWS, Nginx, etc.)
    """
    # Check X-Forwarded-For header (set by load balancers/proxies)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For can contain multiple IPs, first one is the client
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        # Fallback to REMOTE_ADDR
        ip = request.META.get('REMOTE_ADDR')
    
    return ip


def is_on_office_network(request=None):
    """
    Check if user is accessing from office network (Regus)
    Uses IP address checking (works on web servers/AWS)
    
    IMPORTANT: Add your Regus office public IP address below
    """
    if request is None:
        return False
    
    client_ip = get_client_ip(request)
    
    # ═══════════════════════════════════════════════════════════════
    # CONFIGURE YOUR REGUS OFFICE IP ADDRESS HERE:
    # ═══════════════════════════════════════════════════════════════
    # Public IP detected from Regus WiFi network
    
    ALLOWED_OFFICE_IPS = [
        '127.0.0.1',  # Localhost (for local testing only)
        '::1',        # IPv6 localhost (for local testing only)
        '14.195.138.241',  # Regus office public IP (Delhi, India - Tata Teleservices)
    ]
    
    # ═══════════════════════════════════════════════════════════════
    
    # Check if client IP matches office IP
    is_office = client_ip in ALLOWED_OFFICE_IPS
    
    # Debug logging (remove in production if needed)
    if not is_office:
        print(f"Access denied - Client IP: {client_ip} not in allowed office IPs")
    
    return is_office


def has_approved_wfh_today(user):
    """
    Check if user has approved WFH for today
    Returns: Boolean
    """
    today = timezone.now().date()
    
    approved_wfh = WFHRequest.objects.filter(
        employee=user,
        status='approved',
        start_date__lte=today,
        end_date__gte=today
    ).exists()
    
    return approved_wfh


def can_check_in_from_location(user, request=None):
    """
    Validate if user can check-in from current location
    
    RULES:
    1. HR/Admin can check-in from anywhere (bypass all restrictions)
    2. Regular employees MUST be either:
       a) On office network (Regus IP), OR
       b) Have approved WFH for today
    
    Returns: (Boolean, String) - (can_check_in, reason)
    """
    # RULE 1: HR/Admin bypass all network restrictions
    try:
        if user.is_superuser or user.employeeprofile.is_hr:
            return (True, "HR/Admin - No restrictions")
    except EmployeeProfile.DoesNotExist:
        # If no profile, check if superuser
        if user.is_superuser:
            return (True, "Admin - No restrictions")
    
    # RULE 2a: Check if on office network (Regus)
    if is_on_office_network(request):
        return (True, "Office network (Regus)")
    
    # RULE 2b: Check if has approved WFH for today
    if has_approved_wfh_today(user):
        return (True, "Approved WFH - Can work from anywhere")
    
    # Not allowed - must be on office network or have approved WFH
    return (False, "You must be on office WiFi (Regus) or have approved WFH to check-in")


# =========================
# AUDIT LOG HELPER
# =========================
def log_action(user, action, description, request=None, target_user=None):
    """Helper function to create audit log entries"""
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
    
    AuditLog.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=ip_address,
        target_user=target_user
    )


# =========================
# REGISTRATION VIEW
# =========================
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id', '').strip()
        email = request.POST.get('email', '').strip().lower()
        date_of_birth = request.POST.get('date_of_birth', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if not all([employee_id, email, date_of_birth, password, confirm_password]):
            messages.error(request, 'All fields are required!')
            return render(request, 'register.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'register.html')
        
        # Validate against master data
        try:
            from datetime import datetime
            dob_obj = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            
            master_data = EmployeeMasterData.objects.get(
                employee_id=employee_id,
                email__iexact=email,
                date_of_birth=dob_obj
            )
            
            # Check if account already created
            if master_data.account_created:
                messages.error(request, 'An account already exists for this Employee ID!')
                return render(request, 'register.html')
            
            # Create user account
            user = User.objects.create_user(
                username=employee_id,
                email=email,
                password=password,
                first_name=master_data.first_name,
                last_name=master_data.last_name
            )
            
            # Link master data to user
            master_data.linked_user = user
            master_data.account_created = True
            master_data.save()
            
            # Create employee profile from master data
            EmployeeProfile.objects.create(
                user=user,
                employee_id=employee_id,
                date_of_birth=master_data.date_of_birth,
                blood_group=master_data.blood_group,
                phone_number=master_data.phone_number,
                alternate_phone=master_data.alternate_phone or '',
                local_address=master_data.local_address,
                permanent_address=master_data.permanent_address,
                aadhar_number=master_data.aadhar_number,
                pan_number=master_data.pan_number,
                department=master_data.department,
                designation=master_data.designation,
                date_of_joining=master_data.date_of_joining,
                profile_completed=False  # Still need to complete profile
            )
            
            messages.success(request, 'Registration successful! Please login and complete your profile.')
            return redirect('login')
            
        except EmployeeMasterData.DoesNotExist:
            messages.error(request, 'Details Entered Are Not Within Our Organization. Please contact HR if you believe this is an error.')
            return render(request, 'register.html')
        except ValueError:
            messages.error(request, 'Invalid date format. Please use the date picker.')
            return render(request, 'register.html')
        except Exception as e:
            messages.error(request, f'An error occurred during registration. Please try again.')
            return render(request, 'register.html')
    
    return render(request, 'register.html')


# =========================
# LOGIN VIEW
# =========================
def login_view(request):
    # If user is already logged in, redirect based on profile completion
    if request.user.is_authenticated:
        # Superusers go directly to admin or dashboard
        if request.user.is_superuser:
            return redirect('dashboard')
        
        try:
            profile = request.user.employeeprofile
            if not profile.profile_completed:
                return redirect('complete_profile')
            return redirect('dashboard')
        except EmployeeProfile.DoesNotExist:
            # If no profile exists, create one for existing users
            EmployeeProfile.objects.create(
                user=request.user,
                employee_id=request.user.username,
                profile_completed=True
            )
            return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Debug logging
        print(f"Login attempt - Username: {username}")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            print(f"Authentication successful for: {username}")
            login(request, user)
            
            # Log successful login
            log_action(user, 'login', f'User logged in successfully', request)
            
            # Superusers bypass profile check
            if user.is_superuser:
                messages.success(request, f'Welcome back, Admin!')
                return redirect('dashboard')
            
            # Check if profile is completed
            try:
                profile = user.employeeprofile
                if not profile.profile_completed:
                    messages.info(request, 'Please complete your profile to continue.')
                    return redirect('complete_profile')
            except EmployeeProfile.DoesNotExist:
                # Create profile for existing users without one
                EmployeeProfile.objects.create(
                    user=user,
                    employee_id=user.username,
                    profile_completed=True
                )
            
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            print(f"Authentication failed for: {username}")
            messages.error(request, 'Invalid employee ID or password.')
    
    return render(request, 'login.html')


# =========================
# COMPLETE PROFILE VIEW
# =========================
@login_required
def complete_profile(request):
    try:
        profile = request.user.employeeprofile
    except EmployeeProfile.DoesNotExist:
        profile = EmployeeProfile.objects.create(user=request.user)
    
    if profile.profile_completed:
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Update user
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.save()
        
        # Update profile
        profile.phone_number = request.POST.get('phone_number')
        profile.alternate_phone = request.POST.get('alternate_phone', '')
        profile.date_of_birth = request.POST.get('date_of_birth')
        profile.blood_group = request.POST.get('blood_group', '')
        profile.local_address = request.POST.get('local_address', '')
        profile.permanent_address = request.POST.get('permanent_address', '')
        profile.aadhar_number = request.POST.get('aadhar_number', '')
        profile.pan_number = request.POST.get('pan_number', '')
        profile.department = request.POST.get('department')
        profile.designation = request.POST.get('designation')
        profile.date_of_joining = request.POST.get('date_of_joining')
        profile.profile_completed = True
        profile.save()
        
        messages.success(request, 'Profile completed successfully!')
        return redirect('dashboard')
    
    return render(request, 'complete_profile.html', {'profile': profile})


# =========================
# LOGOUT VIEW
# =========================
def logout_view(request):
    user = request.user
    logout(request)
    log_action(user, 'logout', f'User logged out', request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

# =========================
# DASHBOARD
# =========================
@login_required
def dashboard(request):
    today = timezone.now().date()
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    # Today's attendance
    today_attendance = Attendance.objects.filter(
        employee=request.user,
        date=today
    ).first()
    
    # Active break
    active_break = None
    if today_attendance:
        active_break = BreakLog.objects.filter(
            attendance=today_attendance,
            break_end__isnull=True
        ).first()
    
    # Break counts for today - separate morning and evening tea
    tea_morning_count = 0
    tea_evening_count = 0
    lunch_count = 0
    if today_attendance:
        tea_morning_count = BreakLog.objects.filter(
            attendance=today_attendance,
            break_type='tea',
            time_slot='morning'
        ).count()
        tea_evening_count = BreakLog.objects.filter(
            attendance=today_attendance,
            break_type='tea',
            time_slot='evening'
        ).count()
        lunch_count = BreakLog.objects.filter(
            attendance=today_attendance,
            break_type='lunch'
        ).count()
        
        # Handle old records without time_slot (count as morning for safety)
        tea_no_slot_count = BreakLog.objects.filter(
            attendance=today_attendance,
            break_type='tea',
            time_slot__isnull=True
        ).count()
        if tea_no_slot_count > 0:
            tea_morning_count += tea_no_slot_count
    
    # Monthly statistics
    monthly_attendance = Attendance.objects.filter(
        employee=request.user,
        date__month=current_month,
        date__year=current_year
    )
    
    monthly_stats = {
        'present_days': monthly_attendance.filter(status='present').count(),
        'late_days': monthly_attendance.filter(status='late').count(),
        'total_hours': monthly_attendance.aggregate(Sum('total_work_hours'))['total_work_hours__sum'] or 0,
        'absent_days': monthly_attendance.filter(status='absent').count(),
    }
    
    # Recent attendance (last 7 days)
    recent_attendance = Attendance.objects.filter(
        employee=request.user
    ).order_by('-date')[:7]
    
    # Recent notifications
    recent_notifications = Notification.objects.filter(
        employee=request.user
    ).order_by('-created_at')[:5]
    
    unread_notifications = Notification.objects.filter(
        employee=request.user,
        is_read=False
    ).count()
    
    # Check current time for break button availability
    import pytz
    local_tz = pytz.timezone('Asia/Kolkata')
    current_time = timezone.now().astimezone(local_tz).time()
    current_hour = current_time.hour
    current_minute = current_time.minute
    
    # Determine which tea slot is currently active
    is_morning_tea_time = (10 <= current_hour < 11)
    is_evening_tea_time = (current_hour == 16 and current_minute <= 45)
    
    # Tea break allowed if in time window AND haven't taken break for that slot yet
    tea_break_allowed = False
    if is_morning_tea_time and tea_morning_count == 0:
        tea_break_allowed = True
    elif is_evening_tea_time and tea_evening_count == 0:
        tea_break_allowed = True
    
    # Lunch break allowed: 1:00 PM - 1:45 PM
    lunch_break_allowed = (current_hour == 13 and current_minute <= 45) and lunch_count == 0
    
    # Total tea count for display
    tea_count = tea_morning_count + tea_evening_count
    
    context = {
        'today_attendance': today_attendance,
        'active_break': active_break,
        'tea_count': tea_count,
        'tea_morning_count': tea_morning_count,
        'tea_evening_count': tea_evening_count,
        'lunch_count': lunch_count,
        'tea_break_allowed': tea_break_allowed,
        'lunch_break_allowed': lunch_break_allowed,
        'is_morning_tea_time': is_morning_tea_time,
        'is_evening_tea_time': is_evening_tea_time,
        'monthly_stats': monthly_stats,
        'recent_attendance': recent_attendance,
        'recent_notifications': recent_notifications,
        'unread_notifications': unread_notifications,
        'current_date': timezone.now(),
    }
    
    return render(request, 'dashboard.html', context)


# =========================
# CHECK IN
# =========================
@login_required
def check_in(request):
    if request.method == 'POST':
        # Validate location/network
        can_check_in, reason = can_check_in_from_location(request.user, request)
        
        if not can_check_in:
            messages.error(request, reason)
            messages.info(request, 'Please submit a WFH request or come to office.')
            return redirect('dashboard')
        
        today = timezone.now().date()
        
        attendance, created = Attendance.objects.get_or_create(
            employee=request.user,
            date=today
        )
        
        if attendance.check_in is None:
            attendance.check_in = timezone.now()
            
            # Convert to local timezone for comparison
            import pytz
            local_tz = pytz.timezone('Asia/Kolkata')
            check_in_local = attendance.check_in.astimezone(local_tz)
            check_in_time = check_in_local.time()
            
            # Determine status based on check-in time (9:30 AM IST cutoff)
            if check_in_time.hour > 9 or (check_in_time.hour == 9 and check_in_time.minute > 30):
                attendance.status = 'half-day'  # Mark as half-day immediately
                log_action(request.user, 'check_in', f'Checked in late at {check_in_time.strftime("%I:%M %p")} from {reason} - Marked as half-day', request)
                messages.warning(request, f'Late Checked-In at {check_in_time.strftime("%I:%M %p")}, Considered as Half Day Leave')
                
                # Notify HR about late arrival
                hr_users = User.objects.filter(employeeprofile__is_hr=True)
                for hr_user in hr_users:
                    Notification.objects.create(
                        employee=hr_user,
                        message=f'{request.user.get_full_name() or request.user.username} (ID: {request.user.employeeprofile.employee_id}) checked in late at {check_in_time.strftime("%I:%M %p")} - Marked as half-day'
                    )
            else:
                attendance.status = 'present'
                log_action(request.user, 'check_in', f'Checked in on time at {check_in_time.strftime("%I:%M %p")} from {reason}', request)
                messages.success(request, f'Checked in successfully at {check_in_time.strftime("%I:%M %p")}!')
            
            attendance.save()
        else:
            messages.info(request, 'You have already checked in today.')
    
    return redirect('dashboard')


# =========================
# CHECK OUT
# =========================
@login_required
def check_out(request):
    if request.method == 'POST':
        # Validate location/network
        can_check_out, reason = can_check_in_from_location(request.user, request)
        
        if not can_check_out:
            messages.error(request, reason)
            messages.info(request, 'You must be on office WiFi or have approved WFH to check-out.')
            return redirect('dashboard')
        
        today = timezone.now().date()
        
        try:
            attendance = Attendance.objects.get(
                employee=request.user,
                date=today
            )
            
            if attendance.check_out is None and attendance.check_in is not None:
                # Check if there's an active break
                active_break = BreakLog.objects.filter(
                    attendance=attendance,
                    break_end__isnull=True
                ).first()
                
                if active_break:
                    messages.warning(request, 'Please end your break before checking out.')
                    return redirect('dashboard')
                
                attendance.check_out = timezone.now()
                attendance.save()
                attendance.calculate_work_hours()
                
                # Log check-out
                log_action(request.user, 'check_out', f'Checked out from {reason} - Total hours: {attendance.get_work_hours_display()}', request)
                
                # Note: calculate_work_hours() already handles status, no need to override
                
                messages.success(request, f'Checked out successfully! Total work hours: {attendance.get_work_hours_display()}')
            else:
                messages.info(request, 'Invalid check-out attempt.')
        
        except Attendance.DoesNotExist:
            messages.error(request, 'Please check in first.')
    
    return redirect('dashboard')


# =========================
# START BREAK
# =========================
@login_required
def start_break(request, break_type):
    if request.method == 'POST':
        today = timezone.now().date()
        
        attendance = Attendance.objects.filter(
            employee=request.user,
            date=today
        ).first()
        
        if not attendance or not attendance.check_in:
            messages.error(request, 'Please check in first.')
            return redirect('dashboard')
        
        if attendance.check_out:
            messages.error(request, 'You have already checked out.')
            return redirect('dashboard')
        
        # Check current time for break restrictions
        import pytz
        local_tz = pytz.timezone('Asia/Kolkata')
        current_time = timezone.now().astimezone(local_tz).time()
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        # No breaks after 5 PM
        if current_hour >= 17:
            messages.error(request, 'Breaks are not allowed after 5:00 PM.')
            return redirect('dashboard')
        
        # Determine time slot
        time_slot = 'morning'
        
        # Tea break: 10:00 AM - 11:00 AM OR 4:00 PM - 4:45 PM
        if break_type == 'tea':
            is_morning = (10 <= current_hour < 11)
            is_evening = (current_hour == 16 and current_minute <= 45)
            
            if not (is_morning or is_evening):
                messages.error(request, 'Tea break is only allowed between 10:00 AM - 11:00 AM or 4:00 PM - 4:45 PM.')
                return redirect('dashboard')
            
            # Set time slot
            time_slot = 'morning' if is_morning else 'evening'
            
            # Check if already taken break in this slot
            slot_break_count = BreakLog.objects.filter(
                attendance=attendance,
                break_type='tea',
                time_slot=time_slot
            ).count()
            
            if slot_break_count >= 1:
                slot_name = 'morning (10-11 AM)' if time_slot == 'morning' else 'evening (4-4:45 PM)'
                messages.error(request, f'You have already taken your {slot_name} tea break today.')
                return redirect('dashboard')
        
        # Lunch break: 1:00 PM - 1:45 PM
        elif break_type == 'lunch':
            if not (current_hour == 13 and current_minute <= 45):
                messages.error(request, 'Lunch break is only allowed between 1:00 PM and 1:45 PM.')
                return redirect('dashboard')
            
            time_slot = 'afternoon'
            
            # Check if already taken lunch
            lunch_count = BreakLog.objects.filter(
                attendance=attendance,
                break_type='lunch'
            ).count()
            
            if lunch_count >= 1:
                messages.error(request, 'You have already taken your lunch break today.')
                return redirect('dashboard')
        
        # Check for active break
        active_break = BreakLog.objects.filter(
            attendance=attendance,
            break_end__isnull=True
        ).first()
        
        if active_break:
            messages.warning(request, 'You are already on a break.')
            return redirect('dashboard')
        
        # Create new break with time slot
        BreakLog.objects.create(
            attendance=attendance,
            break_type=break_type,
            time_slot=time_slot,
            break_start=timezone.now()
        )
        
        messages.success(request, f'{break_type.title()} break started.')
    
    return redirect('dashboard')


# =========================
# END BREAK
# =========================
@login_required
def end_break(request):
    if request.method == 'POST':
        today = timezone.now().date()
        
        attendance = Attendance.objects.filter(
            employee=request.user,
            date=today
        ).first()
        
        if not attendance:
            messages.error(request, 'No attendance record found.')
            return redirect('dashboard')
        
        active_break = BreakLog.objects.filter(
            attendance=attendance,
            break_end__isnull=True
        ).first()
        
        if not active_break:
            messages.error(request, 'No active break to end.')
            return redirect('dashboard')
        
        active_break.break_end = timezone.now()
        active_break.calculate_break_duration()
        
        # Check if break exceeded limit
        if active_break.is_exceeded():
            messages.warning(
                request,
                f'{active_break.get_break_type_display()} exceeded limit '
                f'({active_break.duration_minutes} mins / {active_break.allowed_minutes()} mins allowed)'
            )
            Notification.objects.create(
                employee=request.user,
                message=f"{active_break.get_break_type_display()} exceeded limit ({active_break.duration_minutes} mins)"
            )
            
            # Notify HR about long break
            hr_users = User.objects.filter(employeeprofile__is_hr=True)
            for hr_user in hr_users:
                Notification.objects.create(
                    employee=hr_user,
                    message=f'{request.user.get_full_name() or request.user.username} (ID: {request.user.employeeprofile.employee_id}) took a long {active_break.get_break_type_display()} break: {active_break.duration_minutes} minutes (limit: {active_break.allowed_minutes()} mins)'
                )
        else:
            messages.success(request, f'{active_break.get_break_type_display()} ended.')
    
    return redirect('dashboard')


# =========================
# ATTENDANCE HISTORY
# =========================
@login_required
def attendance_history(request):
    # Get filter parameters
    month = request.GET.get('month')
    year = request.GET.get('year', timezone.now().year)
    status = request.GET.get('status')
    
    # Base queryset
    attendance_records = Attendance.objects.filter(
        employee=request.user
    ).order_by('-date')
    
    # Apply filters
    if month:
        attendance_records = attendance_records.filter(date__month=month)
    if year:
        attendance_records = attendance_records.filter(date__year=year)
    if status:
        attendance_records = attendance_records.filter(status=status)
    
    # Pagination
    paginator = Paginator(attendance_records, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Generate year list for filter
    years = range(2020, timezone.now().year + 1)
    
    context = {
        'attendance_records': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'years': years,
        'selected_month': month,
        'selected_year': str(year),
        'selected_status': status,
    }
    
    return render(request, 'attendance_history.html', context)


# =========================
# LEAVE REQUEST
# =========================
@login_required
def leave_request(request):
    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        
        LeaveRequest.objects.create(
            employee=request.user,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )
        
        messages.success(request, 'Leave request submitted successfully!')
        return redirect('leave_request')
    
    # Get user's leave requests
    leave_requests = LeaveRequest.objects.filter(
        employee=request.user
    ).order_by('-created_at')
    
    # Calculate leave balance
    try:
        current_year = timezone.now().year
        current_month = timezone.now().month
        
        # Get approved leaves for current year
        approved_leaves = LeaveRequest.objects.filter(
            employee=request.user,
            status='approved',
            start_date__year=current_year
        )
        
        # Count leaves by type (handle potential errors)
        try:
            sick_used = sum(leave.total_days for leave in approved_leaves.filter(leave_type='sick'))
        except:
            sick_used = 0
            
        try:
            casual_used = sum(leave.total_days for leave in approved_leaves.filter(leave_type='casual'))
        except:
            casual_used = 0
            
        try:
            earned_used = sum(leave.total_days for leave in approved_leaves.filter(leave_type='earned'))
        except:
            earned_used = 0
        
        # Menstrual leave - only for female employees
        menstrual_used = 0
        show_menstrual = False
        gender_not_set = False
        
        try:
            profile = request.user.employeeprofile
            if profile.gender:
                if profile.gender.lower() == 'female':
                    show_menstrual = True
                    try:
                        menstrual_used = sum(leave.total_days for leave in approved_leaves.filter(leave_type='menstrual'))
                    except:
                        menstrual_used = 0
            else:
                # Gender not set
                gender_not_set = True
        except (EmployeeProfile.DoesNotExist, AttributeError):
            # No profile exists
            gender_not_set = True
        
        # Annual limits
        SICK_LIMIT = 6
        CASUAL_LIMIT = 6
        EARNED_LIMIT = 6
        MENSTRUAL_LIMIT = 12  # 1 per month, 12 per year
        
        # Calculate remaining
        sick_remaining = max(0, SICK_LIMIT - sick_used)
        casual_remaining = max(0, CASUAL_LIMIT - casual_used)
        earned_remaining = max(0, EARNED_LIMIT - earned_used)
        menstrual_remaining = max(0, MENSTRUAL_LIMIT - menstrual_used) if show_menstrual else 0
        
        # Calculate percentages
        sick_percent = int((sick_remaining / SICK_LIMIT) * 100) if SICK_LIMIT > 0 else 0
        casual_percent = int((casual_remaining / CASUAL_LIMIT) * 100) if CASUAL_LIMIT > 0 else 0
        earned_percent = int((earned_remaining / EARNED_LIMIT) * 100) if EARNED_LIMIT > 0 else 0
        menstrual_percent = int((menstrual_remaining / MENSTRUAL_LIMIT) * 100) if show_menstrual and MENSTRUAL_LIMIT > 0 else 0
        
        leave_balance = {
            'sick_used': sick_used,
            'sick_remaining': sick_remaining,
            'sick_total': SICK_LIMIT,
            'sick_percent': sick_percent,
            
            'casual_used': casual_used,
            'casual_remaining': casual_remaining,
            'casual_total': CASUAL_LIMIT,
            'casual_percent': casual_percent,
            
            'earned_used': earned_used,
            'earned_remaining': earned_remaining,
            'earned_total': EARNED_LIMIT,
            'earned_percent': earned_percent,
            
            'show_menstrual': show_menstrual,
            'gender_not_set': gender_not_set,
            'menstrual_used': menstrual_used,
            'menstrual_remaining': menstrual_remaining,
            'menstrual_total': MENSTRUAL_LIMIT,
            'menstrual_percent': menstrual_percent,
        }
    except Exception as e:
        # If any error in balance calculation, provide default values
        print(f"Error calculating leave balance for {request.user.username}: {e}")
        leave_balance = {
            'sick_used': 0,
            'sick_remaining': 6,
            'sick_total': 6,
            'sick_percent': 100,
            
            'casual_used': 0,
            'casual_remaining': 6,
            'casual_total': 6,
            'casual_percent': 100,
            
            'earned_used': 0,
            'earned_remaining': 6,
            'earned_total': 6,
            'earned_percent': 100,
            
            'show_menstrual': False,
            'menstrual_used': 0,
            'menstrual_remaining': 0,
            'menstrual_total': 12,
            'menstrual_percent': 0,
        }
    
    context = {
        'leave_requests': leave_requests,
        'leave_balance': leave_balance,
    }
    
    return render(request, 'leave_request.html', context)


# =========================
# CANCEL LEAVE
# =========================
@login_required
def cancel_leave(request, leave_id):
    if request.method == 'POST':
        leave = get_object_or_404(LeaveRequest, id=leave_id, employee=request.user)
        if leave.status == 'pending':
            leave.delete()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})


# =========================
# PROFILE
# =========================
@login_required
def profile(request):
    try:
        employee_profile = request.user.employeeprofile
    except EmployeeProfile.DoesNotExist:
        employee_profile = None
    
    if request.method == 'POST':
        # Update user information
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Update employee profile if exists
        if employee_profile:
            employee_profile.gender = request.POST.get('gender', '')
            employee_profile.phone_number = request.POST.get('phone_number', '')
            employee_profile.alternate_phone = request.POST.get('alternate_phone', '')
            employee_profile.date_of_birth = request.POST.get('date_of_birth') or None
            employee_profile.blood_group = request.POST.get('blood_group', '')
            employee_profile.local_address = request.POST.get('local_address', '')
            employee_profile.permanent_address = request.POST.get('permanent_address', '')
            employee_profile.aadhar_number = request.POST.get('aadhar_number', '')
            employee_profile.pan_number = request.POST.get('pan_number', '')
            employee_profile.department = request.POST.get('department', '')
            employee_profile.designation = request.POST.get('designation', '')
            employee_profile.date_of_joining = request.POST.get('date_of_joining') or None
            employee_profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    # Calculate statistics
    total_attendance = Attendance.objects.filter(employee=request.user)
    total_present = total_attendance.filter(status='present').count()
    total_late = total_attendance.filter(status='late').count()
    total_hours = total_attendance.aggregate(Sum('total_work_hours'))['total_work_hours__sum'] or 0
    
    context = {
        'employee_profile': employee_profile,
        'total_present': total_present,
        'total_late': total_late,
        'total_hours': total_hours,
    }
    
    return render(request, 'profile.html', context)


# =========================
# NOTIFICATIONS
# =========================
@login_required
def notifications(request):
    notifications = Notification.objects.filter(
        employee=request.user
    ).order_by('-created_at')
    
    # Mark all as read
    if request.method == 'POST':
        notifications.update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications')
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'notifications.html', context)


# =========================
# HR DASHBOARD
# =========================
@login_required
def hr_dashboard(request):
    # Check if user is HR or superuser
    if not request.user.is_superuser:
        try:
            if not request.user.employeeprofile.is_hr:
                messages.error(request, 'Access denied. HR only.')
                return redirect('dashboard')
        except EmployeeProfile.DoesNotExist:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    
    today = timezone.now().date()
    
    # Statistics
    total_employees = User.objects.filter(is_active=True).count()
    today_attendance = Attendance.objects.filter(date=today)
    present_today = today_attendance.filter(check_in__isnull=False).count()
    absent_today = total_employees - present_today
    
    pending_leaves = LeaveRequest.objects.filter(status='pending').count()
    
    # Today's attendance details
    today_attendance_list = Attendance.objects.filter(
        date=today
    ).select_related('employee', 'employee__employeeprofile').order_by('check_in')
    
    # Pending leave requests
    pending_leave_requests = LeaveRequest.objects.filter(
        status='pending'
    ).select_related('employee').order_by('-created_at')
    
    # Break Logs with filters
    break_period = request.GET.get('break_period', 'today')
    employee_search = request.GET.get('employee_search', '')
    
    break_logs = BreakLog.objects.select_related(
        'attendance__employee__employeeprofile'
    ).order_by('-break_start')
    
    # Apply period filter
    if break_period == 'today':
        break_logs = break_logs.filter(break_start__date=today)
    elif break_period == 'week':
        week_start = today - timedelta(days=today.weekday())
        break_logs = break_logs.filter(break_start__date__gte=week_start)
    elif break_period == 'month':
        break_logs = break_logs.filter(
            break_start__year=today.year,
            break_start__month=today.month
        )
    
    # Apply employee search filter
    if employee_search:
        break_logs = break_logs.filter(
            attendance__employee__employeeprofile__employee_id__icontains=employee_search
        )
    
    # Limit to 100 records for performance
    break_logs = break_logs[:100]
    
    # Chart data (last 7 days)
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        chart_labels.append(date.strftime('%b %d'))
        count = Attendance.objects.filter(date=date, check_in__isnull=False).count()
        chart_data.append(count)
    
    # Department-wise data
    dept_labels = []
    dept_data = []
    departments = EmployeeProfile.objects.values('department').annotate(count=Count('id'))
    for dept in departments:
        dept_labels.append(dept['department'])
        dept_data.append(dept['count'])
    
    # All employees for Employee Profiles tab
    all_employees = EmployeeProfile.objects.select_related('user').filter(
        user__is_active=True
    ).order_by('user__first_name', 'user__username')
    
    # Get unique departments for filter
    unique_departments = EmployeeProfile.objects.values_list('department', flat=True).distinct().exclude(department='')
    
    # Audit Logs with filters
    audit_action = request.GET.get('audit_action', '')
    audit_user = request.GET.get('audit_user', '')
    audit_date = request.GET.get('audit_date', '')
    
    audit_logs_query = AuditLog.objects.select_related('user', 'target_user').all()
    
    if audit_action:
        audit_logs_query = audit_logs_query.filter(action=audit_action)
    if audit_user:
        audit_logs_query = audit_logs_query.filter(user__username__icontains=audit_user)
    if audit_date:
        audit_logs_query = audit_logs_query.filter(timestamp__date=audit_date)
    
    # Paginate audit logs
    paginator = Paginator(audit_logs_query, 50)
    page_number = request.GET.get('page')
    audit_logs_page = paginator.get_page(page_number)
    
    context = {
        'total_employees': total_employees,
        'present_today': present_today,
        'absent_today': absent_today,
        'pending_leaves': pending_leaves,
        'today_attendance': today_attendance_list,
        'pending_leave_requests': pending_leave_requests,
        'break_logs': break_logs,
        'current_date': timezone.now(),
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'dept_labels': dept_labels,
        'dept_data': dept_data,
        'all_employees': all_employees,
        'departments': unique_departments,
        'audit_logs': audit_logs_page,
    }
    
    return render(request, 'hr_dashboard.html', context)


# =========================
# APPROVE LEAVE
# =========================
@login_required
def approve_leave(request, leave_id):
    if request.method == 'POST':
        try:
            if not request.user.employeeprofile.is_hr:
                return JsonResponse({'success': False, 'message': 'Access denied'})
        except EmployeeProfile.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Access denied'})
        
        leave = get_object_or_404(LeaveRequest, id=leave_id)
        leave.status = 'approved'
        leave.save()
        
        Notification.objects.create(
            employee=leave.employee,
            message=f'Your {leave.get_leave_type_display()} request has been approved.'
        )
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


# =========================
# REJECT LEAVE
# =========================
@login_required
def reject_leave(request, leave_id):
    if request.method == 'POST':
        try:
            if not request.user.employeeprofile.is_hr:
                return JsonResponse({'success': False, 'message': 'Access denied'})
        except EmployeeProfile.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Access denied'})
        
        leave = get_object_or_404(LeaveRequest, id=leave_id)
        leave.status = 'rejected'
        
        import json
        data = json.loads(request.body)
        comment = data.get('comment', '')
        if comment:
            leave.hr_comment = comment
        
        leave.save()
        
        Notification.objects.create(
            employee=leave.employee,
            message=f'Your {leave.get_leave_type_display()} request has been rejected.'
        )
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})



# =========================
# OVERTIME VIEWS
# =========================
@login_required
def overtime_view(request):
    # Check if user has completed profile
    try:
        profile = request.user.employeeprofile
    except EmployeeProfile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'request_ot':
            # Employee requests OT permission
            reason = request.POST.get('reason', '')
            ot_date = request.POST.get('ot_date')
            
            if not reason:
                messages.error(request, 'Please provide a reason for overtime.')
                return redirect('overtime')
            
            if not ot_date:
                messages.error(request, 'Please select a date for overtime.')
                return redirect('overtime')
            
            # Convert string date to date object
            try:
                from datetime import datetime
                ot_date_obj = datetime.strptime(ot_date, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Invalid date format.')
                return redirect('overtime')
            
            # Check if already has a request for this date
            existing = Overtime.objects.filter(
                employee=request.user,
                date=ot_date_obj
            ).first()
            
            if existing:
                messages.warning(request, 'You already have an OT request for this date.')
            else:
                # Auto-approve for HR/Admin, pending for employees
                if profile.is_hr or request.user.is_superuser:
                    status = 'approved'
                    approved = True
                else:
                    status = 'pending'
                    approved = False
                
                ot = Overtime.objects.create(
                    employee=request.user,
                    date=ot_date_obj,
                    reason=reason,
                    status=status,
                    approved_by_hr=approved
                )
                
                # Send notification to HR if employee
                if not (profile.is_hr or request.user.is_superuser):
                    hr_users = User.objects.filter(
                        Q(employeeprofile__is_hr=True) | Q(is_superuser=True)
                    )
                    for hr_user in hr_users:
                        Notification.objects.create(
                            employee=hr_user,
                            message=f'{request.user.get_full_name() or request.user.username} has requested overtime permission for {ot.date.strftime("%b %d, %Y")}'
                        )
                
                # Log action
                log_action(request.user, 'overtime_request', f'Requested overtime permission for {ot.date.strftime("%b %d, %Y")}', request)
                
                if status == 'approved':
                    messages.success(request, 'Overtime request auto-approved! You can now start OT.')
                else:
                    messages.success(request, 'Overtime request submitted! Waiting for HR approval.')
        
        elif action == 'start_ot':
            # Start approved OT session
            ot_id = request.POST.get('ot_id')
            
            if not ot_id:
                messages.error(request, 'Invalid OT request.')
                return redirect('overtime')
            
            try:
                ot = Overtime.objects.get(id=ot_id, employee=request.user)
            except Overtime.DoesNotExist:
                messages.error(request, 'OT request not found.')
                return redirect('overtime')
            
            if ot.status != 'approved':
                messages.error(request, 'This OT request is not approved yet.')
            elif ot.start_time:
                messages.warning(request, 'OT session already started.')
            else:
                ot.start_time = timezone.now()
                ot.save()
                
                # Log action
                log_action(request.user, 'overtime_start', f'Started overtime session for {ot.date}', request)
                
                messages.success(request, 'Overtime session started!')
        
        elif action == 'end_ot':
            # End active OT session
            ot_id = request.POST.get('ot_id')
            
            if not ot_id:
                messages.error(request, 'Invalid OT request.')
                return redirect('overtime')
            
            try:
                ot = Overtime.objects.get(id=ot_id, employee=request.user)
            except Overtime.DoesNotExist:
                messages.error(request, 'OT request not found.')
                return redirect('overtime')
            
            if not ot.start_time:
                messages.error(request, 'OT session not started yet.')
            elif ot.end_time:
                messages.warning(request, 'OT session already ended.')
            else:
                ot.end_time = timezone.now()
                ot.status = 'completed'
                ot.calculate_ot_hours()
                
                # Log action
                log_action(request.user, 'overtime_end', f'Ended overtime session - {ot.get_ot_hours_display()}', request)
                
                messages.success(request, f'Overtime ended! Total OT: {ot.get_ot_hours_display()}')
        
        return redirect('overtime')
    
    # Get user's OT records
    ot_records = Overtime.objects.filter(
        employee=request.user
    ).order_by('-date')[:30]
    
    # Get active OT (approved and started but not ended)
    active_ot = Overtime.objects.filter(
        employee=request.user,
        status='approved',
        start_time__isnull=False,
        end_time__isnull=True
    ).first()
    
    # Get approved OT that can be started
    approved_pending_start = Overtime.objects.filter(
        employee=request.user,
        status='approved',
        start_time__isnull=True
    ).order_by('-date')
    
    # Calculate total OT hours this month (only completed)
    current_month = timezone.now().month
    current_year = timezone.now().year
    monthly_ot = Overtime.objects.filter(
        employee=request.user,
        date__month=current_month,
        date__year=current_year,
        status='completed'
    ).aggregate(Sum('total_hours'))['total_hours__sum'] or 0
    
    context = {
        'ot_records': ot_records,
        'active_ot': active_ot,
        'approved_pending_start': approved_pending_start,
        'monthly_ot': monthly_ot,
        'is_hr': profile.is_hr,
    }
    
    return render(request, 'overtime.html', context)


@login_required
def overtime_approval(request):
    # Only HR or superuser can access
    if not request.user.is_superuser:
        try:
            if not request.user.employeeprofile.is_hr:
                messages.error(request, 'Access denied. HR only.')
                return redirect('dashboard')
        except EmployeeProfile.DoesNotExist:
            messages.error(request, 'Profile not found.')
            return redirect('dashboard')
    
    if request.method == 'POST':
        ot_id = request.POST.get('ot_id')
        action = request.POST.get('action')
        hr_comment = request.POST.get('hr_comment', '')
        
        ot = get_object_or_404(Overtime, id=ot_id)
        
        if action == 'approve':
            ot.status = 'approved'
            ot.approved_by_hr = True
            ot.hr_approver = request.user
            ot.hr_comment = hr_comment
            ot.save()
            
            # Send notification to employee
            Notification.objects.create(
                employee=ot.employee,
                message=f'Your overtime request for {ot.date.strftime("%b %d, %Y")} has been approved. You can now start your OT session.'
            )
            
            # Log action
            log_action(request.user, 'overtime_approve', f'Approved overtime request for {ot.employee.username} on {ot.date}', request, target_user=ot.employee)
            
            messages.success(request, 'Overtime request approved successfully!')
        
        elif action == 'reject':
            ot.status = 'rejected'
            ot.approved_by_hr = False
            ot.hr_approver = request.user
            ot.hr_comment = hr_comment
            ot.save()
            
            # Send notification to employee
            Notification.objects.create(
                employee=ot.employee,
                message=f'Your overtime request for {ot.date.strftime("%b %d, %Y")} has been rejected.'
            )
            
            # Log action
            log_action(request.user, 'overtime_reject', f'Rejected overtime request for {ot.employee.username} on {ot.date}', request, target_user=ot.employee)
            
            messages.warning(request, 'Overtime request rejected.')
        
        return redirect('overtime_approval')
    
    # Get pending OT requests (not started yet)
    pending_ot = Overtime.objects.filter(
        status='pending'
    ).select_related('employee').order_by('-requested_at')
    
    # Get all OT records
    all_ot = Overtime.objects.all().select_related('employee', 'hr_approver').order_by('-requested_at')[:50]
    
    context = {
        'pending_ot': pending_ot,
        'all_ot': all_ot,
    }
    
    return render(request, 'overtime_approval.html', context)


# =========================
# EMPLOYEE DETAILS (HR ONLY)
# =========================
@login_required
def employee_details(request, user_id):
    # Only HR or superuser can access
    if not request.user.is_superuser:
        try:
            if not request.user.employeeprofile.is_hr:
                messages.error(request, 'Access denied. HR only.')
                return redirect('dashboard')
        except EmployeeProfile.DoesNotExist:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    
    # Get employee
    employee_user = get_object_or_404(User, id=user_id)
    try:
        employee_profile = employee_user.employeeprofile
    except EmployeeProfile.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('hr_dashboard')
    
    # Get attendance statistics
    total_attendance = Attendance.objects.filter(employee=employee_user)
    total_present = total_attendance.filter(status='present').count()
    total_late = total_attendance.filter(status='late').count()
    total_half_day = total_attendance.filter(status='half-day').count()
    total_hours = total_attendance.aggregate(Sum('total_work_hours'))['total_work_hours__sum'] or 0
    
    # Recent attendance
    recent_attendance = Attendance.objects.filter(
        employee=employee_user
    ).order_by('-date')[:10]
    
    # Leave requests
    leave_requests = LeaveRequest.objects.filter(
        employee=employee_user
    ).order_by('-created_at')[:10]
    
    context = {
        'employee_user': employee_user,
        'employee_profile': employee_profile,
        'total_present': total_present,
        'total_late': total_late,
        'total_half_day': total_half_day,
        'total_hours': total_hours,
        'recent_attendance': recent_attendance,
        'leave_requests': leave_requests,
    }
    
    return render(request, 'employee_details.html', context)


# =========================
# ADD USER (HR ONLY)
# =========================
@login_required
def add_user(request):
    # Only HR or superuser can access
    if not request.user.is_superuser:
        try:
            if not request.user.employeeprofile.is_hr:
                messages.error(request, 'Access denied. HR only.')
                return redirect('hr_dashboard')
        except EmployeeProfile.DoesNotExist:
            messages.error(request, 'Access denied.')
            return redirect('hr_dashboard')
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        department = request.POST.get('department', '')
        designation = request.POST.get('designation', '')
        phone_number = request.POST.get('phone_number', '')
        is_hr = request.POST.get('is_hr') == 'on'
        
        # Email domain validation
        if not email.endswith('@arraafiinfotech.com'):
            messages.error(request, 'Only @arraafiinfotech.com email addresses are allowed!')
            return redirect('hr_dashboard')
        
        # Check if user already exists
        if User.objects.filter(username=employee_id).exists():
            messages.error(request, 'Employee ID already exists!')
            return redirect('hr_dashboard')
        
        # Check if employee_id already exists in profiles
        if EmployeeProfile.objects.filter(employee_id=employee_id).exists():
            messages.error(request, 'Employee ID already exists!')
            return redirect('hr_dashboard')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('hr_dashboard')
        
        # Create user
        user = User.objects.create_user(
            username=employee_id,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create employee profile
        EmployeeProfile.objects.create(
            user=user,
            employee_id=employee_id,
            department=department,
            designation=designation,
            phone_number=phone_number,
            is_hr=is_hr,
            profile_completed=True
        )
        
        # Log user creation
        log_action(request.user, 'user_create', f'Created new user: {employee_id} ({first_name} {last_name})', request, target_user=user)
        
        messages.success(request, f'User {employee_id} created successfully!')
        return redirect('hr_dashboard')
    
    return redirect('hr_dashboard')


# =========================
# DELETE USER (HR ONLY)
# =========================
@login_required
def delete_user(request, user_id):
    # Only HR or superuser can access
    if not request.user.is_superuser:
        try:
            if not request.user.employeeprofile.is_hr:
                return JsonResponse({'success': False, 'message': 'Access denied'})
        except EmployeeProfile.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Access denied'})
    
    if request.method == 'POST':
        try:
            user_to_delete = User.objects.get(id=user_id)
            
            # Prevent deleting superusers
            if user_to_delete.is_superuser:
                return JsonResponse({'success': False, 'message': 'Cannot delete superuser'})
            
            # Prevent self-deletion
            if user_to_delete.id == request.user.id:
                return JsonResponse({'success': False, 'message': 'Cannot delete yourself'})
            
            username = user_to_delete.username
            user_to_delete.delete()
            
            # Log user deletion
            log_action(request.user, 'user_delete', f'Deleted user: {username}', request, target_user=None)
            
            return JsonResponse({'success': True, 'message': f'User {username} deleted successfully'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})



# =========================
# WFH REQUEST
# =========================
@login_required
def wfh_request(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        
        # Convert to date objects
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format.')
            return redirect('wfh_request')
        
        # Validate dates
        today = timezone.now().date()
        if start_date_obj < today:
            messages.error(request, 'Cannot request WFH for past dates.')
            return redirect('wfh_request')
        
        if end_date_obj < start_date_obj:
            messages.error(request, 'End date must be after start date.')
            return redirect('wfh_request')
        
        # Calculate total days
        total_days = (end_date_obj - start_date_obj).days + 1
        
        # Check monthly limit (5 days)
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        # Get approved WFH days for current month
        # We need to check all WFH requests that overlap with current month
        from datetime import date
        month_start = date(current_year, current_month, 1)
        if current_month == 12:
            month_end = date(current_year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(current_year, current_month + 1, 1) - timedelta(days=1)
        
        approved_wfh = WFHRequest.objects.filter(
            employee=request.user,
            status='approved',
            start_date__lte=month_end,
            end_date__gte=month_start
        )
        
        # Calculate actual days used in current month
        used_days = 0
        for wfh in approved_wfh:
            # Calculate overlap with current month
            overlap_start = max(wfh.start_date, month_start)
            overlap_end = min(wfh.end_date, month_end)
            if overlap_start <= overlap_end:
                used_days += (overlap_end - overlap_start).days + 1
        
        if used_days + total_days > 5:
            messages.error(request, f'WFH limit exceeded! You have {5 - used_days} days remaining this month.')
            return redirect('wfh_request')
        
        # Create WFH request
        WFHRequest.objects.create(
            employee=request.user,
            start_date=start_date_obj,
            end_date=end_date_obj,
            reason=reason
        )
        
        # Notify HR
        hr_users = User.objects.filter(
            Q(employeeprofile__is_hr=True) | Q(is_superuser=True)
        )
        for hr_user in hr_users:
            Notification.objects.create(
                employee=hr_user,
                message=f'{request.user.get_full_name() or request.user.username} has requested WFH from {start_date_obj.strftime("%b %d")} to {end_date_obj.strftime("%b %d, %Y")}'
            )
        
        # Log action
        log_action(request.user, 'wfh_request', f'Requested WFH from {start_date_obj} to {end_date_obj}', request)
        
        messages.success(request, 'WFH request submitted successfully!')
        return redirect('wfh_request')
    
    # Get user's WFH requests
    wfh_requests = WFHRequest.objects.filter(
        employee=request.user
    ).order_by('-created_at')
    
    # Calculate remaining WFH days for current month
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    # Get approved WFH days for current month
    from datetime import date
    month_start = date(current_year, current_month, 1)
    if current_month == 12:
        month_end = date(current_year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(current_year, current_month + 1, 1) - timedelta(days=1)
    
    approved_wfh = WFHRequest.objects.filter(
        employee=request.user,
        status='approved',
        start_date__lte=month_end,
        end_date__gte=month_start
    )
    
    # Calculate actual days used in current month
    used_days = 0
    for wfh in approved_wfh:
        # Calculate overlap with current month
        overlap_start = max(wfh.start_date, month_start)
        overlap_end = min(wfh.end_date, month_end)
        if overlap_start <= overlap_end:
            used_days += (overlap_end - overlap_start).days + 1
    
    remaining_days = max(0, 5 - used_days)
    
    context = {
        'wfh_requests': wfh_requests,
        'used_days': used_days,
        'remaining_days': remaining_days,
        'total_allowed': 5,
    }
    
    return render(request, 'wfh_request.html', context)


# =========================
# CANCEL WFH
# =========================
@login_required
def cancel_wfh(request, wfh_id):
    if request.method == 'POST':
        wfh = get_object_or_404(WFHRequest, id=wfh_id, employee=request.user)
        if wfh.status == 'pending':
            wfh.delete()
            log_action(request.user, 'wfh_cancel', f'Cancelled WFH request from {wfh.start_date} to {wfh.end_date}', request)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})


# =========================
# WFH APPROVAL (HR ONLY)
# =========================
@login_required
def wfh_approval(request):
    # Only HR or superuser can access
    if not request.user.is_superuser:
        try:
            if not request.user.employeeprofile.is_hr:
                messages.error(request, 'Access denied. HR only.')
                return redirect('dashboard')
        except EmployeeProfile.DoesNotExist:
            messages.error(request, 'Profile not found.')
            return redirect('dashboard')
    
    if request.method == 'POST':
        wfh_id = request.POST.get('wfh_id')
        action = request.POST.get('action')
        hr_comment = request.POST.get('hr_comment', '')
        
        wfh = get_object_or_404(WFHRequest, id=wfh_id)
        
        if action == 'approve':
            wfh.status = 'approved'
            wfh.hr_approver = request.user
            wfh.hr_comment = hr_comment
            wfh.save()
            
            # Send notification to employee
            Notification.objects.create(
                employee=wfh.employee,
                message=f'Your WFH request from {wfh.start_date.strftime("%b %d")} to {wfh.end_date.strftime("%b %d, %Y")} has been approved.'
            )
            
            # Log action
            log_action(request.user, 'wfh_approve', f'Approved WFH request for {wfh.employee.username} from {wfh.start_date} to {wfh.end_date}', request, target_user=wfh.employee)
            
            messages.success(request, 'WFH request approved successfully!')
        
        elif action == 'reject':
            wfh.status = 'rejected'
            wfh.hr_approver = request.user
            wfh.hr_comment = hr_comment
            wfh.save()
            
            # Send notification to employee
            Notification.objects.create(
                employee=wfh.employee,
                message=f'Your WFH request from {wfh.start_date.strftime("%b %d")} to {wfh.end_date.strftime("%b %d, %Y")} has been rejected.'
            )
            
            # Log action
            log_action(request.user, 'wfh_reject', f'Rejected WFH request for {wfh.employee.username} from {wfh.start_date} to {wfh.end_date}', request, target_user=wfh.employee)
            
            messages.warning(request, 'WFH request rejected.')
        
        return redirect('wfh_approval')
    
    # Get pending WFH requests
    pending_wfh = WFHRequest.objects.filter(
        status='pending'
    ).select_related('employee').order_by('-created_at')
    
    # Get all WFH records
    all_wfh = WFHRequest.objects.all().select_related('employee', 'hr_approver').order_by('-created_at')[:50]
    
    context = {
        'pending_wfh': pending_wfh,
        'all_wfh': all_wfh,
    }
    
    return render(request, 'wfh_approval.html', context)
