from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from attendance.models import EmployeeProfile


@csrf_exempt
@require_http_methods(["POST"])
def register_api(request):
    # This can be implemented later if needed
    return JsonResponse({"error": "Not implemented"}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    data = json.loads(request.body)
    identifier = data.get('identifier')  # employee_id OR email
    password = data.get('password')

    if not identifier or not password:
        return JsonResponse(
            {"error": "Identifier and password required"}, 
            status=400
        )

    # Determine login type
    if '@' in identifier:
        try:
            user = User.objects.get(email=identifier)
            username = user.username
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "Invalid credentials"}, 
                status=401
            )
    else:
        username = identifier  # employee_id stored as username

    user = authenticate(username=username, password=password)

    if user is None:
        return JsonResponse(
            {"error": "Invalid credentials"}, 
            status=401
        )

    login(request, user)

    profile = EmployeeProfile.objects.get(user=user)

    return JsonResponse({
        "message": "Login successful",
        "employee_id": profile.employee_id,
        "is_hr": profile.is_hr,
        "profile_completed": hasattr(profile, 'profile_completed') and profile.profile_completed
    })




@require_http_methods(["GET"])
def test_auth_api(request):
    """Test endpoint to check authentication status"""
    if not request.user.is_authenticated:
        return JsonResponse({
            "authenticated": False,
            "user": "Anonymous"
        })
    
    try:
        profile = request.user.employeeprofile
        return JsonResponse({
            "authenticated": True,
            "user": request.user.username,
            "is_superuser": request.user.is_superuser,
            "employee_id": profile.employee_id,
            "is_hr": profile.is_hr,
            "role": profile.role
        })
    except EmployeeProfile.DoesNotExist:
        return JsonResponse({
            "authenticated": True,
            "user": request.user.username,
            "is_superuser": request.user.is_superuser,
            "employee_id": "NO_PROFILE",
            "is_hr": False,
            "role": "NO_PROFILE"
        })


@require_http_methods(["GET"])
def missing_checkouts_api(request):
    """Get missing checkouts for employee(s) - only for dates before today"""
    from django.utils import timezone
    from attendance.models import Attendance, LeaveRequest, WFHRequest
    from datetime import timedelta
    
    # Authentication and authorization check
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    # Allow superusers OR HR users
    is_authorized = False
    if request.user.is_superuser:
        is_authorized = True
        print(f"DEBUG: Superuser {request.user.username} granted access")
    else:
        try:
            profile = request.user.employeeprofile
            print(f"DEBUG: User {request.user.username}, is_hr: {profile.is_hr}, role: {profile.role}")
            if profile.is_hr:
                is_authorized = True
        except EmployeeProfile.DoesNotExist:
            pass
    
    if not is_authorized:
        return JsonResponse({"error": "HR access only"}, status=403)
    
    
    today = timezone.localtime(timezone.now()).date()
    yesterday = today - timedelta(days=1)
    
    mode = request.GET.get('mode', 'specific')
    
    if request.GET.get('all'):
        # All employees with missing checkouts
        all_missing = Attendance.objects.filter(
            check_in__isnull=False,
            check_out__isnull=True,
            date__lte=yesterday  # Only up to yesterday
        ).select_related('employee', 'employee__employeeprofile').order_by('-date')
        
        results = []
        total_to_assign = 0
        
        for att in all_missing:
            # Check if employee is on leave/WFH
            is_on_leave = LeaveRequest.objects.filter(
                employee=att.employee,
                status='approved',
                start_date__lte=att.date,
                end_date__gte=att.date
            ).exists()
            
            is_on_wfh = WFHRequest.objects.filter(
                employee=att.employee,
                status='approved',
                start_date__lte=att.date,
                end_date__gte=att.date
            ).exists()
            
            skip_reason = None
            if is_on_leave:
                skip_reason = "On Leave"
            elif is_on_wfh:
                skip_reason = "On WFH"
            else:
                total_to_assign += 1
            
            results.append({
                'employee_name': att.employee.get_full_name() or att.employee.username,
                'employee_id': att.employee.employeeprofile.employee_id,
                'date': att.date.strftime('%Y-%m-%d'),
                'date_display': att.date.strftime('%b %d, %Y'),
                'check_in_time': att.check_in.strftime('%I:%M %p'),
                'skip_reason': skip_reason
            })
        
        return JsonResponse({
            'missing_checkouts': results,
            'total_records': len(results),
            'total_employees': len(set(a['employee_id'] for a in results)),
            'total_to_assign': total_to_assign
        })
    else:
        # Specific employee
        employee_id = request.GET.get('employee_id')
        if not employee_id:
            return JsonResponse({"error": "Employee ID is required"}, status=400)
        
        try:
            emp = User.objects.get(id=employee_id)
        except User.DoesNotExist:
            return JsonResponse({"error": f"Employee with ID {employee_id} not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Error fetching employee: {str(e)}"}, status=500)
        
        missing_for_emp = Attendance.objects.filter(
            employee=emp,
            check_in__isnull=False,
            check_out__isnull=True,
            date__lte=yesterday  # Only up to yesterday
        ).order_by('-date')
        
        results = []
        for att in missing_for_emp:
            is_on_leave = LeaveRequest.objects.filter(
                employee=emp,
                status='approved',
                start_date__lte=att.date,
                end_date__gte=att.date
            ).exists()
            
            is_on_wfh = WFHRequest.objects.filter(
                employee=emp,
                status='approved',
                start_date__lte=att.date,
                end_date__gte=att.date
            ).exists()
            
            skip_reason = None
            if is_on_leave:
                skip_reason = "On Leave"
            elif is_on_wfh:
                skip_reason = "On WFH"
            
            results.append({
                'employee_name': emp.get_full_name() or emp.username,
                'date': att.date.strftime('%Y-%m-%d'),
                'date_display': att.date.strftime('%b %d, %Y'),
                'check_in_time': att.check_in.strftime('%I:%M %p'),
                'skip_reason': skip_reason
            })
        
        return JsonResponse({
            'missing_checkouts': results,
            'total_records': len(results)
        })


@csrf_exempt
@require_http_methods(["POST"])
def assign_missing_checkouts_api(request):
    """Assign missing checkouts for employee(s)"""
    from django.utils import timezone
    from datetime import time, timedelta, datetime
    from attendance.models import Attendance, LeaveRequest, WFHRequest, AuditLog
    
    # Authentication and authorization check
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    # Allow superusers OR HR users
    is_authorized = False
    if request.user.is_superuser:
        is_authorized = True
        print(f"DEBUG: Superuser {request.user.username} granted access to assign")
    else:
        try:
            profile = request.user.employeeprofile
            if profile.is_hr:
                is_authorized = True
        except EmployeeProfile.DoesNotExist:
            pass
    
    if not is_authorized:
        return JsonResponse({"error": "HR access only"}, status=403)
    
    data = json.loads(request.body)
    today = timezone.localtime(timezone.now()).date()
    yesterday = today - timedelta(days=1)
    checkout_time = time(19, 0)  # 7 PM
    
    mode = data.get('mode')
    employee_id = data.get('employee_id')
    
    # Validation
    if not mode or mode not in ['all', 'specific']:
        return JsonResponse({"error": "Valid mode ('all' or 'specific') is required"}, status=400)
    
    if mode == 'specific' and not employee_id:
        return JsonResponse({"error": "Employee ID is required for specific mode"}, status=400)
    
    assigned_count = 0
    skipped_count = 0
    results = []
    
    if mode == 'all':
        # Get all employees with missing checkouts
        all_missing = Attendance.objects.filter(
            check_in__isnull=False,
            check_out__isnull=True,
            date__lte=yesterday
        ).select_related('employee').order_by('-date')
        
        for att in all_missing:
            # Check leave/WFH
            is_on_leave = LeaveRequest.objects.filter(
                employee=att.employee,
                status='approved',
                start_date__lte=att.date,
                end_date__gte=att.date
            ).exists()
            
            is_on_wfh = WFHRequest.objects.filter(
                employee=att.employee,
                status='approved',
                start_date__lte=att.date,
                end_date__gte=att.date
            ).exists()
            
            if is_on_leave:
                skipped_count += 1
                results.append({
                    'employee_name': att.employee.get_full_name() or att.employee.username,
                    'date': att.date.strftime('%b %d, %Y'),
                    'check_in_time': att.check_in.strftime('%I:%M %p'),
                    'success': False,
                    'reason': 'On Leave'
                })
            elif is_on_wfh:
                skipped_count += 1
                results.append({
                    'employee_name': att.employee.get_full_name() or att.employee.username,
                    'date': att.date.strftime('%b %d, %Y'),
                    'check_in_time': att.check_in.strftime('%I:%M %p'),
                    'success': False,
                    'reason': 'On WFH'
                })
            else:
                # Assign checkout
                try:
                    checkout_datetime = timezone.make_aware(
                        datetime.combine(att.date, checkout_time)
                    )
                    att.check_out = checkout_datetime
                    att.calculate_work_hours()
                    att.save()
                    
                    # Create audit log
                    AuditLog.objects.create(
                        user=request.user,
                        action='check_out',
                        description=f'Bulk checkout assignment: 7 PM for {att.employee.username} on {att.date}',
                        target_user=att.employee
                    )
                    
                    assigned_count += 1
                    results.append({
                        'employee_name': att.employee.get_full_name() or att.employee.username,
                        'date': att.date.strftime('%b %d, %Y'),
                        'check_in_time': att.check_in.strftime('%I:%M %p'),
                        'success': True,
                        'reason': 'Assigned'
                    })
                except Exception as e:
                    skipped_count += 1
                    results.append({
                        'employee_name': att.employee.get_full_name() or att.employee.username,
                        'date': att.date.strftime('%b %d, %Y'),
                        'check_in_time': att.check_in.strftime('%I:%M %p'),
                        'success': False,
                        'reason': str(e)
                    })
    
    else:
        employee_id = data.get('employee_id')
        if not employee_id or employee_id == 'undefined':
            return JsonResponse({"error": "Valid employee ID is required"}, status=400)
        
        try:
            emp = User.objects.get(id=employee_id)
        except User.DoesNotExist:
            return JsonResponse({"error": f"Employee with ID {employee_id} not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Error fetching employee: {str(e)}"}, status=500)
        
        missing_for_emp = Attendance.objects.filter(
            employee=emp,
            check_in__isnull=False,
            check_out__isnull=True,
            date__lte=yesterday
        ).order_by('-date')
        
        for att in missing_for_emp:
            is_on_leave = LeaveRequest.objects.filter(
                employee=emp,
                status='approved',
                start_date__lte=att.date,
                end_date__gte=att.date
            ).exists()
            
            is_on_wfh = WFHRequest.objects.filter(
                employee=emp,
                status='approved',
                start_date__lte=att.date,
                end_date__gte=att.date
            ).exists()
            
            if is_on_leave:
                skipped_count += 1
                results.append({
                    'employee_name': emp.get_full_name() or emp.username,
                    'date': att.date.strftime('%b %d, %Y'),
                    'check_in_time': att.check_in.strftime('%I:%M %p'),
                    'success': False,
                    'reason': 'On Leave'
                })
            elif is_on_wfh:
                skipped_count += 1
                results.append({
                    'employee_name': emp.get_full_name() or emp.username,
                    'date': att.date.strftime('%b %d, %Y'),
                    'check_in_time': att.check_in.strftime('%I:%M %p'),
                    'success': False,
                    'reason': 'On WFH'
                })
            else:
                try:
                    checkout_datetime = timezone.make_aware(
                        datetime.combine(att.date, checkout_time)
                    )
                    att.check_out = checkout_datetime
                    att.calculate_work_hours()
                    att.save()
                    
                    AuditLog.objects.create(
                        user=request.user,
                        action='check_out',
                        description=f'Bulk checkout assignment: 7 PM for {att.employee.username} on {att.date}',
                        target_user=att.employee
                    )
                    
                    assigned_count += 1
                    results.append({
                        'employee_name': emp.get_full_name() or emp.username,
                        'date': att.date.strftime('%b %d, %Y'),
                        'check_in_time': att.check_in.strftime('%I:%M %p'),
                        'success': True,
                        'reason': 'Assigned'
                    })
                except Exception as e:
                    skipped_count += 1
                    results.append({
                        'employee_name': emp.get_full_name() or emp.username,
                        'date': att.date.strftime('%b %d, %Y'),
                        'check_in_time': att.check_in.strftime('%I:%M %p'),
                        'success': False,
                        'reason': str(e)
                    })
    
    return JsonResponse({
        'assigned_count': assigned_count,
        'skipped_count': skipped_count,
        'results': results
    })
