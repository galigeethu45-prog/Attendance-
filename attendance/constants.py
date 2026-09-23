"""
Constants for the attendance app
Contains standardized dropdown options and leave limits
"""

# Standardized Department List
DEPARTMENT_CHOICES = [
    ('', 'Select Department'),
    ('IT', 'IT'),
    ('HR', 'HR'),
    ('Finance', 'Finance'),
    ('Marketing', 'Marketing'),
    ('Sales', 'Sales'),
    ('Operations', 'Operations'),
    ('Admin', 'Admin'),
    ('Support', 'Support'),
]

# Extract just department names for filtering/display
DEPARTMENTS = [dept[0] for dept in DEPARTMENT_CHOICES if dept[0]]  # ['IT', 'HR', 'Finance', ...]

# Leave Limits (Annual)
SICK_LIMIT = 6
CASUAL_LIMIT = 6
EARNED_LIMIT = 6
MENSTRUAL_LIMIT = 12  # 1 per month

