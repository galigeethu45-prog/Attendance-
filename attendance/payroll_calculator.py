"""
Payroll Calculation Engine
Handles automated salary calculations based on attendance, leaves, and overtime
"""

from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Q, Count, Sum
from .models import (
    EmployeeProfile,
    Attendance,
    LeaveRequest,
    Overtime,
    WFHRequest,
    OnsiteRequest,
    CompanyHoliday,
    PayrollCycle,
    PayrollEntry,
    LeaveBalance,
)


class PayrollCalculator:
    """
    Core payroll calculation engine
    """
    
    def __init__(self, month, year):
        """
        Initialize calculator for a specific month/year
        
        Args:
            month: int (1-12)
            year: int (e.g., 2026)
        """
        self.month = month
        self.year = year
        self.start_date = datetime(year, month, 1).date()
        
        # Calculate last day of month
        if month == 12:
            self.end_date = datetime(year, 12, 31).date()
        else:
            next_month = datetime(year, month + 1, 1).date()
            self.end_date = next_month - timedelta(days=1)
        
        # Calculate working days (excluding weekends and holidays)
        self.working_days = CompanyHoliday.count_working_days(self.start_date, self.end_date)
    
    def calculate_all_employees(self, employee_profiles=None):
        """
        Calculate payroll for all employees (or specific list)
        
        Args:
            employee_profiles: QuerySet or list of EmployeeProfile objects (optional)
            
        Returns:
            list of PayrollEntry objects (not saved to DB)
        """
        if employee_profiles is None:
            # Get all active employees with base_salary > 0
            employee_profiles = EmployeeProfile.objects.filter(
                base_salary__gt=0
            ).select_related('user')
        
        payroll_entries = []
        
        for emp_profile in employee_profiles:
            entry = self.calculate_employee(emp_profile)
            if entry:
                payroll_entries.append(entry)
        
        return payroll_entries
    
    def calculate_employee(self, emp_profile):
        """
        Calculate payroll for a single employee
        
        Args:
            emp_profile: EmployeeProfile object
            
        Returns:
            PayrollEntry object (not saved to DB)
        """
        # Create base payroll entry
        entry = PayrollEntry(
            employee=emp_profile,
            base_salary=emp_profile.base_salary,
            working_days=self.working_days,
            overtime_rate=emp_profile.ot_rate,
        )
        
        # Calculate attendance breakdown
        attendance_data = self._get_attendance_breakdown(emp_profile)
        entry.present_days = attendance_data['present']
        entry.absent_days = attendance_data['absent']
        entry.half_days = attendance_data['half_day']
        entry.late_days = attendance_data['late']
        entry.wfh_days = attendance_data['wfh']
        
        # Calculate leave breakdown
        leave_data = self._get_leave_breakdown(emp_profile)
        entry.paid_leaves = leave_data['paid']
        entry.unpaid_leaves = leave_data['unpaid']
        
        # Calculate approved overtime
        overtime_data = self._get_overtime_hours(emp_profile)
        entry.overtime_hours = overtime_data['hours']
        
        # Calculate all deductions and final salary
        entry.calculate_totals()
        
        return entry
    
    def _get_attendance_breakdown(self, emp_profile):
        """
        Get attendance breakdown for the employee in the current month
        
        Returns:
            dict with keys: present, absent, half_day, late, wfh
        """
        # Get all attendance records for the month
        attendances = Attendance.objects.filter(
            employee=emp_profile.user,
            date__gte=self.start_date,
            date__lte=self.end_date
        )
        
        # Count by status
        present_count = attendances.filter(status='present').count()
        absent_count = attendances.filter(status='absent').count()
        half_day_count = attendances.filter(status='half_day').count()
        late_count = attendances.filter(status='late').count()
        
        # Count WFH days (approved WFH requests)
        wfh_days = WFHRequest.objects.filter(
            employee=emp_profile.user,
            status='approved',
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        ).aggregate(
            total_days=Sum('total_days')
        )['total_days'] or 0
        
        # Note: WFH days are counted as PRESENT days (no deduction)
        # They are tracked separately for reporting purposes only
        
        return {
            'present': present_count,
            'absent': absent_count,
            'half_day': half_day_count,
            'late': late_count,
            'wfh': wfh_days,
        }
    
    def _get_leave_breakdown(self, emp_profile):
        """
        Get leave breakdown (paid vs unpaid)
        
        Returns:
            dict with keys: paid, unpaid
        """
        # Get or create leave balance for this year
        leave_balance, created = LeaveBalance.objects.get_or_create(
            employee=emp_profile,
            year=self.year,
            defaults={
                'sick_leave_allocated': 6,
                'casual_leave_allocated': 6,
                'earned_leave_allocated': 6,
                'total_allocated': 18,
            }
        )
        
        # Get approved leaves for this month
        approved_leaves = LeaveRequest.objects.filter(
            employee=emp_profile.user,
            status='approved',
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        )
        
        # Calculate total leave days in this month
        total_leave_days = 0
        for leave in approved_leaves:
            # Calculate overlap with current month
            leave_start = max(leave.start_date, self.start_date)
            leave_end = min(leave.end_date, self.end_date)
            days = (leave_end - leave_start).days + 1
            total_leave_days += days
        
        # Calculate paid vs unpaid
        # Policy: First 18 leaves are PAID, beyond that are UNPAID
        total_used = leave_balance.total_used
        available_paid = max(0, 18 - total_used)
        
        paid_leaves = min(total_leave_days, available_paid)
        unpaid_leaves = max(0, total_leave_days - paid_leaves)
        
        return {
            'paid': paid_leaves,
            'unpaid': unpaid_leaves,
        }
    
    def _get_overtime_hours(self, emp_profile):
        """
        Get approved overtime hours for the month
        
        Returns:
            dict with key: hours
        """
        # Get approved overtime records
        overtime_records = Overtime.objects.filter(
            employee=emp_profile.user,
            date__gte=self.start_date,
            date__lte=self.end_date,
            approved_by_hr=True
        )
        
        total_hours = overtime_records.aggregate(
            total=Sum('total_hours')
        )['total'] or Decimal('0.00')
        
        return {
            'hours': total_hours,
        }
    
    def create_or_update_cycle(self, processed_by_user):
        """
        Create or update PayrollCycle and generate all PayrollEntry records
        
        Args:
            processed_by_user: User object who is processing the payroll
            
        Returns:
            PayrollCycle object with all entries created
        """
        # Get or create payroll cycle
        cycle, created = PayrollCycle.objects.get_or_create(
            month=self.month,
            year=self.year,
            defaults={
                'processed_by': processed_by_user,
                'status': 'draft',
            }
        )
        
        # If cycle is already finalized or paid, don't recalculate
        if cycle.status in ['finalized', 'paid']:
            return cycle
        
        # Delete existing entries for this cycle (if re-calculating)
        cycle.entries.all().delete()
        
        # Calculate all employees
        payroll_entries = self.calculate_all_employees()
        
        # Save all entries
        for entry in payroll_entries:
            entry.payroll_cycle = cycle
            entry.save()
        
        # Update cycle totals
        self._update_cycle_totals(cycle)
        
        return cycle
    
    def _update_cycle_totals(self, cycle):
        """
        Update aggregated totals in PayrollCycle
        """
        entries = cycle.entries.all()
        
        cycle.total_employees = entries.count()
        cycle.total_gross_salary = entries.aggregate(Sum('gross_salary'))['gross_salary__sum'] or Decimal('0.00')
        cycle.total_deductions = entries.aggregate(Sum('total_deductions'))['total_deductions__sum'] or Decimal('0.00')
        cycle.total_overtime = entries.aggregate(Sum('overtime_amount'))['overtime_amount__sum'] or Decimal('0.00')
        cycle.total_net_salary = entries.aggregate(Sum('net_salary'))['net_salary__sum'] or Decimal('0.00')
        
        cycle.save()
    
    @staticmethod
    def finalize_cycle(cycle, user):
        """
        Finalize a payroll cycle (lock it from further edits)
        
        Args:
            cycle: PayrollCycle object
            user: User who is finalizing
        """
        if cycle.status != 'draft':
            raise ValueError(f"Cannot finalize cycle in status: {cycle.status}")
        
        cycle.status = 'finalized'
        cycle.finalized_at = datetime.now()
        cycle.save()
        
        return cycle
    
    @staticmethod
    def mark_as_paid(cycle, user):
        """
        Mark a payroll cycle as paid
        
        Args:
            cycle: PayrollCycle object
            user: User who is marking as paid
        """
        if cycle.status != 'finalized':
            raise ValueError(f"Cannot mark as paid. Cycle must be finalized first. Current status: {cycle.status}")
        
        cycle.status = 'paid'
        cycle.paid_at = datetime.now()
        cycle.save()
        
        # Update all entries to 'paid' status
        cycle.entries.all().update(payment_status='paid')
        
        return cycle
    
    @staticmethod
    def update_leave_balances(year):
        """
        Update leave balances based on approved leave requests
        Should be run after payroll calculation
        
        Args:
            year: int (e.g., 2026)
        """
        # Get all employees with leave requests
        employees = EmployeeProfile.objects.filter(
            user__leave_requests__status='approved',
            user__leave_requests__start_date__year=year
        ).distinct()
        
        for emp_profile in employees:
            # Get or create leave balance
            leave_balance, created = LeaveBalance.objects.get_or_create(
                employee=emp_profile,
                year=year,
                defaults={
                    'sick_leave_allocated': 6,
                    'casual_leave_allocated': 6,
                    'earned_leave_allocated': 6,
                    'total_allocated': 18,
                }
            )
            
            # Count approved leaves by type
            approved_leaves = LeaveRequest.objects.filter(
                employee=emp_profile.user,
                status='approved',
                start_date__year=year
            )
            
            sick_used = 0
            casual_used = 0
            earned_used = 0
            
            for leave in approved_leaves:
                days = (leave.end_date - leave.start_date).days + 1
                
                if leave.leave_type == 'sick':
                    sick_used += days
                elif leave.leave_type == 'casual':
                    casual_used += days
                elif leave.leave_type == 'earned':
                    earned_used += days
            
            # Update usage
            leave_balance.sick_leave_used = sick_used
            leave_balance.casual_leave_used = casual_used
            leave_balance.earned_leave_used = earned_used
            leave_balance.total_used = sick_used + casual_used + earned_used
            
            # Update balances
            leave_balance.update_balances()
            leave_balance.save()
