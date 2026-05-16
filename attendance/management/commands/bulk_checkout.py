"""
Django Management Command: Bulk Checkout Assignment
Usage: python manage.py bulk_checkout AI0001 AI0002 AI0003
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from attendance.models import Attendance, LeaveRequest, WFHRequest, AuditLog
from datetime import datetime, time


class Command(BaseCommand):
    help = 'Assign 7 PM checkout to all missing checkouts for specified employees'

    def add_arguments(self, parser):
        parser.add_argument('employee_ids', nargs='+', type=str, help='Employee IDs to process')

    def check_leave_or_wfh(self, user, date):
        """Check if user has approved leave or WFH for the date"""
        leave = LeaveRequest.objects.filter(
            employee=user,
            status='approved',
            start_date__lte=date,
            end_date__gte=date
        ).first()
        
        if leave:
            return True, f"On {leave.get_leave_type_display()} leave"
        
        wfh = WFHRequest.objects.filter(
            employee=user,
            status='approved',
            start_date__lte=date,
            end_date__gte=date
        ).first()
        
        if wfh:
            return True, "On approved WFH"
        
        return False, None

    def find_missing_checkouts(self, user):
        """Find all attendance records without checkout for the user"""
        today = timezone.now().date()
        
        missing = Attendance.objects.filter(
            employee=user,
            check_in__isnull=False,
            check_out__isnull=True,
            date__lte=today
        ).order_by('date')
        
        return missing

    def assign_checkout(self, attendance, checkout_time, admin_user):
        """Assign checkout time to attendance record"""
        checkout_datetime = timezone.make_aware(
            datetime.combine(attendance.date, checkout_time)
        )
        
        attendance.check_out = checkout_datetime
        
        if attendance.check_in:
            time_diff = checkout_datetime - attendance.check_in
            hours = time_diff.total_seconds() / 3600
            attendance.hours_worked = round(hours, 2)
        
        attendance.save()
        
        AuditLog.objects.create(
            user=admin_user,
            action='bulk_checkout_command',
            details=f'Bulk checkout: Assigned {checkout_time.strftime("%I:%M %p")} for {attendance.employee.username} on {attendance.date}',
            ip_address='127.0.0.1',
            target_user=attendance.employee
        )

    def handle(self, *args, **options):
        employee_ids = options['employee_ids']
        checkout_time = time(19, 0)  # 7:00 PM
        
        # Get admin user for audit
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.filter(employeeprofile__is_hr=True).first()
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('BULK CHECKOUT ASSIGNMENT'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'Checkout Time: {checkout_time.strftime("%I:%M %p")}')
        self.stdout.write(f'Processing {len(employee_ids)} employee(s)')
        self.stdout.write('')
        
        total_processed = 0
        total_skipped = 0
        
        for employee_id in employee_ids:
            self.stdout.write(self.style.WARNING(f'\nProcessing: {employee_id}'))
            self.stdout.write('-' * 70)
            
            # Find user
            user = None
            try:
                from attendance.models import EmployeeProfile
                profile = EmployeeProfile.objects.get(employee_id=employee_id)
                user = profile.user
            except:
                try:
                    user = User.objects.get(username=employee_id)
                except:
                    self.stdout.write(self.style.ERROR(f'❌ Employee not found: {employee_id}'))
                    continue
            
            self.stdout.write(f'✓ Found: {user.get_full_name() or user.username}')
            
            # Find missing checkouts
            missing_records = self.find_missing_checkouts(user)
            
            if not missing_records:
                self.stdout.write(self.style.SUCCESS('✅ No missing checkouts'))
                continue
            
            self.stdout.write(f'📋 Found {missing_records.count()} missing checkout(s):')
            
            # Process each record
            records_to_process = []
            for attendance in missing_records:
                on_leave, reason = self.check_leave_or_wfh(user, attendance.date)
                
                if on_leave:
                    self.stdout.write(f'  ⏭️  {attendance.date} - Skipped ({reason})')
                    total_skipped += 1
                else:
                    self.stdout.write(f'  ✓ {attendance.date} - Check-in: {attendance.check_in.strftime("%I:%M %p")}')
                    records_to_process.append(attendance)
            
            # Assign checkouts
            if records_to_process:
                for attendance in records_to_process:
                    try:
                        self.assign_checkout(attendance, checkout_time, admin_user)
                        self.stdout.write(self.style.SUCCESS(f'  ✅ {attendance.date} - Checkout assigned'))
                        total_processed += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ❌ {attendance.date} - Error: {str(e)}'))
                        total_skipped += 1
        
        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'✅ Total checkouts assigned: {total_processed}')
        self.stdout.write(f'⏭️  Total skipped: {total_skipped}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Done!'))
