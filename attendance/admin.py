from django.contrib import admin
from datetime import timedelta
from django.utils import timezone

from .models import (
    EmployeeProfile,
    Attendance,
    BreakLog,
    LeaveRequest,
    Notification,
    Overtime,
    AuditLog
)

# =========================
# CUSTOM BREAK DATE FILTER
# =========================
class BreakDateFilter(admin.SimpleListFilter):
    title = 'Break Date'
    parameter_name = 'break_date'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('last_7_days', 'Last 7 Days'),
            ('last_30_days', 'Last 30 Days'),
        )

    def queryset(self, request, queryset):
        today = timezone.now().date()

        if self.value() == 'today':
            return queryset.filter(break_start__date=today)

        if self.value() == 'yesterday':
            return queryset.filter(break_start__date=today - timedelta(days=1))

        if self.value() == 'last_7_days':
            return queryset.filter(break_start__date__gte=today - timedelta(days=7))

        if self.value() == 'last_30_days':
            return queryset.filter(break_start__date__gte=today - timedelta(days=30))

        return queryset


# =========================
# EMPLOYEE PROFILE
# =========================
@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id','user', 'department', 'designation', 'is_hr')
    list_filter = ('department', 'is_hr')
    search_fields = ('employee_id','user__username', 'department', 'designation')


# =========================
# ATTENDANCE
# =========================
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'date',
        'check_in',
        'check_out',
        'work_hours_display',
        'status'
    )
    list_filter = ('status', 'date')
    search_fields = ('employee__username',)
    date_hierarchy = 'date'

    def work_hours_display(self, obj):
        return obj.get_work_hours_display()

    work_hours_display.short_description = "Total Work Hours"


# =========================
# BREAK LOG
# =========================
@admin.register(BreakLog)
class BreakLogAdmin(admin.ModelAdmin):
    list_display = (
        'attendance',
        'break_type',
        'break_start',
        'break_end',
        'duration_minutes'
    )

    list_filter = (
        'break_type',
        BreakDateFilter,   # ✅ custom date filter
    )

    search_fields = ('attendance__employee__username',)

    date_hierarchy = 'break_start'


# =========================
# LEAVE REQUEST
# =========================
@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type')
    list_filter = ('leave_type',)
    search_fields = ('employee__username',)


# =========================
# NOTIFICATION
# =========================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('employee__username', 'message')


# =========================
# OVERTIME
# =========================
@admin.register(Overtime)
class OvertimeAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'start_time', 'end_time', 'total_hours', 'approved_by_hr', 'hr_approver')
    list_filter = ('approved_by_hr', 'date')
    search_fields = ('employee__username', 'hr_approver__username')
    date_hierarchy = 'date'



# =========================
# AUDIT LOG
# =========================
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'description', 'ip_address', 'target_user')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'description', 'ip_address', 'target_user__username')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp', 'user', 'action', 'description', 'ip_address', 'target_user')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
