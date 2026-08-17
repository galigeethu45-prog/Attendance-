"""
Django Management Command: Bulk Check-in Assignment for Missing Attendance
Usage: python manage.py bulk_checkin <employee_id> --month <YYYY-MM>

Example: python manage.py bulk_checkin AI0001 --month 2026-08
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from attendance.models import Attendance, LeaveRequest, WFHRequest, AuditLog, CompanyHoliday
from datetime import datetime, time, timedelta
import calendar


class Command(BaseCommand):
    help = 'Assign 9 AM check-in to all missing attendance days for specified employee and month'

    def add_arguments(self, parser):
        parser.add_argument('employee_id', type=str, help='Employee ID to process')
        parser.add_argument('--month', type=str, required=True, help='Month in YYYY-MM format (e.g., 2026-08)')

    def parse_month(self, month_str):
        """Parse month string and return year, month, and date range"""
        try:
            year, month = map(int, month_str.split('-'))
            
            # Get first and last day of month
            first_day = datetime(year, month, 1).date()
            last_day_num = calendar.monthrange(year, month)[1]
            last_day = datetime(year, month, last_day_num).date()
            
            return year, month, first_day, last_day
        except:
            raise ValueError(f"Invalid month format: {month_str}. Use YYYY-MM format (e.g., 2026-08)")

    def is_weekend(self, date):
        """Check if date is Saturday or Sunday"""
        return date.weekday() in [5, 6]  # 5=Saturday, 6=Sunday

    def is_holiday(self, date):
        """Check if date is a company holiday"""
        return CompanyHoliday.objects.filter(date=date).exists()

    def check_leave(self, user, date):
        """Check if user has approved leave for the date"""
        return LeaveRequest.objects.filter(
            employee=user,
            status='approved',
            start_date__lte=date,
            end_date__gte=date
        ).exists()

    def has_attendance(self, user, date):
        """Check if attendance record already exists for the date"""
        return Attendance.objects.filter(employee=user, date=date).exists()

    def create_checkin(self, user, date, checkin_time, checkout_time, admin_user):
        """Create attendance record with both check-in and check-out time"""
        checkin_datetime = timezone.make_aware(
            datetime.combine(date, checkin_time)
        )
        
        checkout_datetime = timezone.make_aware(
            datetime.combine(date, checkout_time)
        )
        
        # Create attendance with both check-in and check-out
        attendance = Attendance.objects.create(
            employee=user,
            date=date,
            check_in=checkin_datetime,
            check_out=checkout_datetime,
            status='present'
        )
        
        # Calculate work hours and update status
        attendance.calculate_work_hours()
        attendance.save()
        
        # NO AUDIT LOG - as per requirement
        # AuditLog.objects.create(...)
        
        return attendance

    def handle(self, *args, **options):
        employee_id = options['employee_id']
        month_str = options['month']
        checkin_time = time(9, 0)  # 9:00 AM
        checkout_time = time(19, 0)  # 7:00 PM
        
        # Get admin user (though we won't use it for audit)
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.filter(employeeprofile__is_hr=True).first()
        
        # Parse month
        try:
            year, month, first_day, last_day = self.parse_month(month_str)
            month_name = calendar.month_name[month]
        except ValueError as e:
            self.stdout.write(self.style.ERROR(str(e)))
            return
        
        # Today's date - don't process today or future dates
        today = timezone.now().date()
        if last_day >= today:
            last_day = today - timedelta(days=1)  # Process up to yesterday
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('BULK CHECK-IN/CHECK-OUT ASSIGNMENT'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(f'Check-in Time: {checkin_time.strftime("%I:%M %p")}')
        self.stdout.write(f'Check-out Time: {checkout_time.strftime("%I:%M %p")}')
        self.stdout.write(f'Month: {month_name} {year} ({first_day} to {last_day})')
        self.stdout.write(self.style.WARNING('Note: No audit trail will be created'))
        self.stdout.write('')
        
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
                return
        
        self.stdout.write(self.style.WARNING(f'Processing Employee: {employee_id}'))
        self.stdout.write(f'Name: {user.get_full_name() or user.username}')
        self.stdout.write(f'Email: {user.email}')
        self.stdout.write('-' * 80)
        self.stdout.write('')
        
        # Find missing check-ins for each working day in the month
        current_date = first_day
        total_days = 0
        missing_days = []
        skipped_weekend = 0
        skipped_holiday = 0
        skipped_leave = 0
        already_exists = 0
        
        while current_date <= last_day:
            total_days += 1
            
            # Check if should skip
            if self.is_weekend(current_date):
                skipped_weekend += 1
                self.stdout.write(f'⏭️  {current_date} - Weekend (Skipped)')
            elif self.is_holiday(current_date):
                holiday = CompanyHoliday.objects.get(date=current_date)
                skipped_holiday += 1
                self.stdout.write(f'⏭️  {current_date} - Holiday: {holiday.name} (Skipped)')
            elif self.check_leave(user, current_date):
                leave = LeaveRequest.objects.filter(
                    employee=user,
                    status='approved',
                    start_date__lte=current_date,
                    end_date__gte=current_date
                ).first()
                skipped_leave += 1
                self.stdout.write(f'⏭️  {current_date} - On {leave.get_leave_type_display()} Leave (Skipped)')
            elif self.has_attendance(user, current_date):
                already_exists += 1
                self.stdout.write(f'✓ {current_date} - Attendance already exists')
            else:
                # Missing attendance - add to list
                missing_days.append(current_date)
                self.stdout.write(f'📋 {current_date} - Missing attendance (Will create)')
            
            current_date += timedelta(days=1)
        
        self.stdout.write('')
        self.stdout.write('-' * 80)
        self.stdout.write(f'Found {len(missing_days)} missing attendance day(s) to create')
        self.stdout.write('')
        
        if not missing_days:
            self.stdout.write(self.style.WARNING('No missing attendance days found!'))
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=' * 80))
            self.stdout.write(self.style.SUCCESS('SUMMARY'))
            self.stdout.write(self.style.SUCCESS('=' * 80))
            self.stdout.write(f'Total days checked: {total_days}')
            self.stdout.write(f'⏭️  Skipped (Weekends): {skipped_weekend}')
            self.stdout.write(f'⏭️  Skipped (Holidays): {skipped_holiday}')
            self.stdout.write(f'⏭️  Skipped (On Leave): {skipped_leave}')
            self.stdout.write(f'✓ Already exists: {already_exists}')
            self.stdout.write(f'✅ Created: 0')
            return
        
        # Ask for confirmation
        self.stdout.write(self.style.WARNING('⚠️  CONFIRMATION REQUIRED'))
        confirmation = input(f'Create check-in records for {len(missing_days)} day(s)? (yes/no): ')
        
        if confirmation.lower() not in ['yes', 'y']:
            self.stdout.write(self.style.ERROR('❌ Operation cancelled by user'))
            return
        
        self.stdout.write('')
        self.stdout.write('Creating attendance records with check-in and check-out...')
        self.stdout.write('')
        
        # Create check-ins and check-outs
        created_count = 0
        error_count = 0
        
        for date in missing_days:
            try:
                attendance = self.create_checkin(user, date, checkin_time, checkout_time, admin_user)
                created_count += 1
                work_hours = attendance.get_work_hours_display()
                self.stdout.write(self.style.SUCCESS(
                    f'✅ {date} - Check-in: {checkin_time.strftime("%I:%M %p")}, '
                    f'Check-out: {checkout_time.strftime("%I:%M %p")}, '
                    f'Hours: {work_hours}, Status: {attendance.status}'
                ))
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'❌ {date} - Error: {str(e)}'))
        
        # Final Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(f'Employee: {user.get_full_name() or user.username} ({employee_id})')
        self.stdout.write(f'Month: {month_name} {year}')
        self.stdout.write(f'Check-in Time: {checkin_time.strftime("%I:%M %p")}')
        self.stdout.write(f'Check-out Time: {checkout_time.strftime("%I:%M %p")}')
        self.stdout.write('')
        self.stdout.write(f'Total days checked: {total_days}')
        self.stdout.write(f'⏭️  Skipped (Weekends): {skipped_weekend}')
        self.stdout.write(f'⏭️  Skipped (Holidays): {skipped_holiday}')
        self.stdout.write(f'⏭️  Skipped (On Leave): {skipped_leave}')
        self.stdout.write(f'✓ Already exists: {already_exists}')
        self.stdout.write(f'✅ Successfully created (with check-in & check-out): {created_count}')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'❌ Errors: {error_count}'))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✓ Done!'))
