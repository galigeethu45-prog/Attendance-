from django.core.management.base import BaseCommand
from django.utils import timezone
from attendance.models import Attendance, AuditLog
import pytz
from datetime import datetime, time
import logging
import os

# Setup logging
log_dir = '/var/log/attendance'
if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir)
    except:
        log_dir = '/tmp'

logging.basicConfig(
    filename=f'{log_dir}/auto_checkout.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Auto checkout employees at 7 PM if they forgot to check out'

    def handle(self, *args, **kwargs):
        try:
            local_tz = pytz.timezone('Asia/Kolkata')
            now = timezone.now().astimezone(local_tz)
            today = now.date()
            current_time = now.time()
            current_hour = now.hour
            
            # Log execution
            log_msg = f'Auto checkout script running at: {now.strftime("%Y-%m-%d %I:%M %p IST")}'
            self.stdout.write(self.style.WARNING(log_msg))
            logger.info(log_msg)
            
            # CRITICAL: Only run at or after 7 PM IST (19:00)
            if current_hour < 19:
                error_msg = f'❌ STOPPED: Auto checkout only runs at or after 7:00 PM IST. Current time: {now.strftime("%I:%M %p IST")}'
                self.stdout.write(self.style.ERROR(error_msg))
                logger.warning(error_msg)
                return
            
            # Find all attendance records for today that don't have check_out
            pending_checkouts = Attendance.objects.filter(
                date=today,
                check_out__isnull=True,
                check_in__isnull=False
            )
            
            count_msg = f'Found {pending_checkouts.count()} pending checkout(s) for {today}'
            self.stdout.write(self.style.WARNING(count_msg))
            logger.info(count_msg)
            
            count = 0
            for attendance in pending_checkouts:
                try:
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
                    
                    success_msg = f'✓ Auto checked out: {attendance.employee.username} ({attendance.employee.get_full_name() or "No name"}) - Hours: {attendance.get_work_hours_display()}'
                    self.stdout.write(self.style.SUCCESS(success_msg))
                    logger.info(success_msg)
                    
                except Exception as e:
                    error_msg = f'Error processing {attendance.employee.username}: {str(e)}'
                    self.stdout.write(self.style.ERROR(error_msg))
                    logger.error(error_msg)
            
            if count == 0:
                no_checkout_msg = f'No pending checkouts found for {today}. All employees already checked out or no check-ins today.'
                self.stdout.write(self.style.WARNING(no_checkout_msg))
                logger.info(no_checkout_msg)
            else:
                final_msg = f'✓ Successfully auto checked out {count} employee(s) at 7:00 PM IST'
                self.stdout.write(self.style.SUCCESS(final_msg))
                logger.info(final_msg)
                
        except Exception as e:
            critical_error = f'CRITICAL ERROR in auto_checkout command: {str(e)}'
            self.stdout.write(self.style.ERROR(critical_error))
            logger.critical(critical_error)
            raise


