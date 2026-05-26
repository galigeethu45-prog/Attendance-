from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import datetime, timedelta, time as dt_time
from .models import Attendance, BreakLog, Notification, BREAK_RULES, LeaveRequest, EmployeeProfile, Overtime, AuditLog, WFHRequest, EmployeeMasterData, SystemSettings
from django.contrib.auth.models import User


def get_local_today():
    """Get today's date in the local timezone (Asia/Kolkata).
    When USE_TZ=True, timezone.now() returns UTC time.
    We need to convert to local time before extracting the date,
    otherwise after midnight IST (but before midnight UTC) we get yesterday's date.
    """
    return timezone.localtime(timezone.now()).date()


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
    Check if user is accessing from office network
    Now reads allowed IPs from database (SystemSettings model)
    
    This allows HR to manage office IPs without code changes or server restart
    """
    if request is None:
        return False
    
    client_ip = get_client_ip(request)
    
    # Get allowed IPs from database
    from attendance.models import SystemSettings
    settings = SystemSettings.get_settings()
    allowed_ips = settings.get_active_office_ips()
    
    # Fallback to hardcoded IP if database is empty (safety measure)
    if not allowed_ips:
        print("⚠️ WARNING: No office IPs configured in database, using fallback")
        allowed_ips = ['14.195.138.241']  # Fallback to original IP
    
    # Check if client IP matches any allowed office IP
    is_office = client_ip in allowed_ips
    
    # Debug logging
    if not is_office:
        print(f"Access denied - Client IP: {client_ip} not in allowed office IPs: {allowed_ips}")
    else:
        print(f"✅ Access granted - Client IP: {client_ip} matches office network")
    
    return is_office


def has_approved_wfh_today(user):
    """
    Check if user has approved WFH for today
    Returns: Boolean
    """
    today = get_local_today()
    
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
    0. EMERGENCY OVERRIDE: If enabled by HR, everyone can check-in from anywhere
    1. HR/Admin can check-in from anywhere (bypass all restrictions)
    2. Hybrid/Permanent WFH employees can check-in from anywhere
    3. Regular office employees MUST be either:
       a) On office network (Regus IP), OR
       b) Have approved WFH for today
    
    Returns: (Boolean, String) - (can_check_in, reason)
    """
    # Import here to avoid circular import
    from .models import SystemSettings
    
    # RULE 0: EMERGENCY OVERRIDE - Bypass all restrictions
    if SystemSettings.is_emergency_override_active():
        return (True, "🚨 Emergency Override Active - Network restrictions bypassed")
    
    # RULE 1: HR/Admin bypass all network restrictions
    try:
        if user.is_superuser or user.employeeprofile.is_hr:
            return (True, "HR/Admin - No restrictions")
    except EmployeeProfile.DoesNotExist:
        # If no profile, check if superuser
        if user.is_superuser:
            return (True, "Admin - No restrictions")
    
    # RULE 2: Check work mode (hybrid/permanent WFH bypass IP restrictions)
    try:
        profile = user.employeeprofile
        if profile.work_mode == 'hybrid':
            return (True, "Hybrid mode - Can work from anywhere")
        elif profile.work_mode == 'permanent_wfh':
            return (True, "Permanent WFH - Can work from anywhere")
    except EmployeeProfile.DoesNotExist:
        pass  # Continue to regular checks
    
    # RULE 3a: Check if on office network (Regus)
    if is_on_office_network(request):
        return (True, "Office network (Regus)")
    
    # RULE 3b: Check if has approved WFH for today
    if has_approved_wfh_today(user):
        return (True, "Approved WFH - Can work from anywhere")
    
    # Not allowed - provide detailed error message
    client_ip = get_client_ip(request) if request else "Unknown"
    settings = SystemSettings.get_settings()
    allowed_ips = settings.get_active_office_ips()
    
    # Build detailed error message
    error_msg = f"❌ Network Check Failed\n\n"
    error_msg += f"Your IP: {client_ip}\n"
    error_msg += f"Allowed IPs: {', '.join(allowed_ips) if allowed_ips else 'None configured'}\n\n"
    
    # Check if running on localhost
    if client_ip in ['127.0.0.1', '::1', 'localhost']:
        error_msg += "⚠️ LOCALHOST DETECTED: You're running Django locally. "
        error_msg += "The system sees your IP as 127.0.0.1 (localhost), not your public IP. "
        error_msg += "Solutions:\n"
        error_msg += "1. Ask HR to enable Emergency Override for testing\n"
        error_msg += "2. Deploy to a public server (AWS, Heroku, etc.) to use real IP checking\n"
        error_msg += "3. Submit a WFH request and get it approved"
    else:
        error_msg += "You must be on office WiFi (Regus) or have approved WFH to check-in."
    
    return (False, error_msg)


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
    # Store user info before logout
    user = request.user
    username = user.username if user.is_authenticated else 'Unknown'
    
    # Log the action BEFORE logout (while user is still authenticated)
    if user.is_authenticated:
        log_action(user, 'logout', f'User logged out', request)
    
    # Now logout
    logout(request)
    
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

# =========================
# DASHBOARD
# =========================
@login_required
def dashboard(request):
    today = get_local_today()
    current_month = timezone.localtime(timezone.now()).month
    current_year = timezone.localtime(timezone.now()).year
    
    # Check if user is manager
    is_manager = False
    try:
        profile = request.user.employeeprofile
        is_manager = profile.role == 'manager'
    except EmployeeProfile.DoesNotExist:
        pass
    
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
    
    # Manager-specific data
    pending_leave_approvals = 0
    pending_wfh_approvals = 0
    pending_onsite_approvals = 0
    
    if is_manager:
        # Count ALL pending approvals (parallel workflow - manager sees all)
        pending_leave_approvals = LeaveRequest.objects.filter(
            status='pending'
        ).count()
        
        pending_wfh_approvals = WFHRequest.objects.filter(
            status='pending'
        ).count()
        
        from .models import OnsiteRequest
        pending_onsite_approvals = OnsiteRequest.objects.filter(
            status='pending'
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
    
    # Check for approved onsite request for today
    from .models import OnsiteRequest
    approved_onsite_today = OnsiteRequest.objects.filter(
        employee=request.user,
        visit_date=today,
        status='approved'
    ).first()
    
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
        'approved_onsite_today': approved_onsite_today,
        'is_manager': is_manager,
        'pending_leave_approvals': pending_leave_approvals,
        'pending_wfh_approvals': pending_wfh_approvals,
        'pending_onsite_approvals': pending_onsite_approvals,
    }
    
    return render(request, 'dashboard.html', context)


# =========================
# CHECK IN
# =========================
@login_required
def check_in(request):
    if request.method == 'POST':
        today = get_local_today()
        
        # HOLIDAY CHECK: Check if today is a holiday
        from attendance.models import CompanyHoliday
        is_holiday, holiday = CompanyHoliday.is_holiday(today)
        
        if is_holiday:
            # Check if user has approved OT for today
            approved_ot = Overtime.objects.filter(
                employee=request.user,
                date=today,
                status='approved'
            ).exists()
            
            if not approved_ot:
                # No OT approval - show warning but allow check-in
                messages.warning(request, f'⚠️ Today is a holiday: {holiday.name}')
                messages.info(request, 'You don\'t have approved OT for today. This will be counted as a regular working day.')
                messages.info(request, 'If you need to work on a holiday, please request OT approval first.')
                # Continue with check-in (count as normal day)
            else:
                messages.info(request, f'✅ Holiday OT: Working on {holiday.name} with approved overtime.')
        
        # Validate location/network
        can_check_in, reason = can_check_in_from_location(request.user, request)
        
        if not can_check_in:
            # Display detailed error message (preserve line breaks)
            for line in reason.split('\n'):
                if line.strip():
                    if '❌' in line or '⚠️' in line:
                        messages.error(request, line)
                    else:
                        messages.warning(request, line)
            return redirect('dashboard')
        
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
                    try:
                        employee_id = request.user.employeeprofile.employee_id
                    except:
                        employee_id = request.user.username
                    Notification.objects.create(
                        employee=hr_user,
                        message=f'{request.user.get_full_name() or request.user.username} (ID: {employee_id}) checked in late at {check_in_time.strftime("%I:%M %p")} - Marked as half-day'
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
            # Display detailed error message (preserve line breaks)
            for line in reason.split('\n'):
                if line.strip():
                    if '❌' in line or '⚠️' in line:
                        messages.error(request, line)
                    else:
                        messages.warning(request, line)
            return redirect('dashboard')
        
        today = get_local_today()
        
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
        # Validate location/network (same as check-in/check-out)
        can_take_break, reason = can_check_in_from_location(request.user, request)
        
        if not can_take_break:
            # Display detailed error message (preserve line breaks)
            for line in reason.split('\n'):
                if line.strip():
                    if '❌' in line or '⚠️' in line:
                        messages.error(request, line)
                    else:
                        messages.warning(request, line)
            return redirect('dashboard')
        
        today = get_local_today()
        
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
        
        # Check for approved onsite request for today (enables flexible breaks)
        from .models import OnsiteRequest
        has_onsite_today = OnsiteRequest.objects.filter(
            employee=request.user,
            visit_date=today,
            status='approved'
        ).exists()
        
        # No breaks after 5 PM (enforced even with onsite request)
        if current_hour >= 17:
            messages.error(request, 'Breaks are not allowed after 5:00 PM.')
            return redirect('dashboard')
        
        # Determine time slot
        time_slot = 'morning'
        
        # Tea break: 10:00 AM - 11:00 AM OR 4:00 PM - 4:45 PM
        if break_type == 'tea':
            is_morning = (10 <= current_hour < 11)
            is_evening = (current_hour == 16 and current_minute <= 45)
            
            # If NOT in time window AND no onsite request, deny break
            if not (is_morning or is_evening) and not has_onsite_today:
                messages.error(request, 'Tea break is only allowed between 10:00 AM - 11:00 AM or 4:00 PM - 4:45 PM.')
                return redirect('dashboard')
            
            # Set time slot (use 'flexible' if outside normal windows with onsite)
            if has_onsite_today and not (is_morning or is_evening):
                time_slot = 'flexible'
            else:
                time_slot = 'morning' if is_morning else 'evening'
            
            # Check if already taken break in this slot (still enforce limits)
            if time_slot != 'flexible':
                slot_break_count = BreakLog.objects.filter(
                    attendance=attendance,
                    break_type='tea',
                    time_slot=time_slot
                ).count()
                
                if slot_break_count >= 1:
                    slot_name = 'morning (10-11 AM)' if time_slot == 'morning' else 'evening (4-4:45 PM)'
                    messages.error(request, f'You have already taken your {slot_name} tea break today.')
                    return redirect('dashboard')
            else:
                # For flexible breaks, check total tea count (max 2 per day)
                total_tea_count = BreakLog.objects.filter(
                    attendance=attendance,
                    break_type='tea'
                ).count()
                
                if total_tea_count >= 2:
                    messages.error(request, 'You have already taken 2 tea breaks today (maximum allowed).')
                    return redirect('dashboard')
        
        # Lunch break: 1:00 PM - 1:45 PM
        elif break_type == 'lunch':
            # If NOT in time window AND no onsite request, deny break
            if not (current_hour == 13 and current_minute <= 45) and not has_onsite_today:
                messages.error(request, 'Lunch break is only allowed between 1:00 PM and 1:45 PM.')
                return redirect('dashboard')
            
            # Set time slot (use 'flexible' if outside normal window with onsite)
            if has_onsite_today and not (current_hour == 13 and current_minute <= 45):
                time_slot = 'flexible'
            else:
                time_slot = 'afternoon'
            
            # Check if already taken lunch (still enforce 1 lunch per day limit)
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
        new_break = BreakLog.objects.create(
            attendance=attendance,
            break_type=break_type,
            time_slot=time_slot,
            break_start=timezone.now()
        )
        
        # Log flexible break usage if applicable
        if time_slot == 'flexible':
            log_action(request.user, 'flexible_break_start', 
                      f'Started flexible {break_type} break during onsite visit', request)
            messages.success(request, f'{break_type.title()} break started (flexible timing for onsite visit).')
        else:
            messages.success(request, f'{break_type.title()} break started.')
    
    return redirect('dashboard')


# =========================
# END BREAK
# =========================
@login_required
def end_break(request):
    if request.method == 'POST':
        # Validate location/network (same as check-in/check-out)
        can_end_break, reason = can_check_in_from_location(request.user, request)
        
        if not can_end_break:
            messages.error(request, f'Break end is only allowed from office network or with approved WFH.')
            messages.info(request, reason)
            return redirect('dashboard')
        
        today = get_local_today()
        
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
                try:
                    employee_id = request.user.employeeprofile.employee_id
                except:
                    employee_id = request.user.username
                Notification.objects.create(
                    employee=hr_user,
                    message=f'{request.user.get_full_name() or request.user.username} (ID: {employee_id}) took a long {active_break.get_break_type_display()} break: {active_break.duration_minutes} minutes (limit: {active_break.allowed_minutes()} mins)'
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
        from attendance.validators import DateValidator, FieldValidator, OverlapValidator
        
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        selected_dates_json = request.POST.get('selected_dates')
        reason = request.POST.get('reason')
        
        # Validate leave type
        valid_types = ['sick', 'casual', 'earned', 'menstrual', 'unpaid']
        is_valid, error = FieldValidator.validate_choice(leave_type, valid_types, "leave type")
        if not is_valid:
            messages.error(request, error)
            return redirect('leave_request')
        
        # Validate reason
        is_valid, error = FieldValidator.validate_required(reason, "Reason")
        if not is_valid:
            messages.error(request, error)
            return redirect('leave_request')
        
        is_valid, error = FieldValidator.validate_length(reason, min_length=10, max_length=500, field_name="Reason")
        if not is_valid:
            messages.error(request, error)
            return redirect('leave_request')
        
        # Parse and validate selected dates if provided
        selected_dates = None
        start_date_obj = None
        end_date_obj = None
        
        if selected_dates_json:
            selected_dates, error = DateValidator.parse_and_validate_selected_dates(selected_dates_json)
            if error:
                messages.error(request, error)
                return redirect('leave_request')
            
            # Set start_date and end_date to first and last selected dates for backward compatibility
            if selected_dates:
                from datetime import datetime as dt
                start_date_obj = dt.strptime(selected_dates[0], '%Y-%m-%d').date()
                end_date_obj = dt.strptime(selected_dates[-1], '%Y-%m-%d').date()
        else:
            # Validate date range
            is_valid, error = FieldValidator.validate_required(start_date, "Start date")
            if not is_valid:
                messages.error(request, error)
                return redirect('leave_request')
            
            is_valid, error = FieldValidator.validate_required(end_date, "End date")
            if not is_valid:
                messages.error(request, error)
                return redirect('leave_request')
            
            is_valid, error = DateValidator.validate_date_format(start_date, "Start date")
            if not is_valid:
                messages.error(request, error)
                return redirect('leave_request')
            
            is_valid, error = DateValidator.validate_date_format(end_date, "End date")
            if not is_valid:
                messages.error(request, error)
                return redirect('leave_request')
            
            try:
                from datetime import datetime as dt
                start_date_obj = dt.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = dt.strptime(end_date, '%Y-%m-%d').date()
                
                is_valid, error = DateValidator.validate_future_date(start_date_obj, "Start date")
                if not is_valid:
                    messages.error(request, error)
                    return redirect('leave_request')
                
                is_valid, error = DateValidator.validate_date_range(start_date_obj, end_date_obj)
                if not is_valid:
                    messages.error(request, error)
                    return redirect('leave_request')
            except ValueError:
                messages.error(request, 'Invalid date format.')
                return redirect('leave_request')
        
        # Check for overlapping leave requests
        is_valid, error = OverlapValidator.check_leave_overlap(
            request.user, start_date_obj, end_date_obj, selected_dates
        )
        if not is_valid:
            messages.error(request, error)
            return redirect('leave_request')
        
        # Create leave request
        leave_req = LeaveRequest.objects.create(
            employee=request.user,
            leave_type=leave_type,
            start_date=start_date_obj,
            end_date=end_date_obj,
            selected_dates=selected_dates,  # Store JSON array or None
            reason=reason
        )
        
        # Notify Team Leaders about new leave request
        team_leaders = User.objects.filter(employeeprofile__role='tl')
        for tl in team_leaders:
            Notification.objects.create(
                employee=tl,
                message=f'New leave request from {request.user.get_full_name() or request.user.username} - {leave_type.title()} for {leave_req.total_days} days'
            )
        
        # Log action
        log_action(request.user, 'leave_request', 
                  f'Submitted {leave_type} leave request for {leave_req.total_days} days', request)
        
        messages.success(request, f'Leave request submitted successfully for {leave_req.total_days} days!')
        return redirect('leave_request')
    
    # Get user's leave requests
    leave_requests = LeaveRequest.objects.filter(
        employee=request.user
    ).order_by('-created_at')
    
    # Calculate leave balance
    try:
        current_year = timezone.localtime(timezone.now()).year
        current_month = timezone.localtime(timezone.now()).month
        
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
# LEAVE APPROVAL (HIERARCHICAL)
# =========================
@login_required
def leave_approval(request):
    """
    Parallel approval view - ALL approvers see ALL pending requests
    TL, Manager, and HR can all see and act on requests simultaneously
    Each role adds their comment/approval independently
    """
    from attendance.validators import PermissionValidator
    
    # Validate permission
    if not PermissionValidator.can_approve_leave(request.user):
        messages.error(request, 'Access denied. You do not have permission to approve leave requests.')
        return redirect('dashboard')
    
    # Check user role
    try:
        profile = request.user.employeeprofile
        user_role = profile.role
    except EmployeeProfile.DoesNotExist:
        # If no profile, check if superuser
        if request.user.is_superuser:
            user_role = 'hr'
        else:
            messages.error(request, 'Access denied. Profile not found.')
            return redirect('dashboard')
    
    # Only TL, Manager, and HR can access
    if user_role not in ['team_leader', 'manager', 'hr'] and not request.user.is_superuser:
        messages.error(request, 'Access denied. This page is for Team Leaders, Managers, and HR only.')
        return redirect('dashboard')
    
    # Get filter parameter (default: pending)
    status_filter = request.GET.get('status', 'pending')
    
    # PARALLEL WORKFLOW: Show requests based on status filter
    if status_filter == 'pending':
        if user_role == 'team_leader':
            # TL sees all pending requests where they haven't commented yet
            requests = LeaveRequest.objects.filter(
                status='pending',
                tl_comment__isnull=True
            ).select_related('employee', 'employee__employeeprofile').order_by('-created_at')
            
        elif user_role == 'manager':
            # Manager sees all pending requests where they haven't approved/rejected yet
            requests = LeaveRequest.objects.filter(
                status='pending',
                manager_comment__isnull=True
            ).select_related('employee', 'employee__employeeprofile', 'tl_approver').order_by('-created_at')
            
        else:  # HR or superuser
            # HR sees all pending requests where they haven't made final decision yet
            requests = LeaveRequest.objects.filter(
                status='pending'
            ).select_related('employee', 'employee__employeeprofile', 'tl_approver', 'manager_approver').order_by('-created_at')
    
    elif status_filter == 'approved':
        # Show approved requests
        requests = LeaveRequest.objects.filter(
            status='approved'
        ).select_related('employee', 'employee__employeeprofile', 'tl_approver', 'manager_approver').order_by('-created_at')
    
    elif status_filter == 'rejected':
        # Show rejected requests
        requests = LeaveRequest.objects.filter(
            status='rejected'
        ).select_related('employee', 'employee__employeeprofile', 'tl_approver', 'manager_approver').order_by('-created_at')
    
    else:  # 'all'
        # Show all requests
        requests = LeaveRequest.objects.all().select_related(
            'employee', 'employee__employeeprofile', 'tl_approver', 'manager_approver'
        ).order_by('-created_at')
    
    # Count for badges
    pending_count = LeaveRequest.objects.filter(status='pending').count()
    approved_count = LeaveRequest.objects.filter(status='approved').count()
    rejected_count = LeaveRequest.objects.filter(status='rejected').count()
    
    context = {
        'requests': requests,
        'user_role': user_role,
        'status_filter': status_filter,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    
    return render(request, 'leave_approval.html', context)


# =========================
# LEAVE ACTION (PARALLEL WORKFLOW)
# =========================
@login_required
def leave_action(request, leave_id, action):
    """
    Handle leave approval actions based on user role - PARALLEL WORKFLOW
    TL: Add comment (advisory only)
    Manager: Add comment (advisory only)
    HR: Final Approve/Reject (has final authority, can approve/reject regardless of TL/Manager input)
    
    Status changes:
    - Request stays 'pending' until HR makes final decision
    - HR can approve or reject anytime (TL/Manager comments are advisory only)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    
    # Check user role
    try:
        profile = request.user.employeeprofile
        user_role = profile.role
    except EmployeeProfile.DoesNotExist:
        if request.user.is_superuser:
            user_role = 'hr'
        else:
            return JsonResponse({'success': False, 'error': 'Access denied'})
    
    # Get comment from request
    comment = request.POST.get('comment', '').strip()
    
    # Team Leader action - Add comment (PARALLEL - doesn't block others)
    if (user_role == 'team_leader' or user_role == 'tl') and action == 'comment':
        # Comment is optional
        leave.tl_comment = comment if comment else 'Reviewed by TL'
        leave.tl_approver = request.user
        leave.tl_approved_at = timezone.now()
        leave.tl_approved = True
        leave.save()
        
        # Notify employee
        Notification.objects.create(
            employee=leave.employee,
            message=f'Your leave request has been reviewed by Team Leader: {comment[:50]}...'
        )
        
        # Log action
        log_action(request.user, 'leave_tl_comment', 
                  f'Added TL comment for {leave.employee.username}\'s leave request', request, leave.employee)
        
        return JsonResponse({'success': True, 'message': 'Comment added successfully'})
    
    # Manager action - Approve or Reject (PARALLEL - doesn't require TL comment)
    elif user_role == 'manager' and action in ['approve', 'reject', 'comment']:
        # Comment is optional
        leave.manager_comment = comment if comment else 'Reviewed by Manager'
        leave.manager_approver = request.user
        leave.manager_approved_at = timezone.now()
        
        if action == 'comment':
            # Manager only adds comment - no approval/rejection
            leave.save()
            
            # Notify employee
            if comment:
                Notification.objects.create(
                    employee=leave.employee,
                    message=f'Manager added a comment on your leave request: {comment[:50]}...'
                )
            
            # Log action
            log_action(request.user, 'leave_approve', 
                      f'Added Manager comment for {leave.employee.username}\'s leave request', request, leave.employee)
            
            return JsonResponse({'success': True, 'message': 'Comment added successfully'})
        
        elif action == 'approve':
            leave.manager_approved = True
            leave.save()
            
            # Notify employee
            Notification.objects.create(
                employee=leave.employee,
                message=f'Your leave request has been approved by Manager: {comment[:50]}...'
            )
            
            # Notify HR
            hr_users = User.objects.filter(Q(employeeprofile__is_hr=True) | Q(is_superuser=True))
            for hr_user in hr_users:
                Notification.objects.create(
                    employee=hr_user,
                    message=f'Leave request from {leave.employee.get_full_name() or leave.employee.username} approved by Manager - ready for final approval'
                )
            
            # Log action
            log_action(request.user, 'leave_manager_approve', 
                      f'Approved {leave.employee.username}\'s leave request (Manager level)', request, leave.employee)
            
            return JsonResponse({'success': True, 'message': 'Leave approved at Manager level'})
        else:  # reject
            leave.manager_approved = False
            leave.save()
            
            # Notify employee
            Notification.objects.create(
                employee=leave.employee,
                message=f'Your leave request has been rejected by Manager: {comment}'
            )
            
            # Log action
            log_action(request.user, 'leave_manager_reject', 
                      f'Rejected {leave.employee.username}\'s leave request (Manager level)', request, leave.employee)
            
            return JsonResponse({'success': True, 'message': 'Leave rejected by Manager'})
    
    # HR action - Final Approve or Reject (HR has full authority)
    elif user_role == 'hr' and action in ['approve', 'reject']:
        # Comment is optional for HR
        leave.hr_comment = comment if comment else ''
        
        if action == 'approve':
            # HR can approve any leave type directly (no manager approval needed)
            leave.status = 'approved'
            leave.save()
            
            comment_text = f': {comment}' if comment else ''
            Notification.objects.create(
                employee=leave.employee,
                message=f'Your leave request has been APPROVED by HR{comment_text}'
            )
            
            # Notify manager and TL
            if leave.manager_approver:
                Notification.objects.create(
                    employee=leave.manager_approver,
                    message=f'Leave request for {leave.employee.get_full_name() or leave.employee.username} has been approved by HR'
                )
            if leave.tl_approver:
                Notification.objects.create(
                    employee=leave.tl_approver,
                    message=f'Leave request for {leave.employee.get_full_name() or leave.employee.username} has been approved by HR'
                )
            
            # Log action
            log_action(request.user, 'leave_hr_approve', 
                      f'Approved {leave.employee.username}\'s leave request (Final)', request, leave.employee)
            
            return JsonResponse({'success': True, 'message': 'Leave approved (Final)'})
        else:  # reject
            leave.status = 'rejected'
            leave.save()
            
            # Notify employee
            comment_text = f': {comment}' if comment else ''
            Notification.objects.create(
                employee=leave.employee,
                message=f'Your leave request has been rejected by HR{comment_text}'
            )
            
            # Notify manager
            if leave.manager_approver:
                Notification.objects.create(
                    employee=leave.manager_approver,
                    message=f'Leave request for {leave.employee.get_full_name() or leave.employee.username} has been rejected by HR'
                )
            
            # Log action
            log_action(request.user, 'leave_hr_reject', 
                      f'Rejected {leave.employee.username}\'s leave request (Final)', request, leave.employee)
            
            return JsonResponse({'success': True, 'message': 'Leave rejected'})
    
    return JsonResponse({'success': False, 'error': 'Invalid action or insufficient permissions'})


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
            # Handle profile photo removal
            if request.POST.get('remove_photo') == 'true':
                if employee_profile.profile_photo:
                    try:
                        employee_profile.profile_photo.delete(save=False)
                    except:
                        pass
                    employee_profile.profile_photo = None
            # Handle profile photo upload
            elif 'profile_photo' in request.FILES:
                # Delete old photo if exists
                if employee_profile.profile_photo:
                    try:
                        employee_profile.profile_photo.delete(save=False)
                    except:
                        pass
                employee_profile.profile_photo = request.FILES['profile_photo']
            
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
    
    today = get_local_today()
    
    # Check if today is a holiday
    from attendance.models import CompanyHoliday
    is_today_holiday, holiday_obj = CompanyHoliday.is_holiday(today)
    
    # Statistics
    total_employees = User.objects.filter(is_active=True).count()
    today_attendance = Attendance.objects.filter(date=today)
    present_today = today_attendance.filter(check_in__isnull=False).count()
    late_arrivals = today_attendance.filter(status__in=['late', 'half-day']).count()
    
    # Count employees on approved leave today
    leave_today = LeaveRequest.objects.filter(
        status='approved',
        start_date__lte=today,
        end_date__gte=today
    ).count()
    
    # Count employees on approved WFH today
    wfh_today = WFHRequest.objects.filter(
        status='approved',
        start_date__lte=today,
        end_date__gte=today
    ).count()
    
    # Calculate absent - Simple logic
    # Absent = employees who didn't check-in AND don't have leave/WFH approval
    checked_in_ids = today_attendance.filter(check_in__isnull=False).values_list('employee_id', flat=True)
    leave_ids = LeaveRequest.objects.filter(
        status='approved',
        start_date__lte=today,
        end_date__gte=today
    ).values_list('employee_id', flat=True)
    wfh_ids = WFHRequest.objects.filter(
        status='approved',
        start_date__lte=today,
        end_date__gte=today
    ).values_list('employee_id', flat=True)
    
    # Get all employee IDs
    all_employee_ids = User.objects.filter(is_active=True).values_list('id', flat=True)
    
    # Absent = all employees - (checked-in + leave + wfh)
    absent_ids = set(all_employee_ids) - set(checked_in_ids) - set(leave_ids) - set(wfh_ids)
    absent_today = len(absent_ids)
    
    pending_leaves = LeaveRequest.objects.filter(status='pending').count()
    
    # Attendance Filtering (NEW)
    attendance_filter_type = request.GET.get('attendance_filter', 'today')  # today, date_range, month, year
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    filter_month = request.GET.get('filter_month', '')
    filter_year = request.GET.get('filter_year', '')
    
    # Build attendance query based on filter
    if attendance_filter_type == 'date_range' and start_date and end_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            today_attendance_list = Attendance.objects.filter(
                date__range=[start_date_obj, end_date_obj]
            ).select_related('employee', 'employee__employeeprofile').order_by('-date', 'check_in')
        except ValueError:
            today_attendance_list = Attendance.objects.filter(date=today).select_related('employee', 'employee__employeeprofile').order_by('check_in')
    elif attendance_filter_type == 'month' and filter_month and filter_year:
        try:
            month_num = int(filter_month)
            year_num = int(filter_year)
            today_attendance_list = Attendance.objects.filter(
                date__month=month_num,
                date__year=year_num
            ).select_related('employee', 'employee__employeeprofile').order_by('-date', 'check_in')
        except ValueError:
            today_attendance_list = Attendance.objects.filter(date=today).select_related('employee', 'employee__employeeprofile').order_by('check_in')
    elif attendance_filter_type == 'year' and filter_year:
        try:
            year_num = int(filter_year)
            today_attendance_list = Attendance.objects.filter(
                date__year=year_num
            ).select_related('employee', 'employee__employeeprofile').order_by('-date', 'check_in')
        except ValueError:
            today_attendance_list = Attendance.objects.filter(date=today).select_related('employee', 'employee__employeeprofile').order_by('check_in')
    else:
        # Default: Today's attendance
        today_attendance_list = Attendance.objects.filter(
            date=today
        ).select_related('employee', 'employee__employeeprofile').order_by('check_in')
    
    # Pending leave requests
    pending_leave_requests = LeaveRequest.objects.filter(
        status='pending'
    ).select_related('employee').order_by('-created_at')
    
    # Break Logs with filters
    break_period = request.GET.get('break_period', 'week')  # Default to week instead of today
    employee_search = request.GET.get('employee_search', '')
    
    break_logs = BreakLog.objects.select_related(
        'attendance__employee__employeeprofile'
    ).order_by('-break_start')
    
    # Get IST timezone
    import pytz
    local_tz = pytz.timezone('Asia/Kolkata')
    
    # Apply period filter
    if break_period == 'today':
        # Use timezone-aware date range for today in IST
        today_start = timezone.datetime.combine(today, timezone.datetime.min.time())
        today_end = timezone.datetime.combine(today, timezone.datetime.max.time())
        today_start = local_tz.localize(today_start)
        today_end = local_tz.localize(today_end)
        break_logs = break_logs.filter(break_start__range=(today_start, today_end))
    elif break_period == 'week':
        week_start = today - timedelta(days=today.weekday())
        week_start_dt = timezone.datetime.combine(week_start, timezone.datetime.min.time())
        week_start_dt = local_tz.localize(week_start_dt)
        break_logs = break_logs.filter(break_start__gte=week_start_dt)
    elif break_period == 'month':
        month_start = today.replace(day=1)
        month_start_dt = timezone.datetime.combine(month_start, timezone.datetime.min.time())
        month_start_dt = local_tz.localize(month_start_dt)
        break_logs = break_logs.filter(break_start__gte=month_start_dt)
    # else: all time (no filter)
    
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
    
    # Office IP Management
    from attendance.models import SystemSettings
    settings = SystemSettings.get_settings()
    office_ips = settings.office_ips or []
    current_ip = get_client_ip(request)
    
    # Detect if running on localhost
    is_localhost = current_ip in ['127.0.0.1', '::1', 'localhost']
    
    context = {
        'total_employees': total_employees,
        'present_today': present_today,
        'absent_today': absent_today,
        'late_arrivals': late_arrivals,
        'leave_today': leave_today,  # NEW
        'wfh_today': wfh_today,  # NEW
        'pending_leaves': pending_leaves,
        'today_attendance': today_attendance_list,
        'pending_leave_requests': pending_leave_requests,
        'break_logs': break_logs,
        'break_period': break_period,  # Add this for template
        'employee_search': employee_search,  # Add this for template
        'current_date': timezone.now(),
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'dept_labels': dept_labels,
        'dept_data': dept_data,
        'all_employees': all_employees,
        'departments': unique_departments,
        'audit_logs': audit_logs_page,
        # Attendance filter context
        'attendance_filter_type': attendance_filter_type,
        'start_date': start_date,
        'end_date': end_date,
        'filter_month': filter_month,
        'filter_year': filter_year,
        'available_years': range(2020, timezone.now().year + 2),  # Year dropdown
        # Office IP Management
        'office_ips': office_ips,
        'current_ip': current_ip,
        'is_localhost': is_localhost,
    }
    
    return render(request, 'hr_dashboard.html', context)


# =========================
# EXPORT ATTENDANCE CSV
# =========================
@login_required
def export_attendance_csv(request):
    """
    Export attendance records as CSV with comprehensive employee details
    """
    # Check if user is HR or superuser
    if not request.user.is_superuser:
        try:
            if not request.user.employeeprofile.is_hr:
                messages.error(request, 'Access denied. HR only.')
                return redirect('dashboard')
        except EmployeeProfile.DoesNotExist:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    
    import csv
    from django.http import HttpResponse
    
    # Get filter parameters
    filter_type = request.GET.get('filter_type', 'today')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    filter_month = request.GET.get('filter_month', '')
    filter_year = request.GET.get('filter_year', '')
    
    # Build query based on filter
    today = get_local_today()
    
    if filter_type == 'date_range' and start_date and end_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            attendance_records = Attendance.objects.filter(
                date__range=[start_date_obj, end_date_obj]
            ).select_related('employee', 'employee__employeeprofile').order_by('employee__username', 'date')
            filename_suffix = f"{start_date}_to_{end_date}"
        except ValueError:
            attendance_records = Attendance.objects.filter(date=today).select_related('employee', 'employee__employeeprofile').order_by('employee__username', 'date')
            filename_suffix = str(today)
    elif filter_type == 'month' and filter_month and filter_year:
        try:
            month_num = int(filter_month)
            year_num = int(filter_year)
            attendance_records = Attendance.objects.filter(
                date__month=month_num,
                date__year=year_num
            ).select_related('employee', 'employee__employeeprofile').order_by('employee__username', 'date')
            month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            filename_suffix = f"{month_names[month_num]}_{year_num}"
        except ValueError:
            attendance_records = Attendance.objects.filter(date=today).select_related('employee', 'employee__employeeprofile').order_by('employee__username', 'date')
            filename_suffix = str(today)
    elif filter_type == 'year' and filter_year:
        try:
            year_num = int(filter_year)
            attendance_records = Attendance.objects.filter(
                date__year=year_num
            ).select_related('employee', 'employee__employeeprofile').order_by('employee__username', 'date')
            filename_suffix = str(year_num)
        except ValueError:
            attendance_records = Attendance.objects.filter(date=today).select_related('employee', 'employee__employeeprofile').order_by('employee__username', 'date')
            filename_suffix = str(today)
    else:
        # Default: Today
        attendance_records = Attendance.objects.filter(date=today).select_related('employee', 'employee__employeeprofile').order_by('employee__username', 'date')
        filename_suffix = str(today)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_report_{filename_suffix}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Employee ID',
        'Employee Name',
        'Department',
        'Designation',
        'Date',
        'Check In',
        'Check Out',
        'Work Hours',
        'Status',
        'Break Count',
        'WFH Status',
        'Leave Type',
        'Work Mode',
    ])
    
    # Get all employees for summary
    all_employees = User.objects.filter(is_active=True).select_related('employeeprofile')
    
    # Write attendance data
    for attendance in attendance_records:
        try:
            profile = attendance.employee.employeeprofile
            employee_id = profile.employee_id or 'N/A'
            department = profile.department or 'N/A'
            designation = profile.designation or 'N/A'
            work_mode = profile.get_work_mode_display() if profile.work_mode else 'Office Only'
        except EmployeeProfile.DoesNotExist:
            employee_id = 'N/A'
            department = 'N/A'
            designation = 'N/A'
            work_mode = 'N/A'
        
        # Check WFH status for this date
        wfh_status = 'No'
        if WFHRequest.objects.filter(
            employee=attendance.employee,
            status='approved',
            start_date__lte=attendance.date,
            end_date__gte=attendance.date
        ).exists():
            wfh_status = 'Yes (Approved)'
        
        # Check leave for this date
        leave_type = 'N/A'
        leave_record = LeaveRequest.objects.filter(
            employee=attendance.employee,
            status='approved',
            start_date__lte=attendance.date,
            end_date__gte=attendance.date
        ).first()
        if leave_record:
            leave_type = leave_record.get_leave_type_display()
        
        # Break count
        break_count = BreakLog.objects.filter(attendance=attendance).count()
        
        writer.writerow([
            employee_id,
            attendance.employee.get_full_name() or attendance.employee.username,
            department,
            designation,
            attendance.date.strftime('%Y-%m-%d'),
            attendance.check_in.strftime('%I:%M %p') if attendance.check_in else 'Not Checked In',
            attendance.check_out.strftime('%I:%M %p') if attendance.check_out else 'Not Checked Out',
            attendance.get_work_hours_display(),
            attendance.get_status_display(),
            break_count,
            wfh_status,
            leave_type,
            work_mode,
        ])
    
    # Add summary section
    writer.writerow([])  # Empty row
    writer.writerow(['=== SUMMARY ==='])
    writer.writerow([])
    
    # Calculate summary for each employee
    writer.writerow(['Employee ID', 'Employee Name', 'Department', 'Present Days', 'Absent Days', 'Late Arrivals', 'Half Days', 'Total Hours', 'WFH Days', 'Leaves Taken'])
    
    for employee in all_employees:
        try:
            profile = employee.employeeprofile
            employee_id = profile.employee_id or 'N/A'
            department = profile.department or 'N/A'
        except EmployeeProfile.DoesNotExist:
            employee_id = 'N/A'
            department = 'N/A'
        
        # Filter attendance for this employee in the date range
        if filter_type == 'date_range' and start_date and end_date:
            emp_attendance = attendance_records.filter(employee=employee)
        elif filter_type == 'month' and filter_month and filter_year:
            emp_attendance = attendance_records.filter(employee=employee)
        elif filter_type == 'year' and filter_year:
            emp_attendance = attendance_records.filter(employee=employee)
        else:
            emp_attendance = attendance_records.filter(employee=employee)
        
        present_days = emp_attendance.filter(status='present').count()
        late_days = emp_attendance.filter(status='late').count()
        half_days = emp_attendance.filter(status='half-day').count()
        total_hours = emp_attendance.aggregate(Sum('total_work_hours'))['total_work_hours__sum'] or 0
        
        # Calculate absent days (working days - present days - holidays)
        from attendance.models import CompanyHoliday
        
        if filter_type == 'date_range' and start_date and end_date:
            # Count working days (excluding holidays)
            working_days = CompanyHoliday.count_working_days(start_date_obj, end_date_obj)
        elif filter_type == 'month' and filter_month and filter_year:
            # Count working days in the month
            import calendar
            from datetime import date
            month_start = date(year_num, month_num, 1)
            last_day = calendar.monthrange(year_num, month_num)[1]
            month_end = date(year_num, month_num, last_day)
            working_days = CompanyHoliday.count_working_days(month_start, month_end)
        elif filter_type == 'year' and filter_year:
            # Count working days in the year
            from datetime import date
            year_start = date(year_num, 1, 1)
            year_end = date(year_num, 12, 31)
            working_days = CompanyHoliday.count_working_days(year_start, year_end)
        else:
            # Single day - check if it's a working day
            working_days = 1 if CompanyHoliday.is_working_day(today) else 0
        
        attended_days = emp_attendance.count()
        
        # Get approved leave days for this period
        if filter_type == 'date_range' and start_date and end_date:
            leave_requests = LeaveRequest.objects.filter(
                employee=employee,
                status='approved',
                start_date__lte=end_date_obj,
                end_date__gte=start_date_obj
            )
            leave_days = sum([leave.total_days for leave in leave_requests])
        elif filter_type == 'month' and filter_month and filter_year:
            leave_requests = LeaveRequest.objects.filter(
                employee=employee,
                status='approved',
                start_date__month=month_num,
                start_date__year=year_num
            )
            leave_days = sum([leave.total_days for leave in leave_requests])
        elif filter_type == 'year' and filter_year:
            leave_requests = LeaveRequest.objects.filter(
                employee=employee,
                status='approved',
                start_date__year=year_num
            )
            leave_days = sum([leave.total_days for leave in leave_requests])
        else:
            leave_days = 0
        
        # Absent = Working Days - Attended Days - Leave Days
        # (This excludes holidays automatically since working_days already excludes them)
        absent_days = max(0, working_days - attended_days - leave_days)
        
        # WFH days
        if filter_type == 'date_range' and start_date and end_date:
            wfh_days = WFHRequest.objects.filter(
                employee=employee,
                status='approved',
                start_date__lte=end_date_obj,
                end_date__gte=start_date_obj
            ).count()
        elif filter_type == 'month' and filter_month and filter_year:
            wfh_days = WFHRequest.objects.filter(
                employee=employee,
                status='approved',
                start_date__month=month_num,
                start_date__year=year_num
            ).count()
        elif filter_type == 'year' and filter_year:
            wfh_days = WFHRequest.objects.filter(
                employee=employee,
                status='approved',
                start_date__year=year_num
            ).count()
        else:
            wfh_days = 0
        
        # Leaves taken
        if filter_type == 'date_range' and start_date and end_date:
            leaves = LeaveRequest.objects.filter(
                employee=employee,
                status='approved',
                start_date__lte=end_date_obj,
                end_date__gte=start_date_obj
            )
        elif filter_type == 'month' and filter_month and filter_year:
            leaves = LeaveRequest.objects.filter(
                employee=employee,
                status='approved',
                start_date__month=month_num,
                start_date__year=year_num
            )
        elif filter_type == 'year' and filter_year:
            leaves = LeaveRequest.objects.filter(
                employee=employee,
                status='approved',
                start_date__year=year_num
            )
        else:
            leaves = LeaveRequest.objects.filter(
                employee=employee,
                status='approved',
                start_date=today
            )
        
        leave_summary = ', '.join([f"{leave.get_leave_type_display()} ({leave.total_days}d)" for leave in leaves]) or 'None'
        
        writer.writerow([
            employee_id,
            employee.get_full_name() or employee.username,
            department,
            present_days,
            absent_days,
            late_days,
            half_days,
            f"{total_hours:.2f}h",
            wfh_days,
            leave_summary,
        ])
    
    return response


# =========================
# EMPLOYEE ATTENDANCE DASHBOARD (HR/MANAGER ONLY)
# =========================
@login_required
def employee_attendance_dashboard(request):
    """
    Comprehensive employee attendance dashboard for HR and Managers
    Shows attendance statistics per employee with filtering options
    """
    # Check if user is HR, Manager, or superuser
    is_authorized = False
    if request.user.is_superuser:
        is_authorized = True
    else:
        try:
            profile = request.user.employeeprofile
            if profile.is_hr or profile.role == 'manager':
                is_authorized = True
        except EmployeeProfile.DoesNotExist:
            pass
    
    if not is_authorized:
        messages.error(request, 'Access denied. HR or Manager access required.')
        return redirect('dashboard')
    
    # Get filter parameters
    employee_id_filter = request.GET.get('employee_id', '')
    department_filter = request.GET.get('department', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    export_csv = request.GET.get('export', '') == 'csv'
    
    # Default date range: current month
    today = get_local_today()
    if not start_date_str:
        start_date = today.replace(day=1)
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = today.replace(day=1)
    
    if not end_date_str:
        end_date = today
    else:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            end_date = today
    
    # Get all active employees
    employees_query = User.objects.filter(is_active=True).select_related('employeeprofile')
    
    # Apply filters
    if employee_id_filter:
        employees_query = employees_query.filter(employeeprofile__employee_id__icontains=employee_id_filter)
    
    if department_filter:
        employees_query = employees_query.filter(employeeprofile__department=department_filter)
    
    # Calculate statistics for each employee
    employee_stats = []
    total_present = 0
    total_absent = 0
    total_late = 0
    total_half_days = 0
    total_hours = 0
    
    for employee in employees_query:
        try:
            profile = employee.employeeprofile
            employee_id = profile.employee_id or 'N/A'
            department = profile.department or 'N/A'
            profile_photo = profile.profile_photo.url if profile.profile_photo else None
        except EmployeeProfile.DoesNotExist:
            employee_id = 'N/A'
            department = 'N/A'
            profile_photo = None
        
        # Get attendance records for date range
        attendance_records = Attendance.objects.filter(
            employee=employee,
            date__range=[start_date, end_date]
        )
        
        # Calculate statistics
        present_days = attendance_records.filter(status='present').count()
        late_days = attendance_records.filter(status='late').count()
        half_days = attendance_records.filter(status='half-day').count()
        
        # Total working days in range (excluding holidays, Sundays, 2nd/4th Saturdays)
        from attendance.models import CompanyHoliday
        working_days = CompanyHoliday.count_working_days(start_date, end_date)
        
        # WFH days (approved)
        wfh_requests = WFHRequest.objects.filter(
            employee=employee,
            status='approved',
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        wfh_days = sum([wfh.total_days for wfh in wfh_requests])
        
        # Leaves taken (approved)
        leave_requests = LeaveRequest.objects.filter(
            employee=employee,
            status='approved',
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        leaves_taken = sum([leave.total_days for leave in leave_requests])
        
        # Absent = Working Days - Attended Days - Approved Leaves - Approved WFH
        attended_days = attendance_records.count()
        absent_days = max(0, working_days - attended_days - leaves_taken - wfh_days)
        
        # Total hours worked
        hours_sum = attendance_records.aggregate(Sum('total_work_hours'))['total_work_hours__sum'] or 0
        
        # Update totals
        total_present += present_days
        total_absent += absent_days
        total_late += late_days
        total_half_days += half_days
        total_hours += hours_sum
        
        employee_stats.append({
            'employee': employee,
            'employee_id': employee_id,
            'name': employee.get_full_name() or employee.username,
            'department': department,
            'profile_photo': profile_photo,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'half_days': half_days,
            'total_hours': round(hours_sum, 2),
            'wfh_days': wfh_days,
            'leaves_taken': leaves_taken,
            'working_days': working_days,
        })
    
    # Sort by name
    employee_stats.sort(key=lambda x: x['name'])
    
    # Handle CSV export
    if export_csv:
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="employee_attendance_{start_date}_to_{end_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Employee ID', 'Name', 'Department', 'Working Days', 'Present Days', 'Absent Days', 'Late Arrivals', 'Half Days', 'WFH Days', 'Leaves Taken', 'Total Hours'])
        
        for stat in employee_stats:
            writer.writerow([
                stat['employee_id'],
                stat['name'],
                stat['department'],
                stat['working_days'],
                stat['present_days'],
                stat['absent_days'],
                stat['late_days'],
                stat['half_days'],
                stat['wfh_days'],
                stat['leaves_taken'],
                f"{stat['total_hours']:.2f}h",
            ])
        
        # Log CSV export
        log_action(request.user, 'csv_export', f'Exported employee attendance dashboard CSV for {start_date} to {end_date}', request)
        
        return response
    
    # Get list of departments for filter dropdown
    departments = EmployeeProfile.objects.values_list('department', flat=True).distinct().exclude(department='')
    
    # Summary statistics
    summary_stats = {
        'total_employees': len(employee_stats),
        'total_present': total_present,
        'total_absent': total_absent,
        'total_late': total_late,
        'total_half_days': total_half_days,
        'total_hours': round(total_hours, 2),
    }
    
    context = {
        'employee_stats': employee_stats,
        'summary_stats': summary_stats,
        'departments': departments,
        'start_date': start_date,
        'end_date': end_date,
        'employee_id_filter': employee_id_filter,
        'department_filter': department_filter,
    }
    
    return render(request, 'employee_attendance_dashboard.html', context)


# =========================
# EMPLOYEE LIST (FOR DASHBOARD TILES)
# =========================
@login_required
def employee_list_view(request, list_type):
    """
    API endpoint to fetch employee lists for dashboard tiles
    Types: all, present, absent, late
    """
    # Check if user is HR or superuser
    if not request.user.is_superuser:
        try:
            if not request.user.employeeprofile.is_hr:
                return JsonResponse({'success': False, 'message': 'Access denied'})
        except EmployeeProfile.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Access denied'})
    
    today = get_local_today()
    employees = []
    
    if list_type == 'all':
        # All active employees
        all_users = User.objects.filter(is_active=True).select_related('employeeprofile')
        for user in all_users:
            try:
                profile = user.employeeprofile
                employees.append({
                    'employee_id': profile.employee_id or 'N/A',
                    'name': user.get_full_name() or user.username,
                    'department': profile.department or 'N/A',
                })
            except EmployeeProfile.DoesNotExist:
                employees.append({
                    'employee_id': 'N/A',
                    'name': user.get_full_name() or user.username,
                    'department': 'N/A',
                })
    
    elif list_type == 'present':
        # Employees who checked in today
        present_attendance = Attendance.objects.filter(
            date=today,
            check_in__isnull=False
        ).select_related('employee__employeeprofile')
        
        import pytz
        local_tz = pytz.timezone('Asia/Kolkata')
        
        for attendance in present_attendance:
            # Convert check_in time to IST
            check_in_ist = attendance.check_in.astimezone(local_tz)
            
            try:
                profile = attendance.employee.employeeprofile
                employees.append({
                    'employee_id': profile.employee_id or 'N/A',
                    'name': attendance.employee.get_full_name() or attendance.employee.username,
                    'department': profile.department or 'N/A',
                    'check_in_time': check_in_ist.strftime('%I:%M %p'),
                    'status': attendance.get_status_display(),
                    'status_color': 'success' if attendance.status == 'present' else 'warning' if attendance.status == 'late' else 'info',
                })
            except EmployeeProfile.DoesNotExist:
                employees.append({
                    'employee_id': 'N/A',
                    'name': attendance.employee.get_full_name() or attendance.employee.username,
                    'department': 'N/A',
                    'check_in_time': check_in_ist.strftime('%I:%M %p'),
                    'status': attendance.get_status_display(),
                    'status_color': 'success',
                })
    
    elif list_type == 'absent':
        # Employees who didn't check in today (excluding holidays, leave, WFH)
        from attendance.models import CompanyHoliday
        
        # Check if today is a holiday
        is_today_holiday, holiday_obj = CompanyHoliday.is_holiday(today)
        
        if is_today_holiday:
            # On holidays, only show employees with approved OT who didn't check-in
            from attendance.models import Overtime
            employees_with_ot = Overtime.objects.filter(
                date=today,
                status='approved'
            ).values_list('employee_id', flat=True)
            
            checked_in_users = Attendance.objects.filter(
                date=today,
                check_in__isnull=False
            ).values_list('employee_id', flat=True)
            
            # Absent = employees with approved OT who didn't check-in
            absent_user_ids = [emp_id for emp_id in employees_with_ot if emp_id not in checked_in_users]
            absent_users = User.objects.filter(id__in=absent_user_ids).select_related('employeeprofile')
            
            for user in absent_users:
                try:
                    profile = user.employeeprofile
                    employees.append({
                        'employee_id': profile.employee_id or 'N/A',
                        'name': user.get_full_name() or user.username,
                        'department': profile.department or 'N/A',
                        'note': 'Has approved OT but not checked-in',
                    })
                except EmployeeProfile.DoesNotExist:
                    employees.append({
                        'employee_id': 'N/A',
                        'name': user.get_full_name() or user.username,
                        'department': 'N/A',
                        'note': 'Has approved OT but not checked-in',
                    })
        else:
            # Regular working day - exclude employees on leave or WFH
            all_users = User.objects.filter(is_active=True).select_related('employeeprofile')
            checked_in_users = Attendance.objects.filter(
                date=today,
                check_in__isnull=False
            ).values_list('employee_id', flat=True)
            
            # Get employees on approved leave today
            employees_on_leave = LeaveRequest.objects.filter(
                status='approved',
                start_date__lte=today,
                end_date__gte=today
            ).values_list('employee_id', flat=True)
            
            # Get employees on approved WFH today
            employees_on_wfh = WFHRequest.objects.filter(
                status='approved',
                start_date__lte=today,
                end_date__gte=today
            ).values_list('employee_id', flat=True)
            
            for user in all_users:
                # Exclude if: checked-in, on leave, or on WFH
                if (user.id not in checked_in_users and 
                    user.id not in employees_on_leave and 
                    user.id not in employees_on_wfh):
                    try:
                        profile = user.employeeprofile
                        employees.append({
                            'employee_id': profile.employee_id or 'N/A',
                            'name': user.get_full_name() or user.username,
                            'department': profile.department or 'N/A',
                        })
                    except EmployeeProfile.DoesNotExist:
                        employees.append({
                            'employee_id': 'N/A',
                            'name': user.get_full_name() or user.username,
                            'department': 'N/A',
                        })
    
    elif list_type == 'late':
        # Employees who arrived late today
        late_attendance = Attendance.objects.filter(
            date=today,
            status__in=['late', 'half-day']
        ).select_related('employee__employeeprofile')
        
        import pytz
        local_tz = pytz.timezone('Asia/Kolkata')
        
        for attendance in late_attendance:
            # Convert check_in time to IST
            check_in_ist = attendance.check_in.astimezone(local_tz) if attendance.check_in else None
            
            try:
                profile = attendance.employee.employeeprofile
                employees.append({
                    'employee_id': profile.employee_id or 'N/A',
                    'name': attendance.employee.get_full_name() or attendance.employee.username,
                    'department': profile.department or 'N/A',
                    'check_in_time': check_in_ist.strftime('%I:%M %p') if check_in_ist else 'N/A',
                    'status': attendance.get_status_display(),
                    'status_color': 'warning' if attendance.status == 'late' else 'info',
                })
            except EmployeeProfile.DoesNotExist:
                employees.append({
                    'employee_id': 'N/A',
                    'name': attendance.employee.get_full_name() or attendance.employee.username,
                    'department': 'N/A',
                    'check_in_time': check_in_ist.strftime('%I:%M %p') if check_in_ist else 'N/A',
                    'status': attendance.get_status_display(),
                    'status_color': 'warning',
                })
    
    elif list_type == 'leave':
        # Employees on approved leave today
        leave_requests = LeaveRequest.objects.filter(
            status='approved',
            start_date__lte=today,
            end_date__gte=today
        ).select_related('employee__employeeprofile')
        
        for leave in leave_requests:
            try:
                profile = leave.employee.employeeprofile
                # Calculate duration
                duration = f"{leave.start_date.strftime('%b %d')} - {leave.end_date.strftime('%b %d')}"
                employees.append({
                    'employee_id': profile.employee_id or 'N/A',
                    'name': leave.employee.get_full_name() or leave.employee.username,
                    'department': profile.department or 'N/A',
                    'leave_type': leave.get_leave_type_display(),
                    'duration': duration,
                })
            except EmployeeProfile.DoesNotExist:
                duration = f"{leave.start_date.strftime('%b %d')} - {leave.end_date.strftime('%b %d')}"
                employees.append({
                    'employee_id': 'N/A',
                    'name': leave.employee.get_full_name() or leave.employee.username,
                    'department': 'N/A',
                    'leave_type': leave.get_leave_type_display(),
                    'duration': duration,
                })
    
    elif list_type == 'wfh':
        # Employees on approved WFH today
        wfh_requests = WFHRequest.objects.filter(
            status='approved',
            start_date__lte=today,
            end_date__gte=today
        ).select_related('employee__employeeprofile')
        
        for wfh in wfh_requests:
            try:
                profile = wfh.employee.employeeprofile
                # Calculate duration
                duration = f"{wfh.start_date.strftime('%b %d')} - {wfh.end_date.strftime('%b %d')}"
                employees.append({
                    'employee_id': profile.employee_id or 'N/A',
                    'name': wfh.employee.get_full_name() or wfh.employee.username,
                    'department': profile.department or 'N/A',
                    'duration': duration,
                })
            except EmployeeProfile.DoesNotExist:
                duration = f"{wfh.start_date.strftime('%b %d')} - {wfh.end_date.strftime('%b %d')}"
                employees.append({
                    'employee_id': 'N/A',
                    'name': wfh.employee.get_full_name() or wfh.employee.username,
                    'department': 'N/A',
                    'duration': duration,
                })
    
    return JsonResponse({'employees': employees})


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
    current_month = timezone.localtime(timezone.now()).month
    current_year = timezone.localtime(timezone.now()).year
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
    
    # Get filter parameter (default: pending)
    status_filter = request.GET.get('status', 'pending')
    
    # Filter OT requests based on status
    if status_filter == 'pending':
        ot_requests = Overtime.objects.filter(
            status='pending'
        ).select_related('employee').order_by('-requested_at')
    
    elif status_filter == 'approved':
        ot_requests = Overtime.objects.filter(
            status='approved'
        ).select_related('employee', 'hr_approver').order_by('-requested_at')
    
    elif status_filter == 'rejected':
        ot_requests = Overtime.objects.filter(
            status='rejected'
        ).select_related('employee', 'hr_approver').order_by('-requested_at')
    
    else:  # 'all'
        ot_requests = Overtime.objects.all().select_related(
            'employee', 'hr_approver'
        ).order_by('-requested_at')
    
    # Count for badges
    pending_count = Overtime.objects.filter(status='pending').count()
    approved_count = Overtime.objects.filter(status='approved').count()
    rejected_count = Overtime.objects.filter(status='rejected').count()
    
    context = {
        'ot_requests': ot_requests,
        'status_filter': status_filter,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
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
        viewed_profile = employee_user.employeeprofile  # Renamed to avoid conflict with context processor
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
        'viewed_profile': viewed_profile,  # Renamed variable
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
        from attendance.validators import DateValidator, FieldValidator, OverlapValidator
        
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        selected_dates_json = request.POST.get('selected_dates')
        reason = request.POST.get('reason')
        
        # Validate reason
        is_valid, error = FieldValidator.validate_required(reason, "Reason")
        if not is_valid:
            messages.error(request, error)
            return redirect('wfh_request')
        
        is_valid, error = FieldValidator.validate_length(reason, min_length=10, max_length=500, field_name="Reason")
        if not is_valid:
            messages.error(request, error)
            return redirect('wfh_request')
        
        # Parse and validate selected dates if provided
        selected_dates = None
        if selected_dates_json:
            selected_dates, error = DateValidator.parse_and_validate_selected_dates(selected_dates_json)
            if error:
                messages.error(request, error)
                return redirect('wfh_request')
            
            # Set start_date and end_date to first and last selected dates for backward compatibility
            if selected_dates:
                start_date = selected_dates[0]
                end_date = selected_dates[-1]
        else:
            # Validate date range
            is_valid, error = FieldValidator.validate_required(start_date, "Start date")
            if not is_valid:
                messages.error(request, error)
                return redirect('wfh_request')
            
            is_valid, error = FieldValidator.validate_required(end_date, "End date")
            if not is_valid:
                messages.error(request, error)
                return redirect('wfh_request')
            
            is_valid, error = DateValidator.validate_date_format(start_date, "Start date")
            if not is_valid:
                messages.error(request, error)
                return redirect('wfh_request')
            
            is_valid, error = DateValidator.validate_date_format(end_date, "End date")
            if not is_valid:
                messages.error(request, error)
                return redirect('wfh_request')
            
            try:
                from datetime import datetime as dt
                start_obj = dt.strptime(start_date, '%Y-%m-%d').date()
                end_obj = dt.strptime(end_date, '%Y-%m-%d').date()
                
                is_valid, error = DateValidator.validate_future_date(start_obj, "Start date")
                if not is_valid:
                    messages.error(request, error)
                    return redirect('wfh_request')
                
                is_valid, error = DateValidator.validate_date_range(start_obj, end_obj)
                if not is_valid:
                    messages.error(request, error)
                    return redirect('wfh_request')
            except ValueError:
                messages.error(request, 'Invalid date format.')
                return redirect('wfh_request')
        
        # Convert to date objects for storage
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format.')
            return redirect('wfh_request')
        
        # Check for overlapping WFH requests
        is_valid, error = OverlapValidator.check_wfh_overlap(
            request.user, start_date, end_date, selected_dates
        )
        if not is_valid:
            messages.error(request, error)
            return redirect('wfh_request')
        
        # NO WFH LIMIT - Employees can request unlimited WFH days
        # Limit validation removed as per management decision
        
        # Create WFH request
        wfh_req = WFHRequest.objects.create(
            employee=request.user,
            start_date=start_date_obj,
            end_date=end_date_obj,
            selected_dates=selected_dates,  # Store JSON array or None
            reason=reason
        )
        
        # Calculate total days for notification
        if selected_dates:
            total_days = len(selected_dates)
        else:
            total_days = (end_date_obj - start_date_obj).days + 1
        
        # Notify Team Leaders (TL) for hierarchical approval
        team_leaders = User.objects.filter(employeeprofile__role='tl')
        for tl in team_leaders:
            Notification.objects.create(
                employee=tl,
                message=f'New WFH request from {request.user.get_full_name() or request.user.username} for {total_days} days'
            )
        
        # Log action
        log_action(request.user, 'wfh_request', 
                  f'Requested WFH for {total_days} days from {start_date_obj} to {end_date_obj}', request)
        
        messages.success(request, f'WFH request submitted successfully for {total_days} days!')
        return redirect('wfh_request')
    
    # Get user's WFH requests
    wfh_requests = WFHRequest.objects.filter(
        employee=request.user
    ).order_by('-created_at')
    
    # NO WFH LIMIT - Balance calculation removed
    # Employees can request unlimited WFH days
    
    context = {
        'wfh_requests': wfh_requests,
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
# WFH APPROVAL (HIERARCHICAL)
# =========================
@login_required
def wfh_approval(request):
    """
    PARALLEL approval view - all approvers see requests simultaneously
    TL: Sees all pending requests (can add comment)
    Manager: Sees all pending requests (can approve/reject if TL commented)
    HR: Sees all pending requests (can approve/reject if Manager approved)
    """
    # Check user role
    try:
        profile = request.user.employeeprofile
        user_role = profile.role
    except EmployeeProfile.DoesNotExist:
        # If no profile, check if superuser
        if request.user.is_superuser:
            user_role = 'hr'
        else:
            messages.error(request, 'Access denied. Profile not found.')
            return redirect('dashboard')
    
    # Only TL, Manager, and HR can access
    if user_role not in ['team_leader', 'manager', 'hr'] and not request.user.is_superuser:
        messages.error(request, 'Access denied. This page is for Team Leaders, Managers, and HR only.')
        return redirect('dashboard')
    
    # Get filter parameter (default: pending)
    status_filter = request.GET.get('status', 'pending')
    
    # Filter requests based on status
    if status_filter == 'pending':
        requests = WFHRequest.objects.filter(
            status='pending'
        ).select_related('employee', 'employee__employeeprofile', 'tl_approver', 'manager_approver').order_by('-created_at')
    
    elif status_filter == 'approved':
        requests = WFHRequest.objects.filter(
            status='approved'
        ).select_related('employee', 'employee__employeeprofile', 'tl_approver', 'manager_approver', 'hr_approver').order_by('-created_at')
    
    elif status_filter == 'rejected':
        requests = WFHRequest.objects.filter(
            status='rejected'
        ).select_related('employee', 'employee__employeeprofile', 'tl_approver', 'manager_approver').order_by('-created_at')
    
    else:  # 'all'
        requests = WFHRequest.objects.all().select_related(
            'employee', 'employee__employeeprofile', 'tl_approver', 'manager_approver', 'hr_approver'
        ).order_by('-created_at')
    
    # Count for badges
    pending_count = WFHRequest.objects.filter(status='pending').count()
    approved_count = WFHRequest.objects.filter(status='approved').count()
    rejected_count = WFHRequest.objects.filter(status='rejected').count()
    
    context = {
        'requests': requests,
        'user_role': user_role,
        'status_filter': status_filter,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    
    return render(request, 'wfh_approval.html', context)


# =========================
# WFH ACTION (HIERARCHICAL)
# =========================
@login_required
def wfh_action(request, wfh_id, action):
    """
    PARALLEL approval workflow - Handle WFH approval actions based on user role
    TL: Add comment (advisory only)
    Manager: Add comment (advisory only)
    HR: Final Approve/Reject (has final authority, can approve/reject regardless of TL/Manager input)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    wfh = get_object_or_404(WFHRequest, id=wfh_id)
    
    # Check user role
    try:
        profile = request.user.employeeprofile
        user_role = profile.role
    except EmployeeProfile.DoesNotExist:
        if request.user.is_superuser:
            user_role = 'hr'
        else:
            return JsonResponse({'success': False, 'error': 'Access denied'})
    
    # Get comment from request
    comment = request.POST.get('comment', '').strip()
    
    # Team Leader action - Add comment (can act anytime)
    if user_role == 'team_leader' and action == 'comment':
        # Comment is optional
        wfh.tl_comment = comment if comment else 'Reviewed by TL'
        wfh.tl_approver = request.user
        wfh.tl_approved_at = timezone.now()
        wfh.tl_approved = True
        wfh.save()
        
        # Notify Manager
        managers = User.objects.filter(employeeprofile__role='manager')
        for manager in managers:
            Notification.objects.create(
                employee=manager,
                message=f'WFH request from {wfh.employee.get_full_name() or wfh.employee.username} has TL comment'
            )
        
        # Log action
        log_action(request.user, 'wfh_tl_comment', 
                  f'Added TL comment for {wfh.employee.username}\'s WFH request', request, wfh.employee)
        
        return JsonResponse({'success': True, 'message': 'Comment added successfully'})
    
    # Manager action - Approve or Reject (can act anytime)
    elif user_role == 'manager' and action in ['approve', 'reject', 'comment']:
        # Comment is optional
        wfh.manager_comment = comment if comment else 'Reviewed by Manager'
        wfh.manager_approver = request.user
        wfh.manager_approved_at = timezone.now()
        
        if action == 'comment':
            # Manager only adds comment - no approval/rejection
            wfh.save()
            
            # Notify employee
            if comment:
                Notification.objects.create(
                    employee=wfh.employee,
                    message=f'Manager added a comment on your WFH request: {comment[:50]}...'
                )
            
            # Log action
            log_action(request.user, 'wfh_approve', 
                      f'Added Manager comment for {wfh.employee.username}\'s WFH request', request, wfh.employee)
            
            return JsonResponse({'success': True, 'message': 'Comment added successfully'})
        
        elif action == 'approve':
            wfh.manager_approved = True
            wfh.save()
            
            # Notify HR
            hr_users = User.objects.filter(Q(employeeprofile__is_hr=True) | Q(is_superuser=True))
            for hr_user in hr_users:
                Notification.objects.create(
                    employee=hr_user,
                    message=f'WFH request from {wfh.employee.get_full_name() or wfh.employee.username} approved by Manager'
                )
            
            # Log action
            log_action(request.user, 'wfh_manager_approve', 
                      f'Approved {wfh.employee.username}\'s WFH request (Manager level)', request, wfh.employee)
            
            return JsonResponse({'success': True, 'message': 'WFH approved at Manager level'})
        else:  # reject
            wfh.status = 'rejected'
            wfh.save()
            
            # Notify employee
            Notification.objects.create(
                employee=wfh.employee,
                message=f'Your WFH request has been rejected by Manager: {comment}'
            )
            
            # Log action
            log_action(request.user, 'wfh_manager_reject', 
                      f'Rejected {wfh.employee.username}\'s WFH request (Manager level)', request, wfh.employee)
            
            return JsonResponse({'success': True, 'message': 'WFH rejected'})
    
    # HR action - Final Approve or Reject (HR has full authority)
    elif user_role == 'hr' and action in ['approve', 'reject']:
        # Comment is optional for HR
        wfh.hr_comment = comment if comment else ''
        
        if action == 'approve':
            # HR can approve directly (no manager approval needed)
            wfh.status = 'approved'
            wfh.hr_approver = request.user
            wfh.save()
            
            # Notify employee
            comment_text = f': {comment}' if comment else ''
            Notification.objects.create(
                employee=wfh.employee,
                message=f'Your WFH request has been approved by HR{comment_text}'
            )
            
            # Notify manager
            if wfh.manager_approver:
                Notification.objects.create(
                    employee=wfh.manager_approver,
                    message=f'WFH request for {wfh.employee.get_full_name() or wfh.employee.username} has been approved by HR'
                )
            
            # Log action
            log_action(request.user, 'wfh_hr_approve', 
                      f'Approved {wfh.employee.username}\'s WFH request (Final)', request, wfh.employee)
            
            return JsonResponse({'success': True, 'message': 'WFH approved (Final)'})
        else:  # reject
            wfh.status = 'rejected'
            wfh.save()
            
            # Notify employee
            comment_text = f': {comment}' if comment else ''
            Notification.objects.create(
                employee=wfh.employee,
                message=f'Your WFH request has been rejected by HR{comment_text}'
            )
            
            # Notify manager
            if wfh.manager_approver:
                Notification.objects.create(
                    employee=wfh.manager_approver,
                    message=f'WFH request for {wfh.employee.get_full_name() or wfh.employee.username} has been rejected by HR'
                )
            
            # Log action
            log_action(request.user, 'wfh_hr_reject', 
                      f'Rejected {wfh.employee.username}\'s WFH request (Final)', request, wfh.employee)
            
            return JsonResponse({'success': True, 'message': 'WFH rejected'})
    
    return JsonResponse({'success': False, 'error': 'Invalid action or insufficient permissions'})



# =========================
# CHANGE WORK MODE (HR ONLY)
# =========================
@login_required
def change_work_mode(request):
    """
    HR can change employee work mode (office/hybrid/permanent_wfh)
    This determines network access requirements for check-in
    """
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
        user_id = request.POST.get('user_id')
        new_work_mode = request.POST.get('new_work_mode')
        reason = request.POST.get('reason', '')
        
        try:
            target_user = User.objects.get(id=user_id)
            profile = target_user.employeeprofile
            
            old_work_mode = profile.work_mode
            profile.work_mode = new_work_mode
            profile.save()
            
            # Log action
            mode_labels = {
                'office': 'Office Only',
                'hybrid': 'Hybrid',
                'permanent_wfh': 'Permanent WFH'
            }
            log_description = f'Changed work mode for {target_user.get_full_name() or target_user.username} from {mode_labels.get(old_work_mode, "Office Only")} to {mode_labels.get(new_work_mode, "Office Only")}'
            if reason:
                log_description += f'. Reason: {reason}'
            
            log_action(request.user, 'role_change', log_description, request, target_user=target_user)
            
            # Notify employee
            Notification.objects.create(
                employee=target_user,
                message=f'Your work mode has been changed to {mode_labels.get(new_work_mode, "Office Only")} by HR.'
            )
            
            messages.success(request, f'Work mode updated successfully for {target_user.get_full_name() or target_user.username}!')
            
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        except EmployeeProfile.DoesNotExist:
            messages.error(request, 'Employee profile not found.')
        except Exception as e:
            messages.error(request, f'Error updating work mode: {str(e)}')
        
        # Redirect back to employee details
        return redirect('employee_details', user_id=user_id)
    
    return redirect('hr_dashboard')



# =========================
# EMERGENCY OVERRIDE MANAGEMENT
# =========================
@login_required
def emergency_override_status(request):
    """
    Get current emergency override status (for AJAX)
    """
    try:
        profile = request.user.employeeprofile
        if not profile.is_hr and not request.user.is_superuser:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
    except EmployeeProfile.DoesNotExist:
        if not request.user.is_superuser:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    settings = SystemSettings.get_settings()
    
    # Convert timestamp to IST for display
    import pytz
    enabled_at_display = None
    if settings.emergency_override_enabled_at:
        local_tz = pytz.timezone('Asia/Kolkata')
        enabled_at_ist = settings.emergency_override_enabled_at.astimezone(local_tz)
        enabled_at_display = enabled_at_ist.strftime('%Y-%m-%d %H:%M:%S')
    
    return JsonResponse({
        'enabled': settings.emergency_override_enabled,
        'reason': settings.emergency_override_reason or '',
        'enabled_by': settings.emergency_override_enabled_by.get_full_name() if settings.emergency_override_enabled_by else None,
        'enabled_at': enabled_at_display,
    })


@login_required
def toggle_emergency_override(request):
    """
    Toggle emergency override (HR only)
    """
    # Check if user is HR or admin
    try:
        profile = request.user.employeeprofile
        if not profile.is_hr and not request.user.is_superuser:
            messages.error(request, 'Only HR can toggle emergency override')
            return redirect('hr_dashboard')
    except EmployeeProfile.DoesNotExist:
        if not request.user.is_superuser:
            messages.error(request, 'Only HR can toggle emergency override')
            return redirect('dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')  # 'enable' or 'disable'
        reason = request.POST.get('reason', '')
        
        settings = SystemSettings.get_settings()
        
        if action == 'enable':
            settings.emergency_override_enabled = True
            settings.emergency_override_reason = reason
            settings.emergency_override_enabled_by = request.user
            settings.emergency_override_enabled_at = timezone.now()
            settings.last_updated_by = request.user
            settings.save()
            
            # Log the action
            log_action(
                user=request.user,
                action='system_setting_change',
                description=f'Emergency Override ENABLED. Reason: {reason}',
                request=request
            )
            
            messages.success(request, f'🚨 Emergency Override ENABLED - All employees can now check-in from anywhere')
            
        elif action == 'disable':
            settings.emergency_override_enabled = False
            settings.last_updated_by = request.user
            settings.save()
            
            # Log the action
            log_action(
                user=request.user,
                action='system_setting_change',
                description='Emergency Override DISABLED',
                request=request
            )
            
            messages.success(request, '✅ Emergency Override DISABLED - Normal IP restrictions restored')
        
        return redirect('hr_dashboard')
    
    # GET request - show current status
    settings = SystemSettings.get_settings()
    return render(request, 'emergency_override.html', {
        'settings': settings,
    })


# =========================
# ONSITE REQUEST
# =========================
@login_required
def onsite_request(request):
    """
    Employee can request onsite/client visit
    Allows flexible break times during client meetings
    """
    if request.method == 'POST':
        from attendance.validators import DateValidator, FieldValidator, OverlapValidator
        
        visit_type = request.POST.get('visit_type')
        visit_date = request.POST.get('visit_date')
        client_name = request.POST.get('client_name')
        location = request.POST.get('location')
        purpose = request.POST.get('purpose')
        expected_duration = request.POST.get('expected_duration')
        
        # Validate visit type
        valid_types = ['onsite', 'online_meeting']
        is_valid, error = FieldValidator.validate_choice(visit_type, valid_types, "visit type")
        if not is_valid:
            messages.error(request, error)
            return redirect('onsite_request')
        
        # Validate visit date
        is_valid, error = FieldValidator.validate_required(visit_date, "Visit date")
        if not is_valid:
            messages.error(request, error)
            return redirect('onsite_request')
        
        is_valid, error = DateValidator.validate_date_format(visit_date, "Visit date")
        if not is_valid:
            messages.error(request, error)
            return redirect('onsite_request')
        
        try:
            from datetime import datetime as dt
            visit_date_obj = dt.strptime(visit_date, '%Y-%m-%d').date()
            
            is_valid, error = DateValidator.validate_future_date(visit_date_obj, "Visit date")
            if not is_valid:
                messages.error(request, error)
                return redirect('onsite_request')
        except ValueError:
            messages.error(request, 'Invalid date format.')
            return redirect('onsite_request')
        
        # Validate client name
        is_valid, error = FieldValidator.validate_required(client_name, "Client/Project name")
        if not is_valid:
            messages.error(request, error)
            return redirect('onsite_request')
        
        is_valid, error = FieldValidator.validate_length(client_name, min_length=2, max_length=100, field_name="Client/Project name")
        if not is_valid:
            messages.error(request, error)
            return redirect('onsite_request')
        
        # Validate location
        is_valid, error = FieldValidator.validate_required(location, "Location")
        if not is_valid:
            messages.error(request, error)
            return redirect('onsite_request')
        
        is_valid, error = FieldValidator.validate_length(location, min_length=2, max_length=200, field_name="Location")
        if not is_valid:
            messages.error(request, error)
            return redirect('onsite_request')
        
        # Validate purpose
        is_valid, error = FieldValidator.validate_required(purpose, "Purpose")
        if not is_valid:
            messages.error(request, error)
            return redirect('onsite_request')
        
        is_valid, error = FieldValidator.validate_length(purpose, min_length=10, max_length=500, field_name="Purpose")
        if not is_valid:
            messages.error(request, error)
            return redirect('onsite_request')
        
        # Validate expected duration
        is_valid, error = FieldValidator.validate_required(expected_duration, "Expected duration")
        if not is_valid:
            messages.error(request, error)
            return redirect('onsite_request')
        
        # Check for overlapping onsite requests
        is_valid, error = OverlapValidator.check_onsite_overlap(request.user, visit_date_obj)
        if not is_valid:
            messages.error(request, error)
            return redirect('onsite_request')
        
        # Create onsite request
        from .models import OnsiteRequest
        onsite = OnsiteRequest.objects.create(
            employee=request.user,
            visit_type=visit_type,
            visit_date=visit_date_obj,
            client_name=client_name,
            location=location,
            purpose=purpose,
            expected_duration=expected_duration
        )
        
        # Notify Manager
        managers = User.objects.filter(employeeprofile__role='manager')
        for manager in managers:
            Notification.objects.create(
                employee=manager,
                message=f'{request.user.get_full_name() or request.user.username} has requested {onsite.get_visit_type_display()} on {visit_date_obj.strftime("%b %d, %Y")}'
            )
        
        # Log action
        log_action(request.user, 'onsite_request', 
                  f'Requested {visit_type} visit on {visit_date_obj} - Client: {client_name}', request)
        
        messages.success(request, 'Onsite request submitted successfully!')
        return redirect('onsite_request')
    
    # Get user's onsite requests
    from .models import OnsiteRequest
    onsite_requests = OnsiteRequest.objects.filter(
        employee=request.user
    ).order_by('-visit_date')
    
    context = {
        'onsite_requests': onsite_requests,
    }
    
    return render(request, 'onsite_request.html', context)


# =========================
# ONSITE APPROVAL
# =========================
@login_required
def onsite_approval(request):
    """
    PARALLEL approval for onsite requests - all approvers see requests simultaneously
    Manager: Can approve/reject anytime
    HR: Can approve/reject (can only approve if Manager approved)
    """
    from .models import OnsiteRequest
    
    # Check user role
    try:
        profile = request.user.employeeprofile
        user_role = profile.role
    except EmployeeProfile.DoesNotExist:
        if request.user.is_superuser:
            user_role = 'hr'
        else:
            messages.error(request, 'Access denied. Profile not found.')
            return redirect('dashboard')
    
    # Only Manager and HR can access
    if user_role not in ['manager', 'hr'] and not request.user.is_superuser:
        messages.error(request, 'Access denied. This page is for Managers and HR only.')
        return redirect('dashboard')
    
    # Get filter parameter (default: pending)
    status_filter = request.GET.get('status', 'pending')
    
    # Filter requests based on status
    if status_filter == 'pending':
        requests = OnsiteRequest.objects.filter(
            status='pending'
        ).select_related('employee', 'employee__employeeprofile', 'manager_approver').order_by('-visit_date')
    
    elif status_filter == 'approved':
        requests = OnsiteRequest.objects.filter(
            status='approved'
        ).select_related('employee', 'employee__employeeprofile', 'manager_approver', 'hr_approver').order_by('-visit_date')
    
    elif status_filter == 'rejected':
        requests = OnsiteRequest.objects.filter(
            status='rejected'
        ).select_related('employee', 'employee__employeeprofile', 'manager_approver').order_by('-visit_date')
    
    else:  # 'all'
        requests = OnsiteRequest.objects.all().select_related(
            'employee', 'employee__employeeprofile', 'manager_approver', 'hr_approver'
        ).order_by('-visit_date')
    
    # Count for badges
    pending_count = OnsiteRequest.objects.filter(status='pending').count()
    approved_count = OnsiteRequest.objects.filter(status='approved').count()
    rejected_count = OnsiteRequest.objects.filter(status='rejected').count()
    
    context = {
        'requests': requests,
        'user_role': user_role,
        'status_filter': status_filter,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    
    return render(request, 'onsite_approval.html', context)


# =========================
# ONSITE ACTION
# =========================
@login_required
def onsite_action(request, onsite_id, action):
    """
    PARALLEL approval workflow - Handle onsite approval actions
    Manager: Add comment (advisory only)
    HR: Final Approve/Reject (has final authority, can approve/reject regardless of Manager input)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    from .models import OnsiteRequest
    onsite = get_object_or_404(OnsiteRequest, id=onsite_id)
    
    # Check user role
    try:
        profile = request.user.employeeprofile
        user_role = profile.role
    except EmployeeProfile.DoesNotExist:
        if request.user.is_superuser:
            user_role = 'hr'
        else:
            return JsonResponse({'success': False, 'error': 'Access denied'})
    
    # Get comment from request
    comment = request.POST.get('comment', '').strip()
    
    # Manager action - Add comment (can act anytime)
    if user_role == 'manager' and action in ['approve', 'reject', 'comment']:
        onsite.manager_comment = comment if comment else 'Reviewed by Manager'
        onsite.manager_approver = request.user
        onsite.manager_approved_at = timezone.now()
        
        if action == 'comment':
            # Manager only adds comment - no approval/rejection
            onsite.save()
            
            # Notify employee
            if comment:
                Notification.objects.create(
                    employee=onsite.employee,
                    message=f'Manager added a comment on your onsite request: {comment[:50]}...'
                )
            
            # Log action
            log_action(request.user, 'onsite_manager_approve', 
                      f'Added Manager comment for {onsite.employee.username}\'s onsite request', request, onsite.employee)
            
            return JsonResponse({'success': True, 'message': 'Comment added successfully'})
        
        elif action == 'approve':
            onsite.manager_approved = True
            onsite.save()
            
            # Notify HR
            hr_users = User.objects.filter(Q(employeeprofile__is_hr=True) | Q(is_superuser=True))
            for hr_user in hr_users:
                Notification.objects.create(
                    employee=hr_user,
                    message=f'Onsite request from {onsite.employee.get_full_name() or onsite.employee.username} approved by Manager'
                )
            
            # Log action
            log_action(request.user, 'onsite_manager_approve', 
                      f'Approved {onsite.employee.username}\'s onsite request (Manager level)', request, onsite.employee)
            
            return JsonResponse({'success': True, 'message': 'Onsite request approved at Manager level'})
        else:  # reject
            onsite.status = 'rejected'
            onsite.save()
            
            # Notify employee
            Notification.objects.create(
                employee=onsite.employee,
                message=f'Your onsite request for {onsite.visit_date.strftime("%b %d, %Y")} has been rejected by Manager: {comment}'
            )
            
            # Log action
            log_action(request.user, 'onsite_manager_reject', 
                      f'Rejected {onsite.employee.username}\'s onsite request (Manager level)', request, onsite.employee)
            
            return JsonResponse({'success': True, 'message': 'Onsite request rejected'})
    
    # HR action - Final Approve or Reject (HR has final authority)
    elif user_role == 'hr' and action in ['approve', 'reject']:
        # Comment is optional for HR
        onsite.hr_comment = comment if comment else ''
        
        if action == 'approve':
            onsite.status = 'approved'
            onsite.hr_approver = request.user
            onsite.save()
            
            # Notify employee
            comment_text = f': {comment}' if comment else ''
            Notification.objects.create(
                employee=onsite.employee,
                message=f'Your onsite request for {onsite.visit_date.strftime("%b %d, %Y")} has been approved by HR{comment_text}'
            )
            
            # Notify manager
            if onsite.manager_approver:
                Notification.objects.create(
                    employee=onsite.manager_approver,
                    message=f'Onsite request for {onsite.employee.get_full_name() or onsite.employee.username} has been approved by HR'
                )
            
            # Log action
            log_action(request.user, 'onsite_hr_approve', 
                      f'Approved {onsite.employee.username}\'s onsite request (Final)', request, onsite.employee)
            
            return JsonResponse({'success': True, 'message': 'Onsite request approved (Final)'})
        else:  # reject
            onsite.status = 'rejected'
            onsite.save()
            
            # Notify employee
            comment_text = f': {comment}' if comment else ''
            Notification.objects.create(
                employee=onsite.employee,
                message=f'Your onsite request for {onsite.visit_date.strftime("%b %d, %Y")} has been rejected by HR{comment_text}'
            )
            
            # Notify manager
            if onsite.manager_approver:
                Notification.objects.create(
                    employee=onsite.manager_approver,
                    message=f'Onsite request for {onsite.employee.get_full_name() or onsite.employee.username} has been rejected by HR'
                )
            
            # Log action
            log_action(request.user, 'onsite_hr_reject', 
                      f'Rejected {onsite.employee.username}\'s onsite request (Final)', request, onsite.employee)
            
            return JsonResponse({'success': True, 'message': 'Onsite request rejected'})
    
    return JsonResponse({'success': False, 'error': 'Invalid action or insufficient permissions'})


# =========================
# ONSITE CHECK-IN
# =========================
@login_required
def onsite_check_in(request):
    """
    Check-in for approved onsite visit
    Allowed from any location (not restricted to office network)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    from .models import OnsiteRequest
    today = get_local_today()
    
    # Check if there's an approved onsite request for today
    onsite = OnsiteRequest.objects.filter(
        employee=request.user,
        visit_date=today,
        status='approved'
    ).first()
    
    if not onsite:
        return JsonResponse({'success': False, 'error': 'No approved onsite request for today'})
    
    if onsite.actual_check_in:
        return JsonResponse({'success': False, 'error': 'Already checked in for onsite visit'})
    
    # Record check-in
    onsite.actual_check_in = timezone.now()
    onsite.save()
    
    # Log action
    log_action(request.user, 'onsite_check_in', 
              f'Checked in for onsite visit - Client: {onsite.client_name}', request)
    
    return JsonResponse({'success': True, 'message': 'Checked in for onsite visit successfully'})


# =========================
# ONSITE CHECK-OUT
# =========================
@login_required
def onsite_check_out(request):
    """
    Check-out from onsite visit
    Calculates total onsite hours
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    from .models import OnsiteRequest
    today = get_local_today()
    
    # Check if there's an approved onsite request for today
    onsite = OnsiteRequest.objects.filter(
        employee=request.user,
        visit_date=today,
        status='approved'
    ).first()
    
    if not onsite:
        return JsonResponse({'success': False, 'error': 'No approved onsite request for today'})
    
    if not onsite.actual_check_in:
        return JsonResponse({'success': False, 'error': 'Please check in first'})
    
    if onsite.actual_check_out:
        return JsonResponse({'success': False, 'error': 'Already checked out from onsite visit'})
    
    # Record check-out
    onsite.actual_check_out = timezone.now()
    onsite.save()
    
    # Calculate total hours
    duration = onsite.actual_check_out - onsite.actual_check_in
    total_hours = round(duration.total_seconds() / 3600, 2)
    
    # Log action
    log_action(request.user, 'onsite_check_out', 
              f'Checked out from onsite visit - Total hours: {total_hours}', request)
    
    return JsonResponse({
        'success': True, 
        'message': f'Checked out successfully. Total onsite hours: {total_hours}'
    })
