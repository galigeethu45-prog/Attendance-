"""
EOD API Integration - Read-Only Views
Purpose: Provide employee and attendance data to EOD system
Authentication: X-API-Key header required
Methods: GET only (read-only)

SmartPunch is the source of truth. EOD must NOT calculate attendance.
"""

import os
from functools import wraps
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User

from attendance.models import EmployeeMasterData, Attendance, LeaveRequest, WFHRequest
from .eod_serializers import EODEmployeeSerializer, EODAttendanceSerializer


# =========================
# AUTHENTICATION DECORATOR
# =========================

def eod_api_key_required(view_func):
    """
    Decorator to validate EOD API key authentication.
    
    Checks:
    - X-API-Key header is present
    - X-API-Key matches environment variable EOD_API_KEY
    
    Returns:
    - 401 Unauthorized if API key is missing or incorrect
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Get API key from header
        api_key = request.META.get('HTTP_X_API_KEY')
        
        # Get expected key from environment
        expected_key = os.environ.get('EOD_API_KEY', '')
        
        # Validate API key
        if not api_key:
            return JsonResponse({
                "error": "Unauthorized"
            }, status=401)
        
        if not expected_key:
            # API key not configured - security issue
            return JsonResponse({
                "error": "Unauthorized"
            }, status=401)
        
        if api_key != expected_key:
            return JsonResponse({
                "error": "Unauthorized"
            }, status=401)
        
        # API key valid - proceed
        return view_func(request, *args, **kwargs)
    
    return wrapper


# =========================
# HELPER FUNCTIONS
# =========================

def get_final_attendance_status(employee_id, date):
    """
    Determine final attendance status for employee on given date.
    
    SmartPunch determines the status. EOD receives only the final result.
    Uses EmployeeMasterData as the authoritative source for employee identity.
    
    Logic:
    1. Check approved LeaveRequest → LEAVE
    2. Check approved WFHRequest → WFH
    3. Check Attendance record:
       - present/late/half-day → PRESENT
       - absent → ABSENT
    4. No record + no leave + no WFH → ABSENT
    
    Args:
        employee_id (str): Employee ID
        date (datetime.date): Date to check
    
    Returns:
        str: One of 'PRESENT', 'ABSENT', 'WFH', 'LEAVE'
    """
    
    # Get User from EmployeeMasterData (authoritative source)
    try:
        master_data = EmployeeMasterData.objects.filter(
            employee_id=employee_id
        ).select_related('linked_user').first()
        
        if not master_data or not master_data.linked_user:
            # No user found for this employee_id
            return 'ABSENT'
        
        user = master_data.linked_user
        
    except Exception:
        return 'ABSENT'
    
    # 1. Check for approved leave
    has_approved_leave = LeaveRequest.objects.filter(
        employee=user,
        status='approved',
        start_date__lte=date,
        end_date__gte=date
    ).exists()
    
    if has_approved_leave:
        return 'LEAVE'
    
    # 2. Check for approved WFH
    has_approved_wfh = WFHRequest.objects.filter(
        employee=user,
        status='approved',
        start_date__lte=date,
        end_date__gte=date
    ).exists()
    
    if has_approved_wfh:
        return 'WFH'
    
    # 3. Check Attendance record
    attendance = Attendance.objects.filter(
        employee=user,
        date=date
    ).first()
    
    if attendance:
        # Normalize SmartPunch status to EOD status
        if attendance.status in ['present', 'late', 'half-day']:
            return 'PRESENT'
        elif attendance.status == 'absent':
            return 'ABSENT'
        else:
            # Unknown status - default to ABSENT
            return 'ABSENT'
    
    # 4. No attendance record, no leave, no WFH
    return 'ABSENT'


# =========================
# API ENDPOINTS
# =========================

@require_http_methods(["GET"])
@eod_api_key_required
def eod_employee_list(request):
    """
    EOD API: Get list of all active employees.
    
    **Endpoint:** GET /attendance/api/eod/employees/
    
    **Authentication:** X-API-Key header required
    
    **Returns:**
    - 200: JSON with employee list
    - 401: Unauthorized (missing or invalid API key)
    - 405: Method not allowed (POST/PUT/DELETE/PATCH)
    
    **Response Format:**
    {
        "employees": [
            {
                "employee_id": "AI0001",
                "first_name": "John",
                "last_name": "Doe",
                "department": "Engineering",
                "designation": "Software Developer"
            }
        ]
    }
    
    **Note:** Only returns non-sensitive fields. Does NOT expose:
    - Aadhaar, PAN, email, phone, address, DOB, gender, bank details, salary
    """
    
    # Query only active employees (those with account_created=True or linked_user)
    employees = EmployeeMasterData.objects.filter(
        account_created=True
    ).only(
        'employee_id', 'first_name', 'last_name', 'department', 'designation'
    ).order_by('employee_id')
    
    # Serialize employees
    serializer = EODEmployeeSerializer(employees, many=True)
    
    return JsonResponse({
        'employees': serializer.data
    }, status=200)


@require_http_methods(["GET"])
@eod_api_key_required
def eod_attendance_list(request):
    """
    EOD API: Get daily attendance status for all employees.
    
    **Endpoint:** GET /attendance/api/eod/attendance/?date=YYYY-MM-DD
    
    **Authentication:** X-API-Key header required
    
    **Query Parameters:**
    - date (required): Date in YYYY-MM-DD format (e.g., 2026-10-01)
    
    **Returns:**
    - 200: JSON with attendance data
    - 400: Bad request (missing or invalid date)
    - 401: Unauthorized (missing or invalid API key)
    - 405: Method not allowed (POST/PUT/DELETE/PATCH)
    
    **Response Format:**
    {
        "date": "2026-10-01",
        "attendance": [
            {
                "employee_id": "AI0001",
                "status": "PRESENT"
            },
            {
                "employee_id": "AI0002",
                "status": "WFH"
            },
            {
                "employee_id": "AI0003",
                "status": "LEAVE"
            },
            {
                "employee_id": "AI0004",
                "status": "ABSENT"
            }
        ]
    }
    
    **Status Values:**
    - PRESENT: Employee checked in (present/late/half-day in SmartPunch)
    - ABSENT: No attendance record + no leave + no WFH
    - WFH: Approved work-from-home request
    - LEAVE: Approved leave request
    
    **Note:** 
    - SmartPunch determines the final status
    - EOD must NOT calculate attendance
    - Does NOT expose check-in/check-out/work-hours
    """
    
    # Get date parameter
    date_str = request.GET.get('date')
    
    # Validate date parameter
    if not date_str:
        return JsonResponse({
            "error": "date parameter is required"
        }, status=400)
    
    # Parse date
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({
            "error": "Invalid date format. Use YYYY-MM-DD."
        }, status=400)
    
    # Get all active employees
    employees = EmployeeMasterData.objects.filter(
        account_created=True
    ).only('employee_id').order_by('employee_id')
    
    # Build attendance data
    attendance_data = []
    
    for employee in employees:
        # Get final status for this employee and date
        status = get_final_attendance_status(employee.employee_id, date_obj)
        
        attendance_data.append({
            'employee_id': employee.employee_id,
            'status': status
        })
    
    # Serialize and return
    serializer = EODAttendanceSerializer(attendance_data, many=True)
    
    return JsonResponse({
        'date': date_str,
        'attendance': serializer.data
    }, status=200)
