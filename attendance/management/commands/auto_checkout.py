from django.core.management.base import BaseCommand
from django.utils import timezone
from attendance.models import Attendance, AuditLog
import pytz


class Command(BaseCommand):
    help = 'Auto checkout employees at 7 PM if they forgot to check out'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        local_tz = pytz.timezone('Asia/Kolkata')
        
        # Find all attendance records for today that don't have check_out
        pending_checkouts = Attendance.objects.filter(
            date=today,
            check_out__isnull=True,
            check_in__isnull=False
        )
        
        count = 0
        for attendance in pending_checkouts:
            # Set check_out to 7 PM IST
            checkout_time = timezone.datetime.combine(
                today,
                timezone.datetime.strptime('19:00', '%H:%M').time()
            )
            checkout_time = local_tz.localize(checkout_time)
            
            attendance.check_out = checkout_time
            attendance.save()
            attendance.calculate_work_hours()
            
            # Log auto checkout
            AuditLog.objects.create(
                user=attendance.employee,
                action='check_out',
                description=f'Auto checked out at 7:00 PM (system)',
                ip_address=None
            )
            
            count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Auto checked out {attendance.employee.username} at 7 PM - Hours: {attendance.get_work_hours_display()}'
                )
            )
        
        if count == 0:
            self.stdout.write(self.style.WARNING('No pending checkouts found'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully auto checked out {count} employee(s)')
            )
