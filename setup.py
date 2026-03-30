"""
Setup script for AttendanceHub
Run this after installing requirements to set up the database and create initial data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import EmployeeProfile

def create_demo_users():
    """Create demo users for testing"""
    print("Creating demo users...")
    
    # Create HR user
    if not User.objects.filter(username='hr_admin').exists():
        hr_user = User.objects.create_user(
            username='hr_admin',
            email='hr@attendancehub.com',
            password='admin123',
            first_name='HR',
            last_name='Admin'
        )
        EmployeeProfile.objects.create(
            user=hr_user,
            department='Human Resources',
            designation='HR Manager',
            is_hr=True
        )
        print("✓ HR Admin created (username: hr_admin, password: admin123)")
    
    # Create regular employee
    if not User.objects.filter(username='employee1').exists():
        emp_user = User.objects.create_user(
            username='employee1',
            email='employee1@attendancehub.com',
            password='emp123',
            first_name='John',
            last_name='Doe'
        )
        EmployeeProfile.objects.create(
            user=emp_user,
            department='IT',
            designation='Software Developer',
            is_hr=False
        )
        print("✓ Employee created (username: employee1, password: emp123)")
    
    # Create another employee
    if not User.objects.filter(username='employee2').exists():
        emp_user2 = User.objects.create_user(
            username='employee2',
            email='employee2@attendancehub.com',
            password='emp123',
            first_name='Jane',
            last_name='Smith'
        )
        EmployeeProfile.objects.create(
            user=emp_user2,
            department='Marketing',
            designation='Marketing Executive',
            is_hr=False
        )
        print("✓ Employee 2 created (username: employee2, password: emp123)")
    
    print("\n✅ Demo users created successfully!")
    print("\nLogin credentials:")
    print("HR Admin: hr_admin / admin123")
    print("Employee 1: employee1 / emp123")
    print("Employee 2: employee2 / emp123")

if __name__ == '__main__':
    create_demo_users()
