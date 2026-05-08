from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# =========================
# EMPLOYEE MASTER DATA
# =========================
class EmployeeMasterData(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    # Primary identification
    employee_id = models.CharField(max_length=20, unique=True, db_index=True)
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    
    # Company Information
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    date_of_joining = models.DateField()
    
    # Contact Details
    phone_number = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True, db_index=True)
    
    # Address
    local_address = models.TextField()
    permanent_address = models.TextField()
    
    # Identity Documents
    aadhar_number = models.CharField(max_length=12)
    pan_number = models.CharField(max_length=10)
    
    # Account Status
    account_created = models.BooleanField(default=False)
    linked_user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='master_data')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_master_data')
    
    class Meta:
        verbose_name = 'Employee Master Data'
        verbose_name_plural = 'Employee Master Data'
        ordering = ['employee_id']
        indexes = [
            models.Index(fields=['employee_id', 'email', 'date_of_birth']),
        ]
    
    def __str__(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name}"
    
    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"


# =========================
# BREAK RULE CONFIGURATION
# =========================
BREAK_RULES = {
    'tea': {
        'max_count': 2,
        'allowed_minutes': 15,
    },
    'lunch': {
        'max_count': 1,
        'allowed_minutes': 45,
    }
}

# Break time windows (IST)
BREAK_TIME_WINDOWS = {
    'tea_morning': {
        'start_hour': 10,
        'start_minute': 0,
        'end_hour': 11,
        'end_minute': 0,
    },
    'lunch': {
        'start_hour': 13,  # 1 PM
        'start_minute': 0,
        'end_hour': 13,
        'end_minute': 45,
    },
    'tea_evening': {
        'start_hour': 16,  # 4 PM
        'start_minute': 0,
        'end_hour': 16,
        'end_minute': 45,
    }
}

# =========================
# EMPLOYEE PROFILE
# =========================
class EmployeeProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    WORK_MODE_CHOICES = [
        ('office', 'Office Only'),
        ('hybrid', 'Hybrid (Office + WFH)'),
        ('permanent_wfh', 'Permanent Work From Home'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Employee ID
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True)
    
    # Profile Photo
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    
    # Work Mode (for hybrid/remote employees)
    work_mode = models.CharField(
        max_length=20, 
        choices=WORK_MODE_CHOICES, 
        default='office',
        help_text='Determines network access requirements for check-in'
    )

    # Personal Information
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    alternate_phone = models.CharField(max_length=15, blank=True)
    
    # Address
    local_address = models.TextField(blank=True)
    permanent_address = models.TextField(blank=True)
    
    # Documents
    aadhar_number = models.CharField(max_length=12, blank=True)
    pan_number = models.CharField(max_length=10, blank=True)
    
    # Company Information
    department = models.CharField(max_length=100, blank=True, db_index=True)
    designation = models.CharField(max_length=100, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    is_hr = models.BooleanField(default=False, db_index=True)
    
    # Role Management
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('team_leader', 'Team Leader'),
        ('manager', 'Manager'),
        ('hr', 'HR/Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee', db_index=True)
    
    # Profile completion
    profile_completed = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['employee_id', 'is_hr']),
            models.Index(fields=['department']),
        ]

    def __str__(self):
        return self.employee_id or self.user.username
    
    def save(self, *args, **kwargs):
        """
        Override save to automatically set is_hr=True when role is 'manager'
        This ensures managers have HR dashboard access
        """
        if self.role == 'manager':
            self.is_hr = True
        elif self.role == 'hr':
            self.is_hr = True
        elif self.role in ['employee', 'team_leader']:
            # Don't automatically remove is_hr for employees/TLs
            # in case they were manually granted HR access
            pass
        
        super().save(*args, **kwargs)
    
    def is_birthday_today(self):
        """
        Check if today is the employee's birthday
        Returns: Boolean
        """
        if not self.date_of_birth:
            return False
        
        from django.utils import timezone
        today = timezone.now().date()
        return (self.date_of_birth.month == today.month and 
                self.date_of_birth.day == today.day)
    
    def get_age(self):
        """
        Calculate employee's current age
        Returns: Integer or None
        """
        if not self.date_of_birth:
            return None
        
        from django.utils import timezone
        today = timezone.now().date()
        age = today.year - self.date_of_birth.year
        
        # Adjust if birthday hasn't occurred yet this year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        
        return age


# =========================
# ATTENDANCE
# =========================
class Attendance(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    date = models.DateField(default=timezone.now, db_index=True)

    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)

    # Stored in decimal format (example: 7.75)
    total_work_hours = models.FloatField(default=0)

    status = models.CharField(
        max_length=20,
        choices=[
            ('present', 'Present'),
            ('late', 'Late'),
            ('half-day', 'Half-Day'),
            ('absent', 'Absent'),
        ],
        default='present',
        db_index=True
    )
    
    # HR/Admin Edit Tracking
    status_modified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='modified_attendances'
    )
    status_modified_at = models.DateTimeField(null=True, blank=True)
    status_change_reason = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('employee', 'date')
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date', 'status']),
            models.Index(fields=['-date']),
        ]
        ordering = ['-date']

    def calculate_work_hours(self):
        """
        Calculate total working hours based ONLY on check-in and check-out.
        Break time is INCLUDED as per company policy.
        Also sets attendance status automatically.
        If marked as half-day at check-in (late arrival), cap hours at 3.75 (half of 7.5).
        """
        if self.check_in and self.check_out:
            duration = self.check_out - self.check_in
            total_hours = duration.total_seconds() / 3600
            
            # If already marked as half-day (late check-in), cap at 3.75 hours
            if self.status == 'half-day':
                self.total_work_hours = min(round(total_hours, 2), 3.75)
            else:
                self.total_work_hours = round(total_hours, 2)
                
                # Attendance status logic (manager-approved)
                if total_hours >= 7.5:
                    self.status = 'present'
                elif total_hours < 6:
                    self.status = 'half-day'
                else:
                    self.status = 'half-day'  # policy zone (6h–7h29m)

            self.save()

    def get_work_hours_display(self):
        """
        Converts decimal hours to readable format (e.g. 7h 30m)
        """
        total_minutes = int(self.total_work_hours * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours}h {minutes}m"

    def __str__(self):
        return f"{self.employee.username} - {self.date}"


# =========================
# BREAK LOG
# =========================
class BreakLog(models.Model):
    BREAK_TYPES = [
        ('tea', 'Tea Break'),
        ('lunch', 'Lunch Break'),
    ]
    
    TIME_SLOTS = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
    ]

    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE,
        related_name='breaks'
    )
    break_type = models.CharField(
        max_length=10,
        choices=BREAK_TYPES
    )
    time_slot = models.CharField(
        max_length=10,
        choices=TIME_SLOTS,
        default='morning',
        null=True,
        blank=True
    )
    break_start = models.DateTimeField(null=True, blank=True)
    break_end = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)

    def calculate_break_duration(self):
        if self.break_start and self.break_end:
            duration = self.break_end - self.break_start
            self.duration_minutes = int(duration.total_seconds() / 60)
            self.save()

    def is_exceeded(self):
        """
        Check if break duration exceeded allowed time
        """
        rule = BREAK_RULES.get(self.break_type)
        if not rule:
            return False
        return self.duration_minutes > rule['allowed_minutes']

    def allowed_minutes(self):
        """
        Return allowed minutes for this break type
        """
        rule = BREAK_RULES.get(self.break_type)
        return rule['allowed_minutes'] if rule else 0

    def __str__(self):
        return f"{self.attendance.employee.username} - {self.break_type}"


# =========================
# LEAVE REQUEST
# =========================
class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('earned', 'Earned Leaves'),
        ('menstrual', 'Menstrual Leave'),
        ('unpaid', 'Unpaid Leaves'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    
    # Multi-date selection support (JSON field for non-consecutive dates)
    # Format: ["2026-05-21", "2026-05-25", "2026-05-30"]
    selected_dates = models.JSONField(null=True, blank=True, help_text="List of specific dates (for non-consecutive leaves)")
    
    reason = models.TextField(default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    hr_comment = models.TextField(blank=True, null=True)
    
    # Hierarchical approval fields
    tl_comment = models.TextField(blank=True, null=True, help_text="Team Leader's comment")
    tl_approved = models.BooleanField(default=False, help_text="Team Leader approval status")
    tl_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tl_approved_leaves')
    tl_approved_at = models.DateTimeField(null=True, blank=True)
    
    manager_comment = models.TextField(blank=True, null=True, help_text="Manager's comment")
    manager_approved = models.BooleanField(default=False, help_text="Manager approval status")
    manager_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='manager_approved_leaves')
    manager_approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_days(self):
        """Calculate total days - uses selected_dates if available, otherwise date range
        EXCLUDES HOLIDAYS from the count"""
        dates_list = self.get_dates_list()
        
        # Count only working days (exclude holidays)
        working_days = 0
        for date in dates_list:
            if CompanyHoliday.is_working_day(date):
                working_days += 1
        
        return working_days
    
    def get_dates_list(self):
        """Get list of all dates covered by this leave request"""
        if self.selected_dates:
            # Return selected dates as date objects
            from datetime import datetime
            return [datetime.strptime(d, '%Y-%m-%d').date() for d in self.selected_dates]
        else:
            # Return date range
            from datetime import timedelta
            dates = []
            current = self.start_date
            while current <= self.end_date:
                dates.append(current)
                current += timedelta(days=1)
            return dates

    def __str__(self):
        return f"{self.employee.username} - {self.get_leave_type_display()} ({self.status})"


# =========================
# NOTIFICATION
# =========================
class Notification(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message[:30]


# =========================
# OVERTIME (OT)
# =========================
class Overtime(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    reason = models.TextField(default='No reason provided', blank=True)  # Why OT is needed
    
    # Request phase
    requested_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    hr_comment = models.TextField(blank=True, null=True)
    hr_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_overtimes')
    
    # Execution phase (after approval)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_hours = models.FloatField(default=0)
    
    # Keep for backward compatibility
    approved_by_hr = models.BooleanField(default=False)
    
    def calculate_ot_hours(self):
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            self.total_hours = round(duration.total_seconds() / 3600, 2)
            self.save()
    
    def get_ot_hours_display(self):
        if self.total_hours == 0:
            return "Not started"
        total_minutes = int(self.total_hours * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours}h {minutes}m"
    
    def __str__(self):
        return f"{self.employee.username} - OT on {self.date}"


# =========================
# WORK FROM HOME (WFH) REQUEST
# =========================
class WFHRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Multi-date selection support (JSON field for non-consecutive dates)
    # Format: ["2026-05-21", "2026-05-25", "2026-05-30"]
    selected_dates = models.JSONField(null=True, blank=True, help_text="List of specific dates (for non-consecutive WFH)")
    
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    hr_comment = models.TextField(blank=True, null=True)
    hr_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_wfh_requests')
    
    # Hierarchical approval fields
    tl_comment = models.TextField(blank=True, null=True, help_text="Team Leader's comment")
    tl_approved = models.BooleanField(default=False, help_text="Team Leader approval status")
    tl_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tl_approved_wfh')
    tl_approved_at = models.DateTimeField(null=True, blank=True)
    
    manager_comment = models.TextField(blank=True, null=True, help_text="Manager's comment")
    manager_approved = models.BooleanField(default=False, help_text="Manager approval status")
    manager_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='manager_approved_wfh')
    manager_approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_days(self):
        """Calculate total days - uses selected_dates if available, otherwise date range
        EXCLUDES HOLIDAYS from the count"""
        dates_list = self.get_dates_list()
        
        # Count only working days (exclude holidays)
        working_days = 0
        for date in dates_list:
            if CompanyHoliday.is_working_day(date):
                working_days += 1
        
        return working_days
    
    def get_dates_list(self):
        """Get list of all dates covered by this WFH request"""
        if self.selected_dates:
            # Return selected dates as date objects
            from datetime import datetime
            return [datetime.strptime(d, '%Y-%m-%d').date() for d in self.selected_dates]
        else:
            # Return date range
            from datetime import timedelta
            dates = []
            current = self.start_date
            while current <= self.end_date:
                dates.append(current)
                current += timedelta(days=1)
            return dates
    
    def __str__(self):
        return f"{self.employee.username} - WFH ({self.start_date} to {self.end_date})"


# =========================
# ONSITE/CLIENT VISIT REQUEST
# =========================
class OnsiteRequest(models.Model):
    """
    Request for onsite/client visit where employee goes directly to client location
    instead of office. Allows flexible break times during client meetings.
    """
    VISIT_TYPES = [
        ('onsite', 'Onsite Visit (Physical)'),
        ('online_meeting', 'Online Client Meeting (From Office)'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPES, default='onsite')
    visit_date = models.DateField()
    client_name = models.CharField(max_length=200, help_text="Client/Project name")
    location = models.TextField(help_text="Client location or 'Online' for virtual meetings")
    purpose = models.TextField(help_text="Purpose of visit/meeting")
    expected_duration = models.CharField(max_length=50, help_text="e.g., '2 hours', '10 AM - 4 PM'")
    
    # Approval fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    hr_comment = models.TextField(blank=True, null=True)
    hr_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_onsite_requests')
    
    # Hierarchical approval
    manager_comment = models.TextField(blank=True, null=True)
    manager_approved = models.BooleanField(default=False)
    manager_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='manager_approved_onsite')
    manager_approved_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Actual visit tracking
    actual_check_in = models.DateTimeField(null=True, blank=True, help_text="When employee checked in for onsite visit")
    actual_check_out = models.DateTimeField(null=True, blank=True, help_text="When employee checked out from onsite visit")
    
    class Meta:
        ordering = ['-visit_date']
        indexes = [
            models.Index(fields=['employee', 'visit_date']),
            models.Index(fields=['status', 'visit_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.username} - {self.get_visit_type_display()} on {self.visit_date}"
    
    def is_active_today(self):
        """Check if this onsite request is for today and approved"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.visit_date == today and self.status == 'approved'


# =========================
# AUDIT LOG
# =========================
class AuditLog(models.Model):
    ACTION_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
        ('break_start', 'Break Start'),
        ('break_end', 'Break End'),
        ('leave_request', 'Leave Request'),
        ('leave_approve', 'Leave Approved'),
        ('leave_reject', 'Leave Rejected'),
        ('leave_cancel', 'Leave Cancelled'),
        ('profile_update', 'Profile Updated'),
        ('user_create', 'User Created'),
        ('user_delete', 'User Deleted'),
        ('overtime_request', 'Overtime Requested'),
        ('overtime_start', 'Overtime Start'),
        ('overtime_end', 'Overtime End'),
        ('overtime_approve', 'Overtime Approved'),
        ('overtime_reject', 'Overtime Rejected'),
        ('wfh_request', 'WFH Requested'),
        ('wfh_approve', 'WFH Approved'),
        ('wfh_reject', 'WFH Rejected'),
        ('wfh_cancel', 'WFH Cancelled'),
        ('role_change', 'Role Changed'),
        ('attendance_status_change', 'Attendance Status Changed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs', db_index=True)
    action = models.CharField(max_length=50, choices=ACTION_TYPES, db_index=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_target')
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'System'} - {self.get_action_display()} - {self.timestamp}"



# =========================
# SYSTEM SETTINGS
# =========================
class SystemSettings(models.Model):
    """
    System-wide settings (Singleton pattern)
    Only one record should exist in this table
    """
    # Office Network IP Management
    office_ips = models.JSONField(
        default=list,
        blank=True,
        help_text="List of allowed office IP addresses with metadata (JSON format)"
    )
    
    # Emergency Override - Bypass IP restrictions
    emergency_override_enabled = models.BooleanField(
        default=False,
        help_text="When enabled, all employees can check-in from any location (bypasses IP restrictions)"
    )
    emergency_override_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for enabling emergency override (e.g., 'Regus network down')"
    )
    emergency_override_enabled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emergency_overrides_enabled',
        help_text="HR user who enabled the override"
    )
    emergency_override_enabled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the override was enabled"
    )
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_settings_updates'
    )
    
    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"
    
    def __str__(self):
        status = "ENABLED" if self.emergency_override_enabled else "DISABLED"
        return f"System Settings - Emergency Override: {status}"
    
    @classmethod
    def get_settings(cls):
        """
        Get or create the singleton settings instance
        """
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    def save(self, *args, **kwargs):
        """
        Ensure only one instance exists (Singleton pattern)
        """
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Prevent deletion of settings
        """
        pass
    
    @classmethod
    def is_emergency_override_active(cls):
        """
        Quick check if emergency override is enabled
        """
        settings = cls.get_settings()
        return settings.emergency_override_enabled
    
    def get_active_office_ips(self):
        """
        Get list of active office IP addresses
        Returns: List of IP strings
        """
        if not self.office_ips:
            return []
        
        active_ips = []
        for ip_entry in self.office_ips:
            if isinstance(ip_entry, dict) and ip_entry.get('is_active', True):
                active_ips.append(ip_entry.get('ip'))
        
        return active_ips
    
    def add_office_ip(self, ip_address, description, added_by_user):
        """
        Add a new office IP address
        """
        from django.utils import timezone
        
        if not self.office_ips:
            self.office_ips = []
        
        # Check if IP already exists
        for ip_entry in self.office_ips:
            if ip_entry.get('ip') == ip_address:
                return False, "IP address already exists"
        
        # Add new IP
        new_ip = {
            'ip': ip_address,
            'description': description,
            'added_at': timezone.now().isoformat(),
            'added_by': added_by_user.username if added_by_user else 'System',
            'is_active': True
        }
        
        self.office_ips.append(new_ip)
        self.save()
        return True, "IP address added successfully"
    
    def remove_office_ip(self, ip_address):
        """
        Remove an office IP address
        """
        if not self.office_ips:
            return False, "No IPs configured"
        
        # Prevent removing last IP
        active_count = sum(1 for ip in self.office_ips if ip.get('is_active', True))
        if active_count <= 1:
            return False, "Cannot remove the last active IP address"
        
        # Remove IP
        self.office_ips = [ip for ip in self.office_ips if ip.get('ip') != ip_address]
        self.save()
        return True, "IP address removed successfully"
    
    def toggle_office_ip(self, ip_address, is_active):
        """
        Enable/disable an office IP address
        """
        if not self.office_ips:
            return False, "No IPs configured"
        
        # Prevent disabling last active IP
        if not is_active:
            active_count = sum(1 for ip in self.office_ips if ip.get('is_active', True))
            if active_count <= 1:
                return False, "Cannot disable the last active IP address"
        
        # Toggle IP
        for ip_entry in self.office_ips:
            if ip_entry.get('ip') == ip_address:
                ip_entry['is_active'] = is_active
                self.save()
                return True, f"IP address {'enabled' if is_active else 'disabled'} successfully"
        
        return False, "IP address not found"



# =========================
# COMPANY HOLIDAY CALENDAR
# =========================
class CompanyHoliday(models.Model):
    """
    Company Holiday Calendar
    Manages all holidays including weekly offs, 2nd/4th Saturdays, and company holidays
    """
    HOLIDAY_TYPES = [
        ('weekly_off', 'Weekly Off (Sunday)'),
        ('second_saturday', '2nd Saturday'),
        ('fourth_saturday', '4th Saturday'),
        ('national', 'National Holiday'),
        ('company', 'Company Holiday'),
        ('optional', 'Optional Holiday'),
    ]
    
    date = models.DateField(db_index=True, help_text='Holiday date')
    name = models.CharField(max_length=200, help_text='Holiday name (e.g., Republic Day)')
    holiday_type = models.CharField(
        max_length=20,
        choices=HOLIDAY_TYPES,
        default='company',
        help_text='Type of holiday'
    )
    description = models.TextField(blank=True, null=True, help_text='Additional details about the holiday')
    is_active = models.BooleanField(default=True, help_text='Whether this holiday is active')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Company Holiday'
        verbose_name_plural = 'Company Holidays'
        ordering = ['date']
    
    def __str__(self):
        return f"{self.name} - {self.date.strftime('%d %b %Y')}"
    
    @classmethod
    def is_holiday(cls, date):
        """
        Check if a given date is a holiday
        Returns: (Boolean, Holiday object or None)
        """
        holiday = cls.objects.filter(date=date, is_active=True).first()
        return (holiday is not None, holiday)
    
    @classmethod
    def get_holidays_for_month(cls, year, month):
        """
        Get all holidays for a specific month
        """
        from datetime import date
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        
        return cls.objects.filter(
            date__gte=start_date,
            date__lt=end_date,
            is_active=True
        ).order_by('date')
    
    @classmethod
    def get_holidays_for_year(cls, year):
        """
        Get all holidays for a specific year
        """
        from datetime import date
        start_date = date(year, 1, 1)
        end_date = date(year + 1, 1, 1)
        
        return cls.objects.filter(
            date__gte=start_date,
            date__lt=end_date,
            is_active=True
        ).order_by('date')
    
    @classmethod
    def auto_generate_weekly_offs(cls, year):
        """
        Auto-generate all Sundays for a given year
        """
        from datetime import date, timedelta
        
        # Start from first Sunday of the year
        current_date = date(year, 1, 1)
        # Find first Sunday
        while current_date.weekday() != 6:  # 6 = Sunday
            current_date += timedelta(days=1)
        
        created_count = 0
        while current_date.year == year:
            # Create or update Sunday holiday
            holiday, created = cls.objects.get_or_create(
                date=current_date,
                name='Sunday',
                defaults={
                    'holiday_type': 'weekly_off',
                    'description': 'Weekly off',
                    'is_active': True
                }
            )
            if created:
                created_count += 1
            
            current_date += timedelta(days=7)  # Next Sunday
        
        return created_count
    
    @classmethod
    def auto_generate_saturdays(cls, year):
        """
        Auto-generate 2nd and 4th Saturdays for a given year
        """
        from datetime import date
        import calendar
        
        created_count = 0
        
        for month in range(1, 13):
            # Get all Saturdays in the month
            saturdays = []
            for day in range(1, calendar.monthrange(year, month)[1] + 1):
                d = date(year, month, day)
                if d.weekday() == 5:  # 5 = Saturday
                    saturdays.append(d)
            
            # 2nd Saturday
            if len(saturdays) >= 2:
                second_sat = saturdays[1]
                holiday, created = cls.objects.get_or_create(
                    date=second_sat,
                    name='2nd Saturday',
                    defaults={
                        'holiday_type': 'second_saturday',
                        'description': 'Second Saturday of the month',
                        'is_active': True
                    }
                )
                if created:
                    created_count += 1
            
            # 4th Saturday
            if len(saturdays) >= 4:
                fourth_sat = saturdays[3]
                holiday, created = cls.objects.get_or_create(
                    date=fourth_sat,
                    name='4th Saturday',
                    defaults={
                        'holiday_type': 'fourth_saturday',
                        'description': 'Fourth Saturday of the month',
                        'is_active': True
                    }
                )
                if created:
                    created_count += 1
        
        return created_count
    
    @classmethod
    def is_working_day(cls, date):
        """
        Check if a date is a working day (not a holiday)
        Returns: Boolean
        """
        is_hol, _ = cls.is_holiday(date)
        return not is_hol
    
    @classmethod
    def count_working_days(cls, start_date, end_date):
        """
        Count working days between two dates (excluding holidays)
        """
        from datetime import timedelta
        
        working_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            if cls.is_working_day(current_date):
                working_days += 1
            current_date += timedelta(days=1)
        
        return working_days
