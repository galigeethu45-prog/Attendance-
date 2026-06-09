from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from attendance.models import EmployeeProfile
from .serializers import RegisterSerializer


@api_view(['POST'])
def register_api(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Registration successful"},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_api(request):
    identifier = request.data.get('identifier')  # employee_id OR email
    password = request.data.get('password')

    if not identifier or not password:
        return Response(
            {"error": "Identifier and password required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Determine login type
    if '@' in identifier:
        try:
            user = User.objects.get(email=identifier)
            username = user.username
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
    else:
        username = identifier  # employee_id stored as username

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    login(request, user)

    profile = EmployeeProfile.objects.get(user=user)

    return Response({
        "message": "Login successful",
        "employee_id": profile.employee_id,
        "is_hr": profile.is_hr,
        "profile_completed": hasattr(profile, 'profile_completed') and profile.profile_completed
    })



# =============================
# MISSING CHECKOUTS API
# =============================
@api_view(['GET'])
def missing_checkouts_api(request):
    """Get missing checkouts for employee(s) - only for dates before today"""
    from django.utils import timezone
    from attendance.models import Attendance, LeaveRequest, WFHRequest
    from datetime import timedelta
    
    # Authentication and authorization check
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        profile = request.user.employeeprofile
        if not profile.is_hr:
            return Response({"error": "HR access only"}, status=status.HTTP_403_FORBIDDEN)
    except EmployeeProfile.DoesNotExist:
        return Response({"error": "Employee profile not found"}, status=status.HTTP_404_NOT_FOUND)
    
    
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
        
        return Response({
            'missing_checkouts': results,
            'total_records': len(results),
            'total_employees': len(set(a['employee_id'] for a in results)),
            'total_to_assign': total_to_assign
        })
    else:
        # Specific employee
        employee_id = request.GET.get('employee_id')
        if not employee_id:
            return Response({"error": "Employee ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            emp = User.objects.get(id=employee_id)
        except User.DoesNotExist:
            return Response({"error": f"Employee with ID {employee_id} not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Error fetching employee: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
        
        return Response({
            'missing_checkouts': results,
            'total_records': len(results)
        })


@api_view(['POST'])
def assign_missing_checkouts_api(request):
    """Assign missing checkouts for employee(s)"""
    from django.utils import timezone
    from datetime import time, timedelta, datetime
    from attendance.models import Attendance, LeaveRequest, WFHRequest, AuditLog
    
    # Authentication and authorization check
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        profile = request.user.employeeprofile
        if not profile.is_hr:
            return Response({"error": "HR access only"}, status=status.HTTP_403_FORBIDDEN)
    except EmployeeProfile.DoesNotExist:
        return Response({"error": "Employee profile not found"}, status=status.HTTP_404_NOT_FOUND)
    
    today = timezone.localtime(timezone.now()).date()
    yesterday = today - timedelta(days=1)
    checkout_time = time(19, 0)  # 7 PM
    
    mode = request.data.get('mode')
    employee_id = request.data.get('employee_id')
    
    # Validation
    if not mode or mode not in ['all', 'specific']:
        return Response({"error": "Valid mode ('all' or 'specific') is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    if mode == 'specific' and not employee_id:
        return Response({"error": "Employee ID is required for specific mode"}, status=status.HTTP_400_BAD_REQUEST)
    
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
        # Specific employee
        employee_id = request.data.get('employee_id')
        if not employee_id or employee_id == 'undefined':
            return Response({"error": "Valid employee ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            emp = User.objects.get(id=employee_id)
        except User.DoesNotExist:
            return Response({"error": f"Employee with ID {employee_id} not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Error fetching employee: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
    
    return Response({
        'assigned_count': assigned_count,
        'skipped_count': skipped_count,
        'results': results
    })
