# SmartPunch 2.0 - Software Requirements Specification (SRS)

**Version:** 2.0  
**Date:** December 3, 2024  
**Product Name:** SmartPunch - Workplace Companion  
**Organization:** Arraafi Technologies  

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 3, 2024 | Development Team | Initial SRS for SmartPunch 2.0 |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Product Vision](#2-product-vision)
3. [Implementation Phases](#3-implementation-phases)
4. [Phase 1: Web Application Enhancements](#4-phase-1-web-application-enhancements)
5. [Phase 2: Desktop Application](#5-phase-2-desktop-application)
6. [Database Schema](#6-database-schema)
7. [API Specifications](#7-api-specifications)
8. [Security Requirements](#8-security-requirements)
9. [Performance Requirements](#9-performance-requirements)
10. [Testing Strategy](#10-testing-strategy)
11. [Appendices](#11-appendices)

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) document provides a complete description of SmartPunch 2.0, a transformational upgrade from a traditional attendance management system to a comprehensive workplace companion. This document is intended for:

- Development team (implementation reference)
- Project managers (planning and tracking)
- QA team (testing criteria)
- Stakeholders (understanding product scope)

### 1.2 Scope

SmartPunch 2.0 encompasses two major implementation phases:

**Phase 1: Web Application Enhancements**
- Team Management System
- Integrated Payroll System

**Phase 2: Desktop Companion Application**
- Electron-based desktop application
- AI-driven workplace assistant
- Presence status tracking with system idle detection
- Face recognition for attendance verification
- Device trust and security framework
- Proactive notifications and reminders
- Productivity analytics and insights

### 1.3 Definitions and Acronyms

| Term | Definition |
|------|------------|
| **SmartPunch** | Product name for the workplace companion system |
| **HRMS** | Human Resource Management System |
| **TL** | Team Leader |
| **WFH** | Work From Home |
| **OT** | Overtime |
| **DND** | Do Not Disturb |
| **IST** | Indian Standard Time (Asia/Kolkata timezone, UTC+5:30) |
| **SRS** | Software Requirements Specification |
| **Electron** | Cross-platform desktop application framework |
| **Presence Status** | Real-time employee availability indicator (Available, Away, On Break, DND, Offline) |

### 1.4 Product Philosophy

SmartPunch 2.0 is built on a fundamentally different philosophy than traditional HRMS systems:

**Traditional HRMS:**
- Employee asks → System responds
- Feature-focused
- Manual, reactive processes
- Desktop as afterthought

**SmartPunch 2.0:**
- System observes → System helps proactively
- Experience-focused
- Automated, intelligent workflows
- Desktop-first companion experience

**Core Principle:** *"The employee should never think. The assistant should guide them throughout their day."*

### 1.5 Reference Documents

- SmartPunch v1.0 codebase (current Django application)
- Phase 3 Implementation Specs (existing features documentation)
- Microsoft Teams presence system (reference for status tracking)
- Slack desktop app (reference for system tray UX)

---

## 2. Product Vision

### 2.1 Vision Statement

**SmartPunch is not an attendance management system. It's a workplace companion that makes employees forget it's running while seamlessly managing their workday.**

### 2.2 Target Users

| User Role | Description | Key Needs |
|-----------|-------------|-----------|
| **Employee** | Regular system user | Simple check-in/out, leave requests, minimal friction |
| **Team Leader** | Leads one or more teams | View team member requests, add comments, monitor team status |
| **Manager** | Approves requests, manages multiple teams | Approval workflows, team analytics, request management |
| **HR/Admin** | Full system access | Payroll processing, team management, company-wide analytics, configuration |

### 2.3 Key Differentiators

**vs. Traditional Attendance Systems:**
- Proactive reminders (not reactive commands)
- Desktop companion (not browser-only)
- AI-driven suggestions (not manual tracking)
- Experience-focused (not feature-heavy)

**vs. Attendify and Competitors:**
- Not just "face recognition attendance"
- Complete workplace experience platform
- Intelligent assistant, not surveillance tool
- Respects privacy while ensuring accountability

### 2.4 Success Metrics

**Phase 1 (Web Enhancements):**
- 100% payroll automation (eliminate manual calculations)
- <5 min average time for HR to process monthly payroll
- Team Leader dashboard adoption rate >80%
- Zero payroll calculation errors

**Phase 2 (Desktop Application):**
- >95% employee adoption within 30 days
- <3 seconds average check-in time (face recognition)
- Employee NPS score >8/10
- <100 MB idle RAM usage
- <2% false positive rate in face recognition

---

## 3. Implementation Phases

### 3.1 Phase 1: Web Application Enhancements

**Timeline:** 5-7 weeks  
**Platform:** Django web application (existing)  
**Delivery:** Production-ready web features

**Modules:**
1. Team Management System
2. Payroll Integration System

**Rationale:**
- Immediate business value
- No architectural changes required
- Builds foundation for Phase 2
- Tests data models before desktop integration

### 3.2 Phase 2: Desktop Companion Application

**Timeline:** 12-16 weeks  
**Platform:** Electron desktop app + Django backend  
**Delivery:** Windows desktop application (macOS/Linux future)

**Modules:**
1. Desktop Foundation (Electron shell, system tray, auto-start)
2. Presence Status Tracking (system idle detection, auto-status)
3. Face Recognition (registration, verification, device trust)
4. AI Assistant (proactive reminders, smart suggestions)
5. Analytics & Reports (visual timeline, productivity insights)

**Rationale:**
- Enables accurate system-wide presence tracking (impossible in browser)
- Provides seamless companion experience
- Leverages desktop APIs for enhanced functionality
- Transforms user experience fundamentally

---


## 4. Phase 1: Web Application Enhancements

### 4.1 Team Management System

#### 4.1.1 Overview

The Team Management System enables HR/Admin to organize employees into teams with designated Team Leaders, providing role-based access to team information and request management.

#### 4.1.2 Key Features

**Team Structure:**
- Multi-team membership (one employee can belong to multiple teams)
- Multi-team leadership (one Team Leader can lead multiple teams)
- Hierarchical organization (Company → Department → Team → Members)
- Team Leader role with limited permissions

**Team Operations:**
- Create/edit/delete teams (HR/Admin only)
- Assign/remove team members
- Designate team leaders
- View team hierarchies
- Filter data by team

#### 4.1.3 User Stories

**US-TM-001: Create Team (HR/Admin)**
```
As an HR/Admin,
I want to create a new team with a designated team leader,
So that I can organize employees by project or function.

Acceptance Criteria:
- HR/Admin can access team management interface
- Form includes: Team Name, Department, Team Leader (dropdown), Description
- Team name must be unique within company
- Team Leader must be an active employee
- System validates all required fields
- Success confirmation displayed
- Audit log created for team creation
```

**US-TM-002: Assign Team Members (HR/Admin)**
```
As an HR/Admin,
I want to add employees to teams,
So that team leaders can monitor their team's activities.

Acceptance Criteria:
- HR/Admin can search and select employees
- Employee can be added to multiple teams
- System prevents duplicate assignments (same employee + same team)
- Bulk assignment supported (select multiple employees)
- Confirmation message shows number of members added
- Audit log created for each assignment
```

**US-TM-003: View Team Dashboard (Team Leader)**
```
As a Team Leader,
I want to see a dashboard showing my team's pending requests and status,
So that I can stay informed about my team members' activities.

Acceptance Criteria:
- Team Leader sees only teams they lead
- Dashboard shows: Team name, member count, today's attendance, pending requests
- Separate sections for: Leave requests, WFH requests, OT requests, Onsite requests
- Each request shows: Employee name, dates, type, status
- Team Leader can click to view request details
- Team Leader can add comments to requests
- Real-time updates when requests are approved/rejected
```

**US-TM-004: View Team Member Details (Team Leader)**
```
As a Team Leader,
I want to view my team members' information,
So that I can understand their current status and requests.

Acceptance Criteria:
- Team Leader sees list of team members with photos and current status
- Each member shows: Name, Role, Department, Current Presence Status
- Team Leader can click to view: Attendance history, leave balance, pending requests
- Team Leader CANNOT view: Salary, payroll data, personal documents
- System respects privacy boundaries
```

**US-TM-005: Comment on Team Member Requests (Team Leader)**
```
As a Team Leader,
I want to add comments on my team members' leave/WFH/OT/onsite requests,
So that I can provide context to managers and HR.

Acceptance Criteria:
- Team Leader can add comments on pending requests from their team only
- Comment field is text area (max 500 characters)
- Comments are visible to: Employee, Manager, HR (not public)
- Comment timestamp and author recorded
- Notification sent to Manager when Team Leader comments
- Team Leader CANNOT approve/reject (only comment)
```

**US-TM-006: Receive Team Notifications (Team Leader)**
```
As a Team Leader,
I want to receive notifications when my team members submit requests,
So that I can respond promptly.

Acceptance Criteria:
- Notification when team member submits leave request
- Notification when team member submits WFH request
- Notification when team member submits OT request
- Notification when team member submits onsite request
- Notification when Manager/HR approves/rejects team member request
- Notifications show: Employee name, request type, action required
- Team Leader can click notification to view request
```

#### 4.1.4 Functional Requirements

**FR-TM-001: Team Model**
- Team has: ID, Name, Department, Team Leader (FK to User), Description, Created At, Is Active
- Unique constraint on team name
- Soft delete support (is_active flag)

**FR-TM-002: Team Membership Model**
- TeamMembership has: ID, Team (FK), Employee (FK), Joined At, Is Active
- Unique constraint on (Team, Employee) combination
- Cascade delete when team is deleted
- Many-to-many relationship (employee can have multiple teams)

**FR-TM-003: Team Leader Assignment**
- Employee Profile extended with: is_team_leader (Boolean)
- When user is assigned as Team Leader of any team → is_team_leader = True
- When user is removed from all Team Leader positions → is_team_leader = False
- Team Leader flag controls access to Team Leader Dashboard

**FR-TM-004: Role-Based Access Control**
- Team Leader can view: Own teams only
- Team Leader can comment on: Own team members' requests only
- Team Leader CANNOT: Approve/reject requests, view payroll, manage teams
- Manager can view: All teams
- HR/Admin can: Manage all teams, assign members, change leaders

**FR-TM-005: Team Leader Dashboard**
- Shows all teams the user leads
- Per team: Member count, today's attendance summary, pending request count
- Pending requests aggregated from all led teams
- Filterable by team
- Search functionality for finding specific employee requests

**FR-TM-006: Team Visibility**
- Employees CANNOT see team structures or other employees' team assignments
- Team Leaders CAN see list of all teams but details only for teams they lead
- Managers CAN see all teams with full details
- HR/Admin CAN see and manage all teams

**FR-TM-007: Notification System**
- Team Leader notified on: Team member request submission
- Team Leader notified on: Manager/HR action on team member request
- Notification includes: Direct link to request, employee name, request type
- Notifications stored in database (Notification model)
- Unread notification count shown in header

#### 4.1.5 Non-Functional Requirements

**NFR-TM-001: Performance**
- Team dashboard loads in <2 seconds
- Team member list loads in <1 second
- Notification delivery in <3 seconds after event

**NFR-TM-002: Scalability**
- Support up to 100 teams per company
- Support up to 100 members per team
- Support up to 10 teams per Team Leader

**NFR-TM-003: Usability**
- Team Leader dashboard requires <5 minutes training
- Navigation between teams intuitive
- Mobile-responsive (tablets and phones)

**NFR-TM-004: Data Integrity**
- No orphaned team memberships
- Cascade deletes handled properly
- Audit logs for all team changes

#### 4.1.6 Database Schema

**Team Table:**
```sql
CREATE TABLE teams (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    team_leader_id BIGINT NOT NULL,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    FOREIGN KEY (team_leader_id) REFERENCES auth_user(id),
    INDEX idx_team_leader (team_leader_id),
    INDEX idx_department (department),
    INDEX idx_is_active (is_active)
);
```

**TeamMembership Table:**
```sql
CREATE TABLE team_memberships (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    team_id BIGINT NOT NULL,
    employee_id BIGINT NOT NULL,
    joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    UNIQUE KEY unique_team_member (team_id, employee_id),
    INDEX idx_team (team_id),
    INDEX idx_employee (employee_id)
);
```

**EmployeeProfile Extension:**
```sql
ALTER TABLE attendance_employeeprofile
ADD COLUMN is_team_leader BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX idx_is_team_leader ON attendance_employeeprofile(is_team_leader);
```

#### 4.1.7 API Endpoints

**Team Management (HR/Admin only):**
```
POST   /api/teams/                    - Create team
GET    /api/teams/                    - List all teams
GET    /api/teams/{id}/               - Get team details
PUT    /api/teams/{id}/               - Update team
DELETE /api/teams/{id}/               - Delete team (soft delete)
POST   /api/teams/{id}/members/       - Add members to team
DELETE /api/teams/{id}/members/{uid}/ - Remove member from team
```

**Team Leader Dashboard:**
```
GET    /api/teams/my-teams/              - Get teams I lead
GET    /api/teams/{id}/pending-requests/ - Get pending requests for team
GET    /api/teams/{id}/members/          - Get team members
POST   /api/teams/{id}/requests/{rid}/comment/ - Add comment to request
```

**Team Information:**
```
GET    /api/teams/list/                  - List all teams (names only)
GET    /api/teams/{id}/summary/          - Get team summary (if authorized)
```

---

### 4.2 Payroll Integration System

#### 4.2.1 Overview

The Payroll Integration System automates salary calculations based on attendance data, including present days, absent days, half-days, leaves, WFH, and overtime hours. The system is designed for HR/Admin use only; employees have zero visibility into payroll data.

#### 4.2.2 Key Features

**Payroll Calculation:**
- Automated monthly salary calculation
- Attendance-based deductions (absent, half-day, unpaid leave)
- Overtime payment calculation
- Leave policy enforcement (18 paid leaves: 6 sick + 6 casual + 6 earned)
- Mid-month joiner/exit proration
- Manual adjustment capability (HR override)

**Payroll Processing:**
- Monthly processing (last day of month)
- Custom date range processing
- Draft → Review → Finalize workflow
- CSV export for payment processing
- Historical payroll records

**Privacy & Security:**
- HR/Admin exclusive access
- No employee visibility
- Encrypted salary data
- Audit trail for all changes

#### 4.2.3 User Stories

**US-PAY-001: Process Monthly Payroll (HR/Admin)**
```
As an HR/Admin,
I want to automatically calculate monthly salaries for all employees,
So that I don't have to manually calculate attendance-based deductions.

Acceptance Criteria:
- HR/Admin can select month/year to process
- System calculates for all active employees
- Calculation includes: Base salary, deductions, OT, net salary
- Draft payroll created (not finalized)
- HR can review before finalizing
- Process completes in <60 seconds for 100 employees
```

**US-PAY-002: Review Payroll Calculations (HR/Admin)**
```
As an HR/Admin,
I want to review calculated salaries before finalizing,
So that I can verify accuracy and make adjustments if needed.

Acceptance Criteria:
- HR sees list of all employees with calculated salaries
- Each entry shows: Name, Base salary, Working days, Present days, Deductions, OT, Net salary
- HR can click to see detailed breakdown
- Breakdown shows: Each absent day, each half-day, each unpaid leave, each OT hour
- Color-coded indicators for anomalies (high deductions, zero OT, etc.)
```

**US-PAY-003: Make Manual Adjustments (HR/Admin)**
```
As an HR/Admin,
I want to manually adjust salaries before finalizing payroll,
So that I can handle exceptional cases (sick employee, compassionate reasons).

Acceptance Criteria:
- HR can edit net salary for any employee
- Adjustment reason required (text field, max 500 characters)
- Original calculated value preserved
- Adjustment amount clearly shown
- Audit log records: Who adjusted, when, original value, new value, reason
- Warning if adjustment is >20% of calculated salary
```

**US-PAY-004: Finalize Payroll (HR/Admin)**
```
As an HR/Admin,
I want to finalize payroll after review,
So that I can lock the data and export for payment processing.

Acceptance Criteria:
- Finalize button available only after review
- Confirmation dialog: "Finalize payroll for November 2024? This cannot be undone."
- Once finalized: No edits allowed
- Status changes from "Draft" to "Finalized"
- Export CSV button enabled
- Audit log created with finalization timestamp
```

**US-PAY-005: Export Payroll for Payment (HR/Admin)**
```
As an HR/Admin,
I want to export payroll data as CSV,
So that I can upload to bank or accounting system.

Acceptance Criteria:
- Export button available only for finalized payroll
- CSV includes: Employee ID, Name, Bank Account, IFSC, Net Salary, Month, Year
- File named: payroll_YYYY_MM.csv
- Download starts immediately
- Audit log records export action
```

**US-PAY-006: View Payroll History (HR/Admin)**
```
As an HR/Admin,
I want to view past payroll records,
So that I can reference previous months or answer employee queries.

Acceptance Criteria:
- HR can see list of all processed payrolls (by month/year)
- Each shows: Month, Year, Total employees, Total amount, Status, Processed by, Processed date
- HR can click to view details of any past payroll
- Past payrolls are read-only (no edits)
- Search and filter by month, year, employee
```

#### 4.2.4 Functional Requirements

**FR-PAY-001: Salary Calculation Logic**
```
Base Salary (from EmployeeProfile)
  ↓
Calculate Working Days = CompanyHoliday.count_working_days(start_date, end_date)
  ↓
Calculate Per Day Salary = Base Salary / Working Days
  ↓
Get Attendance Data:
  - Present Days = Count(status='present')
  - Half Days = Count(status='half-day')
  - Late Days = Count(status='late')
  - Absent Days = Working Days - Present - Half - Late
  ↓
Calculate Leave Deductions:
  - Paid Leaves Taken = LeaveRequest(status='approved', within 18 limit).total_days
  - Unpaid Leaves Taken = LeaveRequest(status='approved', beyond 18 limit).total_days
  ↓
Calculate Deductions:
  - Half Day Deduction = (Per Day Salary / 2) × Half Days
  - Late Day Deduction = 0 (late is just status, no deduction)
  - Absent Day Deduction = Per Day Salary × Absent Days
  - Unpaid Leave Deduction = Per Day Salary × Unpaid Leaves
  - Total Deductions = Sum of above
  ↓
Calculate OT Earnings:
  - OT Hours = Overtime(status='approved').total_hours
  - OT Amount = OT Hours × Employee OT Rate
  ↓
Calculate Gross Salary = Base Salary - Total Deductions + OT Amount
  ↓
Apply Statutory Deductions (future):
  - TDS (income tax)
  - PF (provident fund)
  - ESI (employee state insurance)
  ↓
Calculate Net Salary = Gross Salary - Statutory Deductions
```

**FR-PAY-002: Leave Policy Implementation**
```
Annual Leave Entitlement = 18 days
  - Sick Leaves: 6 (paid)
  - Casual Leaves: 6 (paid)
  - Earned Leaves: 6 (paid)
  - Total: 18 paid leaves

Leave Deduction Logic:
  IF (Total Approved Leaves <= 18):
      All leaves are paid (no deduction)
  ELSE:
      First 18 leaves = paid (no deduction)
      Remaining leaves = unpaid (deduct per day salary)

Example:
  Employee takes 22 days leave in year
  → 18 paid (no deduction)
  → 4 unpaid (deduct 4 × per day salary)
```

**FR-PAY-003: WFH Handling**
```
WFH Days = Counted as PRESENT days
  - Employee checks in from home
  - Attendance record created with location='WFH'
  - No salary deduction
  - Full pay

WFH Days should NOT be separately deducted from salary
```

**FR-PAY-004: Half-Day Calculation**
```
Half-Day occurs when:
  - Check-in after 10:00 AM
  - Attendance status = 'half-day'

Deduction:
  - Half Day Deduction = (Base Salary / Working Days) / 2
  - Example: ₹40,000 / 22 days = ₹1,818 per day
  - Half day deduction = ₹1,818 / 2 = ₹909
```

**FR-PAY-005: OT Payment Calculation**
```
OT Payment = OT Hours × OT Rate

OT Rate stored in EmployeeProfile:
  - Default: ₹300 per hour (configurable)
  - Can be different per employee (based on designation)

Only APPROVED overtime is paid
Overtime.status = 'approved'
```

**FR-PAY-006: Mid-Month Joiner/Exit Proration**
```
Mid-Month Joiner:
  Employee joins on 15th of month (30 days)
  Working days for employee = 30 - 15 + 1 = 16 days
  Prorated Salary = (Base Salary / 30) × 16

Mid-Month Exit:
  Employee last day is 20th of month (30 days)
  Working days for employee = 20 days
  Prorated Salary = (Base Salary / 30) × 20

Use EmployeeProfile.date_of_joining and exit_date (if exists)
```

**FR-PAY-007: Manual Adjustment**
```
HR can manually adjust any employee's net salary

Adjustments stored separately:
  - Original calculated value preserved
  - Adjustment amount recorded
  - Adjustment reason required
  - Audit trail maintained

Final Net Salary = Calculated Net Salary + Adjustment Amount
```

**FR-PAY-008: Payroll Workflow**
```
1. Draft State:
   - HR initiates payroll processing
   - System calculates for all employees
   - Payroll status = 'draft'
   - HR can review and adjust

2. Review State:
   - HR reviews each employee's calculation
   - Makes manual adjustments if needed
   - Verifies anomalies

3. Finalized State:
   - HR clicks "Finalize"
   - Payroll status = 'finalized'
   - No more edits allowed
   - Export CSV enabled

4. Paid State (optional):
   - After payment processed
   - HR marks payroll as 'paid'
   - Status = 'paid'
```

#### 4.2.5 Non-Functional Requirements

**NFR-PAY-001: Performance**
- Payroll calculation for 100 employees in <60 seconds
- Payroll dashboard loads in <2 seconds
- CSV export generates in <5 seconds

**NFR-PAY-002: Accuracy**
- 100% accuracy in calculations (verified by unit tests)
- Rounding to 2 decimal places for currency
- No floating-point errors in salary calculations

**NFR-PAY-003: Security**
- Payroll data encrypted at rest
- Only HR/Admin can access payroll module
- Audit logs for all payroll actions (create, adjust, finalize, export)
- No API endpoints accessible to non-HR users

**NFR-PAY-004: Data Integrity**
- Finalized payroll cannot be edited
- Deletion not allowed (soft delete with archive flag)
- Historical payroll preserved permanently
- Backup before each payroll finalization

#### 4.2.6 Database Schema

**PayrollCycle Table:**
```sql
CREATE TABLE payroll_cycles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    month INT NOT NULL,  -- 1-12
    year INT NOT NULL,   -- 2024, 2025, etc.
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('draft', 'finalized', 'paid') NOT NULL DEFAULT 'draft',
    total_employees INT NOT NULL DEFAULT 0,
    total_gross_amount DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    total_deductions DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    total_net_amount DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    processed_by_id BIGINT NOT NULL,
    processed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finalized_at DATETIME NULL,
    notes TEXT,
    
    FOREIGN KEY (processed_by_id) REFERENCES auth_user(id),
    UNIQUE KEY unique_month_year (month, year),
    INDEX idx_status (status),
    INDEX idx_month_year (month, year)
);
```

**PayrollEntry Table:**
```sql
CREATE TABLE payroll_entries (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    payroll_cycle_id BIGINT NOT NULL,
    employee_id BIGINT NOT NULL,
    
    -- Salary Components
    base_salary DECIMAL(10, 2) NOT NULL,
    
    -- Attendance Metrics
    working_days INT NOT NULL,
    present_days INT NOT NULL,
    absent_days INT NOT NULL,
    half_days INT NOT NULL,
    late_days INT NOT NULL,
    
    -- Leave Metrics
    paid_leaves_taken DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    unpaid_leaves_taken DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    wfh_days INT NOT NULL DEFAULT 0,
    
    -- OT Metrics
    ot_hours DECIMAL(6, 2) NOT NULL DEFAULT 0.00,
    ot_rate DECIMAL(8, 2) NOT NULL DEFAULT 0.00,
    ot_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    
    -- Deductions
    half_day_deduction DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    absent_deduction DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    unpaid_leave_deduction DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    other_deductions DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_deductions DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    
    -- Calculated Amounts
    gross_salary DECIMAL(10, 2) NOT NULL,
    
    -- Statutory Deductions (future)
    tds_deduction DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    pf_deduction DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    esi_deduction DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    
    -- Manual Adjustments
    manual_adjustment DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    adjustment_reason TEXT,
    adjusted_by_id BIGINT NULL,
    adjusted_at DATETIME NULL,
    
    -- Final Amount
    net_salary DECIMAL(10, 2) NOT NULL,
    
    -- Payment Status
    payment_status ENUM('pending', 'processed', 'failed') NOT NULL DEFAULT 'pending',
    payment_date DATETIME NULL,
    payment_reference VARCHAR(100),
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (payroll_cycle_id) REFERENCES payroll_cycles(id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES auth_user(id),
    FOREIGN KEY (adjusted_by_id) REFERENCES auth_user(id),
    UNIQUE KEY unique_cycle_employee (payroll_cycle_id, employee_id),
    INDEX idx_employee (employee_id),
    INDEX idx_payroll_cycle (payroll_cycle_id),
    INDEX idx_payment_status (payment_status)
);
```

**LeaveBalance Table:**
```sql
CREATE TABLE leave_balances (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    employee_id BIGINT NOT NULL,
    year INT NOT NULL,
    
    -- Leave Allocations
    sick_leaves_total INT NOT NULL DEFAULT 6,
    casual_leaves_total INT NOT NULL DEFAULT 6,
    earned_leaves_total INT NOT NULL DEFAULT 6,
    
    -- Leave Usage
    sick_leaves_used DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    casual_leaves_used DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    earned_leaves_used DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    
    -- Calculated Fields
    total_leaves_allocated INT NOT NULL DEFAULT 18,
    total_leaves_used DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    total_leaves_remaining DECIMAL(5, 2) NOT NULL DEFAULT 18.00,
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (employee_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    UNIQUE KEY unique_employee_year (employee_id, year),
    INDEX idx_employee (employee_id),
    INDEX idx_year (year)
);
```

**EmployeeProfile Extension:**
```sql
ALTER TABLE attendance_employeeprofile
ADD COLUMN base_salary DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
ADD COLUMN ot_rate DECIMAL(8, 2) NOT NULL DEFAULT 300.00,
ADD COLUMN bank_account_number VARCHAR(50),
ADD COLUMN bank_ifsc_code VARCHAR(20),
ADD COLUMN bank_name VARCHAR(100),
ADD COLUMN pan_number VARCHAR(20),
ADD COLUMN pf_number VARCHAR(50),
ADD COLUMN uan_number VARCHAR(20),
ADD COLUMN esi_number VARCHAR(20);

CREATE INDEX idx_base_salary ON attendance_employeeprofile(base_salary);
```

#### 4.2.7 API Endpoints

**Payroll Processing:**
```
POST   /api/payroll/process/              - Process payroll for month/year
GET    /api/payroll/cycles/               - List all payroll cycles
GET    /api/payroll/cycles/{id}/          - Get payroll cycle details
PUT    /api/payroll/cycles/{id}/finalize/ - Finalize payroll
GET    /api/payroll/cycles/{id}/export/   - Export CSV
```

**Payroll Entries:**
```
GET    /api/payroll/cycles/{id}/entries/         - Get all entries for cycle
GET    /api/payroll/entries/{id}/                - Get entry details
PUT    /api/payroll/entries/{id}/adjust/         - Make manual adjustment
GET    /api/payroll/entries/{id}/breakdown/      - Get detailed salary breakdown
```

**Leave Balance:**
```
GET    /api/payroll/leave-balance/{employee_id}/{year}/ - Get leave balance
PUT    /api/payroll/leave-balance/{id}/update/          - Update leave balance (admin)
```

**Reports:**
```
GET    /api/payroll/reports/summary/{cycle_id}/     - Payroll summary report
GET    /api/payroll/reports/department/{cycle_id}/  - Department-wise payroll
GET    /api/payroll/reports/comparison/             - Month-over-month comparison
```

---


## 5. Phase 2: Desktop Companion Application

### 5.1 Desktop Foundation

#### 5.1.1 Overview

The Desktop Foundation module establishes the core infrastructure for the SmartPunch desktop companion application using Electron framework. It provides system tray integration, auto-start capability, and embeds the existing Django HRMS web application.

#### 5.1.2 Key Features

**Desktop Shell:**
- Electron-based cross-platform application (Windows primary, macOS/Linux future)
- System tray icon with context menu
- Auto-start on Windows boot
- Lightweight (40-80 MB RAM idle)
- Silent updates

**Embedded HRMS:**
- Existing Django web application loaded in BrowserWindow
- Seamless integration (no visible browser chrome)
- Session management (persistent login)
- Deep linking from notifications to specific pages

**System Integration:**
- Windows notification API
- System idle detection
- Camera access
- Network detection
- Device fingerprinting

#### 5.1.3 User Stories

**US-DESK-001: Install Desktop Application**
```
As an Employee,
I want to install SmartPunch desktop app with a simple installer,
So that I can start using the companion without technical knowledge.

Acceptance Criteria:
- Double-click .exe installer
- Installation wizard with: Welcome, License, Install Location, Finish
- Default install location: C:\Program Files\SmartPunch
- Creates desktop shortcut (optional)
- Creates start menu entry
- Installs silently in background (<1 minute)
- No manual configuration required
- Auto-starts after installation
```

**US-DESK-002: Auto-Start on Boot**
```
As an Employee,
I want SmartPunch to start automatically when I boot my computer,
So that I don't have to remember to launch it.

Acceptance Criteria:
- App registered in Windows startup programs
- Launches silently on boot (no splash screen)
- Appears in system tray within 3 seconds
- Does not show main window (minimized to tray)
- Employee can disable auto-start from settings (optional)
```

**US-DESK-003: System Tray Interaction**
```
As an Employee,
I want to access SmartPunch from the system tray,
So that it stays out of my way while remaining accessible.

Acceptance Criteria:
- Purple SmartPunch icon appears in system tray
- Right-click shows context menu:
  - Open Dashboard
  - Quick Check-in
  - Start Break
  - End Break
  - Check-out
  - Settings
  - Quit
- Double-click opens main dashboard
- Hover shows tooltip: "SmartPunch - Available"
- Icon changes based on status (green/yellow/red dot overlay)
```

**US-DESK-004: Embedded HRMS Access**
```
As an Employee,
I want to access all HRMS features within the desktop app,
So that I don't need to open a browser separately.

Acceptance Criteria:
- Clicking "Open Dashboard" loads HRMS in Electron window
- Window size: 1200x800px (resizable)
- Window title: "SmartPunch"
- All web features work identically (attendance, leave, WFH, etc.)
- Session persists (no repeated logins)
- External links open in default browser
- Navigation within HRMS stays in Electron window
```

**US-DESK-005: Desktop Notifications**
```
As an Employee,
I want to receive desktop notifications from SmartPunch,
So that I stay informed even when the app is minimized.

Acceptance Criteria:
- Notifications appear as Windows toast notifications
- Notification types: Morning greeting, break reminder, check-out reminder, approvals
- Each notification shows: Icon, title, message, action buttons
- Clicking notification opens relevant page in app
- Notifications respect Windows "Do Not Disturb" mode
- Notification history accessible in app
```

**US-DESK-006: Silent Updates**
```
As an Employee,
I want SmartPunch to update automatically,
So that I always have the latest features without manual effort.

Acceptance Criteria:
- App checks for updates on startup
- If update available: Shows notification "Update available. Install now?"
- User can choose: Install Now, Install on Exit, Remind Tomorrow
- Update downloads in background
- Installation on next restart (no disruption to current work)
- Rollback capability if update fails
```

#### 5.1.4 Technical Architecture

**Electron Application Structure:**
```
smartpunch-desktop/
├── main/                   # Main process (Node.js)
│   ├── index.js           # Entry point
│   ├── window-manager.js  # Window creation/management
│   ├── tray-manager.js    # System tray icon/menu
│   ├── auto-updater.js    # Update mechanism
│   ├── session-manager.js # Login session persistence
│   └── native-apis.js     # System APIs (idle, camera, etc.)
├── renderer/              # Renderer process (Browser)
│   ├── preload.js        # Bridge between main and renderer
│   ├── notifications.js  # Notification handling
│   └── status-indicator.js # Status icon updates
├── assets/
│   ├── icons/            # Tray icons, app icons
│   └── sounds/           # Notification sounds
├── package.json
└── electron-builder.json # Build configuration
```

**Main Process Responsibilities:**
- System tray management
- Window lifecycle
- Native API access (camera, idle detection)
- Auto-start registration
- Update management
- IPC (Inter-Process Communication) with renderer

**Renderer Process Responsibilities:**
- Load Django HRMS (WebView)
- Handle notifications
- UI interactions
- Communicate with main process via IPC

#### 5.1.5 Functional Requirements

**FR-DESK-001: Electron Setup**
- Electron version: Latest stable (currently v28+)
- Target OS: Windows 10/11 (64-bit)
- Node.js bundled (no separate installation)
- Chromium engine for web content
- Native modules: node-gyp for camera, idle detection

**FR-DESK-002: System Tray Icon**
- Icon formats: .ico (Windows), .png (fallback)
- Icon states:
  - Default: Purple dot
  - Available: Green dot overlay
  - Away: Yellow dot overlay
  - On Break: Orange dot overlay
  - DND: Red dot overlay
  - Offline: Gray dot
- Context menu updates based on current status
- Menu items enabled/disabled based on context (e.g., "End Break" only if break active)

**FR-DESK-003: Auto-Start Registration**
- Windows Registry key: HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
- Entry name: "SmartPunch"
- Entry value: Path to smartpunch.exe with --hidden flag
- Uninstaller removes registry entry
- User can toggle auto-start from settings

**FR-DESK-004: Embedded HRMS**
- BrowserWindow with webPreferences:
  - nodeIntegration: false (security)
  - contextIsolation: true
  - sandbox: true
  - preload: preload.js (IPC bridge)
- Load URL: https://attendance.arraafi.com (or localhost for dev)
- Session persistence using electron-store
- Cookies saved locally
- Deep linking support (e.g., smartpunch://leave/request/123)

**FR-DESK-005: Notification System**
- Use Electron Notification API (wraps Windows notifications)
- Notification structure:
  ```javascript
  {
    title: "Good Morning, Ace!",
    body: "Ready to start your day?",
    icon: "assets/icons/icon.png",
    actions: [
      { type: "button", text: "Start My Day" },
      { type: "button", text: "Later" }
    ],
    urgency: "normal", // low, normal, critical
    timeoutType: "default" // never, default
  }
  ```
- Action handling in main process
- Notification clicks route to appropriate page

**FR-DESK-006: Update Mechanism**
- electron-updater library
- Update server: GitHub Releases or S3 bucket
- Update manifest: latest.yml
- Differential updates (download only changed files)
- Update flow:
  1. Check for update on startup
  2. Download in background if available
  3. Notify user when ready
  4. Install on restart or user action
- Rollback: Previous version backed up, restored if new version crashes

**FR-DESK-007: IPC Communication**
- Main → Renderer: Send notifications, status updates
- Renderer → Main: User actions, status changes, API calls
- Event types:
  - `notification-show`
  - `notification-click`
  - `status-change`
  - `check-in-request`
  - `open-page`
- Security: Validate all IPC messages, sanitize inputs

**FR-DESK-008: Resource Management**
- Idle RAM target: 40-80 MB
- Active RAM target: <300 MB
- CPU idle: ~0%
- Network: Periodic sync (every 30 seconds), not constant polling
- Cleanup on exit: Close windows, save state, disconnect WebSockets

#### 5.1.6 Non-Functional Requirements

**NFR-DESK-001: Performance**
- Startup time: <3 seconds from boot to tray icon
- Window open time: <1 second
- Notification delivery: <500ms
- Memory footprint: <100 MB idle

**NFR-DESK-002: Reliability**
- 99.9% uptime (no crashes during work hours)
- Auto-restart on crash
- Graceful degradation if backend unavailable
- Offline queue for failed API calls

**NFR-DESK-003: Security**
- No credentials stored in plain text
- Session tokens encrypted
- HTTPS only for backend communication
- Code signing certificate for installer
- Sandboxed renderer process

**NFR-DESK-004: Usability**
- <5 minutes to install and configure
- No user training required for basic features
- Tooltip help on all tray menu items
- Keyboard shortcuts for common actions

---

### 5.2 Presence Status Tracking

#### 5.2.1 Overview

The Presence Status Tracking module monitors employee activity and automatically updates their availability status. It uses system-level idle detection to accurately track presence without invasive monitoring.

#### 5.2.2 Key Features

**Status Types:**
- 🟢 Available (actively working)
- 🟡 Away (idle for 10+ minutes)
- ☕ On Break (official tea/lunch break)
- 🔴 Do Not Disturb (focus mode)
- ⚫ Offline (not checked in)

**Detection:**
- Hybrid mode: Manual status selection + automatic idle detection
- System-level idle monitoring (Windows API)
- 10-minute idle threshold (configurable)
- Auto-return to Available when activity detected

**Reporting:**
- Real-time status visible to all employees
- Detailed timeline (HR only)
- Daily/weekly/monthly reports
- Productivity analytics

#### 5.2.3 User Stories

**US-PRES-001: Automatic Idle Detection**
```
As an Employee,
I want my status to automatically change to Away when I'm idle,
So that my colleagues know I'm not at my desk.

Acceptance Criteria:
- System monitors mouse/keyboard activity
- After 10 minutes of no activity → Status changes to Away
- Desktop notification: "You've been marked as Away"
- When employee returns and moves mouse → Status changes to Available
- Automatic transitions logged with timestamps
- Employee can manually override if needed
```

**US-PRES-002: Manual Status Selection**
```
As an Employee,
I want to manually set my status,
So that I can indicate when I'm in a meeting or focusing.

Acceptance Criteria:
- Status dropdown in system tray menu
- Options: Available, Away, Do Not Disturb
- Selected status stays until changed or auto-away triggered
- DND prevents all notifications except critical ones
- Status change synced to backend immediately
- Other employees see updated status within 3 seconds
```

**US-PRES-003: Break Status Automatic**
```
As an Employee,
I want my status to automatically change when I start a break,
So that I don't have to manually update it.

Acceptance Criteria:
- Clicking "Start Tea Break" → Status changes to On Break
- Clicking "Start Lunch Break" → Status changes to On Break
- Break timer shown in notification
- Clicking "End Break" → Status changes to Available
- If break exceeds limit, status stays On Break with warning notification
```

**US-PRES-004: Check-in/Check-out Status**
```
As an Employee,
I want my status to automatically reflect my check-in state,
So that others know when I'm working.

Acceptance Criteria:
- Before check-in → Status: Offline
- After check-in → Status: Available
- After check-out → Status: Offline
- Status persists across app restarts (saved to backend)
```

**US-PRES-005: View Team Status (All Employees)**
```
As an Employee,
I want to see my colleagues' current status,
So that I know when it's a good time to reach out.

Acceptance Criteria:
- Team member list shows current status with colored dot
- List updates in real-time (WebSocket or polling)
- Status shows: Name, Status, Since (time in current status)
- Can filter by status (e.g., show only Available)
- No access to detailed timeline (only current status)
```

**US-PRES-006: View Detailed Timeline (HR/Admin)**
```
As an HR/Admin,
I want to see a detailed timeline of employee presence throughout the day,
So that I can analyze productivity patterns.

Acceptance Criteria:
- Visual timeline showing status changes throughout day
- Color-coded bars: Green (Available), Yellow (Away), Orange (Break), Red (DND)
- Hover over timeline shows exact time and duration
- Summary statistics: Total Available time, Total Away time, etc.
- Export timeline as image or PDF
- Productivity score calculated
```

**US-PRES-007: Productivity Insights (HR/Team Leader)**
```
As an HR/Team Leader,
I want to see productivity analytics for my team,
So that I can identify patterns and support team members.

Acceptance Criteria:
- Team average productivity score
- Individual scores with comparison to average
- Trends: Day-over-day, week-over-week
- Insights: "Kiran's away time increased 30% this week"
- No punitive framing (supportive tone)
- Export reports as Excel
```

#### 5.2.4 Functional Requirements

**FR-PRES-001: System Idle Detection (Windows)**
- Use Windows API: `GetLastInputInfo()`
- Returns milliseconds since last input event
- Poll every 60 seconds (not continuous)
- Idle threshold: 600,000ms (10 minutes)
- Calculation:
  ```
  idleTime = CurrentTime - LastInputTime
  if (idleTime >= 600000 && currentStatus != 'away') {
      changeStatus('away', 'auto');
  }
  ```

**FR-PRES-002: Status Change Logic**
- Status changes trigger API call to backend
- Endpoint: `POST /api/presence/status/update/`
- Payload:
  ```json
  {
    "status": "away",
    "changed_by": "auto",  // or "manual"
    "timestamp": "2024-12-03T10:15:00Z"
  }
  ```
- Backend calculates duration of previous status
- New PresenceLog record created

**FR-PRES-003: Status Transitions**
```
Check-in → Available
Available + 10min idle → Away
Away + activity → Available (if was Available before)
Start Break → On Break
End Break → Available
Manual DND → Do Not Disturb
Check-out → Offline
```

**FR-PRES-004: PresenceLog Model**
```python
class PresenceLog(models.Model):
    employee = ForeignKey(User)
    status = CharField(choices=[
        ('available', 'Available'),
        ('away', 'Away'),
        ('on_break', 'On Break'),
        ('dnd', 'Do Not Disturb'),
        ('offline', 'Offline'),
    ])
    changed_at = DateTimeField(auto_now_add=True)
    changed_by = CharField(choices=[
        ('auto', 'Auto-detected'),
        ('manual', 'Manual'),
        ('system', 'System'),
    ])
    duration_seconds = IntegerField(null=True)  # Calculated when next status change
    
    class Meta:
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['employee', '-changed_at']),
            models.Index(fields=['status', '-changed_at']),
        ]
```

**FR-PRES-005: Current Status Storage**
- EmployeeProfile extended with:
  ```python
  current_status = CharField(max_length=20, default='offline')
  last_status_change = DateTimeField(null=True)
  last_activity_at = DateTimeField(null=True)
  ```
- Updated on every status change
- Used for real-time status queries

**FR-PRES-006: Real-Time Status Updates**
- WebSocket connection for real-time updates (optional)
- Or: Polling every 30 seconds
- Endpoint: `GET /api/presence/team-status/`
- Returns:
  ```json
  [
    {
      "employee_id": 1,
      "name": "Raju Kumar",
      "status": "available",
      "since": "2024-12-03T09:00:00Z",
      "profile_photo": "/media/photos/raju.jpg"
    },
    ...
  ]
  ```

**FR-PRES-007: Timeline Generation**
- Fetch PresenceLog records for employee and date
- Group consecutive records of same status
- Generate timeline data:
  ```json
  {
    "date": "2024-12-03",
    "employee_id": 1,
    "timeline": [
      {
        "status": "available",
        "start": "09:00:00",
        "end": "11:00:00",
        "duration_minutes": 120
      },
      {
        "status": "on_break",
        "start": "11:00:00",
        "end": "11:15:00",
        "duration_minutes": 15
      },
      ...
    ],
    "summary": {
      "available_minutes": 375,
      "away_minutes": 45,
      "on_break_minutes": 60,
      "dnd_minutes": 30,
      "productivity_score": 87
    }
  }
  ```

**FR-PRES-008: Productivity Score Calculation**
```
Productive Time = Available Time + On Break Time
Non-Productive Time = Away Time
Total Time = Check-in to Check-out duration

Productivity Score = (Productive Time / Total Time) × 100

Example:
  Available: 6h 15m (375 min)
  On Break: 1h (60 min)
  Away: 45m
  Total: 8h (480 min)
  
  Productive = 375 + 60 = 435 min
  Score = (435 / 480) × 100 = 90.6%
```

#### 5.2.5 Non-Functional Requirements

**NFR-PRES-001: Performance**
- Status change latency: <1 second (local), <3 seconds (sync to server)
- Timeline generation: <2 seconds for 1 day, <5 seconds for 1 month
- Real-time updates: <3 seconds delay

**NFR-PRES-002: Privacy**
- No screenshots
- No keystroke logging
- No application usage tracking
- Only idle/active state recorded
- Employees can view their own timeline
- Detailed timelines restricted to HR/Team Leaders

**NFR-PRES-003: Accuracy**
- <1% false positives (marking idle when active)
- <1 minute granularity in timeline
- Correct status even if app crashes (recovery from last known state)

**NFR-PRES-004: Reliability**
- Offline queue if backend unavailable
- Status synced when connection restored
- No data loss during network interruptions

---

### 5.3 Face Recognition System

#### 5.3.1 Overview

The Face Recognition System provides secure, touchless attendance verification using facial recognition technology. It implements a one-time registration process followed by daily verification with device trust and fallback mechanisms.

#### 5.3.2 Key Features

**Face Registration:**
- One-time setup during onboarding
- Multiple angle capture (front, left, right)
- Liveness detection (optional)
- Face embedding stored securely on backend

**Face Verification:**
- Daily check-in via camera
- <3 second verification
- Works in various lighting conditions
- Fallback to manual if camera fails

**Device Trust:**
- Device fingerprinting
- HR assigns devices to employees
- New device requires HR approval
- Multi-device support per employee

**Security:**
- Face embeddings encrypted at rest
- No raw images stored
- Verification done locally (embeddings compared)
- Audit trail for all attempts

#### 5.3.3 User Stories

**US-FACE-001: Register Face (New Employee)**
```
As a new Employee,
I want to register my face during onboarding,
So that I can use face recognition for daily check-in.

Acceptance Criteria:
- First login triggers face registration wizard
- Wizard guides: "Look straight", "Turn left", "Turn right"
- Camera captures 3 photos (front, left, right)
- System generates face embedding
- Embedding uploaded to backend (encrypted)
- Success message: "Face registered successfully"
- Can skip if camera unavailable (manual check-in only)
- Can re-register anytime from settings
```

**US-FACE-002: Check-in with Face Recognition**
```
As an Employee,
I want to check in using my face,
So that I don't have to enter credentials or click buttons.

Acceptance Criteria:
- Morning notification: "Good morning! Ready to start?"
- Click "Start My Day" → Camera activates
- System captures photo and verifies against stored embedding
- Verification takes <3 seconds
- Success: "Attendance marked. Have a great day!"
- Face match confidence >85% required
- Shows friendly message during verification
- Camera auto-closes after verification
```

**US-FACE-003: Face Recognition Failure Handling**
```
As an Employee,
I want a fallback option if face recognition fails,
So that I can still check in when camera has issues.

Acceptance Criteria:
- If verification fails 3 times → Fallback offered
- Fallback options:
  1. Manual check-in (if on office IP and trusted device)
  2. Request manager approval
- Manual check-in requires: Confirm button only
- Manager approval sends notification to manager
- Reason captured: "Face recognition failed"
- Audit log records fallback usage
```

**US-FACE-004: Device Registration (New Device)**
```
As an Employee using a new laptop,
I want to register the device so I can check in,
So that the system trusts my work-from-anywhere setup.

Acceptance Criteria:
- First check-in attempt on new device → Device not recognized
- System prompts: "This device isn't registered. Register now?"
- Employee enters: Employee ID, Password, Date of Birth
- System verifies credentials
- Device registration request sent to HR
- HR receives notification: "Raju requested device registration"
- HR can approve/reject with reason
- If approved: Device ID added to whitelist
- Employee notified of approval
- Future check-ins allowed on this device
```

**US-FACE-005: View Registered Devices (Employee)**
```
As an Employee,
I want to see which devices are registered to me,
So that I know where I can check in from.

Acceptance Criteria:
- Settings → My Devices
- List shows: Device name, OS, Last used, Status (Active/Inactive)
- Can request device removal (sends request to HR)
- Cannot add devices manually (only via check-in flow)
```

**US-FACE-006: Manage Employee Devices (HR/Admin)**
```
As an HR/Admin,
I want to manage which devices employees can use,
So that I maintain security and prevent unauthorized access.

Acceptance Criteria:
- HR dashboard → Device Management
- List shows: All device registration requests
- Per request: Employee name, Device ID, OS, Requested date
- HR can: Approve, Reject (with reason), Revoke existing
- Approved devices added to employee's whitelist
- Revoked devices immediately blocked from check-in
- Email notification sent to employee on approval/rejection
```

#### 5.3.4 Functional Requirements

**FR-FACE-001: Face Recognition Technology**
- Library: face-api.js or TensorFlow.js (browser-based)
- Or: OpenCV + dlib (native, more accurate)
- Model: FaceNet or similar (generates 128-dimensional embedding)
- Liveness detection: Optional (blink detection, head movement)

**FR-FACE-002: Face Registration Process**
```
1. Capture Images:
   - Front view (straight)
   - Left profile (45° turn)
   - Right profile (45° turn)
   
2. Face Detection:
   - Detect face in each image
   - Verify face size (not too small/large)
   - Check face alignment
   
3. Generate Embeddings:
   - Extract 128-dim vector from each image
   - Average embeddings → Final embedding
   
4. Store Securely:
   - Encrypt embedding (AES-256)
   - Store in FaceEmbedding model
   - Delete captured images (don't store raw photos)
```

**FR-FACE-003: Face Verification Process**
```
1. Capture Live Photo:
   - Camera activates
   - Capture single photo
   - Detect face in photo
   
2. Generate Embedding:
   - Extract 128-dim vector from photo
   
3. Compare with Stored:
   - Fetch employee's stored embedding
   - Calculate Euclidean distance
   - Distance < threshold → Match
   
4. Verify:
   - Threshold: 0.6 (configurable)
   - Confidence = (1 - distance) × 100
   - Minimum confidence: 85%
   
5. Result:
   - Match → Check-in successful
   - No match → Retry or fallback
```

**FR-FACE-004: Device Fingerprinting**
- Collect device information:
  ```javascript
  {
    os: "Windows 10",
    osVersion: "21H2",
    browser: "Electron",
    browserVersion: "28.0.0",
    cpuCores: 8,
    ram: "16GB",
    screenResolution: "1920x1080",
    timezone: "Asia/Kolkata",
    language: "en-US",
    macAddress: "XX:XX:XX:XX:XX:XX"  // Hashed
  }
  ```
- Generate device fingerprint: `SHA256(os + cpuCores + macAddress + ...)`
- Store in DeviceAssignment model

**FR-FACE-005: Device Assignment Model**
```python
class DeviceAssignment(models.Model):
    employee = ForeignKey(User)
    device_id = CharField(max_length=64, unique=True)  # SHA256 hash
    device_name = CharField(max_length=100)  # "Raju's Laptop"
    os_info = CharField(max_length=100)
    registered_at = DateTimeField(auto_now_add=True)
    last_used_at = DateTimeField(null=True)
    status = CharField(choices=[
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('revoked', 'Revoked'),
    ])
    approved_by = ForeignKey(User, null=True, related_name='approved_devices')
    approved_at = DateTimeField(null=True)
```

**FR-FACE-006: FaceEmbedding Model**
```python
class FaceEmbedding(models.Model):
    employee = OneToOneField(User)
    embedding = BinaryField()  # Encrypted 128-dim vector
    registered_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    registration_device = CharField(max_length=64)
    
    # Metadata
    registration_photos_count = IntegerField(default=3)
    last_verification_at = DateTimeField(null=True)
    verification_attempts = IntegerField(default=0)
    verification_failures = IntegerField(default=0)
```

**FR-FACE-007: Face Verification Audit**
```python
class FaceVerificationLog(models.Model):
    employee = ForeignKey(User)
    attempt_at = DateTimeField(auto_now_add=True)
    device_id = CharField(max_length=64)
    result = CharField(choices=[
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('fallback', 'Fallback Used'),
    ])
    confidence = DecimalField(max_digits=5, decimal_places=2, null=True)  # 0-100
    failure_reason = CharField(max_length=200, null=True)
    ip_address = GenericIPAddressField()
```

**FR-FACE-008: Fallback Logic**
```
Verification Failed 3 times in a row
  ↓
Check device trust:
  IF device is trusted AND on office IP:
      Allow manual check-in (button click)
  ELSE:
      Block check-in
      Send notification to manager for approval
```

**FR-FACE-009: Camera Permissions**
- Request camera permission on first use
- Handle permission denied gracefully
- Show clear error message if camera unavailable
- Offer settings link to enable camera
- Test camera before verification (show preview)

#### 5.3.5 Non-Functional Requirements

**NFR-FACE-001: Accuracy**
- False acceptance rate (FAR): <1%
- False rejection rate (FRR): <2%
- Confidence threshold tunable (default 85%)

**NFR-FACE-002: Performance**
- Registration time: <10 seconds (3 photos)
- Verification time: <3 seconds
- Embedding generation: <1 second

**NFR-FACE-003: Security**
- Face embeddings encrypted (AES-256)
- No raw photos stored
- HTTPS for all API calls
- Device fingerprints hashed

**NFR-FACE-004: Privacy**
- Employees control face data (can delete anytime)
- Face used only for attendance (not surveillance)
- Clear privacy policy displayed during registration
- Comply with GDPR/data protection laws

**NFR-FACE-005: Robustness**
- Works in varying lighting conditions
- Tolerates glasses, facial hair changes
- Age-invariant (embeddings valid for years)
- Multi-device support (embedding works across devices)

---


### 5.4 AI Assistant & Proactive Notifications

#### 5.4.1 Overview

The AI Assistant transforms SmartPunch from a reactive tool into a proactive companion that guides employees throughout their workday. It uses rule-based logic and optional machine learning to deliver contextual, timely suggestions without being intrusive.

#### 5.4.2 Key Features

**Proactive Reminders:**
- Morning greeting with quick check-in
- Break reminders based on work duration
- Lunch suggestions
- Check-out reminders
- Weekend wishes

**Context-Aware Messages:**
- Personalized greetings ("Good morning, Ace!")
- Contextual mood (late arrival → supportive message, not punitive)
- Achievement celebrations
- Birthday wishes
- Salary credited notifications

**Smart Suggestions:**
- "You've worked 4 hours, take a break?"
- "Office hours ending, check out?"
- "Tomorrow is a holiday, enjoy!"

**Non-Intrusive Design:**
- Small toast notifications (disappear after 5 seconds)
- Critical reminders persist until addressed
- Respects Do Not Disturb mode
- No forced interruptions

####  5.4.3 User Stories

**US-AI-001: Morning Greeting & Check-in**
```
As an Employee,
I want a friendly morning greeting when I start my computer,
So that I feel welcomed and can quickly check in.

Acceptance Criteria:
- Notification appears within 30 seconds of app start (if between 8-11 AM)
- Message: "Good morning, Ace! 👋 Ready to start your day?"
- Button: "Start My Day"
- Clicking button triggers face recognition check-in
- If already checked in: "Welcome back! You're already checked in."
- Greeting adapts to time: Morning (6-12), Afternoon (12-6), Evening (6-12)
```

**US-AI-002: Break Reminders**
```
As an Employee,
I want reminders to take breaks,
So that I don't work continuously for too long.

Acceptance Criteria:
- After 2 hours of continuous work (Available status) → Tea break reminder
- Message: "☕ You've been working for 2 hours. Coffee break?"
- Buttons: [Take Break] [Remind in 15 min] [Dismiss]
- If dismissed: Don't remind again until next continuous work session
- If "Remind in 15 min": Show reminder again after 15 min
- Lunch reminder at 1:00 PM if no break taken yet
```

**US-AI-003: Check-out Reminder**
```
As an Employee,
I want a reminder to check out when office hours end,
So that I don't forget to mark my attendance.

Acceptance Criteria:
- At 5:30 PM: "🎯 You're close to full day. 25 min remaining."
- At 6:00 PM: "✅ You've completed your work hours. Check out?"
- Buttons: [Check Out] [Working OT]
- If working OT without approval: "⚠️ You don't have OT approval. Continue?"
- If checked out: No more reminders
```

**US-AI-004: Achievement Celebrations**
```
As an Employee,
I want recognition when I achieve milestones,
So that I feel motivated and appreciated.

Acceptance Criteria:
- 100% attendance month: "🎉 Perfect attendance this month! Excellent work!"
- 100 perfect attendance days: "🏆 100 days of perfect attendance! You're a star!"
- Consistent early arrival: "⭐ You've been early every day this week!"
- No specific rewards, just positive reinforcement
```

**US-AI-005: Birthday Wishes**
```
As an Employee,
I want birthday wishes from the system,
So that I feel special on my birthday.

Acceptance Criteria:
- On birthday (from EmployeeProfile.date_of_birth):
- Morning notification: "🎂 Happy Birthday, Ace! Everyone at Arraafi wishes you a wonderful year ahead!"
- Notification stays visible (doesn't auto-dismiss)
- Plays birthday sound (optional)
- Shown to all team members: "Today is Raju's birthday! 🎉"
```

**US-AI-006: Leave/Request Status Updates**
```
As an Employee,
I want real-time notifications when my requests are approved/rejected,
So that I stay informed without checking the dashboard.

Acceptance Criteria:
- Leave approved: "🌴 Great news! Your leave request (Dec 5-7) has been approved."
- Leave rejected: "❌ Your leave request (Dec 5-7) was not approved. Reason: [reason]"
- WFH approved: "🏠 Your WFH request (Dec 10) has been approved."
- OT approved: "💪 Your overtime request has been approved. Keep up the great work!"
- Notification links to request details page
```

**US-AI-007: Smart Context-Aware Messages**
```
As an Employee,
I want messages that adapt to my situation,
So that the system feels understanding rather than robotic.

Acceptance Criteria:
- Late arrival: "Good morning, Ace! Looks like today started a little later. Have a productive day!"
  (Not: "You're late!")
- Sick leave: "Hope you feel better soon, Ace. Take care!"
- Friday: "Happy Friday! You've had a great week. Enjoy your weekend!"
- Monday: "Good morning! Ready for a productive week?"
- Holiday tomorrow: "Tomorrow is Independence Day. Enjoy your holiday!"
```

#### 5.4.4 Functional Requirements

**FR-AI-001: Rule-Based Engine**
```javascript
// Morning Greeting Rule
if (timeNow >= 8:00 && timeNow <= 11:00 && !checkedInToday) {
    showNotification({
        title: `Good morning, ${employeeName}!`,
        body: "Ready to start your day?",
        actions: [{ text: "Start My Day", action: "check-in" }]
    });
}

// Break Reminder Rule
if (statusAvailableDuration >= 120min && !onBreak && breaksTakenToday < 2) {
    showNotification({
        title: "Time for a break!",
        body: "You've been working for 2 hours. Coffee? ☕",
        actions: [
            { text: "Take Break", action: "start-break" },
            { text: "Remind in 15 min", action: "snooze-15" },
            { text: "Dismiss", action: "dismiss" }
        ]
    });
}

// Check-out Reminder Rule
if (timeNow >= 18:00 && checkedInToday && !checkedOutToday) {
    if (hasApprovedOT) {
        showNotification({
            title: "Overtime approved",
            body: "🔥 Keep up the great work!",
            actions: [{ text: "End OT", action: "check-out" }]
        });
    } else {
        showNotification({
            title: "Office hours are over",
            body: "Would you like to check out?",
            actions: [
                { text: "Check Out", action: "check-out" },
                { text: "Later", action: "dismiss" }
            ]
        });
    }
}
```

**FR-AI-002: Machine Learning (Optional - Future)**
- Learn employee patterns:
  - Typical break times
  - Usual work hours
  - Preferred notification times
- Adapt reminder timing based on learned patterns
- Predict when employee likely to need reminders
- Not required for MVP (rule-based sufficient)

**FR-AI-003: Notification Manager**
```javascript
class NotificationManager {
    // Queue to prevent notification spam
    queue = [];
    maxConcurrentNotifications = 1;
    
    // Notification priorities
    priorities = {
        critical: 3,   // Immediate (check-out reminder)
        high: 2,       // Important (leave approved)
        normal: 1,     // Standard (break reminder)
        low: 0         // Nice-to-have (achievement)
    };
    
    // Show notification with priority
    show(notification) {
        if (this.isDNDMode()) {
            if (notification.priority < priorities.critical) {
                return; // Skip non-critical in DND
            }
        }
        
        this.queue.push(notification);
        this.processQueue();
    }
    
    // Snooze handling
    snooze(notificationId, minutes) {
        setTimeout(() => {
            this.reshowNotification(notificationId);
        }, minutes * 60 * 1000);
    }
}
```

**FR-AI-004: Personalization**
- Store employee preferences:
  ```python
  class EmployeePreferences(models.Model):
      employee = OneToOneField(User)
      preferred_name = CharField(max_length=50)  # "Ace" instead of "Raju"
      enable_break_reminders = BooleanField(default=True)
      enable_achievement_notifications = BooleanField(default=True)
      break_reminder_frequency = IntegerField(default=120)  # minutes
      notification_sound = BooleanField(default=True)
  ```

**FR-AI-005: Context Detection**
```python
def get_greeting_context(employee, current_time):
    """Generate context-aware greeting message"""
    
    # Check if late
    if current_time > datetime.time(10, 0):
        return f"Good morning, {employee.first_name}! "\
               f"Looks like today started a little later. Have a productive day!"
    
    # Check if birthday
    if is_birthday(employee):
        return f"🎂 Happy Birthday, {employee.first_name}! "\
               f"Everyone at Arraafi wishes you a wonderful year ahead!"
    
    # Check if Monday
    if current_time.weekday() == 0:
        return f"Good morning, {employee.first_name}! Ready for a productive week?"
    
    # Check if Friday
    if current_time.weekday() == 4:
        return f"Happy Friday, {employee.first_name}! "\
               f"You've had a great week. Enjoy your weekend!"
    
    # Default
    return f"Good morning, {employee.first_name}! 👋 Ready to start your day?"
```

**FR-AI-006: Notification Persistence**
- First notification: Auto-dismiss after 5 seconds
- Second notification (same type): Persist until action taken
- Critical notifications: Never auto-dismiss
- Store notification history in database

#### 5.4.5 Non-Functional Requirements

**NFR-AI-001: User Experience**
- Notifications feel helpful, not annoying
- Never interrupt critical work
- Respect DND mode
- Maximum 5 notifications per day (excluding critical)

**NFR-AI-002: Performance**
- Notification delivery: <500ms
- Rule evaluation: <100ms
- No battery drain from notification checks

**NFR-AI-003: Personalization**
- Messages use employee's preferred name
- Tone matches employee's interaction history
- Frequency adapts to employee preferences

---

## 6. Database Schema

### 6.1 Phase 1 - New Tables

#### Team
- id (PK)
- name (VARCHAR, UNIQUE)
- department (VARCHAR)
- team_leader_id (FK → User)
- description (TEXT)
- created_at (DATETIME)
- is_active (BOOLEAN)

#### TeamMembership
- id (PK)
- team_id (FK → Team)
- employee_id (FK → User)
- joined_at (DATETIME)
- is_active (BOOLEAN)
- UNIQUE(team_id, employee_id)

#### PayrollCycle
- id (PK)
- month (INT)
- year (INT)
- start_date (DATE)
- end_date (DATE)
- status (ENUM: draft, finalized, paid)
- total_employees (INT)
- total_net_amount (DECIMAL)
- processed_by_id (FK → User)
- processed_at (DATETIME)
- finalized_at (DATETIME)
- UNIQUE(month, year)

#### PayrollEntry
- id (PK)
- payroll_cycle_id (FK → PayrollCycle)
- employee_id (FK → User)
- base_salary (DECIMAL)
- working_days (INT)
- present_days (INT)
- absent_days (INT)
- half_days (INT)
- paid_leaves_taken (DECIMAL)
- unpaid_leaves_taken (DECIMAL)
- ot_hours (DECIMAL)
- ot_amount (DECIMAL)
- total_deductions (DECIMAL)
- gross_salary (DECIMAL)
- manual_adjustment (DECIMAL)
- adjustment_reason (TEXT)
- net_salary (DECIMAL)
- UNIQUE(payroll_cycle_id, employee_id)

#### LeaveBalance
- id (PK)
- employee_id (FK → User)
- year (INT)
- sick_leaves_total (INT, default 6)
- casual_leaves_total (INT, default 6)
- earned_leaves_total (INT, default 6)
- sick_leaves_used (DECIMAL)
- casual_leaves_used (DECIMAL)
- earned_leaves_used (DECIMAL)
- total_leaves_remaining (DECIMAL)
- UNIQUE(employee_id, year)

### 6.2 Phase 2 - New Tables

#### PresenceLog
- id (PK)
- employee_id (FK → User)
- status (ENUM: available, away, on_break, dnd, offline)
- changed_at (DATETIME)
- changed_by (ENUM: auto, manual, system)
- duration_seconds (INT, nullable)

#### FaceEmbedding
- id (PK)
- employee_id (FK → User, UNIQUE)
- embedding (BINARY)
- registered_at (DATETIME)
- registration_device (VARCHAR)

#### DeviceAssignment
- id (PK)
- employee_id (FK → User)
- device_id (VARCHAR, UNIQUE)
- device_name (VARCHAR)
- os_info (VARCHAR)
- status (ENUM: pending, active, revoked)
- registered_at (DATETIME)
- approved_by_id (FK → User, nullable)

#### FaceVerificationLog
- id (PK)
- employee_id (FK → User)
- attempt_at (DATETIME)
- device_id (VARCHAR)
- result (ENUM: success, failure, fallback)
- confidence (DECIMAL, nullable)
- ip_address (INET)

#### EmployeePreferences
- id (PK)
- employee_id (FK → User, UNIQUE)
- preferred_name (VARCHAR)
- enable_break_reminders (BOOLEAN)
- enable_achievement_notifications (BOOLEAN)
- notification_sound (BOOLEAN)

### 6.3 Existing Tables - Extensions

#### EmployeeProfile
- Add: is_team_leader (BOOLEAN)
- Add: base_salary (DECIMAL)
- Add: ot_rate (DECIMAL)
- Add: bank_account_number (VARCHAR)
- Add: bank_ifsc_code (VARCHAR)
- Add: current_status (VARCHAR)
- Add: last_status_change (DATETIME)
- Add: last_activity_at (DATETIME)

---

## 7. API Specifications

[API documentation would include detailed endpoint specs - omitted for brevity but follows RESTful patterns shown in functional requirements]

---

## 8. Security Requirements

### 8.1 Data Encryption
- Face embeddings: AES-256 encryption at rest
- Payroll data: Encrypted in database
- Session tokens: Encrypted, HTTPOnly cookies
- HTTPS required for all API communication

### 8.2 Access Control
- Role-based permissions enforced at API level
- JWT tokens for desktop app authentication
- Device fingerprints for trusted devices
- IP whitelist for office network validation

### 8.3 Privacy
- Face images deleted after embedding generation
- No screenshot or keystroke logging
- Presence data restricted to authorized users
- GDPR compliance for data deletion requests

### 8.4 Audit Trail
- All payroll actions logged
- Face verification attempts logged
- Device registrations logged
- Team management changes logged

---

## 9. Performance Requirements

### 9.1 Desktop Application
- Startup time: <3 seconds
- Idle RAM: 40-80 MB
- Active RAM: <300 MB
- CPU idle: ~0%
- Face verification: <3 seconds

### 9.2 Backend API
- API response time: <500ms (P95)
- Payroll calculation: <60 seconds for 100 employees
- Real-time status updates: <3 seconds
- Database queries: <100ms (P95)

### 9.3 Scalability
- Support 500+ concurrent users
- Support 1000+ employees
- Support 100+ teams
- Handle 10,000+ presence status changes/day

---

## 10. Testing Strategy

### 10.1 Phase 1 Testing
- Unit tests for payroll calculations
- Integration tests for team management
- API endpoint tests
- Database migration tests
- Performance tests (payroll with large datasets)

### 10.2 Phase 2 Testing
- Desktop app unit tests
- Face recognition accuracy tests
- System idle detection tests
- Notification delivery tests
- Device fingerprinting tests
- End-to-end user flow tests
- Cross-platform compatibility tests (Windows)
- Security penetration tests

### 10.3 User Acceptance Testing
- Beta testing with 10-20 employees
- Feedback collection via surveys
- Bug reporting mechanism
- Performance monitoring in production

---

## 11. Appendices

### 11.1 Glossary
[Already defined in section 1.3]

### 11.2 Technology Stack

**Backend:**
- Django 4.2+
- Python 3.10+
- MySQL 8.0+
- Redis (for caching/WebSockets)

**Frontend (Web):**
- HTML5, CSS3, JavaScript
- Bootstrap 5
- jQuery (existing)

**Desktop:**
- Electron 28+
- Node.js 20+
- face-api.js or OpenCV

**Infrastructure:**
- AWS EC2 (existing)
- S3 (for file storage)
- CloudFront (CDN)

### 11.3 Timeline Summary

**Phase 1:** 5-7 weeks
- Sprint 1: Team Management (2-3 weeks)
- Sprint 2: Payroll System (3-4 weeks)

**Phase 2:** 12-16 weeks
- Sprint 3: Desktop Foundation (3-4 weeks)
- Sprint 4: Presence Tracking (2-3 weeks)
- Sprint 5: Face Recognition (3-4 weeks)
- Sprint 6: AI Assistant (2-3 weeks)
- Sprint 7: Analytics (2 weeks)

**Total:** 17-23 weeks (~4-6 months)

---

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | | | |
| Technical Lead | | | |
| QA Lead | | | |

---

**END OF DOCUMENT**
