from django.urls import path
from . import views

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
    
    # HR functions
    path('hr/', views.hr_dashboard, name='hr_dashboard'),
    path('leave/approve/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('leave/reject/<int:leave_id>/', views.reject_leave, name='reject_leave'),
    path('employee/<int:user_id>/details/', views.employee_details, name='employee_details'),
    path('user/add/', views.add_user, name='add_user'),
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),
]
