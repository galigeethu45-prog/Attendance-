"""
Holiday Calendar Views
Displays company holidays to employees and allows HR to manage them
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from attendance.models import CompanyHoliday
import calendar
from datetime import date, timedelta


@login_required
def holiday_calendar(request):
    """
    Holiday calendar view for all users
    Shows all holidays for the selected year/month
    """
    # Get year and month from request (default to current)
    current_date = timezone.now().date()
    year = int(request.GET.get('year', current_date.year))
    month = int(request.GET.get('month', current_date.month))
    
    # Get holidays for the selected month
    holidays = CompanyHoliday.get_holidays_for_month(year, month)
    
    # Create a dictionary for quick holiday lookup by day number
    holidays_dict = {}
    for holiday in holidays:
        holidays_dict[holiday.date.day] = holiday
    
    # Get all holidays for the year (for sidebar)
    year_holidays = CompanyHoliday.get_holidays_for_year(year)
    
    # Group holidays by type
    holidays_by_type = {
        'weekly_off': [],
        'second_saturday': [],
        'fourth_saturday': [],
        'national': [],
        'company': [],
        'optional': [],
    }
    
    for holiday in year_holidays:
        holidays_by_type[holiday.holiday_type].append(holiday)
    
    # Calendar data - create enhanced structure with holiday info
    # Set first day of week to Sunday (6) to match our headers
    calendar.setfirstweekday(calendar.SUNDAY)
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Create enhanced calendar with holiday data embedded
    enhanced_calendar = []
    for week in cal:
        enhanced_week = []
        for day in week:
            if day == 0:
                enhanced_week.append({'day': 0, 'is_holiday': False})
            else:
                holiday = holidays_dict.get(day)
                enhanced_week.append({
                    'day': day,
                    'is_holiday': holiday is not None,
                    'holiday': holiday,
                    'is_today': (day == current_date.day and month == current_date.month and year == current_date.year)
                })
        enhanced_calendar.append(enhanced_week)
    
    # Get upcoming holidays (next 5)
    upcoming_holidays = CompanyHoliday.objects.filter(
        date__gte=current_date,
        is_active=True
    ).order_by('date')[:5]
    
    context = {
        'year': year,
        'month': month,
        'month_name': month_name,
        'calendar': enhanced_calendar,  # Use enhanced calendar
        'holidays': holidays,
        'holidays_dict': holidays_dict,
        'year_holidays': year_holidays,
        'holidays_by_type': holidays_by_type,
        'upcoming_holidays': upcoming_holidays,
        'current_date': current_date,
        'available_years': range(2020, 2030),
    }
    
    return render(request, 'holiday_calendar.html', context)


@login_required
def hr_manage_holidays(request):
    """
    HR view to manage holidays
    Add/Edit/Delete holidays
    """
    # Check if user is HR
    if not request.user.is_superuser:
        try:
            if not request.user.employeeprofile.is_hr:
                messages.error(request, 'Access denied. HR only.')
                return redirect('holiday_calendar')
        except:
            messages.error(request, 'Access denied.')
            return redirect('holiday_calendar')
    
    year = int(request.GET.get('year', timezone.now().year))
    
    # Get all holidays for the year
    holidays = CompanyHoliday.get_holidays_for_year(year)
    
    # Group by type
    holidays_by_type = {}
    for htype, hname in CompanyHoliday.HOLIDAY_TYPES:
        holidays_by_type[htype] = holidays.filter(holiday_type=htype)
    
    context = {
        'year': year,
        'holidays': holidays,
        'holidays_by_type': holidays_by_type,
        'holiday_types': CompanyHoliday.HOLIDAY_TYPES,
        'available_years': range(2020, 2030),
    }
    
    return render(request, 'hr_manage_holidays.html', context)


@login_required
def add_holiday(request):
    """
    Add a new holiday (HR only)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    # Check if user is HR
    if not request.user.is_superuser:
        try:
            if not request.user.employeeprofile.is_hr:
                return JsonResponse({'success': False, 'error': 'Access denied'})
        except:
            return JsonResponse({'success': False, 'error': 'Access denied'})
    
    try:
        from datetime import datetime
        
        date_str = request.POST.get('date')
        name = request.POST.get('name')
        holiday_type = request.POST.get('holiday_type')
        description = request.POST.get('description', '')
        
        # Validate
        if not all([date_str, name, holiday_type]):
            return JsonResponse({'success': False, 'error': 'All fields are required'})
        
        # Parse date
        holiday_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Create holiday
        holiday = CompanyHoliday.objects.create(
            date=holiday_date,
            name=name,
            holiday_type=holiday_type,
            description=description,
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Holiday "{name}" added successfully',
            'holiday': {
                'id': holiday.id,
                'date': holiday.date.strftime('%Y-%m-%d'),
                'name': holiday.name,
                'type': holiday.get_holiday_type_display()
            }
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def delete_holiday(request, holiday_id):
    """
    Delete a holiday (HR only)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    # Check if user is HR
    if not request.user.is_superuser:
        try:
            if not request.user.employeeprofile.is_hr:
                return JsonResponse({'success': False, 'error': 'Access denied'})
        except:
            return JsonResponse({'success': False, 'error': 'Access denied'})
    
    try:
        holiday = CompanyHoliday.objects.get(id=holiday_id)
        holiday_name = holiday.name
        holiday.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Holiday "{holiday_name}" deleted successfully'
        })
    
    except CompanyHoliday.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Holiday not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def auto_generate_holidays(request):
    """
    Auto-generate holidays for a year (HR only)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
    # Check if user is HR
    if not request.user.is_superuser:
        try:
            if not request.user.employeeprofile.is_hr:
                return JsonResponse({'success': False, 'error': 'Access denied'})
        except:
            return JsonResponse({'success': False, 'error': 'Access denied'})
    
    try:
        year = int(request.POST.get('year'))
        
        # Generate Sundays
        sunday_count = CompanyHoliday.auto_generate_weekly_offs(year)
        
        # Generate 2nd and 4th Saturdays
        saturday_count = CompanyHoliday.auto_generate_saturdays(year)
        
        return JsonResponse({
            'success': True,
            'message': f'Generated {sunday_count} Sundays and {saturday_count} Saturdays for {year}'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
