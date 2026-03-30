from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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

# =========================
# EMPLOYEE PROFILE
# =========================
class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Employee ID
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True)

    # Personal Information
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
    
    # Profile completion
    profile_completed = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['employee_id', 'is_hr']),
            models.Index(fields=['department']),
        ]

    def __str__(self):
        return self.employee_id or self.user.username


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
        """
        if self.check_in and self.check_out:
            duration = self.check_out - self.check_in
            total_hours = duration.total_seconds() / 3600
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

    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE,
        related_name='breaks'
    )
    break_type = models.CharField(
        max_length=10,
        choices=BREAK_TYPES
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
        ('vacation', 'Vacation'),
        ('emergency', 'Emergency'),
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
    reason = models.TextField(default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    hr_comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_days(self):
        return (self.end_date - self.start_date).days + 1

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

