"""
Payroll System Serializers
REST API serializers for payroll models
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    EmployeeProfile,
    PayrollCycle,
    PayrollEntry,
    LeaveBalance,
)


class EmployeeBasicSerializer(serializers.ModelSerializer):
    """Basic employee info for nested serialization"""
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = EmployeeProfile
        fields = ['id', 'employee_id', 'username', 'first_name', 'last_name', 'full_name', 'department', 'designation']
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username


class PayrollCycleSerializer(serializers.ModelSerializer):
    """PayrollCycle serializer with computed fields"""
    month_name = serializers.CharField(source='get_month_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    processed_by_name = serializers.SerializerMethodField()
    entry_count = serializers.IntegerField(source='entries.count', read_only=True)
    
    class Meta:
        model = PayrollCycle
        fields = [
            'id',
            'month',
            'year',
            'month_name',
            'status',
            'status_display',
            'total_employees',
            'total_gross_salary',
            'total_deductions',
            'total_overtime',
            'total_net_salary',
            'processed_by',
            'processed_by_name',
            'processed_at',
            'finalized_at',
            'paid_at',
            'notes',
            'entry_count',
        ]
        read_only_fields = [
            'id',
            'total_employees',
            'total_gross_salary',
            'total_deductions',
            'total_overtime',
            'total_net_salary',
            'processed_at',
            'finalized_at',
            'paid_at',
            'entry_count',
        ]
    
    def get_processed_by_name(self, obj):
        if obj.processed_by:
            return f"{obj.processed_by.first_name} {obj.processed_by.last_name}".strip() or obj.processed_by.username
        return None


class PayrollCycleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing payroll cycles"""
    month_name = serializers.CharField(source='get_month_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PayrollCycle
        fields = [
            'id',
            'month',
            'year',
            'month_name',
            'status',
            'status_display',
            'total_employees',
            'total_net_salary',
            'processed_at',
        ]


class PayrollEntrySerializer(serializers.ModelSerializer):
    """PayrollEntry serializer with employee details"""
    employee_details = EmployeeBasicSerializer(source='employee', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    cycle_month = serializers.IntegerField(source='payroll_cycle.month', read_only=True)
    cycle_year = serializers.IntegerField(source='payroll_cycle.year', read_only=True)
    cycle_status = serializers.CharField(source='payroll_cycle.status', read_only=True)
    
    class Meta:
        model = PayrollEntry
        fields = [
            'id',
            'payroll_cycle',
            'cycle_month',
            'cycle_year',
            'cycle_status',
            'employee',
            'employee_details',
            'base_salary',
            'working_days',
            'per_day_salary',
            'present_days',
            'absent_days',
            'half_days',
            'late_days',
            'wfh_days',
            'paid_leaves',
            'unpaid_leaves',
            'overtime_hours',
            'overtime_rate',
            'overtime_amount',
            'half_day_deduction',
            'absent_deduction',
            'unpaid_leave_deduction',
            'other_deductions',
            'total_deductions',
            'gross_salary',
            'net_salary',
            'manual_adjustment',
            'adjustment_reason',
            'payment_status',
            'payment_status_display',
            'payment_date',
            'payment_reference',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'per_day_salary',
            'overtime_amount',
            'half_day_deduction',
            'absent_deduction',
            'unpaid_leave_deduction',
            'total_deductions',
            'gross_salary',
            'net_salary',
            'created_at',
            'updated_at',
        ]


class PayrollEntryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing payroll entries"""
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    employee_name = serializers.SerializerMethodField()
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    class Meta:
        model = PayrollEntry
        fields = [
            'id',
            'employee_id',
            'employee_name',
            'base_salary',
            'present_days',
            'absent_days',
            'half_days',
            'total_deductions',
            'net_salary',
            'payment_status',
            'payment_status_display',
        ]
    
    def get_employee_name(self, obj):
        return f"{obj.employee.user.first_name} {obj.employee.user.last_name}".strip() or obj.employee.user.username


class PayrollEntryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating payroll entry (manual adjustments)"""
    
    class Meta:
        model = PayrollEntry
        fields = [
            'manual_adjustment',
            'adjustment_reason',
            'other_deductions',
            'notes',
            'payment_status',
            'payment_date',
            'payment_reference',
        ]
    
    def validate(self, data):
        """Validate that adjustment has a reason"""
        manual_adjustment = data.get('manual_adjustment', self.instance.manual_adjustment if self.instance else 0)
        adjustment_reason = data.get('adjustment_reason', self.instance.adjustment_reason if self.instance else '')
        
        # If manual adjustment is non-zero, require a reason
        if manual_adjustment != 0 and not adjustment_reason:
            raise serializers.ValidationError({
                'adjustment_reason': 'Reason is required when manual adjustment is applied.'
            })
        
        return data
    
    def update(self, instance, validated_data):
        """Update and recalculate totals"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Recalculate totals
        instance.calculate_totals()
        instance.save()
        
        return instance


class LeaveBalanceSerializer(serializers.ModelSerializer):
    """LeaveBalance serializer"""
    employee_details = EmployeeBasicSerializer(source='employee', read_only=True)
    available_paid_leaves = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveBalance
        fields = [
            'id',
            'employee',
            'employee_details',
            'year',
            'sick_leave_allocated',
            'sick_leave_used',
            'sick_leave_balance',
            'casual_leave_allocated',
            'casual_leave_used',
            'casual_leave_balance',
            'earned_leave_allocated',
            'earned_leave_used',
            'earned_leave_balance',
            'total_allocated',
            'total_used',
            'total_balance',
            'available_paid_leaves',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'sick_leave_balance',
            'casual_leave_balance',
            'earned_leave_balance',
            'total_balance',
            'created_at',
            'updated_at',
        ]
    
    def get_available_paid_leaves(self, obj):
        """Get paid leaves still available (max 18)"""
        return obj.get_available_paid_leaves()


class PayrollGenerateRequestSerializer(serializers.Serializer):
    """Serializer for payroll generation request"""
    month = serializers.IntegerField(min_value=1, max_value=12)
    year = serializers.IntegerField(min_value=2020, max_value=2050)
    regenerate = serializers.BooleanField(default=False, help_text='Regenerate if already exists')


class PayrollFinalizeRequestSerializer(serializers.Serializer):
    """Serializer for payroll finalization request"""
    notes = serializers.CharField(required=False, allow_blank=True)


class PayrollMarkPaidRequestSerializer(serializers.Serializer):
    """Serializer for marking payroll as paid"""
    payment_date = serializers.DateField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)


class PayrollCSVExportRequestSerializer(serializers.Serializer):
    """Serializer for CSV export request"""
    cycle_id = serializers.IntegerField()
    include_fields = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='List of fields to include in CSV'
    )
