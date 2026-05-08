"""
Management command to populate 2026 company holidays
Run: python manage.py populate_holidays_2026
"""

from django.core.management.base import BaseCommand
from attendance.models import CompanyHoliday
from datetime import date


class Command(BaseCommand):
    help = 'Populate 2026 company holidays including Sundays, 2nd/4th Saturdays, and company holidays'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('POPULATING 2026 COMPANY HOLIDAYS'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        year = 2026
        
        # Step 1: Auto-generate Sundays
        self.stdout.write('\n1. Generating all Sundays for 2026...')
        sunday_count = CompanyHoliday.auto_generate_weekly_offs(year)
        self.stdout.write(self.style.SUCCESS(f'   ✓ Created {sunday_count} Sunday holidays'))
        
        # Step 2: Auto-generate 2nd and 4th Saturdays
        self.stdout.write('\n2. Generating 2nd and 4th Saturdays for 2026...')
        saturday_count = CompanyHoliday.auto_generate_saturdays(year)
        self.stdout.write(self.style.SUCCESS(f'   ✓ Created {saturday_count} Saturday holidays'))
        
        # Step 3: Add company-specific holidays for 2026
        self.stdout.write('\n3. Adding company-specific holidays for 2026...')
        
        company_holidays = [
            {
                'date': date(2026, 1, 1),
                'name': "New Year's Day",
                'holiday_type': 'national',
                'description': 'New Year celebration'
            },
            {
                'date': date(2026, 1, 14),
                'name': 'Pongal',
                'holiday_type': 'company',
                'description': 'Tamil harvest festival'
            },
            {
                'date': date(2026, 1, 26),
                'name': 'Republic Day',
                'holiday_type': 'national',
                'description': 'Indian Republic Day'
            },
            {
                'date': date(2026, 3, 19),
                'name': 'Ugadi',
                'holiday_type': 'company',
                'description': 'Kannada and Telugu New Year'
            },
            {
                'date': date(2026, 3, 21),
                'name': 'Ramadan Id/Eid-ul-Fitr',
                'holiday_type': 'national',
                'description': 'Islamic festival marking end of Ramadan'
            },
            {
                'date': date(2026, 5, 1),
                'name': "International Worker's Day",
                'holiday_type': 'national',
                'description': 'Labour Day / May Day'
            },
            {
                'date': date(2026, 5, 27),
                'name': 'Bakrid/Eid-Ul-Adha',
                'holiday_type': 'national',
                'description': 'Islamic festival of sacrifice'
            },
            {
                'date': date(2026, 8, 15),
                'name': 'Independence Day',
                'holiday_type': 'national',
                'description': 'Indian Independence Day'
            },
            {
                'date': date(2026, 9, 14),
                'name': 'Ganesh Chaturthi/Vinayaka Chaturthi',
                'holiday_type': 'company',
                'description': 'Hindu festival celebrating Lord Ganesha'
            },
            {
                'date': date(2026, 10, 2),
                'name': 'Gandhi Jayanthi',
                'holiday_type': 'national',
                'description': 'Birthday of Mahatma Gandhi'
            },
            {
                'date': date(2026, 10, 20),
                'name': 'Dussehra',
                'holiday_type': 'company',
                'description': 'Hindu festival celebrating victory of good over evil'
            },
            {
                'date': date(2026, 11, 1),
                'name': 'Karnataka Rajyotsava Day',
                'holiday_type': 'company',
                'description': 'Karnataka Formation Day'
            },
            {
                'date': date(2026, 11, 7),
                'name': 'Diwali/Deepavali',
                'holiday_type': 'company',
                'description': 'Hindu festival of lights'
            },
            {
                'date': date(2026, 12, 25),
                'name': 'Christmas',
                'holiday_type': 'national',
                'description': 'Christian festival celebrating birth of Jesus Christ'
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for holiday_data in company_holidays:
            holiday, created = CompanyHoliday.objects.get_or_create(
                date=holiday_data['date'],
                name=holiday_data['name'],
                defaults={
                    'holiday_type': holiday_data['holiday_type'],
                    'description': holiday_data['description'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'   ✓ Created: {holiday.name} - {holiday.date.strftime("%d %b %Y")}')
            else:
                updated_count += 1
                self.stdout.write(f'   → Already exists: {holiday.name} - {holiday.date.strftime("%d %b %Y")}')
        
        self.stdout.write(self.style.SUCCESS(f'\n   ✓ Created {created_count} new company holidays'))
        if updated_count > 0:
            self.stdout.write(self.style.WARNING(f'   → {updated_count} holidays already existed'))
        
        # Summary
        total_holidays = CompanyHoliday.objects.filter(
            date__year=2026,
            is_active=True
        ).count()
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS(f'✅ COMPLETE! Total holidays for 2026: {total_holidays}'))
        self.stdout.write('=' * 70)
        
        # Breakdown by type
        self.stdout.write('\nBreakdown by type:')
        for htype, hname in CompanyHoliday.HOLIDAY_TYPES:
            count = CompanyHoliday.objects.filter(
                date__year=2026,
                holiday_type=htype,
                is_active=True
            ).count()
            if count > 0:
                self.stdout.write(f'  - {hname}: {count}')
        
        self.stdout.write('\n' + self.style.SUCCESS('Run this command again for future years to auto-generate holidays!'))
        self.stdout.write('=' * 70 + '\n')
