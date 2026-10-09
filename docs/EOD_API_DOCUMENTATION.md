# EOD API Documentation
## SmartPunch → EOD Integration (Phase 1)

**Version:** 1.0  
**Date:** October 1, 2026  
**Status:** Phase 1 - Read-Only API

---

## Overview

This API provides read-only access to SmartPunch employee and attendance data for the EOD (End of Day) system.

**Key Points:**
- ✅ SmartPunch is the **source of truth**
- ✅ EOD receives **final attendance status only**
- ✅ No check-in/check-out/work-hour data exposed
- ✅ API key authentication required
- ✅ Read-only (GET requests only)
- ✅ No database writes possible

---

## Base URL

```
Production: https://your-smartpunch-server.com/attendance/api/eod/
Development: http://localhost:8000/attendance/api/eod/
```

---

## Authentication

### API Key Authentication

All requests must include an API key in the header:

```http
X-API-Key: your-secret-api-key
```

### Obtaining an API Key

Contact SmartPunch administrator to receive your unique API key.

**Security Notes:**
- Never share your API key
- Never commit API key to source code
- Store securely in environment variables
- Rotate key periodically

### Error Response (No/Invalid API Key)

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "error": "Unauthorized"
}
```

---

## Endpoints

### 1. Get Employee List

Retrieves list of all active employees with basic information.

**Endpoint:** `GET /employees/`

**Authentication:** Required

**Request:**
```http
GET /attendance/api/eod/employees/ HTTP/1.1
Host: your-smartpunch-server.com
X-API-Key: your-secret-api-key
```

**Response (Success):**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "employees": [
    {
      "employee_id": "AI0001",
      "first_name": "John",
      "last_name": "Doe",
      "department": "Engineering",
      "designation": "Software Developer"
    },
    {
      "employee_id": "AI0002",
      "first_name": "Jane",
      "last_name": "Smith",
      "department": "Marketing",
      "designation": "Manager"
    }
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `employee_id` | string | Unique employee identifier |
| `first_name` | string | Employee first name |
| `last_name` | string | Employee last name |
| `department` | string | Department name |
| `designation` | string | Job title |

**Sensitive Data NOT Exposed:**
- Aadhaar number
- PAN number
- Email address
- Phone number
- Home address
- Date of birth
- Gender
- Blood group
- Bank account details
- Salary information
- Profile photo

**Error Responses:**

| Status Code | Description |
|-------------|-------------|
| 401 | Missing or invalid API key |
| 405 | Method not allowed (POST/PUT/DELETE) |

---

### 2. Get Daily Attendance Status

Retrieves final attendance status for all employees on a specific date.

**Endpoint:** `GET /attendance/?date=YYYY-MM-DD`

**Authentication:** Required

**Query Parameters:**

| Parameter | Required | Type | Format | Description |
|-----------|----------|------|--------|-------------|
| `date` | Yes | string | YYYY-MM-DD | Date to query (e.g., 2026-10-01) |

**Request:**
```http
GET /attendance/api/eod/attendance/?date=2026-10-01 HTTP/1.1
Host: your-smartpunch-server.com
X-API-Key: your-secret-api-key
```

**Response (Success):**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "date": "2026-10-01",
  "attendance": [
    {
      "employee_id": "AI0001",
      "status": "PRESENT"
    },
    {
      "employee_id": "AI0002",
      "status": "WFH"
    },
    {
      "employee_id": "AI0003",
      "status": "LEAVE"
    },
    {
      "employee_id": "AI0004",
      "status": "ABSENT"
    }
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `date` | string | Date queried (YYYY-MM-DD) |
| `attendance` | array | List of employee attendance records |
| `attendance[].employee_id` | string | Employee identifier |
| `attendance[].status` | enum | Final attendance status |

**Status Values:**

| Status | Description |
|--------|-------------|
| `PRESENT` | Employee was present (includes late arrivals and half-days) |
| `ABSENT` | Employee was absent (no check-in, no leave, no WFH) |
| `WFH` | Employee had approved work-from-home request |
| `LEAVE` | Employee had approved leave request |

**Data NOT Exposed:**
- Check-in time
- Check-out time
- Total work hours
- Break duration
- Overtime hours
- Attendance calculation rules

---

## Status Determination Logic

SmartPunch determines the final attendance status using this priority order:

```
1. LEAVE (highest priority)
   ↓
2. WFH
   ↓
3. PRESENT/ABSENT (from attendance record)
   ↓
4. ABSENT (default if no record exists)
```

### Status Mapping Examples

| SmartPunch Internal Status | EOD Status Returned |
|----------------------------|---------------------|
| Checked in on time | PRESENT |
| Checked in late (after 10 AM) | PRESENT |
| Half-day attendance | PRESENT |
| Marked absent in system | ABSENT |
| Approved sick leave | LEAVE |
| Approved casual leave | LEAVE |
| Approved earned leave | LEAVE |
| Approved work-from-home | WFH |
| No check-in + no leave + no WFH | ABSENT |

### Priority Examples

**Example 1:** Employee has approved leave AND attendance record
- **Result:** `LEAVE` (leave takes priority)

**Example 2:** Employee has approved WFH AND attendance record
- **Result:** `WFH` (WFH takes priority)

**Example 3:** Employee has both leave and WFH approved (edge case)
- **Result:** `LEAVE` (leave takes highest priority)

**Example 4:** Employee checked in late
- **Result:** `PRESENT` (normalized from 'late' status)

**Example 5:** Employee worked half-day
- **Result:** `PRESENT` (normalized from 'half-day' status)

---

## Error Handling

### Error Response Format

```json
{
  "error": "Error message description"
}
```

### Common Errors

#### 1. Missing Date Parameter
```http
GET /attendance/api/eod/attendance/

HTTP/1.1 400 Bad Request
{
  "error": "date parameter is required"
}
```

#### 2. Invalid Date Format
```http
GET /attendance/api/eod/attendance/?date=01-10-2026

HTTP/1.1 400 Bad Request
{
  "error": "Invalid date format. Use YYYY-MM-DD."
}
```

#### 3. Missing API Key
```http
GET /attendance/api/eod/employees/

HTTP/1.1 401 Unauthorized
{
  "error": "Unauthorized"
}
```

#### 4. Invalid API Key
```http
GET /attendance/api/eod/employees/
X-API-Key: wrong-key

HTTP/1.1 401 Unauthorized
{
  "error": "Unauthorized"
}
```

#### 5. Method Not Allowed
```http
POST /attendance/api/eod/employees/

HTTP/1.1 405 Method Not Allowed
{
  "error": "Method not allowed"
}
```

---

## HTTP Status Codes

| Status Code | Meaning | When It Occurs |
|-------------|---------|----------------|
| 200 | OK | Successful request |
| 400 | Bad Request | Missing or invalid date parameter |
| 401 | Unauthorized | Missing or invalid API key |
| 405 | Method Not Allowed | Used POST/PUT/DELETE instead of GET |
| 500 | Internal Server Error | Unexpected server error (rare) |

---

## Code Examples

### Python (requests library)

```python
import requests

API_KEY = "your-secret-api-key"
BASE_URL = "https://your-smartpunch-server.com/attendance/api/eod"

headers = {
    "X-API-Key": API_KEY
}

# Get employee list
response = requests.get(f"{BASE_URL}/employees/", headers=headers)
if response.status_code == 200:
    employees = response.json()["employees"]
    print(f"Found {len(employees)} employees")
else:
    print(f"Error: {response.status_code} - {response.json()}")

# Get attendance for specific date
date = "2026-10-01"
response = requests.get(f"{BASE_URL}/attendance/", params={"date": date}, headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"Attendance for {data['date']}:")
    for record in data["attendance"]:
        print(f"  {record['employee_id']}: {record['status']}")
else:
    print(f"Error: {response.status_code} - {response.json()}")
```

### cURL

```bash
# Get employee list
curl -X GET "https://your-smartpunch-server.com/attendance/api/eod/employees/" \
  -H "X-API-Key: your-secret-api-key"

# Get attendance for specific date
curl -X GET "https://your-smartpunch-server.com/attendance/api/eod/attendance/?date=2026-10-01" \
  -H "X-API-Key: your-secret-api-key"
```

### JavaScript (fetch)

```javascript
const API_KEY = "your-secret-api-key";
const BASE_URL = "https://your-smartpunch-server.com/attendance/api/eod";

const headers = {
  "X-API-Key": API_KEY
};

// Get employee list
fetch(`${BASE_URL}/employees/`, { headers })
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.employees.length} employees`);
  })
  .catch(error => console.error("Error:", error));

// Get attendance for specific date
const date = "2026-10-01";
fetch(`${BASE_URL}/attendance/?date=${date}`, { headers })
  .then(response => response.json())
  .then(data => {
    console.log(`Attendance for ${data.date}:`);
    data.attendance.forEach(record => {
      console.log(`  ${record.employee_id}: ${record.status}`);
    });
  })
  .catch(error => console.error("Error:", error));
```

---

## Best Practices

### 1. Error Handling
Always check HTTP status codes before processing response data:

```python
if response.status_code == 200:
    # Success - process data
    data = response.json()
else:
    # Error - log and handle
    error = response.json().get("error", "Unknown error")
    logger.error(f"API error: {error}")
```

### 2. Date Format
Always use ISO 8601 format (YYYY-MM-DD):

```python
from datetime import date

# Correct
today = date.today().isoformat()  # "2026-10-01"

# Incorrect
today = date.today().strftime("%d-%m-%Y")  # Don't use DD-MM-YYYY
```

### 3. API Key Security
Never hard-code API keys:

```python
# Good ✅
import os
API_KEY = os.environ.get("EOD_API_KEY")

# Bad ❌
API_KEY = "abc123xyz"  # Never do this!
```

### 4. Caching
Cache employee list to reduce API calls:

```python
import time

class SmartPunchAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.employees_cache = None
        self.cache_timestamp = None
        self.cache_ttl = 3600  # 1 hour
    
    def get_employees(self):
        now = time.time()
        if self.employees_cache and (now - self.cache_timestamp) < self.cache_ttl:
            return self.employees_cache
        
        # Fetch from API
        response = requests.get(f"{BASE_URL}/employees/", headers={"X-API-Key": self.api_key})
        self.employees_cache = response.json()["employees"]
        self.cache_timestamp = now
        return self.employees_cache
```

### 5. Rate Limiting (Recommendation)
Implement exponential backoff for retries:

```python
import time

def fetch_with_retry(url, headers, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:  # Rate limit
            wait_time = 2 ** attempt  # Exponential backoff
            time.sleep(wait_time)
        else:
            raise Exception(f"API error: {response.status_code}")
    
    raise Exception("Max retries exceeded")
```

---

## Integration Checklist

Before going live with EOD integration:

- [ ] Obtained API key from SmartPunch administrator
- [ ] Stored API key securely in environment variable
- [ ] Tested employee endpoint successfully
- [ ] Tested attendance endpoint successfully
- [ ] Verified error handling (401, 400, 405)
- [ ] Implemented proper date formatting (YYYY-MM-DD)
- [ ] Implemented API key security (no hard-coding)
- [ ] Tested with missing/invalid date parameter
- [ ] Tested with missing/invalid API key
- [ ] Verified all 4 status values handled (PRESENT, ABSENT, WFH, LEAVE)
- [ ] Implemented caching for employee list
- [ ] Implemented error logging
- [ ] Implemented retry logic
- [ ] Documented integration in EOD codebase
- [ ] Scheduled regular data sync (e.g., every 15 minutes)

---

## Troubleshooting

### Issue: 401 Unauthorized

**Possible Causes:**
1. API key is missing from request
2. API key is incorrect
3. API key environment variable not set

**Solution:**
```bash
# Verify API key is set
echo $EOD_API_KEY

# Test with cURL
curl -v -H "X-API-Key: your-actual-key" \
  https://your-smartpunch-server.com/attendance/api/eod/employees/
```

### Issue: 400 Bad Request (Invalid date format)

**Possible Causes:**
1. Date format is not YYYY-MM-DD
2. Date parameter is missing

**Solution:**
```python
# Use ISO format
from datetime import date
correct_date = date(2026, 10, 1).isoformat()  # "2026-10-01"
```

### Issue: Empty attendance list

**Possible Causes:**
1. No employees in SmartPunch system
2. Date is in the future
3. All employees filtered out

**Solution:**
- Verify employees exist in SmartPunch
- Use past dates only (today or earlier)
- Check SmartPunch database for employee account_created flag

---

## Limitations (Phase 1)

Current limitations that may be addressed in future phases:

1. **No pagination** - Returns all employees/attendance in single response
2. **No date range queries** - Must query one date at a time
3. **No filtering** - Cannot filter by department or status
4. **No individual employee endpoint** - Must fetch all employees
5. **No rate limiting** - Implement your own throttling
6. **No webhooks** - Must poll for changes
7. **No bulk queries** - Cannot query multiple dates in one request

---

## Support

For API issues or questions:

1. **Technical Issues:** Contact SmartPunch technical support
2. **API Key Issues:** Contact SmartPunch administrator
3. **Integration Questions:** Refer to this documentation
4. **Bug Reports:** Report to SmartPunch development team

---

## Changelog

### Version 1.0 (October 1, 2026)
- Initial release
- Employee list endpoint
- Daily attendance status endpoint
- API key authentication
- Read-only access

---

## Appendix A: Complete Field List

### Employee Fields (Exposed to EOD)

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `employee_id` | string | "AI0001" | Unique identifier |
| `first_name` | string | "John" | First name |
| `last_name` | string | "Doe" | Last name |
| `department` | string | "Engineering" | Department name |
| `designation` | string | "Developer" | Job title |

### Employee Fields (NOT Exposed)

| Field | Reason Not Exposed |
|-------|-------------------|
| `middle_name` | Not required by EOD |
| `email` | Sensitive PII |
| `phone_number` | Sensitive PII |
| `alternate_phone` | Sensitive PII |
| `date_of_birth` | Sensitive PII |
| `gender` | Sensitive PII |
| `blood_group` | Sensitive medical data |
| `local_address` | Sensitive PII |
| `permanent_address` | Sensitive PII |
| `aadhar_number` | Sensitive government ID |
| `pan_number` | Sensitive government ID |
| `bank_account_number` | Sensitive financial data |
| `bank_ifsc_code` | Sensitive financial data |
| `base_salary` | Sensitive financial data |
| `ot_rate` | Sensitive financial data |
| `work_mode` | Internal SmartPunch data |
| `profile_photo` | Not required by EOD |

### Attendance Fields (Exposed to EOD)

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `employee_id` | string | "AI0001" | Employee identifier |
| `status` | enum | "PRESENT" | Final attendance status |

### Attendance Fields (NOT Exposed)

| Field | Reason Not Exposed |
|-------|-------------------|
| `check_in` | Internal SmartPunch data |
| `check_out` | Internal SmartPunch data |
| `total_work_hours` | Internal SmartPunch calculation |
| `break_start` | Internal SmartPunch data |
| `break_end` | Internal SmartPunch data |
| `break_duration` | Internal SmartPunch calculation |
| `overtime_hours` | Internal SmartPunch calculation |
| `late_arrival` | Normalized to PRESENT |
| `half_day` | Normalized to PRESENT |

---

**End of Documentation**

*For the latest version of this documentation, contact SmartPunch administrator.*
