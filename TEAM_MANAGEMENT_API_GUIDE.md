# Team Management API Guide

## 🎯 Overview
Complete API documentation for SmartPunch Team Management features (Phase 1 - Sprint 1).

**Base URL:** `/api/`  
**Authentication:** Session-based (Django authentication)  
**Authorization:** Role-based (HR/Admin, Team Leader, Employee)

---

## 🔐 Permission Levels

| Role | Create Teams | Edit Teams | Delete Teams | Add/Remove Members | View All Teams | View Own Teams | Comment on Requests |
|------|--------------|------------|--------------|-------------------|----------------|----------------|---------------------|
| **HR/Admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Manager** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Team Leader** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Employee** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 📚 API Endpoints

### 1. List All Teams
**Endpoint:** `GET /api/teams/`  
**Permission:** HR/Admin only  
**Description:** Returns list of all active teams

**Response (200 OK):**
```json
{
  "teams": [
    {
      "id": 1,
      "name": "Frontend Team",
      "department": "Engineering",
      "team_leader": 5,
      "team_leader_name": "John Doe",
      "member_count": 8,
      "is_active": true
    }
  ],
  "count": 1
}
```

**Error Responses:**
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not HR/Admin

---

### 2. Get Team Details
**Endpoint:** `GET /api/teams/<team_id>/`  
**Permission:** HR/Admin (all teams), Team Leader (own teams only)  
**Description:** Get detailed team information including members

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Frontend Team",
  "department": "Engineering",
  "team_leader": 5,
  "team_leader_details": {
    "id": 5,
    "username": "john.doe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@arraafiinfotech.com",
    "employee_id": "EMP001",
    "department": "Engineering",
    "designation": "Senior Developer"
  },
  "description": "Responsible for React and Angular projects",
  "is_active": true,
  "created_at": "2026-08-07T10:00:00Z",
  "updated_at": "2026-08-07T10:00:00Z",
  "created_by": 2,
  "created_by_name": "Admin User",
  "member_count": 8,
  "members": [
    {
      "id": 10,
      "employee": {
        "id": 15,
        "username": "jane.smith",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@arraafiinfotech.com",
        "employee_id": "EMP015",
        "department": "Engineering",
        "designation": "Frontend Developer"
      },
      "is_active": true,
      "added_at": "2026-08-07T11:00:00Z",
      "added_by": 2,
      "added_by_name": "Admin User",
      "removed_at": null
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Team Leader trying to view other team
- `404 Not Found` - Team doesn't exist

---

### 3. Create Team
**Endpoint:** `POST /api/teams/create/`  
**Permission:** HR/Admin only  
**Description:** Create a new team

**Request Body:**
```json
{
  "name": "Backend Team",
  "department": "Engineering",
  "team_leader": 7,
  "description": "Node.js and Python projects"
}
```

**Response (201 Created):**
```json
{
  "message": "Team created successfully",
  "team": {
    "id": 2,
    "name": "Backend Team",
    "department": "Engineering",
    "team_leader": 7,
    "team_leader_details": { ... },
    "description": "Node.js and Python projects",
    "is_active": true,
    "created_at": "2026-08-07T12:00:00Z",
    "created_by": 2,
    "member_count": 0,
    "members": []
  }
}
```

**Error Responses:**
- `400 Bad Request` - Invalid data or duplicate team name
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not HR/Admin

---

### 4. Update Team
**Endpoint:** `PUT /api/teams/<team_id>/update/` or `PATCH /api/teams/<team_id>/update/`  
**Permission:** HR/Admin only  
**Description:** Update team details (partial updates supported with PATCH)

**Request Body:**
```json
{
  "name": "Frontend & Mobile Team",
  "description": "Updated description"
}
```

**Response (200 OK):**
```json
{
  "message": "Team updated successfully",
  "team": { ... }
}
```

**Error Responses:**
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not HR/Admin
- `404 Not Found` - Team doesn't exist

---

### 5. Delete Team (Soft Delete)
**Endpoint:** `DELETE /api/teams/<team_id>/delete/`  
**Permission:** HR/Admin only  
**Description:** Deactivate team and all memberships (soft delete)

**Response (200 OK):**
```json
{
  "message": "Team deactivated successfully"
}
```

**Error Responses:**
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not HR/Admin
- `404 Not Found` - Team doesn't exist

---

### 6. Add Member to Team
**Endpoint:** `POST /api/teams/<team_id>/add-member/`  
**Permission:** HR/Admin only  
**Description:** Add a single employee to team

**Request Body:**
```json
{
  "employee_id": 15
}
```

**Response (201 Created):**
```json
{
  "message": "User added to team",
  "membership_id": 25
}
```

**Error Responses:**
- `400 Bad Request` - Invalid employee_id or already member
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not HR/Admin
- `404 Not Found` - Team or employee doesn't exist

---

### 7. Remove Member from Team
**Endpoint:** `POST /api/teams/<team_id>/remove-member/`  
**Permission:** HR/Admin only  
**Description:** Remove an employee from team (soft delete)

**Request Body:**
```json
{
  "employee_id": 15
}
```

**Response (200 OK):**
```json
{
  "message": "User removed from team"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid employee_id or not a member
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not HR/Admin
- `404 Not Found` - Team or employee doesn't exist

---

### 8. Bulk Add Members to Team
**Endpoint:** `POST /api/teams/bulk-add-members/`  
**Permission:** HR/Admin only  
**Description:** Add multiple employees to a team in one request

**Request Body:**
```json
{
  "team_id": 1,
  "employee_ids": [15, 20, 25, 30, 35]
}
```

**Response (200 OK):**
```json
{
  "message": "Bulk operation completed",
  "added_count": 4,
  "skipped_count": 1,
  "error_count": 0,
  "added": [
    {
      "employee_id": 15,
      "name": "Jane Smith"
    },
    {
      "employee_id": 20,
      "name": "Bob Johnson"
    }
  ],
  "skipped": [
    {
      "employee_id": 25,
      "name": "Alice Brown",
      "reason": "User is already a member of this team"
    }
  ],
  "errors": []
}
```

**Error Responses:**
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not HR/Admin
- `404 Not Found` - Team doesn't exist

---

### 9. Get My Teams (Team Leader)
**Endpoint:** `GET /api/teams/my-teams/`  
**Permission:** Team Leader, HR, Admin  
**Description:** Get all teams where logged-in user is the team leader

**Response (200 OK):**
```json
{
  "teams": [
    {
      "id": 1,
      "name": "Frontend Team",
      "department": "Engineering",
      "team_leader": 5,
      "team_leader_details": { ... },
      "description": "...",
      "is_active": true,
      "member_count": 8,
      "members": [ ... ]
    }
  ],
  "count": 1
}
```

**Error Responses:**
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not Team Leader/HR/Admin

---

### 10. Get Team Members
**Endpoint:** `GET /api/teams/<team_id>/members/`  
**Permission:** Any authenticated user  
**Description:** Get all active members of a specific team

**Response (200 OK):**
```json
{
  "team_name": "Frontend Team",
  "members": [
    {
      "id": 15,
      "username": "jane.smith",
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane.smith@arraafiinfotech.com",
      "employee_id": "EMP015",
      "department": "Engineering",
      "designation": "Frontend Developer"
    }
  ],
  "count": 8
}
```

**Error Responses:**
- `401 Unauthorized` - Not logged in
- `404 Not Found` - Team doesn't exist

---

## 🧪 Testing with cURL

### Test Authentication Status
```bash
curl -X GET http://localhost:8000/api/test-auth/ \
  --cookie "sessionid=YOUR_SESSION_ID"
```

### Create a Team
```bash
curl -X POST http://localhost:8000/api/teams/create/ \
  -H "Content-Type: application/json" \
  --cookie "sessionid=YOUR_SESSION_ID" \
  -d '{
    "name": "DevOps Team",
    "department": "Operations",
    "team_leader": 8,
    "description": "CI/CD and Infrastructure"
  }'
```

### List All Teams
```bash
curl -X GET http://localhost:8000/api/teams/ \
  --cookie "sessionid=YOUR_SESSION_ID"
```

### Add Member to Team
```bash
curl -X POST http://localhost:8000/api/teams/1/add-member/ \
  -H "Content-Type: application/json" \
  --cookie "sessionid=YOUR_SESSION_ID" \
  -d '{"employee_id": 15}'
```

### Bulk Add Members
```bash
curl -X POST http://localhost:8000/api/teams/bulk-add-members/ \
  -H "Content-Type: application/json" \
  --cookie "sessionid=YOUR_SESSION_ID" \
  -d '{
    "team_id": 1,
    "employee_ids": [15, 20, 25, 30]
  }'
```

---

## 🔍 Django Admin Access

Team Management models are available in Django Admin:

1. Navigate to: `http://localhost:8000/admin/`
2. Login with superuser credentials
3. Access:
   - **Attendance → Teams** - Manage teams
   - **Attendance → Team Memberships** - Manage memberships

**Features:**
- Filter by department, active status, created date
- Search by team name, leader, department
- Inline member editing
- Auto-set `created_by` and `added_by` fields
- Readonly audit fields

---

## 📊 Database Schema

### Team Table
```sql
- id (BigInt, PK)
- name (VARCHAR(100), UNIQUE, INDEXED)
- department (VARCHAR(100), INDEXED)
- team_leader_id (BigInt, FK → auth_user, NULLABLE)
- description (TEXT, NULLABLE)
- is_active (BOOLEAN, INDEXED, DEFAULT TRUE)
- created_at (DATETIME)
- updated_at (DATETIME)
- created_by_id (BigInt, FK → auth_user, NULLABLE)

INDEXES:
- (department, is_active)
- (team_leader_id, is_active)
```

### TeamMembership Table
```sql
- id (BigInt, PK)
- team_id (BigInt, FK → attendance_team, CASCADE)
- employee_id (BigInt, FK → auth_user, CASCADE)
- is_active (BOOLEAN, INDEXED, DEFAULT TRUE)
- added_at (DATETIME)
- added_by_id (BigInt, FK → auth_user, NULLABLE)
- removed_at (DATETIME, NULLABLE)

INDEXES:
- (team_id, employee_id, is_active)
- (employee_id, is_active)
```

### EmployeeProfile Extensions
```sql
- is_team_leader (BOOLEAN, INDEXED, DEFAULT FALSE)
  # Auto-set when user becomes team leader
```

---

## ✅ Tasks Completed

- ✅ **TEAM-001** - Team Model Created
- ✅ **TEAM-002** - TeamMembership Model Created
- ✅ **TEAM-003** - Database Migration Applied
- ✅ **TEAM-004** - Django Admin Interface Registered
- ✅ **TEAM-005** - Team CRUD API Endpoints (Create, Read, Update, Delete)
- ✅ **TEAM-006** - Team Member Assignment API (Single + Bulk)
- ✅ **TEAM-007** - Role-Based Permission Checks (Decorators)
- ✅ **TEAM-008** - EmployeeProfile Extended with is_team_leader
- ✅ **TEAM-009** - Team Leader Assignment Logic (Auto-flag management)
- ✅ **TEAM-010** - Team List API
- ✅ **TEAM-011** - Team Detail API
- ✅ **TEAM-019** - Request Models Updated (tl_comment fields)

---

## 🚀 Next Steps

**Frontend Implementation (TEAM-012 to TEAM-024):**
- TEAM-012: Create HR Team Management Page
- TEAM-013: Create Team Member Search UI
- TEAM-014: Create Bulk Member Assignment UI
- TEAM-015: Create Team Leader Dashboard
- TEAM-016: Create Team Pending Requests View
- TEAM-017: Create Team Member List View
- TEAM-018: Add Comment Functionality for Team Leaders

**Testing (TEAM-025 to TEAM-027):**
- TEAM-025: Create Team Management Tests
- TEAM-026: Create Team Leader Permission Tests
- TEAM-027: Create Integration Tests

**Additional Features (TEAM-028 to TEAM-030):**
- TEAM-028: Update Notification Model
- TEAM-029: Create Audit Logs for Team Changes ✅ (Already implemented)
- TEAM-030: Add Team Validation Rules ✅ (Already implemented)

---

## 🐛 Error Handling

All API endpoints follow consistent error response format:

```json
{
  "error": "Error message here"
}
```

**Common HTTP Status Codes:**
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Not authorized (insufficient permissions)
- `404 Not Found` - Resource doesn't exist

---

## 💡 Best Practices

1. **Always check authentication first** - Use `@hr_required` decorator
2. **Use soft deletes** - Set `is_active=False` instead of deleting
3. **Audit logging** - All create/update/delete operations are logged
4. **Validation** - Serializers handle all input validation
5. **Permissions** - Role-based access control enforced at API level
6. **Query optimization** - Use `select_related()` and `prefetch_related()`

---

**Version:** 1.0  
**Last Updated:** August 7, 2026  
**Author:** SmartPunch Development Team
