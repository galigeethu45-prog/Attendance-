#!/usr/bin/env python
"""
Debug template rendering
"""
import os
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.template.loader import get_template
from django.contrib.auth.models import User
from attendance.models import EmployeeProfile, Attendance, LeaveRequest
from django.db.models import Sum

try:
    # Get employee
    employee_user = User.objects.filter(is_superuser=False).first()
    if not employee_user:
        print("No employee found")
        exit(1)
    
    print(f"Testing template for: {employee_user.username}")
    
    # Get profile
    try:
        employee_profile = employee_user.employeeprofile
        print(f"✓ Profile found: {employee_profile.employee_id}")
        print(f"✓ Work mode: {employee_profile.work_mode}")
    except EmployeeProfile.DoesNotExist:
        print("✗ No profile")
        employee_profile = None
    
    # Get stats
    total_attendance = Attendance.objects.filter(employee=employee_user)
    total_present = total_attendance.filter(status='present').count()
    total_late = total_attendance.filter(status='late').count()
    total_half_day = total_attendance.filter(status='half-day').count()
    total_hours = total_attendance.aggregate(Sum('total_work_hours'))['total_work_hours__sum'] or 0
    
    # Recent attendance
    recent_attendance = Attendance.objects.filter(employee=employee_user).order_by('-date')[:10]
    
    # Leave requests
    leave_requests = LeaveRequest.objects.filter(employee=employee_user).order_by('-created_at')[:10]
    
    context = {
        'employee_user': employee_user,
        'employee_profile': employee_profile,
        'total_present': total_present,
        'total_late': total_late,
        'total_half_day': total_half_day,
        'total_hours': total_hours,
        'recent_attendance': recent_attendance,
        'leave_requests': leave_requests,
        'user': User.objects.filter(is_superuser=True).first(),  # For base template
    }
    
    print(f"\nContext prepared:")
    for key, value in context.items():
        if key not in ['recent_attendance', 'leave_requests']:
            print(f"  {key}: {value}")
    
    # Load template
    print(f"\nLoading template...")
    template = get_template('employee_details.html')
    
    # Render
    print(f"Rendering template...")
    html = template.render(context)
    
    print(f"\n✓ Template rendered successfully!")
    print(f"✓ Output length: {len(html)} bytes")
    
    if len(html) < 100:
        print(f"\n❌ OUTPUT TOO SHORT!")
        print(f"Content: {html}")
    else:
        print(f"\n✓ Template looks good!")
        # Check for key elements
        if 'Employee Details' in html:
            print(f"✓ Contains 'Employee Details'")
        if 'Work Mode' in html:
            print(f"✓ Contains 'Work Mode'")
        if employee_profile and employee_profile.get_work_mode_display() in html:
            print(f"✓ Contains work mode value: {employee_profile.get_work_mode_display()}")
        
except Exception as e:
    print(f"\n❌ ERROR:")
    print(traceback.format_exc())
