from django.urls import path
from . import views
from . import master_data_views

urlpatterns = [
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
    
    # HR functions
    path('hr/', views.hr_dashboard, name='hr_dashboard'),
    path('leave/approve/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('leave/reject/<int:leave_id>/', views.reject_leave, name='reject_leave'),
    path('employee/<int:user_id>/details/', views.employee_details, name='employee_details'),
    path('user/add/', views.add_user, name='add_user'),
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    
    # Master Data Management (HR Only)
    path('master-data/', master_data_views.master_data_list, name='master_data_list'),
    path('master-data/add/', master_data_views.add_master_data, name='add_master_data'),
    path('master-data/bulk-upload/', master_data_views.bulk_upload_master_data, name='bulk_upload_master_data'),
    path('master-data/edit/<int:master_id>/', master_data_views.edit_master_data, name='edit_master_data'),
    path('master-data/delete/<int:master_id>/', master_data_views.delete_master_data, name='delete_master_data'),
    path('user/reset-password/<int:user_id>/', master_data_views.reset_employee_password, name='reset_employee_password'),
    path('user/change-role/<int:user_id>/', master_data_views.change_employee_role, name='change_employee_role'),
    path('attendance/edit-status/<int:attendance_id>/', master_data_views.edit_attendance_status, name='edit_attendance_status'),
]
