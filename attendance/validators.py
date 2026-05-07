"""
Server-side validation utilities for attendance system
"""
from datetime import datetime, date
from django.utils import timezone
from django.contrib import messages
from attendance.models import LeaveRequest, WFHRequest, OnsiteRequest
import json


class DateValidator:
    """Validate dates and date ranges"""
    
    @staticmethod
    def validate_date_format(date_string, field_name="Date"):
        """Validate date format (YYYY-MM-DD)"""
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True, None
        except ValueError:
            return False, f"{field_name} must be in YYYY-MM-DD format"
    
    @staticmethod
    def validate_future_date(date_obj, field_name="Date", allow_today=True):
        """Validate that date is in the future (or today if allowed)"""
        today = timezone.now().date()
        if allow_today:
            if date_obj < today:
                return False, f"{field_name} cannot be in the past"
        else:
            if date_obj <= today:
                return False, f"{field_name} must be in the future"
        return True, None
    
    @staticmethod
    def validate_date_range(start_date, end_date):
        """Validate that end date is after or equal to start date"""
        if end_date < start_date:
            return False, "End date cannot be before start date"
        return True, None
    
    @staticmethod
    def parse_and_validate_selected_dates(selected_dates_json):
        """Parse and validate JSON array of selected dates"""
        if not selected_dates_json:
            return None, None
        
        try:
            selected_dates = json.loads(selected_dates_json)
            
            if not isinstance(selected_dates, list):
                return None, "Selected dates must be a list"
            
            if len(selected_dates) == 0:
                return None, "At least one date must be selected"
            
            # Validate each date
            today = timezone.now().date()
            validated_dates = []
            
            for date_str in selected_dates:
                # Validate format
                is_valid, error = DateValidator.validate_date_format(date_str, "Selected date")
                if not is_valid:
                    return None, error
                
                # Parse date
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # Validate future date
                is_valid, error = DateValidator.validate_future_date(date_obj, "Selected date")
                if not is_valid:
                    return None, f"{error}: {date_str}"
                
                validated_dates.append(date_str)
            
            # Remove duplicates and sort
            validated_dates = sorted(list(set(validated_dates)))
            
            return validated_dates, None
            
        except json.JSONDecodeError:
            return None, "Invalid date selection format"
        except Exception as e:
            return None, f"Error parsing dates: {str(e)}"


class FieldValidator:
    """Validate form fields"""
    
    @staticmethod
    def validate_required(value, field_name):
        """Validate required field"""
        if not value or (isinstance(value, str) and value.strip() == ''):
            return False, f"{field_name} is required"
        return True, None
    
    @staticmethod
    def validate_length(value, min_length=None, max_length=None, field_name="Field"):
        """Validate field length"""
        if not value:
            return True, None
        
        length = len(value.strip())
        
        if min_length and length < min_length:
            return False, f"{field_name} must be at least {min_length} characters"
        
        if max_length and length > max_length:
            return False, f"{field_name} must not exceed {max_length} characters"
        
        return True, None
    
    @staticmethod
    def validate_choice(value, choices, field_name="Field"):
        """Validate that value is in allowed choices"""
        if value not in choices:
            return False, f"Invalid {field_name}"
        return True, None


class OverlapValidator:
    """Validate overlapping requests"""
    
    @staticmethod
    def check_leave_overlap(user, start_date, end_date, selected_dates=None, exclude_id=None):
        """Check for overlapping leave requests"""
        # Get all pending or approved leave requests for this user
        existing_requests = LeaveRequest.objects.filter(
            employee=user,
            status__in=['pending', 'approved']
        )
        
        if exclude_id:
            existing_requests = existing_requests.exclude(id=exclude_id)
        
        # Check for overlaps
        for request in existing_requests:
            if OverlapValidator._dates_overlap(
                start_date, end_date, selected_dates,
                request.start_date, request.end_date, request.selected_dates
            ):
                return False, f"This leave request overlaps with an existing {request.get_leave_type_display()} leave request"
        
        return True, None
    
    @staticmethod
    def check_wfh_overlap(user, start_date, end_date, selected_dates=None, exclude_id=None):
        """Check for overlapping WFH requests"""
        # Get all pending or approved WFH requests for this user
        existing_requests = WFHRequest.objects.filter(
            employee=user,
            status__in=['pending', 'approved']
        )
        
        if exclude_id:
            existing_requests = existing_requests.exclude(id=exclude_id)
        
        # Check for overlaps
        for request in existing_requests:
            if OverlapValidator._dates_overlap(
                start_date, end_date, selected_dates,
                request.start_date, request.end_date, request.selected_dates
            ):
                return False, "This WFH request overlaps with an existing WFH request"
        
        return True, None
    
    @staticmethod
    def check_onsite_overlap(user, visit_date, exclude_id=None):
        """Check for overlapping onsite requests"""
        # Get all pending or approved onsite requests for this user on the same date
        existing_requests = OnsiteRequest.objects.filter(
            employee=user,
            visit_date=visit_date,
            status__in=['pending', 'approved']
        )
        
        if exclude_id:
            existing_requests = existing_requests.exclude(id=exclude_id)
        
        if existing_requests.exists():
            return False, "You already have an onsite request for this date"
        
        return True, None
    
    @staticmethod
    def _dates_overlap(start1, end1, selected1, start2, end2, selected2):
        """Check if two date ranges or selected dates overlap"""
        # Convert to date objects if needed
        if isinstance(start1, str):
            start1 = datetime.strptime(start1, '%Y-%m-%d').date()
        if isinstance(end1, str):
            end1 = datetime.strptime(end1, '%Y-%m-%d').date()
        if isinstance(start2, str):
            start2 = datetime.strptime(start2, '%Y-%m-%d').date()
        if isinstance(end2, str):
            end2 = datetime.strptime(end2, '%Y-%m-%d').date()
        
        # If both have selected dates, check for common dates
        if selected1 and selected2:
            dates1 = set(selected1)
            dates2 = set(selected2)
            return bool(dates1 & dates2)
        
        # If first has selected dates, check against second's range
        if selected1:
            for date_str in selected1:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                if start2 <= date_obj <= end2:
                    return True
            return False
        
        # If second has selected dates, check against first's range
        if selected2:
            for date_str in selected2:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                if start1 <= date_obj <= end1:
                    return True
            return False
        
        # Both are ranges, check for overlap
        return start1 <= end2 and end1 >= start2


class PermissionValidator:
    """Validate user permissions"""
    
    @staticmethod
    def can_approve_leave(user):
        """Check if user can approve leave requests"""
        if user.is_superuser:
            return True
        
        try:
            profile = user.employeeprofile
            return profile.role in ['team_leader', 'manager'] or profile.is_hr
        except:
            return False
    
    @staticmethod
    def can_approve_wfh(user):
        """Check if user can approve WFH requests"""
        return PermissionValidator.can_approve_leave(user)
    
    @staticmethod
    def can_approve_onsite(user):
        """Check if user can approve onsite requests"""
        if user.is_superuser:
            return True
        
        try:
            profile = user.employeeprofile
            return profile.role == 'manager' or profile.is_hr
        except:
            return False
    
    @staticmethod
    def is_hr_or_manager(user):
        """Check if user is HR or Manager"""
        if user.is_superuser:
            return True
        
        try:
            profile = user.employeeprofile
            return profile.is_hr or profile.role == 'manager'
        except:
            return False
