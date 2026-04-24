from django.core.management.base import BaseCommand
from django.utils import timezone
from attendance.models import Attendance, AuditLog
import pytz
from datetime import datetime, time


class Command(BaseCommand):
    help = 'Auto checkout employees at 7 PM if they forgot to check out'

    def handle(self, *args, **kwargs):
        local_tz = pytz.timezone('Asia/Kolkata')
        now = timezone.now().astimezone(local_tz)
        today = now.date()
        current_time = now.time()
        current_hour = now.hour
        
        # Log execution
        self.stdout.write(
            self.style.WARNING(
                f'Auto checkout script running at: {now.strftime("%Y-%m-%d %I:%M %p IST")}'
            )
        )
        
        # CRITICAL: Only run at or after 7 PM IST (19:00)
        if current_hour < 19:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ STOPPED: Auto checkout only runs at or after 7:00 PM IST'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    f'Current time: {now.strftime("%I:%M %p IST")} - Too early!'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    f'Please run this command at 7:00 PM or later.'
                )
            )
            return
        
        # Find all attendance records for today that don't have check_out
        pending_checkouts = Attendance.objects.filter(
            date=today,
            check_out__isnull=True,
            check_in__isnull=False
        )
        
        self.stdout.write(
            self.style.WARNING(
                f'Found {pending_checkouts.count()} pending checkout(s) for {today}'
            )
        )
        
        count = 0
        for attendance in pending_checkouts:
            # Set check_out to 7 PM IST (19:00)
            checkout_time = datetime.combine(
                today,
                time(19, 0, 0)  # 7:00 PM
            )
            # Make it timezone-aware (IST)
            checkout_time = local_tz.localize(checkout_time)
            
            attendance.check_out = checkout_time
            attendance.save()
            attendance.calculate_work_hours()
            
            # Log auto checkout
            AuditLog.objects.create(
                user=attendance.employee,
                action='check_out',
                description=f'Auto checked out at 7:00 PM IST (system)',
                ip_address=None
            )
            
            count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Auto checked out: {attendance.employee.username} ({attendance.employee.get_full_name() or "No name"}) - Hours: {attendance.get_work_hours_display()}'
                )
            )
        
        if count == 0:
            self.stdout.write(
                self.style.WARNING(
                    f'No pending checkouts found for {today}. All employees already checked out or no check-ins today.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Successfully auto checked out {count} employee(s) at 7:00 PM IST'
                )
            )

