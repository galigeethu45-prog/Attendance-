"""
Payroll System API Views
HR-only access to payroll management
"""

import csv
from datetime import datetime
from decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import (
    EmployeeProfile,
    PayrollCycle,
    PayrollEntry,
    LeaveBalance,
)
from .payroll_serializers import (
    PayrollCycleSerializer,
    PayrollCycleListSerializer,
    PayrollEntrySerializer,
    PayrollEntryListSerializer,
    PayrollEntryUpdateSerializer,
    LeaveBalanceSerializer,
    PayrollGenerateRequestSerializer,
    PayrollFinalizeRequestSerializer,
    PayrollMarkPaidRequestSerializer,
    PayrollCSVExportRequestSerializer,
)
from .payroll_calculator import PayrollCalculator


# ============================================
# CUSTOM PERMISSION: HR ONLY
# ============================================
class IsHRUser(IsAuthenticated):
    """
    Custom permission to only allow HR users or superusers
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        # Superusers always have access
        if request.user.is_superuser:
            return True
        
        # Check if user has HR profile
        try:
            profile = request.user.employeeprofile
            return profile.is_hr
        except EmployeeProfile.DoesNotExist:
            return False


# ============================================
# PAYROLL CYCLE VIEWSET
# ============================================
class PayrollCycleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payroll cycles
    HR-only access
    """
    permission_classes = [IsHRUser]
    serializer_class = PayrollCycleSerializer
    queryset = PayrollCycle.objects.all().order_by('-year', '-month')
    
    def get_serializer_class(self):
        """Use lightweight serializer for list action"""
        if self.action == 'list':
            return PayrollCycleListSerializer
        return PayrollCycleSerializer
    
    def list(self, request, *args, **kwargs):
        """List all payroll cycles with filters"""
        queryset = self.get_queryset()
        
        # Filter by year
        year = request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=year)
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """Get single payroll cycle with all entries"""
        cycle = get_object_or_404(PayrollCycle, pk=pk)
        serializer = PayrollCycleSerializer(cycle)
        
        # Include entries summary
        entries = cycle.entries.all().select_related('employee', 'employee__user')
        entries_serializer = PayrollEntryListSerializer(entries, many=True)
        
        data = serializer.data
        data['entries'] = entries_serializer.data
        
        return Response(data)
    
    @action(detail=False, methods=['post'], url_path='generate')
    def generate_payroll(self, request):
        """
        Generate payroll for a specific month/year
        POST /api/payroll/cycles/generate/
        Body: {"month": 8, "year": 2026, "regenerate": false}
        """
        serializer = PayrollGenerateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        month = serializer.validated_data['month']
        year = serializer.validated_data['year']
        regenerate = serializer.validated_data.get('regenerate', False)
        
        # Check if cycle already exists
        existing_cycle = PayrollCycle.objects.filter(month=month, year=year).first()
        
        if existing_cycle and not regenerate:
            return Response({
                'error': 'Payroll cycle already exists for this month/year',
                'cycle_id': existing_cycle.id,
                'status': existing_cycle.status,
                'message': 'Use regenerate=true to recalculate'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if existing_cycle and existing_cycle.status in ['finalized', 'paid']:
            return Response({
                'error': f'Cannot regenerate payroll in status: {existing_cycle.status}',
                'message': 'Finalized or paid cycles cannot be regenerated'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate payroll
        try:
            calculator = PayrollCalculator(month, year)
            cycle = calculator.create_or_update_cycle(processed_by_user=request.user)
            
            # Update leave balances
            PayrollCalculator.update_leave_balances(year)
            
            serializer = PayrollCycleSerializer(cycle)
            
            return Response({
                'message': 'Payroll generated successfully',
                'cycle': serializer.data,
                'regenerated': existing_cycle is not None
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': str(e),
                'message': 'Failed to generate payroll'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], url_path='finalize')
    def finalize_cycle(self, request, pk=None):
        """
        Finalize a payroll cycle (lock from edits)
        POST /api/payroll/cycles/{id}/finalize/
        """
        cycle = get_object_or_404(PayrollCycle, pk=pk)
        
        if cycle.status != 'draft':
            return Response({
                'error': f'Cannot finalize cycle in status: {cycle.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            serializer = PayrollFinalizeRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            notes = serializer.validated_data.get('notes', '')
            if notes:
                cycle.notes = notes
            
            PayrollCalculator.finalize_cycle(cycle, request.user)
            
            response_serializer = PayrollCycleSerializer(cycle)
            return Response({
                'message': 'Payroll cycle finalized successfully',
                'cycle': response_serializer.data
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_as_paid(self, request, pk=None):
        """
        Mark a payroll cycle as paid
        POST /api/payroll/cycles/{id}/mark-paid/
        """
        cycle = get_object_or_404(PayrollCycle, pk=pk)
        
        if cycle.status != 'finalized':
            return Response({
                'error': f'Cannot mark as paid. Cycle must be finalized first. Current status: {cycle.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            serializer = PayrollMarkPaidRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            payment_date = serializer.validated_data.get('payment_date')
            notes = serializer.validated_data.get('notes', '')
            
            if notes:
                cycle.notes = cycle.notes + '\n' + notes if cycle.notes else notes
            
            PayrollCalculator.mark_as_paid(cycle, request.user)
            
            # Update payment date on all entries
            if payment_date:
                cycle.entries.all().update(payment_date=payment_date)
            
            response_serializer = PayrollCycleSerializer(cycle)
            return Response({
                'message': 'Payroll cycle marked as paid successfully',
                'cycle': response_serializer.data
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='export-csv')
    def export_csv(self, request, pk=None):
        """
        Export payroll cycle to CSV
        GET /api/payroll/cycles/{id}/export-csv/
        """
        cycle = get_object_or_404(PayrollCycle, pk=pk)
        entries = cycle.entries.all().select_related('employee', 'employee__user')
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="payroll_{cycle.year}_{cycle.month:02d}.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'Employee ID',
            'Employee Name',
            'Department',
            'Designation',
            'Base Salary',
            'Working Days',
            'Present Days',
            'Absent Days',
            'Half Days',
            'WFH Days',
            'Paid Leaves',
            'Unpaid Leaves',
            'OT Hours',
            'OT Amount',
            'Total Deductions',
            'Gross Salary',
            'Manual Adjustment',
            'Net Salary',
            'Bank Account',
            'IFSC Code',
            'Bank Name',
            'PAN Number',
            'Payment Status',
        ])
        
        # Write data rows
        for entry in entries:
            emp = entry.employee
            writer.writerow([
                emp.employee_id,
                f"{emp.user.first_name} {emp.user.last_name}".strip() or emp.user.username,
                emp.department,
                emp.designation,
                float(entry.base_salary),
                entry.working_days,
                entry.present_days,
                entry.absent_days,
                entry.half_days,
                entry.wfh_days,
                entry.paid_leaves,
                entry.unpaid_leaves,
                float(entry.overtime_hours),
                float(entry.overtime_amount),
                float(entry.total_deductions),
                float(entry.gross_salary),
                float(entry.manual_adjustment),
                float(entry.net_salary),
                emp.bank_account_number,
                emp.bank_ifsc_code,
                emp.bank_name,
                emp.pan_number,
                entry.get_payment_status_display(),
            ])
        
        return response


# ============================================
# PAYROLL ENTRY VIEWSET
# ============================================
class PayrollEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing individual payroll entries
    HR-only access
    """
    permission_classes = [IsHRUser]
    serializer_class = PayrollEntrySerializer
    queryset = PayrollEntry.objects.all().select_related('employee', 'employee__user', 'payroll_cycle')
    
    def get_serializer_class(self):
        """Use appropriate serializer based on action"""
        if self.action == 'list':
            return PayrollEntryListSerializer
        elif self.action in ['update', 'partial_update']:
            return PayrollEntryUpdateSerializer
        return PayrollEntrySerializer
    
    def list(self, request, *args, **kwargs):
        """List payroll entries with filters"""
        queryset = self.get_queryset()
        
        # Filter by cycle
        cycle_id = request.query_params.get('cycle_id')
        if cycle_id:
            queryset = queryset.filter(payroll_cycle_id=cycle_id)
        
        # Filter by employee
        employee_id = request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee__employee_id=employee_id)
        
        # Filter by payment status
        payment_status_filter = request.query_params.get('payment_status')
        if payment_status_filter:
            queryset = queryset.filter(payment_status=payment_status_filter)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update payroll entry (manual adjustments)"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check if cycle is finalized or paid
        if instance.payroll_cycle.status in ['finalized', 'paid']:
            return Response({
                'error': f'Cannot update entry. Cycle is {instance.payroll_cycle.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return full details
        response_serializer = PayrollEntrySerializer(instance)
        return Response(response_serializer.data)
    
    @action(detail=True, methods=['post'], url_path='recalculate')
    def recalculate(self, request, pk=None):
        """
        Recalculate a single payroll entry
        POST /api/payroll/entries/{id}/recalculate/
        """
        entry = get_object_or_404(PayrollEntry, pk=pk)
        
        # Check if cycle is finalized or paid
        if entry.payroll_cycle.status in ['finalized', 'paid']:
            return Response({
                'error': f'Cannot recalculate. Cycle is {entry.payroll_cycle.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Recalculate using calculator
            calculator = PayrollCalculator(entry.payroll_cycle.month, entry.payroll_cycle.year)
            new_entry = calculator.calculate_employee(entry.employee)
            
            # Update existing entry with new calculations
            entry.working_days = new_entry.working_days
            entry.present_days = new_entry.present_days
            entry.absent_days = new_entry.absent_days
            entry.half_days = new_entry.half_days
            entry.late_days = new_entry.late_days
            entry.wfh_days = new_entry.wfh_days
            entry.paid_leaves = new_entry.paid_leaves
            entry.unpaid_leaves = new_entry.unpaid_leaves
            entry.overtime_hours = new_entry.overtime_hours
            
            # Preserve manual adjustments
            # entry.manual_adjustment (keep existing)
            # entry.adjustment_reason (keep existing)
            
            # Recalculate totals
            entry.calculate_totals()
            entry.save()
            
            serializer = PayrollEntrySerializer(entry)
            return Response({
                'message': 'Payroll entry recalculated successfully',
                'entry': serializer.data
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================
# LEAVE BALANCE VIEWSET
# ============================================
class LeaveBalanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leave balances
    HR-only access
    """
    permission_classes = [IsHRUser]
    serializer_class = LeaveBalanceSerializer
    queryset = LeaveBalance.objects.all().select_related('employee', 'employee__user')
    
    def list(self, request, *args, **kwargs):
        """List leave balances with filters"""
        queryset = self.get_queryset()
        
        # Filter by year
        year = request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=year)
        
        # Filter by employee
        employee_id = request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee__employee_id=employee_id)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def perform_update(self, serializer):
        """Auto-update balances on save"""
        instance = serializer.save()
        instance.update_balances()
        instance.save()


# ============================================
# DASHBOARD STATS API
# ============================================
@api_view(['GET'])
@permission_classes([IsHRUser])
def payroll_dashboard_stats(request):
    """
    Get payroll dashboard statistics
    GET /api/payroll/dashboard-stats/
    """
    # Get current month/year
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    # Get current cycle
    current_cycle = PayrollCycle.objects.filter(month=current_month, year=current_year).first()
    
    # Get all cycles count
    total_cycles = PayrollCycle.objects.count()
    draft_cycles = PayrollCycle.objects.filter(status='draft').count()
    finalized_cycles = PayrollCycle.objects.filter(status='finalized').count()
    paid_cycles = PayrollCycle.objects.filter(status='paid').count()
    
    # Get total employees with salary
    total_employees = EmployeeProfile.objects.filter(base_salary__gt=0).count()
    
    # Recent cycles
    recent_cycles = PayrollCycle.objects.all().order_by('-year', '-month')[:5]
    recent_cycles_data = PayrollCycleListSerializer(recent_cycles, many=True).data
    
    return Response({
        'current_month': current_month,
        'current_year': current_year,
        'current_cycle': PayrollCycleSerializer(current_cycle).data if current_cycle else None,
        'total_cycles': total_cycles,
        'draft_cycles': draft_cycles,
        'finalized_cycles': finalized_cycles,
        'paid_cycles': paid_cycles,
        'total_employees': total_employees,
        'recent_cycles': recent_cycles_data,
    })



# ============================================
# TEMPLATE VIEWS (FOR FRONTEND UI)
# ============================================

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def payroll_dashboard_view(request):
    """
    Payroll dashboard page (HR only)
    """
    # Check if user is HR or superuser
    if not request.user.is_superuser:
        try:
            profile = request.user.employeeprofile
            if not profile.is_hr:
                from django.contrib import messages
                messages.error(request, 'Access denied. HR privileges required.')
                return redirect('dashboard')
        except EmployeeProfile.DoesNotExist:
            from django.contrib import messages
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    
    return render(request, 'payroll_dashboard.html')


@login_required
def payroll_cycle_detail_view(request, cycle_id):
    """
    Payroll cycle detail page (HR only)
    """
    # Check if user is HR or superuser
    if not request.user.is_superuser:
        try:
            profile = request.user.employeeprofile
            if not profile.is_hr:
                from django.contrib import messages
                messages.error(request, 'Access denied. HR privileges required.')
                return redirect('dashboard')
        except EmployeeProfile.DoesNotExist:
            from django.contrib import messages
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    
    # Get cycle to set title context
    cycle = get_object_or_404(PayrollCycle, pk=cycle_id)
    
    context = {
        'cycle_id': cycle_id,
        'cycle_month_name': cycle.get_month_name(),
        'cycle_year': cycle.year,
    }
    
    return render(request, 'payroll_cycle_detail.html', context)
