"""
Constants for the attendance app
Contains standardized dropdown options
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
