"""
Context processors for attendance app
Provides global template variables
"""

def employee_profile(request):
    """
    Add employee_profile to all template contexts
    Safely handles cases where profile doesn't exist
    """
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.employeeprofile
        except:
            profile = None
    
    return {
        'employee_profile': profile
    }
