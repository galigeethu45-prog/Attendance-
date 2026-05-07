"""
Office IP Management Views
Allows HR to manage allowed office IP addresses through the dashboard
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import re
from attendance.models import SystemSettings, AuditLog


def is_valid_ip(ip_address):
    """
    Validate IP address format (IPv4)
    """
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip_address):
        return False
    
    # Check each octet is 0-255
    octets = ip_address.split('.')
    for octet in octets:
        if int(octet) > 255:
            return False
    
    return True


@login_required
def office_ip_management(request):
    """
    Office IP Management page (HR only)
    """
    # Check if user is HR
    if not (request.user.is_superuser or hasattr(request.user, 'employeeprofile') and request.user.employeeprofile.is_hr):
        messages.error(request, "Access denied. HR privileges required.")
        return redirect('dashboard')
    
    settings = SystemSettings.get_settings()
    
    # Get current user's IP for easy copying
    from attendance.views import get_client_ip
    current_ip = get_client_ip(request)
    
    context = {
        'office_ips': settings.office_ips or [],
        'current_ip': current_ip,
    }
    
    return render(request, 'office_ip_management.html', context)


@login_required
@require_http_methods(["POST"])
def add_office_ip(request):
    """
    Add a new office IP address
    """
    # Check if user is HR
    if not (request.user.is_superuser or hasattr(request.user, 'employeeprofile') and request.user.employeeprofile.is_hr):
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
    
    ip_address = request.POST.get('ip_address', '').strip()
    description = request.POST.get('description', '').strip()
    
    # Validation
    if not ip_address:
        return JsonResponse({'success': False, 'error': 'IP address is required'})
    
    if not is_valid_ip(ip_address):
        return JsonResponse({'success': False, 'error': 'Invalid IP address format'})
    
    if not description:
        return JsonResponse({'success': False, 'error': 'Description is required'})
    
    # Add IP
    settings = SystemSettings.get_settings()
    success, message = settings.add_office_ip(ip_address, description, request.user)
    
    if success:
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action='role_change',  # Using existing action type
            description=f"Added office IP: {ip_address} ({description})",
            ip_address=get_client_ip(request)
        )
        
        return JsonResponse({'success': True, 'message': message})
    else:
        return JsonResponse({'success': False, 'error': message})


@login_required
@require_http_methods(["POST"])
def remove_office_ip(request):
    """
    Remove an office IP address
    """
    # Check if user is HR
    if not (request.user.is_superuser or hasattr(request.user, 'employeeprofile') and request.user.employeeprofile.is_hr):
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
    
    ip_address = request.POST.get('ip_address', '').strip()
    
    if not ip_address:
        return JsonResponse({'success': False, 'error': 'IP address is required'})
    
    # Remove IP
    settings = SystemSettings.get_settings()
    success, message = settings.remove_office_ip(ip_address)
    
    if success:
        # Create audit log
        from attendance.views import get_client_ip
        AuditLog.objects.create(
            user=request.user,
            action='role_change',
            description=f"Removed office IP: {ip_address}",
            ip_address=get_client_ip(request)
        )
        
        return JsonResponse({'success': True, 'message': message})
    else:
        return JsonResponse({'success': False, 'error': message})


@login_required
@require_http_methods(["POST"])
def toggle_office_ip(request):
    """
    Enable/disable an office IP address
    """
    # Check if user is HR
    if not (request.user.is_superuser or hasattr(request.user, 'employeeprofile') and request.user.employeeprofile.is_hr):
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
    
    ip_address = request.POST.get('ip_address', '').strip()
    is_active = request.POST.get('is_active') == 'true'
    
    if not ip_address:
        return JsonResponse({'success': False, 'error': 'IP address is required'})
    
    # Toggle IP
    settings = SystemSettings.get_settings()
    success, message = settings.toggle_office_ip(ip_address, is_active)
    
    if success:
        # Create audit log
        from attendance.views import get_client_ip
        AuditLog.objects.create(
            user=request.user,
            action='role_change',
            description=f"{'Enabled' if is_active else 'Disabled'} office IP: {ip_address}",
            ip_address=get_client_ip(request)
        )
        
        return JsonResponse({'success': True, 'message': message})
    else:
        return JsonResponse({'success': False, 'error': message})


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
