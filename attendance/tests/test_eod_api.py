"""
EOD API Integration - Test Suite
Purpose: Validate read-only API endpoints for EOD integration
Security: Test authentication, authorization, and data exposure
"""

import os
from datetime import date
from django.test import TestCase, Client
from django.contrib.auth.models import User
from attendance.models import (
    EmployeeMasterData,
    EmployeeProfile,
    Attendance,
    LeaveRequest,
    WFHRequest
)


class EODAPITestCase(TestCase):
    """
    Test suite for EOD read-only API endpoints.
    
    Tests:
    1. Authentication (API key validation)
    2. Employee endpoint (data exposure, HTTP methods)
    3. Attendance endpoint (status normalization, logic)
    4. Error handling
    5. Read-only enforcement
    """
    
    def setUp(self):
        """Set up test data and API key"""
        
        # Set test API key
        os.environ['EOD_API_KEY'] = 'test-api-key-12345'
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='TEST001',
            password='test123',
            first_name='Test',
            last_name='User'
        )
        
        self.user2 = User.objects.create_user(
            username='TEST002',
            password='test123',
            first_name='Jane',
            last_name='Doe'
        )
        
        # Create EmployeeProfiles
        self.profile1 = EmployeeProfile.objects.create(
            user=self.user1,
            employee_id='TEST001',
            department='Engineering',
            designation='Developer'
        )
        
        self.profile2 = EmployeeProfile.objects.create(
            user=self.user2,
            employee_id='TEST002',
            department='Marketing',
            designation='Manager'
        )
        
        # Create EmployeeMasterData records
        self.employee1 = EmployeeMasterData.objects.create(
            employee_id='TEST001',
            first_name='Test',
            last_name='User',
            department='Engineering',
            designation='Developer',
            email='test001@arraafiinfotech.com',
            phone_number='1234567890',
            date_of_birth=date(1990, 1, 1),
            date_of_joining=date(2020, 1, 1),
            gender='male',
            blood_group='O+',
            local_address='123 Test Street',
            permanent_address='456 Test Avenue',
            aadhar_number='123456789012',
            pan_number='ABCDE1234F',
            account_created=True,
            linked_user=self.user1
        )
        
        self.employee2 = EmployeeMasterData.objects.create(
            employee_id='TEST002',
            first_name='Jane',
            last_name='Doe',
            department='Marketing',
            designation='Manager',
            email='test002@arraafiinfotech.com',
            phone_number='0987654321',
            date_of_birth=date(1985, 5, 15),
            date_of_joining=date(2018, 3, 10),
            gender='female',
            blood_group='A+',
            local_address='789 Test Lane',
            permanent_address='012 Test Road',
            aadhar_number='987654321098',
            pan_number='XYZAB9876C',
            account_created=True,
            linked_user=self.user2
        )
        
        # Test date
        self.test_date = date(2026, 10, 1)
        
        # HTTP Client
        self.client = Client()
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove test API key
        if 'EOD_API_KEY' in os.environ:
            del os.environ['EOD_API_KEY']
    
    # =========================
    # AUTHENTICATION TESTS
    # =========================
    
    def test_employee_endpoint_missing_api_key(self):
        """Test 14: Missing API key returns HTTP 401"""
        response = self.client.get('/attendance/api/eod/employees/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['error'], 'Unauthorized')
    
    def test_employee_endpoint_incorrect_api_key(self):
        """Test 15: Incorrect API key returns HTTP 401"""
        response = self.client.get(
            '/attendance/api/eod/employees/',
            HTTP_X_API_KEY='wrong-key'
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['error'], 'Unauthorized')
    
    def test_attendance_endpoint_missing_api_key(self):
        """Test 14: Missing API key returns HTTP 401"""
        response = self.client.get('/attendance/api/eod/attendance/?date=2026-10-01')
        self.assertEqual(response.status_code, 401)
    
    def test_attendance_endpoint_incorrect_api_key(self):
        """Test 15: Incorrect API key returns HTTP 401"""
        response = self.client.get(
            '/attendance/api/eod/attendance/?date=2026-10-01',
            HTTP_X_API_KEY='wrong-key'
        )
        self.assertEqual(response.status_code, 401)
    
    # =========================
    # EMPLOYEE ENDPOINT TESTS
    # =========================
    
    def test_employee_list_success(self):
        """Test 1: Employee endpoint returns HTTP 200 with valid authentication"""
        response = self.client.get(
            '/attendance/api/eod/employees/',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('employees', response.json())
    
    def test_employee_list_contains_required_fields(self):
        """Test 2: Employee endpoint returns ONLY required fields"""
        response = self.client.get(
            '/attendance/api/eod/employees/',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        
        employees = response.json()['employees']
        self.assertGreater(len(employees), 0)
        
        # Check first employee has required fields
        employee = employees[0]
        self.assertIn('employee_id', employee)
        self.assertIn('first_name', employee)
        self.assertIn('last_name', employee)
        self.assertIn('department', employee)
        self.assertIn('designation', employee)
    
    def test_employee_list_does_not_expose_sensitive_fields(self):
        """Test 3: Employee endpoint does NOT expose sensitive fields"""
        response = self.client.get(
            '/attendance/api/eod/employees/',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        
        employees = response.json()['employees']
        employee = employees[0]
        
        # Verify sensitive fields are NOT present
        self.assertNotIn('aadhar_number', employee)
        self.assertNotIn('pan_number', employee)
        self.assertNotIn('email', employee)
        self.assertNotIn('phone_number', employee)
        self.assertNotIn('alternate_phone', employee)
        self.assertNotIn('local_address', employee)
        self.assertNotIn('permanent_address', employee)
        self.assertNotIn('date_of_birth', employee)
        self.assertNotIn('gender', employee)
        self.assertNotIn('blood_group', employee)
        self.assertNotIn('bank_account_number', employee)
        self.assertNotIn('bank_ifsc_code', employee)
        self.assertNotIn('base_salary', employee)
        self.assertNotIn('ot_rate', employee)
    
    def test_employee_list_post_not_allowed(self):
        """Test 16: POST to employee endpoint returns HTTP 405"""
        response = self.client.post(
            '/attendance/api/eod/employees/',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        self.assertEqual(response.status_code, 405)
    
    def test_employee_list_put_not_allowed(self):
        """Test 18: PUT to employee endpoint returns HTTP 405"""
        response = self.client.put(
            '/attendance/api/eod/employees/',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        self.assertEqual(response.status_code, 405)
    
    def test_employee_list_delete_not_allowed(self):
        """Test 18: DELETE to employee endpoint returns HTTP 405"""
        response = self.client.delete(
            '/attendance/api/eod/employees/',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        self.assertEqual(response.status_code, 405)
    
    # =========================
    # ATTENDANCE ENDPOINT TESTS
    # =========================
    
    def test_attendance_list_success(self):
        """Test 4: Attendance endpoint returns HTTP 200 with valid date and authentication"""
        response = self.client.get(
            '/attendance/api/eod/attendance/?date=2026-10-01',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('date', response.json())
        self.assertIn('attendance', response.json())
    
    def test_attendance_missing_date_parameter(self):
        """Test 12: Missing date returns HTTP 400"""
        response = self.client.get(
            '/attendance/api/eod/attendance/',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'date parameter is required')
    
    def test_attendance_invalid_date_format(self):
        """Test 13: Invalid date returns HTTP 400"""
        response = self.client.get(
            '/attendance/api/eod/attendance/?date=invalid',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid date format. Use YYYY-MM-DD.')
    
    def test_attendance_status_present(self):
        """Test 5: Attendance correctly returns PRESENT"""
        # Create attendance record with status='present'
        Attendance.objects.create(
            employee=self.user1,
            date=self.test_date,
            status='present',
            total_work_hours=8.0
        )
        
        response = self.client.get(
            f'/attendance/api/eod/attendance/?date={self.test_date}',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        
        attendance_data = response.json()['attendance']
        test001_status = next(a['status'] for a in attendance_data if a['employee_id'] == 'TEST001')
        self.assertEqual(test001_status, 'PRESENT')
    
    def test_attendance_normalizes_late_to_present(self):
        """Test 6: Attendance correctly normalizes late → PRESENT"""
        # Create attendance record with status='late'
        Attendance.objects.create(
            employee=self.user1,
            date=self.test_date,
            status='late',
            total_work_hours=7.0
        )
        
        response = self.client.get(
            f'/attendance/api/eod/attendance/?date={self.test_date}',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        
        attendance_data = response.json()['attendance']
        test001_status = next(a['status'] for a in attendance_data if a['employee_id'] == 'TEST001')
        self.assertEqual(test001_status, 'PRESENT')
    
    def test_attendance_normalizes_halfday_to_present(self):
        """Test 7: Attendance correctly normalizes half-day → PRESENT"""
        # Create attendance record with status='half-day'
        Attendance.objects.create(
            employee=self.user1,
            date=self.test_date,
            status='half-day',
            total_work_hours=4.0
        )
        
        response = self.client.get(
            f'/attendance/api/eod/attendance/?date={self.test_date}',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        
        attendance_data = response.json()['attendance']
        test001_status = next(a['status'] for a in attendance_data if a['employee_id'] == 'TEST001')
        self.assertEqual(test001_status, 'PRESENT')
    
    def test_attendance_status_absent(self):
        """Test 8: Attendance correctly returns ABSENT"""
        # Create attendance record with status='absent'
        Attendance.objects.create(
            employee=self.user1,
            date=self.test_date,
            status='absent',
            total_work_hours=0.0
        )
        
        response = self.client.get(
            f'/attendance/api/eod/attendance/?date={self.test_date}',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        
        attendance_data = response.json()['attendance']
        test001_status = next(a['status'] for a in attendance_data if a['employee_id'] == 'TEST001')
        self.assertEqual(test001_status, 'ABSENT')
    
    def test_attendance_approved_wfh_returns_wfh(self):
        """Test 9: Approved WFH returns WFH"""
        # Create approved WFH request
        WFHRequest.objects.create(
            employee=self.user1,
            start_date=self.test_date,
            end_date=self.test_date,
            reason='Working from home',
            status='approved'
        )
        
        response = self.client.get(
            f'/attendance/api/eod/attendance/?date={self.test_date}',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        
        attendance_data = response.json()['attendance']
        test001_status = next(a['status'] for a in attendance_data if a['employee_id'] == 'TEST001')
        self.assertEqual(test001_status, 'WFH')
    
    def test_attendance_approved_leave_returns_leave(self):
        """Test 10: Approved Leave returns LEAVE"""
        # Create approved leave request
        LeaveRequest.objects.create(
            employee=self.user1,
            leave_type='casual',
            start_date=self.test_date,
            end_date=self.test_date,
            reason='Personal',
            status='approved'
        )
        
        response = self.client.get(
            f'/attendance/api/eod/attendance/?date={self.test_date}',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        
        attendance_data = response.json()['attendance']
        test001_status = next(a['status'] for a in attendance_data if a['employee_id'] == 'TEST001')
        self.assertEqual(test001_status, 'LEAVE')
    
    def test_attendance_no_record_returns_absent(self):
        """Test 11: Missing attendance + no WFH + no Leave returns ABSENT"""
        # No attendance record, no WFH, no leave for user1
        
        response = self.client.get(
            f'/attendance/api/eod/attendance/?date={self.test_date}',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        
        attendance_data = response.json()['attendance']
        test001_status = next(a['status'] for a in attendance_data if a['employee_id'] == 'TEST001')
        self.assertEqual(test001_status, 'ABSENT')
    
    def test_attendance_post_not_allowed(self):
        """Test 17: POST to attendance endpoint returns HTTP 405"""
        response = self.client.post(
            '/attendance/api/eod/attendance/?date=2026-10-01',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        self.assertEqual(response.status_code, 405)
    
    def test_attendance_put_not_allowed(self):
        """Test 18: PUT to attendance endpoint returns HTTP 405"""
        response = self.client.put(
            '/attendance/api/eod/attendance/?date=2026-10-01',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        self.assertEqual(response.status_code, 405)
    
    def test_attendance_delete_not_allowed(self):
        """Test 18: DELETE to attendance endpoint returns HTTP 405"""
        response = self.client.delete(
            '/attendance/api/eod/attendance/?date=2026-10-01',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        self.assertEqual(response.status_code, 405)
    
    # =========================
    # PRIORITY LOGIC TESTS
    # =========================
    
    def test_leave_priority_over_wfh(self):
        """Test: Approved leave takes priority over WFH"""
        # Create both approved leave and WFH for same date
        LeaveRequest.objects.create(
            employee=self.user1,
            leave_type='sick',
            start_date=self.test_date,
            end_date=self.test_date,
            reason='Sick',
            status='approved'
        )
        
        WFHRequest.objects.create(
            employee=self.user1,
            start_date=self.test_date,
            end_date=self.test_date,
            reason='WFH',
            status='approved'
        )
        
        response = self.client.get(
            f'/attendance/api/eod/attendance/?date={self.test_date}',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        
        attendance_data = response.json()['attendance']
        test001_status = next(a['status'] for a in attendance_data if a['employee_id'] == 'TEST001')
        # Leave takes priority
        self.assertEqual(test001_status, 'LEAVE')
    
    def test_leave_priority_over_attendance(self):
        """Test: Approved leave takes priority over attendance record"""
        # Create both approved leave and attendance
        LeaveRequest.objects.create(
            employee=self.user1,
            leave_type='casual',
            start_date=self.test_date,
            end_date=self.test_date,
            reason='Personal',
            status='approved'
        )
        
        Attendance.objects.create(
            employee=self.user1,
            date=self.test_date,
            status='present',
            total_work_hours=8.0
        )
        
        response = self.client.get(
            f'/attendance/api/eod/attendance/?date={self.test_date}',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        
        attendance_data = response.json()['attendance']
        test001_status = next(a['status'] for a in attendance_data if a['employee_id'] == 'TEST001')
        # Leave takes priority
        self.assertEqual(test001_status, 'LEAVE')
    
    def test_wfh_priority_over_attendance(self):
        """Test: Approved WFH takes priority over attendance record"""
        # Create both approved WFH and attendance
        WFHRequest.objects.create(
            employee=self.user1,
            start_date=self.test_date,
            end_date=self.test_date,
            reason='WFH',
            status='approved'
        )
        
        Attendance.objects.create(
            employee=self.user1,
            date=self.test_date,
            status='present',
            total_work_hours=8.0
        )
        
        response = self.client.get(
            f'/attendance/api/eod/attendance/?date={self.test_date}',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        
        attendance_data = response.json()['attendance']
        test001_status = next(a['status'] for a in attendance_data if a['employee_id'] == 'TEST001')
        # WFH takes priority
        self.assertEqual(test001_status, 'WFH')
    
    # =========================
    # READ-ONLY ENFORCEMENT
    # =========================
    
    def test_readonly_no_database_writes(self):
        """Test 19: Verify API does not modify database"""
        # Get initial counts
        initial_employee_count = EmployeeMasterData.objects.count()
        initial_attendance_count = Attendance.objects.count()
        initial_leave_count = LeaveRequest.objects.count()
        initial_wfh_count = WFHRequest.objects.count()
        
        # Call both endpoints
        self.client.get(
            '/attendance/api/eod/employees/',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        
        self.client.get(
            f'/attendance/api/eod/attendance/?date={self.test_date}',
            HTTP_X_API_KEY='test-api-key-12345'
        )
        
        # Verify counts unchanged
        self.assertEqual(EmployeeMasterData.objects.count(), initial_employee_count)
        self.assertEqual(Attendance.objects.count(), initial_attendance_count)
        self.assertEqual(LeaveRequest.objects.count(), initial_leave_count)
        self.assertEqual(WFHRequest.objects.count(), initial_wfh_count)
