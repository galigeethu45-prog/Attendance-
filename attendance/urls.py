from django.urls import path, include
from . import views
from . import master_data_views
from . import office_ip_views
from . import holiday_views

urlpatterns = [
    # API endpoints
    path('api/', include('attendance.api.urls')),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Attendance actions
    path('check-in/', views.check_in, name='check_in'),
    path('check-out/', views.check_out, name='check_out'),
    
    # Break management
    path('break/start/<str:break_type>/', views.start_break, name='start_break'),
    path('break/end/', views.end_break, name='end_break'),
    
    # History and reports
    path('history/', views.attendance_history, name='attendance_history'),
    
    # Leave management
    path('leave/', views.leave_request, name='leave_request'),
    path('leave/cancel/<int:leave_id>/', views.cancel_leave, name='cancel_leave'),
    path('leave/approval/', views.leave_approval, name='leave_approval'),
    path('leave/action/<int:leave_id>/<str:action>/', views.leave_action, name='leave_action'),
    
    # Profile and notifications
    path('profile/', views.profile, name='profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    
    # Overtime
    path('overtime/', views.overtime_view, name='overtime'),
    path('overtime/approval/', views.overtime_approval, name='overtime_approval'),
    
    # WFH (Work From Home)
    path('wfh/', views.wfh_request, name='wfh_request'),
    path('wfh/cancel/<int:wfh_id>/', views.cancel_wfh, name='cancel_wfh'),
    path('wfh/approval/', views.wfh_approval, name='wfh_approval'),
    path('wfh/action/<int:wfh_id>/<str:action>/', views.wfh_action, name='wfh_action'),
    
    # Onsite/Client Visit
    path('onsite/', views.onsite_request, name='onsite_request'),
    path('onsite/approval/', views.onsite_approval, name='onsite_approval'),
    path('onsite/action/<int:onsite_id>/<str:action>/', views.onsite_action, name='onsite_action'),
    path('onsite/check-in/', views.onsite_check_in, name='onsite_check_in'),
    path('onsite/check-out/', views.onsite_check_out, name='onsite_check_out'),
    
    # HR functions
    path('hr/', views.hr_dashboard, name='hr_dashboard'),
    path('hr/employee-attendance/', views.employee_attendance_dashboard, name='employee_attendance_dashboard'),
    path('hr/export-attendance-csv/', views.export_attendance_csv, name='export_attendance_csv'),
    path('hr/employee-list/<str:list_type>/', views.employee_list_view, name='employee_list_view'),
    path('leave/approve/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('leave/reject/<int:leave_id>/', views.reject_leave, name='reject_leave'),
    path('employee/<int:user_id>/details/', views.employee_details, name='employee_details'),
    path('user/add/', views.add_user, name='add_user'),
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('user/change-work-mode/', views.change_work_mode, name='change_work_mode'),
    
    # Emergency Override (HR Only)
    path('emergency-override/status/', views.emergency_override_status, name='emergency_override_status'),
    path('emergency-override/toggle/', views.toggle_emergency_override, name='toggle_emergency_override'),
    
    # Office IP Management (HR Only)
    path('office-ips/', office_ip_views.office_ip_management, name='office_ip_management'),
    path('office-ips/add/', office_ip_views.add_office_ip, name='add_office_ip'),
    path('office-ips/remove/', office_ip_views.remove_office_ip, name='remove_office_ip'),
    path('office-ips/toggle/', office_ip_views.toggle_office_ip, name='toggle_office_ip'),
    
    # Master Data Management (HR Only)
    path('master-data/', master_data_views.master_data_list, name='master_data_list'),
    path('master-data/add/', master_data_views.add_master_data, name='add_master_data'),
    path('master-data/bulk-upload/', master_data_views.bulk_upload_master_data, name='bulk_upload_master_data'),
    path('master-data/edit/<int:master_id>/', master_data_views.edit_master_data, name='edit_master_data'),
    path('master-data/delete/<int:master_id>/', master_data_views.delete_master_data, name='delete_master_data'),
    path('user/reset-password/<int:user_id>/', master_data_views.reset_employee_password, name='reset_employee_password'),
    path('user/change-role/<int:user_id>/', master_data_views.change_employee_role, name='change_employee_role'),
    path('attendance/edit-status/<int:attendance_id>/', master_data_views.edit_attendance_status, name='edit_attendance_status'),
    
    # Holiday Calendar
    path('holidays/', holiday_views.holiday_calendar, name='holiday_calendar'),
    path('holidays/manage/', holiday_views.hr_manage_holidays, name='hr_manage_holidays'),
    path('holidays/add/', holiday_views.add_holiday, name='add_holiday'),
    path('holidays/delete/<int:holiday_id>/', holiday_views.delete_holiday, name='delete_holiday'),
    path('holidays/auto-generate/', holiday_views.auto_generate_holidays, name='auto_generate_holidays'),
]
