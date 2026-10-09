# EOD API Integration - Comprehensive Analysis
## Read-Only API Layer for SmartPunch → EOD Integration

**Date:** October 1, 2026  
**Analyst:** Kiro AI  
**Status:** ANALYSIS COMPLETE - AWAITING APPROVAL

---

## 📋 EXECUTIVE SUMMARY

This document provides a complete analysis of the SmartPunch attendance system for implementing a **read-only API integration** with the EOD (End of Day) system. SmartPunch will remain the **source of truth** for all employee and attendance data.

---

## 🔍 1. RELEVANT FILES IDENTIFIED

### Core Models
- **`attendance/models.py`** (1625 lines)
  - EmployeeMasterData (Lines 7-79)
  - EmployeeProfile (Lines 125-286)
  - Attendance (Lines 290-362)

### Existing API Infrastructure
- **`attendance/api/views.py`** (918+ lines)
  - Already has custom decorators (@hr_required, @team_leader_or_hr_required)
  - Uses JSON responses, not DRF ViewSets
  - Authentication via SessionAuthentication
  
- **`attendance/api/serializers.py`** (103 lines)
  - Uses DRF serializers (rest_framework.serializers)
  - Existing serializers: RegisterSerializer, UserBasicSerializer, TeamSerializer

- **`attendance/api/urls.py`** (42 lines)
  - Currently has ~15 endpoints for teams, auth, bulk checkout

### Configuration Files
- **`core/settings.py`** (171+ lines)
  - Django REST Framework already installed
  - SessionAuthentication configured
  - IsAuthenticated default permission
  
- **`core/urls.py`** (40 lines)
  - API routes included via `path('attendance/api/', include('attendance.api.urls'))`

---

## 🗄️ 2. RELEVANT MODELS & EXACT FIELDS

### 2.1 EmployeeMasterData Model
**Location:** `attendance/models.py` Lines 7-79

**Purpose:** Stores comprehensive employee information (master data source)

**Fields:**
```python
# Primary Identification
employee_id = CharField(max_length=20, unique=True, db_index=True)

# Personal Information
first_name = CharField(max_length=100)
middle_name = CharField(max_length=100, blank=True, null=True)
last_name = CharField(max_length=100)
gender = CharField(max_length=10, choices=GENDER_CHOICES)
date_of_birth = DateField()
blood_group = CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)

# Company Information
department = CharField(max_length=100)
designation = CharField(max_length=100)
date_of_joining = DateField()

# Contact Details
phone_number = CharField(max_length=15)
alternate_phone = CharField(max_length=15, blank=True, null=True)
email = EmailField(unique=True, db_index=True)

# Address
local_address = TextField()
permanent_address = TextField()

# Identity Documents
aadhar_number = CharField(max_length=12)
pan_number = CharField(max_length=10)

# Account Status
account_created = BooleanField(default=False)
linked_user = OneToOneField(User, on_delete=SET_NULL, null=True, blank=True, related_name='master_data')

# Metadata
created_at = DateTimeField(auto_now_add=True)
updated_at = DateTimeField(auto_now=True)
created_by = ForeignKey(User, on_delete=SET_NULL, null=True, related_name='created_master_data')
```

**Key Methods:**
- `get_full_name()` → Returns formatted full name with middle name if present

**Notes:**
- This is the MASTER data source (authoritative)
- Separate from EmployeeProfile which is user-facing
- Has indexes on `employee_id`, `email`, `date_of_birth`

---

### 2.2 EmployeeProfile Model
**Location:** `attendance/models.py` Lines 125-286

**Purpose:** User-facing employee profile (linked to Django User model)

**Fields:**
```python
user = OneToOneField(User, on_delete=CASCADE)

# Employee ID
employee_id = CharField(max_length=20, unique=True, null=True, blank=True, db_index=True)

# Work Mode
work_mode = CharField(max_length=20, choices=WORK_MODE_CHOICES, default='office')
# Choices: 'office', 'hybrid', 'permanent_wfh'

# Personal Information
gender = CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
date_of_birth = DateField(null=True, blank=True)
blood_group = CharField(max_length=5, blank=True)
phone_number = CharField(max_length=15, blank=True)
alternate_phone = CharField(max_length=15, blank=True)

# Company Information
department = CharField(max_length=100, blank=True, db_index=True)
designation = CharField(max_length=100, blank=True)
date_of_joining = DateField(null=True, blank=True)
is_hr = BooleanField(default=False, db_index=True)

# Role Management
role = CharField(max_length=20, choices=ROLE_CHOICES, default='employee', db_index=True)
# Choices: 'employee', 'team_leader', 'manager', 'hr'

is_team_leader = BooleanField(default=False, db_index=True)

# Profile completion
profile_completed = BooleanField(default=False)

# Salary & Bank Information
base_salary = DecimalField(max_digits=10, decimal_places=2, default=0.00)
ot_rate = DecimalField(max_digits=8, decimal_places=2, default=300.00)
bank_account_number = CharField(max_length=50, blank=True)
bank_ifsc_code = CharField(max_length=20, blank=True)
bank_name = CharField(max_length=100, blank=True)
```

**Relationship:**
- `OneToOne` with Django `User` model
- Can be linked to `EmployeeMasterData` via `employee_id`

**Notes:**
- Some profiles may NOT have employee_id if created manually
- Department is indexed for fast filtering
- Role field controls permissions

---

### 2.3 Attendance Model
**Location:** `attendance/models.py` Lines 290-362

**Purpose:** Daily attendance records for employees

**Fields:**
```python
employee = ForeignKey(User, on_delete=CASCADE, db_index=True)
date = DateField(default=timezone.now, db_index=True)

check_in = DateTimeField(null=True, blank=True)
check_out = DateTimeField(null=True, blank=True)

total_work_hours = FloatField(default=0)

status = CharField(max_length=20, choices=[...], default='present', db_index=True)
# Choices: 'present', 'late', 'half-day', 'absent'

# HR/Admin Edit Tracking
status_modified_by = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True, related_name='modified_attendances')
status_modified_at = DateTimeField(null=True, blank=True)
status_change_reason = TextField(blank=True, null=True)
```

**Constraints:**
- `unique_together = ('employee', 'date')` → One record per employee per day

**Key Methods:**
- `calculate_work_hours()` → Calculates hours and auto-updates status
- `get_work_hours_display()` → Returns "7h 30m" format

**Indexes:**
- `('employee', 'date')` - Fast lookup by employee and date
- `('date', 'status')` - Fast filtering by date and status
- `('-date')` - Fast reverse chronological ordering

**Notes:**
- Status is calculated automatically based on work hours
- Can be manually modified by HR (tracked in status_modified_by)

---

### 2.4 Related Models for Status Determination

#### LeaveRequest Model
**Location:** `attendance/models.py` Lines 443-546

**Fields:**
```python
employee = ForeignKey(User, on_delete=CASCADE)
leave_type = CharField(max_length=20, choices=LEAVE_TYPES)
# Choices: 'sick', 'casual', 'earned', 'halfday', 'menstrual', 'unpaid'
start_date = DateField(default=timezone.now)
end_date = DateField(default=timezone.now)
selected_dates = JSONField(null=True, blank=True)  # For non-consecutive dates
status = CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
# Choices: 'pending', 'approved', 'rejected'
```

**Usage:** If `status='approved'` for a date → Attendance status = LEAVE

---

#### WFHRequest Model
**Location:** `attendance/models.py` Lines 642-706

**Fields:**
```python
employee = ForeignKey(User, on_delete=CASCADE)
start_date = DateField()
end_date = DateField()
selected_dates = JSONField(null=True, blank=True)
status = CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
# Choices: 'pending', 'approved', 'rejected'
```

**Usage:** If `status='approved'` for a date → Attendance status = WFH

---

## 📊 3. ATTENDANCE STATUS CALCULATION LOGIC

### Current Status Values in Database:
```python
STATUS_CHOICES = [
    ('present', 'Present'),
    ('late', 'Late'),
    ('half-day', 'Half-Day'),
    ('absent', 'Absent'),
]
```

### How Status is Determined:

#### 1. **PRESENT**
- Attendance record exists with check_in AND check_out
- `total_work_hours >= 7.5`
- No approved leave for that date

#### 2. **LATE**
- Attendance record exists
- Check-in time > 10:00 AM (late arrival)
- Status remains as stored in DB

#### 3. **HALF-DAY**
- Attendance record exists with check_in AND check_out
- `6 <= total_work_hours < 7.5`
- OR: Arrived very late (status set at check-in)

#### 4. **ABSENT**
- No attendance record for a working day
- No approved leave for that date
- No approved WFH for that date

#### 5. **LEAVE** (Not in Attendance.status choices)
- Determined by: `LeaveRequest.objects.filter(employee=user, status='approved', start_date__lte=date, end_date__gte=date).exists()`

#### 6. **WFH** (Not in Attendance.status choices)
- Determined by: `WFHRequest.objects.filter(employee=user, status='approved', start_date__lte=date, end_date__gte=date).exists()`

### EOD Status Mapping:

For EOD integration, we need to normalize to:
- **PRESENT** → Maps to 'present' or 'late' in Attendance model
- **ABSENT** → No attendance record + no leave + no WFH
- **WFH** → Approved WFH request for that date
- **LEAVE** → Approved leave request for that date

---

## 🔐 4. EXISTING AUTHENTICATION MECHANISM

### 4.1 Authentication Method
**Type:** Session-based Authentication (Django's built-in)

**Configuration:**
```python
# core/settings.py Line 158
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### 4.2 Existing Decorators

**Location:** `attendance/api/views.py` Lines 11-65

#### @hr_required
```python
def hr_required(view_func):
    """
    Restricts access to HR/Admin users only
    Checks: is_authenticated AND (is_superuser OR is_hr flag OR role in ['hr', 'manager'])
    """
```

#### @team_leader_or_hr_required
```python
def team_leader_or_hr_required(view_func):
    """
    Restricts access to Team Leaders, HR, or Admin
    Checks: is_authenticated AND (is_superuser OR is_hr OR is_team_leader)
    """
```

### 4.3 Login Flow
**Endpoint:** `/api/login/` (POST)

**Request:**
```json
{
  "identifier": "AI0001" or "employee@arraafiinfotech.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "employee_id": "AI0001",
  "is_hr": true,
  "profile_completed": true
}
```

**Session:** Creates Django session cookie → Used for subsequent authenticated requests

---

## 🏗️ 5. EXISTING API ARCHITECTURE

### 5.1 Current Pattern
- **NOT using DRF ViewSets** (despite DRF being installed)
- Using **custom function-based views** with `@csrf_exempt` and `@require_http_methods`
- Returns `JsonResponse` directly (not DRF Response)
- Uses custom permission decorators (not DRF permission classes)

### 5.2 Current API Endpoints
```
/api/login/                           POST   - User login
/api/register/                        POST   - User registration (not implemented)
/api/test-auth/                       GET    - Test authentication status
/api/missing-checkouts/               GET    - Get missing checkouts (HR only)
/api/assign-missing-checkouts/        POST   - Assign bulk checkouts (HR only)
/api/teams/                           GET    - List all teams (HR required)
/api/teams/create/                    POST   - Create team (HR only)
/api/teams/<id>/                      GET    - Team details
/api/teams/<id>/update/               PUT    - Update team (HR only)
/api/teams/<id>/delete/               DELETE - Delete team (HR only)
/api/teams/<id>/add-member/           POST   - Add member (HR only)
/api/teams/<id>/remove-member/        POST   - Remove member (HR only)
/api/teams/bulk-add-members/          POST   - Bulk add (HR only)
```

### 5.3 Response Format
All API views use:
```python
from django.http import JsonResponse

return JsonResponse({
    'key': 'value'
}, status=200)
```

**Error Responses:**
```python
return JsonResponse({
    "error": "Error message"
}, status=400/401/403/404/500)
```

---

## 📦 6. EXISTING SERIALIZERS

### 6.1 Available Serializers
**File:** `attendance/api/serializers.py`

```python
- RegisterSerializer (Lines 6-44)
- UserBasicSerializer (Lines 50-59)
- TeamMembershipSerializer (Lines 62-71)
- TeamSerializer (Lines 74-94)
- TeamListSerializer (Lines 97-103)
- BulkMemberAssignmentSerializer (Lines 106-125)
```

### 6.2 Pattern
- Extends `serializers.ModelSerializer` or `serializers.Serializer`
- Uses DRF serialization (not Django's native JSONField)
- Includes validation methods (validate_*)

---

## ✅ 7. RECOMMENDED IMPLEMENTATION PLAN

### 7.1 Files to CREATE

#### **NEW:** `attendance/api/eod_serializers.py`
**Purpose:** Serializers specifically for EOD read-only integration

```python
from rest_framework import serializers
from attendance.models import EmployeeMasterData, Attendance, LeaveRequest, WFHRequest
from django.contrib.auth.models import User

class EODEmployeeSerializer(serializers.ModelSerializer):
    """Read-only serializer for employee master data → EOD"""
    class Meta:
        model = EmployeeMasterData
        fields = ['employee_id', 'first_name', 'last_name', 'department', 'designation']
        read_only_fields = '__all__'

class EODAttendanceSerializer(serializers.Serializer):
    """Read-only serializer for attendance status → EOD"""
    employee_id = serializers.CharField()
    date = serializers.DateField()
    attendance_status = serializers.ChoiceField(
        choices=['PRESENT', 'ABSENT', 'WFH', 'LEAVE']
    )
```

---

#### **NEW:** `attendance/api/eod_views.py`
**Purpose:** Read-only API views for EOD integration

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from datetime import datetime

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def eod_employee_list(request):
    """
    GET /api/eod/employees/
    Returns: List of all active employees
    Auth: Required (any authenticated user)
    """
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def eod_employee_detail(request, employee_id):
    """
    GET /api/eod/employees/<employee_id>/
    Returns: Single employee details
    Auth: Required
    """
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def eod_attendance_list(request):
    """
    GET /api/eod/attendance/?date=YYYY-MM-DD&employee_id=AI0001
    Returns: Attendance records (filtered by date and/or employee_id)
    Auth: Required
    """
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def eod_attendance_status(request, employee_id):
    """
    GET /api/eod/attendance/<employee_id>/?date=YYYY-MM-DD
    Returns: Single employee attendance status for a date
    Auth: Required
    """
    pass
```

---

#### **UPDATE:** `attendance/api/urls.py`
**Add EOD endpoints:**

```python
from .eod_views import (
    eod_employee_list,
    eod_employee_detail,
    eod_attendance_list,
    eod_attendance_status,
)

urlpatterns = [
    # ... existing endpoints ...
    
    # EOD Read-Only Integration
    path('eod/employees/', eod_employee_list, name='eod_employee_list'),
    path('eod/employees/<str:employee_id>/', eod_employee_detail, name='eod_employee_detail'),
    path('eod/attendance/', eod_attendance_list, name='eod_attendance_list'),
    path('eod/attendance/<str:employee_id>/', eod_attendance_status, name='eod_attendance_status'),
]
```

---

### 7.2 Files to MODIFY

#### **UPDATE:** `attendance/api/views.py`
**Add:** Optional EOD-specific authentication decorator (if needed)

```python
def eod_api_key_required(view_func):
    """
    Optional: Add API key authentication for EOD system
    Checks: X-API-Key header matches configured EOD API key
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        api_key = request.META.get('HTTP_X_API_KEY')
        expected_key = os.environ.get('EOD_API_KEY')
        
        if not api_key or api_key != expected_key:
            return JsonResponse({"error": "Invalid API key"}, status=401)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
```

---

#### **UPDATE:** `core/settings.py`
**Add:** EOD API configuration (optional)

```python
# EOD Integration Configuration
EOD_API_ENABLED = os.environ.get('EOD_API_ENABLED', 'False') == 'True'
EOD_API_KEY = os.environ.get('EOD_API_KEY', '')  # Optional API key for EOD system
```

---

#### **UPDATE:** `.env`
**Add:** Environment variables

```env
# EOD Integration
EOD_API_ENABLED=True
EOD_API_KEY=your-secret-eod-api-key-here  # Optional
```

---

### 7.3 Files to CREATE (Testing)

#### **NEW:** `attendance/tests/test_eod_api.py`
**Purpose:** Unit tests for EOD API endpoints

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from attendance.models import EmployeeMasterData, Attendance, LeaveRequest
from datetime import date

class EODAPITestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='test', password='test123')
        self.client = Client()
        self.client.login(username='test', password='test123')
        
        # Create test employee
        self.employee = EmployeeMasterData.objects.create(
            employee_id='TEST001',
            first_name='Test',
            last_name='User',
            department='Engineering',
            designation='Developer',
            email='test@arraafiinfotech.com',
            phone_number='1234567890',
            date_of_birth=date(1990, 1, 1),
            date_of_joining=date(2020, 1, 1),
            gender='male',
            blood_group='O+',
            local_address='Address',
            permanent_address='Address',
            aadhar_number='123456789012',
            pan_number='ABCDE1234F'
        )
    
    def test_employee_list(self):
        response = self.client.get('/attendance/api/eod/employees/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('employees', response.json())
    
    def test_employee_detail(self):
        response = self.client.get(f'/attendance/api/eod/employees/{self.employee.employee_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['employee_id'], 'TEST001')
    
    def test_attendance_list(self):
        response = self.client.get('/attendance/api/eod/attendance/?date=2026-10-01')
        self.assertEqual(response.status_code, 200)
        self.assertIn('attendance', response.json())
    
    def test_readonly_enforcement(self):
        # Test that POST/PUT/DELETE are not allowed
        response = self.client.post('/attendance/api/eod/employees/', {})
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
```

---

## ⚠️ 8. IDENTIFIED RISKS & CONFLICTS

### 8.1 CONFLICTS: None Identified ✅

**Analysis:**
1. ✅ No naming conflicts - Using `eod_*` prefix for all new endpoints
2. ✅ No model changes needed - Using existing models as read-only
3. ✅ No authentication conflicts - Can use existing SessionAuthentication OR add API key
4. ✅ No serializer conflicts - Creating separate `eod_serializers.py`
5. ✅ No URL conflicts - All endpoints under `/api/eod/*` namespace

---

### 8.2 RISKS: Low-Medium

#### Risk 1: Performance (LOW)
**Issue:** Large employee lists or date ranges could cause slow queries

**Mitigation:**
- Add pagination (already configured: `PAGE_SIZE = 100`)
- Add query parameter limits (max 30 days per request)
- Use `select_related()` and `prefetch_related()` for efficient queries
- Add database indexes (already exist on key fields)

#### Risk 2: Data Synchronization (MEDIUM)
**Issue:** EOD might cache data that becomes stale

**Mitigation:**
- Document that SmartPunch is source of truth
- Recommend EOD polls regularly (e.g., every 15 minutes)
- Add `updated_at` timestamp to responses
- Add optional webhook support (future enhancement)

#### Risk 3: Authentication (LOW)
**Issue:** Session authentication might not work well for server-to-server

**Mitigation:**
- Option 1: Use Django session authentication (current system)
- Option 2: Add optional API key authentication for EOD
- Option 3: Add token-based authentication (future)

#### Risk 4: Status Calculation Complexity (MEDIUM)
**Issue:** Determining ABSENT vs PRESENT vs LEAVE vs WFH requires multiple queries

**Mitigation:**
- Create optimized query that checks:
  1. Attendance record
  2. LeaveRequest (status='approved')
  3. WFHRequest (status='approved')
- Cache results for performance
- Document the logic clearly

---

## 📝 9. API ENDPOINT SPECIFICATIONS

### 9.1 GET /api/eod/employees/

**Purpose:** List all active employees (master data)

**Authentication:** Required (session or API key)

**Query Parameters:**
- `page` (optional, integer): Page number for pagination
- `page_size` (optional, integer, max 100): Number of results per page
- `department` (optional, string): Filter by department

**Request:**
```http
GET /attendance/api/eod/employees/?department=Engineering&page=1&page_size=50
Authorization: Session or X-API-Key: <key>
```

**Response (200 OK):**
```json
{
  "count": 150,
  "next": "/api/eod/employees/?page=2",
  "previous": null,
  "employees": [
    {
      "employee_id": "AI0001",
      "first_name": "John",
      "last_name": "Doe",
      "department": "Engineering",
      "designation": "Senior Developer"
    },
    {
      "employee_id": "AI0002",
      "first_name": "Jane",
      "last_name": "Smith",
      "department": "Engineering",
      "designation": "Team Leader"
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Not authorized (if we add role-based access)

---

### 9.2 GET /api/eod/employees/<employee_id>/

**Purpose:** Get single employee details

**Authentication:** Required

**Path Parameters:**
- `employee_id` (required, string): Employee ID (e.g., "AI0001")

**Request:**
```http
GET /attendance/api/eod/employees/AI0001/
Authorization: Session or X-API-Key: <key>
```

**Response (200 OK):**
```json
{
  "employee_id": "AI0001",
  "first_name": "John",
  "last_name": "Doe",
  "department": "Engineering",
  "designation": "Senior Developer"
}
```

**Error Responses:**
- `401 Unauthorized` - Not authenticated
- `404 Not Found` - Employee not found

---

### 9.3 GET /api/eod/attendance/

**Purpose:** List attendance records (filtered)

**Authentication:** Required

**Query Parameters:**
- `date` (optional, YYYY-MM-DD): Filter by specific date
- `start_date` (optional, YYYY-MM-DD): Filter by date range (start)
- `end_date` (optional, YYYY-MM-DD): Filter by date range (end)
- `employee_id` (optional, string): Filter by employee
- `status` (optional, enum): Filter by status (PRESENT, ABSENT, WFH, LEAVE)
- `page` (optional, integer): Page number
- `page_size` (optional, integer, max 100): Results per page

**Constraints:**
- If using `start_date` and `end_date`, maximum 30 days range
- If no date filter, returns last 7 days by default

**Request:**
```http
GET /attendance/api/eod/attendance/?start_date=2026-10-01&end_date=2026-10-07&employee_id=AI0001
Authorization: Session or X-API-Key: <key>
```

**Response (200 OK):**
```json
{
  "count": 7,
  "next": null,
  "previous": null,
  "attendance": [
    {
      "employee_id": "AI0001",
      "date": "2026-10-01",
      "attendance_status": "PRESENT"
    },
    {
      "employee_id": "AI0001",
      "date": "2026-10-02",
      "attendance_status": "WFH"
    },
    {
      "employee_id": "AI0001",
      "date": "2026-10-03",
      "attendance_status": "LEAVE"
    },
    {
      "employee_id": "AI0001",
      "date": "2026-10-04",
      "attendance_status": "ABSENT"
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request` - Invalid query parameters (e.g., date range > 30 days)
- `401 Unauthorized` - Not authenticated

---

### 9.4 GET /api/eod/attendance/<employee_id>/

**Purpose:** Get attendance status for specific employee

**Authentication:** Required

**Path Parameters:**
- `employee_id` (required, string): Employee ID

**Query Parameters:**
- `date` (required, YYYY-MM-DD): Specific date

**Request:**
```http
GET /attendance/api/eod/attendance/AI0001/?date=2026-10-01
Authorization: Session or X-API-Key: <key>
```

**Response (200 OK):**
```json
{
  "employee_id": "AI0001",
  "date": "2026-10-01",
  "attendance_status": "PRESENT"
}
```

**Error Responses:**
- `400 Bad Request` - Missing or invalid date parameter
- `401 Unauthorized` - Not authenticated
- `404 Not Found` - Employee not found

---

## 🔒 10. SECURITY CONSIDERATIONS

### 10.1 Read-Only Enforcement

**Implementation:**
- Only allow GET requests (no POST, PUT, DELETE, PATCH)
- Add `@require_http_methods(['GET'])` decorator to all views
- Return `405 Method Not Allowed` for non-GET requests

### 10.2 Authentication Options

**Option A: Session Authentication (Current System)**
- EOD logs in via `/api/login/`
- Receives session cookie
- Uses cookie for subsequent requests
- **Pros:** Already implemented, no new code
- **Cons:** Requires session management, cookies

**Option B: API Key Authentication (Recommended)**
- Add `X-API-Key` header validation
- Store EOD API key in environment variable
- **Pros:** Simpler for server-to-server, stateless
- **Cons:** Requires additional code

**Recommendation:** Support BOTH (session for testing, API key for production)

### 10.3 Rate Limiting

**Recommendation:** Add rate limiting to prevent abuse

**Implementation:**
```python
from django.core.cache import cache
from django.utils import timezone

def rate_limit(max_requests=100, window_seconds=3600):
    """Rate limit decorator: max_requests per window_seconds"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Use API key or user ID as rate limit key
            key = f"rate_limit:{request.user.id}"
            
            # Get current request count
            count = cache.get(key, 0)
            
            if count >= max_requests:
                return JsonResponse({
                    "error": "Rate limit exceeded"
                }, status=429)
            
            # Increment counter
            cache.set(key, count + 1, window_seconds)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

---

## 📚 11. DOCUMENTATION TO CREATE

### 11.1 API Documentation (Markdown)

**NEW:** `docs/EOD_API_INTEGRATION_GUIDE.md`

Contents:
- Authentication methods
- Endpoint specifications
- Request/response examples
- Error handling
- Rate limits
- Best practices
- Troubleshooting

### 11.2 Code Documentation

Add docstrings to all new views:
```python
def eod_employee_list(request):
    """
    EOD Integration: Get list of all active employees.
    
    **Endpoint:** GET /api/eod/employees/
    
    **Authentication:** Required (Session or API Key)
    
    **Query Parameters:**
    - page (int, optional): Page number for pagination
    - page_size (int, optional, max 100): Number of results per page
    - department (str, optional): Filter by department
    
    **Returns:**
    - 200: JSON with paginated employee list
    - 401: Unauthorized
    
    **Example:**
        GET /api/eod/employees/?department=Engineering&page=1
        
        Response:
        {
            "count": 150,
            "employees": [...]
        }
    """
```

---

## ✅ 12. APPROVAL CHECKLIST

Before proceeding with implementation:

- [ ] **Confirm endpoint structure** - Are the 4 proposed endpoints sufficient?
- [ ] **Authentication method** - Session only, API Key only, or both?
- [ ] **Rate limiting** - What limits? (Suggested: 100 requests/hour)
- [ ] **Pagination** - Default page size? (Current: 100)
- [ ] **Date range limits** - Max days per query? (Suggested: 30 days)
- [ ] **Error handling** - Error format acceptable?
- [ ] **Documentation** - What format for EOD team? (Markdown, Swagger, Postman?)
- [ ] **Testing** - Run tests before deploying?
- [ ] **Deployment** - Staging environment first?

---

## 🎯 13. IMPLEMENTATION CHECKLIST

Once approved, I will:

### Phase 1: Core Implementation
- [ ] Create `attendance/api/eod_serializers.py`
- [ ] Create `attendance/api/eod_views.py`
- [ ] Update `attendance/api/urls.py`
- [ ] Update `.env.example` with EOD configuration

### Phase 2: Authentication
- [ ] Implement API key authentication decorator (if approved)
- [ ] Update `core/settings.py` with EOD config

### Phase 3: Testing
- [ ] Create `attendance/tests/test_eod_api.py`
- [ ] Write unit tests for all 4 endpoints
- [ ] Test authentication (session and API key)
- [ ] Test pagination
- [ ] Test error handling
- [ ] Test rate limiting (if implemented)

### Phase 4: Documentation
- [ ] Create `docs/EOD_API_INTEGRATION_GUIDE.md`
- [ ] Add inline code documentation
- [ ] Create API usage examples

### Phase 5: Validation
- [ ] Run Django migrations (if any model changes)
- [ ] Run all tests: `python manage.py test attendance.tests.test_eod_api`
- [ ] Manual testing with Postman/cURL
- [ ] Security audit
- [ ] Performance testing

---

## 📊 14. ESTIMATED IMPACT

### Code Changes:
- **New Files:** 3 (eod_serializers.py, eod_views.py, test_eod_api.py)
- **Modified Files:** 3 (api/urls.py, settings.py, .env)
- **Documentation:** 2 files

### Lines of Code:
- **New Code:** ~400-500 lines
- **Modified Code:** ~50 lines
- **Tests:** ~200 lines

### Database Impact:
- **No migrations needed** ✅
- **No schema changes** ✅
- **Read-only operations** ✅

### Performance Impact:
- **Low** - All queries use existing indexes
- **Pagination** prevents large result sets
- **No write operations** means no locks

---

## 🔗 15. EXISTING DATABASE RELATIONSHIPS

### User → EmployeeProfile (1:1)
```
User.id → EmployeeProfile.user_id
```

### EmployeeMasterData → User (1:1 optional)
```
EmployeeMasterData.linked_user_id → User.id
```

### User → Attendance (1:Many)
```
User.id → Attendance.employee_id
```

### User → LeaveRequest (1:Many)
```
User.id → LeaveRequest.employee_id
```

### User → WFHRequest (1:Many)
```
User.id → WFHRequest.employee_id
```

### Query Strategy:
For attendance status calculation, we need:
1. **Attendance record** - Check if exists for date
2. **LeaveRequest** - Check if approved for date
3. **WFHRequest** - Check if approved for date

**Optimized Query:**
```python
from django.db.models import Q, Exists, OuterRef

# Get attendance with leave/WFH status in single query
attendance_with_status = Attendance.objects.filter(
    date=target_date
).annotate(
    has_approved_leave=Exists(
        LeaveRequest.objects.filter(
            employee=OuterRef('employee'),
            status='approved',
            start_date__lte=target_date,
            end_date__gte=target_date
        )
    ),
    has_approved_wfh=Exists(
        WFHRequest.objects.filter(
            employee=OuterRef('employee'),
            status='approved',
            start_date__lte=target_date,
            end_date__gte=target_date
        )
    )
).select_related('employee__employeeprofile')
```

---

## 📞 16. NEXT STEPS - AWAITING YOUR APPROVAL

Please review this analysis and provide approval or feedback on:

1. **Endpoint Structure** - Are the 4 proposed endpoints correct?
   - GET /api/eod/employees/
   - GET /api/eod/employees/<employee_id>/
   - GET /api/eod/attendance/
   - GET /api/eod/attendance/<employee_id>/

2. **Authentication** - Which method(s)?
   - [ ] Session Authentication only
   - [ ] API Key Authentication only
   - [ ] Both (recommended)

3. **Rate Limiting** - What limits?
   - Suggested: 100 requests/hour per API key

4. **Date Range Limits** - Max days per query?
   - Suggested: 30 days maximum

5. **Pagination** - Page size?
   - Current default: 100
   - Suggested: Keep at 100

6. **Documentation Format** - What does EOD team prefer?
   - [ ] Markdown (in repo)
   - [ ] Swagger/OpenAPI
   - [ ] Postman Collection
   - [ ] All of the above

7. **Testing** - Run on staging first?
   - [ ] Yes (recommended)
   - [ ] Deploy directly to production

Once you approve, I will proceed with implementation immediately.

---

## 📝 APPENDIX A: Status Calculation Pseudocode

```python
def get_eod_attendance_status(employee_id, date):
    """
    Calculate EOD attendance status for employee on date
    Returns: 'PRESENT', 'ABSENT', 'WFH', or 'LEAVE'
    """
    
    # Check for approved leave
    has_leave = LeaveRequest.objects.filter(
        employee__employeeprofile__employee_id=employee_id,
        status='approved',
        start_date__lte=date,
        end_date__gte=date
    ).exists()
    
    if has_leave:
        return 'LEAVE'
    
    # Check for approved WFH
    has_wfh = WFHRequest.objects.filter(
        employee__employeeprofile__employee_id=employee_id,
        status='approved',
        start_date__lte=date,
        end_date__gte=date
    ).exists()
    
    if has_wfh:
        return 'WFH'
    
    # Check attendance record
    attendance = Attendance.objects.filter(
        employee__employeeprofile__employee_id=employee_id,
        date=date
    ).first()
    
    if attendance:
        # Has attendance record (checked in)
        # Normalize: 'present', 'late', 'half-day' all map to PRESENT
        return 'PRESENT'
    else:
        # No attendance record, no leave, no WFH
        return 'ABSENT'
```

---

## 📝 APPENDIX B: Example cURL Commands

### Login (Session Auth)
```bash
curl -X POST http://localhost:8000/attendance/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"identifier": "AI0001", "password": "password123"}' \
  -c cookies.txt
```

### Get Employees (Session Auth)
```bash
curl -X GET http://localhost:8000/attendance/api/eod/employees/ \
  -b cookies.txt
```

### Get Employees (API Key Auth)
```bash
curl -X GET http://localhost:8000/attendance/api/eod/employees/ \
  -H "X-API-Key: your-eod-api-key-here"
```

### Get Attendance by Date
```bash
curl -X GET "http://localhost:8000/attendance/api/eod/attendance/?date=2026-10-01" \
  -H "X-API-Key: your-eod-api-key-here"
```

### Get Attendance by Date Range
```bash
curl -X GET "http://localhost:8000/attendance/api/eod/attendance/?start_date=2026-10-01&end_date=2026-10-07" \
  -H "X-API-Key: your-eod-api-key-here"
```

### Get Single Employee Attendance
```bash
curl -X GET "http://localhost:8000/attendance/api/eod/attendance/AI0001/?date=2026-10-01" \
  -H "X-API-Key: your-eod-api-key-here"
```

---

**END OF ANALYSIS DOCUMENT**

*No code has been modified yet. Awaiting your approval to proceed with implementation.*
