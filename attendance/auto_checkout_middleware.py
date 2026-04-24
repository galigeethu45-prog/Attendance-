"""
Auto Checkout Middleware
Automatically checks out employees at 7 PM if they forgot
Runs on every request after 7 PM
"""
from django.utils import timezone
from .models import Attendance, AuditLog
import pytz
from datetime import datetime, time as dt_time


class AutoCheckoutMiddleware:
    """
    Middleware to automatically checkout employees at 7 PM
    Simple logic: If time >= 7 PM, check for pending checkouts and auto-checkout
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.last_check = None
    
    def __call__(self, request):
        # Run auto-checkout check
        self.check_and_auto_checkout()
        
        response = self.get_response(request)
        return response
    
    def check_and_auto_checkout(self):
        """
        Simple auto-checkout logic:
        1. Check if current time >= 7 PM IST
        2. Find all attendance records without checkout
        3. Set checkout to 7 PM
        """
        local_tz = pytz.timezone('Asia/Kolkata')
        now = timezone.now().astimezone(local_tz)
        today = now.date()
        current_time = now.time()
        
        # Only run after 7 PM (19:00)
        checkout_time_threshold = dt_time(19, 0)  # 7:00 PM
        
        if current_time < checkout_time_threshold:
            return  # Not time yet
        
        # Prevent running multiple times in same minute
        current_minute = now.strftime('%Y-%m-%d %H:%M')
        if self.last_check == current_minute:
            return  # Already checked this minute
        
        self.last_check = current_minute
        
        # Find pending checkouts for today
        pending_checkouts = Attendance.objects.filter(
            date=today,
            check_out__isnull=True,
            check_in__isnull=False
        )
        
        if not pending_checkouts.exists():
            return  # No one to checkout
        
        # Auto checkout everyone
        checkout_datetime = timezone.datetime.combine(
            today,
            dt_time(19, 0)  # 7:00 PM
        )
        checkout_datetime = local_tz.localize(checkout_datetime)
        
        for attendance in pending_checkouts:
            attendance.check_out = checkout_datetime
            attendance.calculate_work_hours()
            attendance.save()
            
            # Log it
            try:
                AuditLog.objects.create(
                    user=attendance.employee,
                    action='check_out',
                    description='Auto checked out at 7:00 PM (system)',
                    ip_address=None
                )
            except:
                pass  # Don't fail if audit log fails
