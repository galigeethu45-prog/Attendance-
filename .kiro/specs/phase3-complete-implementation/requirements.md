# Requirements Document

## Introduction

This document specifies the requirements for implementing Phase 3 features of the attendance management system. The database models have been completed and migrated (migration 0021), but all user-facing features need implementation. This includes multi-date selection for leave/WFH requests, manager role functionality, hierarchical approval workflows, onsite/client visit requests, flexible break times, and an employee attendance dashboard for HR.

The system is a Django-based attendance management application using Asia/Kolkata timezone (IST = UTC+5:30). All features must integrate seamlessly with existing functionality without disrupting current operations.

## Glossary

- **System**: The Django-based attendance management application
- **Employee**: A regular user of the system who can mark attendance, request leaves, and submit WFH/onsite requests
- **Team_Leader**: An employee with authority to add comments on leave and WFH requests
- **Manager**: An employee with HR-level dashboard access who can approve/reject leave and WFH requests (one step below HR in hierarchy)
- **HR**: Human Resources personnel with final approval authority and full system access
- **Admin**: System administrator with superuser privileges
- **Leave_Request**: A request by an employee for time off from work
- **WFH_Request**: A request by an employee to work from home
- **Onsite_Request**: A request by an employee to visit a client location or attend online client meetings from office
- **Multi_Date_Selection**: The ability to select non-consecutive dates (e.g., 21st, 25th, 30th) for leave or WFH
- **Hierarchical_Approval**: A multi-step approval process: Team Leader comments → Manager approves/rejects → HR final decision
- **Flexible_Break**: The ability to take breaks outside normal time windows when on approved onsite visits
- **Break_Time_Window**: Normal break periods (10-11 AM for morning tea, 1-1:45 PM for lunch, 4-4:45 PM for evening tea)
- **Attendance_Dashboard**: An HR view showing individual employee statistics (present days, absent days, late arrivals, half-days, total hours)
- **IST**: Indian Standard Time (Asia/Kolkata timezone, UTC+5:30)
- **Profile_Photo**: Employee profile picture displayed throughout the system
- **Mobile_Access**: Access to the system from mobile devices (restricted for regular employees, allowed for HR/Admin/Manager)

## Requirements

### Requirement 1: Multi-Date Selection for Leave Requests

**User Story:** As an employee, I want to select non-consecutive dates for my leave requests using either a calendar picker or manual entry, so that I can request leave for specific days without taking consecutive days off.

#### Acceptance Criteria

1. WHEN an employee accesses the leave request form, THE System SHALL display both a calendar picker and a manual date entry field
2. WHEN an employee selects dates using the calendar picker, THE System SHALL allow selection of non-consecutive dates
3. WHEN an employee enters dates manually, THE System SHALL accept comma-separated dates in YYYY-MM-DD format
4. WHEN an employee submits a leave request with selected dates, THE System SHALL store the dates in the selected_dates JSON field
5. WHEN an employee submits a leave request with a date range (start_date and end_date), THE System SHALL maintain backward compatibility with existing functionality
6. THE System SHALL calculate total_days correctly for both selected dates and date ranges
7. WHEN displaying a leave request, THE System SHALL show all dates covered by the request (whether selected dates or date range)
8. THE Leave_Request_View SHALL validate that selected dates are in the future
9. THE Leave_Request_View SHALL prevent duplicate date selection
10. THE Leave_Request_View SHALL update the leave_request view to handle the selected_dates JSON field

### Requirement 2: Multi-Date Selection for WFH Requests

**User Story:** As an employee, I want to select non-consecutive dates for my WFH requests using either a calendar picker or manual entry, so that I can work from home on specific days without consecutive WFH days.

#### Acceptance Criteria

1. WHEN an employee accesses the WFH request form, THE System SHALL display both a calendar picker and a manual date entry field
2. WHEN an employee selects dates using the calendar picker, THE System SHALL allow selection of non-consecutive dates
3. WHEN an employee enters dates manually, THE System SHALL accept comma-separated dates in YYYY-MM-DD format
4. WHEN an employee submits a WFH request with selected dates, THE System SHALL store the dates in the selected_dates JSON field
5. WHEN an employee submits a WFH request with a date range (start_date and end_date), THE System SHALL maintain backward compatibility with existing functionality
6. THE System SHALL calculate total_days correctly for both selected dates and date ranges
7. WHEN displaying a WFH request, THE System SHALL show all dates covered by the request (whether selected dates or date range)
8. THE WFH_Request_View SHALL validate that selected dates are in the future
9. THE WFH_Request_View SHALL prevent duplicate date selection
10. THE WFH_Request_View SHALL update the wfh_request view to handle the selected_dates JSON field

### Requirement 3: Manager Role Access and Permissions

**User Story:** As a manager, I want to have the same dashboard access as HR but with approval authority one step below HR, so that I can manage my team's leave and WFH requests effectively.

#### Acceptance Criteria

1. WHEN a user has the role 'manager', THE System SHALL grant access to all HR dashboard features
2. WHEN a user has the role 'manager', THE System SHALL set the is_hr flag to True in the EmployeeProfile
3. WHEN a manager accesses the HR dashboard, THE System SHALL display pending leave requests requiring manager approval
4. WHEN a manager accesses the HR dashboard, THE System SHALL display pending WFH requests requiring manager approval
5. WHEN a manager accesses the HR dashboard, THE System SHALL display employee attendance statistics
6. WHEN a manager accesses the system from a mobile device, THE System SHALL allow full access (not blocked like regular employees)
7. THE System SHALL display the manager's profile photo in the dashboard header
8. WHEN HR changes an employee's role to 'manager', THE System SHALL update the is_hr flag automatically
9. THE System SHALL distinguish between manager and HR roles in audit logs
10. WHEN a manager approves or rejects a request, THE System SHALL route it to HR for final decision

### Requirement 4: Hierarchical Approval Workflow for Leave Requests

**User Story:** As an employee, I want my leave requests to go through a structured approval chain (Team Leader → Manager → HR), so that all stakeholders can review and approve my request.

#### Acceptance Criteria

1. WHEN an employee submits a leave request, THE System SHALL set the status to 'pending' and notify the Team Leader
2. WHEN a Team Leader views a pending leave request, THE System SHALL display a comment field
3. WHEN a Team Leader adds a comment to a leave request, THE System SHALL store the comment in tl_comment field and make it visible to Manager and HR
4. WHEN a Manager views a leave request with TL comments, THE System SHALL display the TL comment
5. WHEN a Manager approves a leave request, THE System SHALL set manager_approved to True, store the manager's comment, record the approver and timestamp, and notify HR
6. WHEN a Manager rejects a leave request, THE System SHALL set the status to 'rejected', store the manager's comment, and notify the employee
7. WHEN HR views a manager-approved leave request, THE System SHALL display the full approval chain (TL comment → Manager approval)
8. WHEN HR gives final approval, THE System SHALL set the status to 'approved' and notify the employee
9. WHEN HR rejects a manager-approved request, THE System SHALL set the status to 'rejected' and notify the employee and manager
10. THE System SHALL create audit log entries for each step in the approval chain
11. THE System SHALL display the approval status and chain in the employee's leave request history
12. WHEN displaying the approval workflow UI, THE System SHALL show TL → Manager → HR chain with status indicators

### Requirement 5: Hierarchical Approval Workflow for WFH Requests

**User Story:** As an employee, I want my WFH requests to go through a structured approval chain (Team Leader → Manager → HR), so that all stakeholders can review and approve my request.

#### Acceptance Criteria

1. WHEN an employee submits a WFH request, THE System SHALL set the status to 'pending' and notify the Team Leader
2. WHEN a Team Leader views a pending WFH request, THE System SHALL display a comment field
3. WHEN a Team Leader adds a comment to a WFH request, THE System SHALL store the comment in tl_comment field and make it visible to Manager and HR
4. WHEN a Manager views a WFH request with TL comments, THE System SHALL display the TL comment
5. WHEN a Manager approves a WFH request, THE System SHALL set manager_approved to True, store the manager's comment, record the approver and timestamp, and notify HR
6. WHEN a Manager rejects a WFH request, THE System SHALL set the status to 'rejected', store the manager's comment, and notify the employee
7. WHEN HR views a manager-approved WFH request, THE System SHALL display the full approval chain (TL comment → Manager approval)
8. WHEN HR gives final approval, THE System SHALL set the status to 'approved' and notify the employee
9. WHEN HR rejects a manager-approved request, THE System SHALL set the status to 'rejected' and notify the employee and manager
10. THE System SHALL create audit log entries for each step in the approval chain
11. THE System SHALL display the approval status and chain in the employee's WFH request history
12. WHEN displaying the approval workflow UI, THE System SHALL show TL → Manager → HR chain with status indicators

### Requirement 6: Onsite Request Creation

**User Story:** As an employee, I want to request approval for onsite client visits or online client meetings from office, so that I can get advance approval and enable flexible break times during client interactions.

#### Acceptance Criteria

1. WHEN an employee accesses the onsite request form, THE System SHALL display fields for visit_type, visit_date, client_name, location, purpose, and expected_duration
2. WHEN an employee selects visit_type, THE System SHALL offer two options: 'Onsite Visit (Physical)' and 'Online Client Meeting (From Office)'
3. WHEN an employee submits an onsite request, THE System SHALL validate that visit_date is in the future
4. WHEN an employee submits an onsite request, THE System SHALL set the status to 'pending' and notify the Manager
5. THE System SHALL store the onsite request in the OnsiteRequest model
6. THE System SHALL create an audit log entry for the onsite request creation
7. WHEN an employee views their onsite request history, THE System SHALL display all submitted requests with status
8. THE System SHALL display the employee's profile photo in the onsite request form
9. THE Onsite_Request_Form SHALL require all fields except hr_comment and manager_comment
10. THE System SHALL validate that expected_duration is provided in a readable format

### Requirement 7: Onsite Request Approval Workflow

**User Story:** As a manager, I want to review and approve onsite requests from my team, so that employees can visit clients or attend online meetings with proper authorization.

#### Acceptance Criteria

1. WHEN a Manager views pending onsite requests, THE System SHALL display all requests awaiting manager approval
2. WHEN a Manager approves an onsite request, THE System SHALL set manager_approved to True, record the approver and timestamp, and route to HR for final approval
3. WHEN a Manager rejects an onsite request, THE System SHALL set the status to 'rejected', store the manager's comment, and notify the employee
4. WHEN HR views manager-approved onsite requests, THE System SHALL display the manager's approval details
5. WHEN HR gives final approval, THE System SHALL set the status to 'approved' and notify the employee
6. WHEN HR rejects a manager-approved onsite request, THE System SHALL set the status to 'rejected' and notify the employee and manager
7. THE System SHALL create audit log entries for each approval step
8. THE System SHALL display the approval chain (Manager → HR) in the onsite request details
9. WHEN displaying pending onsite requests, THE System SHALL show employee profile photos
10. THE System SHALL allow HR to override manager decisions

### Requirement 8: Onsite Visit Check-In and Check-Out Tracking

**User Story:** As an employee with an approved onsite request, I want to check in and check out for my client visit, so that my attendance is tracked accurately during onsite work.

#### Acceptance Criteria

1. WHEN an employee has an approved onsite request for today, THE System SHALL display a check-in button for the onsite visit
2. WHEN an employee clicks the onsite check-in button, THE System SHALL record the actual_check_in timestamp
3. WHEN an employee has checked in for an onsite visit, THE System SHALL display a check-out button
4. WHEN an employee clicks the onsite check-out button, THE System SHALL record the actual_check_out timestamp
5. THE System SHALL create audit log entries for onsite check-in and check-out
6. WHEN displaying onsite request details, THE System SHALL show actual check-in and check-out times if recorded
7. THE System SHALL allow onsite check-in and check-out from any location (not restricted to office network)
8. WHEN an employee checks in for an onsite visit, THE System SHALL enable flexible break times for that day
9. THE System SHALL validate that check-out time is after check-in time
10. THE System SHALL calculate total onsite hours based on actual check-in and check-out times

### Requirement 9: Flexible Break Times for Onsite Visits

**User Story:** As an employee on an approved onsite visit or online client meeting, I want to take breaks at any time during the day, so that I can manage my time flexibly during client interactions.

#### Acceptance Criteria

1. WHEN an employee has an approved onsite request for today, THE System SHALL bypass normal break time window restrictions
2. WHEN an employee on an onsite visit attempts to start a tea break, THE System SHALL allow the break regardless of the current time (except after 5 PM)
3. WHEN an employee on an onsite visit attempts to start a lunch break, THE System SHALL allow the break regardless of the current time (except after 5 PM)
4. WHEN an employee on an online client meeting from office attempts to start a break, THE System SHALL allow the break regardless of the current time (except after 5 PM)
5. THE System SHALL check for active approved onsite requests before validating break time windows
6. WHEN an employee without an approved onsite request attempts to start a break, THE System SHALL enforce normal break time windows
7. THE System SHALL maintain the break count limits (2 tea breaks, 1 lunch break) even for onsite visits
8. THE System SHALL maintain the break duration limits (15 minutes for tea, 45 minutes for lunch) even for onsite visits
9. THE System SHALL create audit log entries indicating flexible break usage during onsite visits
10. WHEN displaying break buttons, THE System SHALL show a message indicating flexible break times are enabled for onsite visits

### Requirement 10: Employee Attendance Dashboard for HR

**User Story:** As an HR personnel, I want to view individual employee attendance statistics with filtering and export capabilities, so that I can monitor and analyze employee attendance patterns.

#### Acceptance Criteria

1. WHEN HR accesses the employee attendance dashboard, THE System SHALL display a list of all employees with their profile photos
2. WHEN HR selects an employee, THE System SHALL display statistics including present days, absent days, late arrivals, half-days, and total hours
3. WHEN HR applies a date range filter, THE System SHALL recalculate statistics for the selected period
4. WHEN HR applies a department filter, THE System SHALL display only employees from the selected department
5. WHEN HR applies an employee filter, THE System SHALL display statistics for the selected employee
6. WHEN HR clicks the export button, THE System SHALL generate a CSV file with attendance statistics
7. THE System SHALL display the employee's profile photo in the statistics view
8. THE System SHALL calculate present days as the count of attendance records with status 'present'
9. THE System SHALL calculate absent days as the count of attendance records with status 'absent'
10. THE System SHALL calculate late arrivals as the count of attendance records with status 'late' or 'half-day'
11. THE System SHALL calculate total hours as the sum of total_work_hours from all attendance records
12. THE System SHALL display statistics in a clear, tabular format
13. WHEN HR views the dashboard, THE System SHALL show summary statistics for all employees
14. THE System SHALL allow HR to drill down into individual employee details
15. THE System SHALL display the date range for which statistics are calculated

### Requirement 11: UI Integration and Dark Theme Consistency

**User Story:** As a user, I want all new features to match the existing dark theme and UI patterns, so that the system maintains a consistent look and feel.

#### Acceptance Criteria

1. THE System SHALL apply the existing dark theme CSS to all new templates
2. THE System SHALL use consistent button styles across all new forms
3. THE System SHALL use consistent card layouts for displaying information
4. THE System SHALL use consistent color schemes for status indicators (green for approved, red for rejected, yellow for pending)
5. THE System SHALL display profile photos in a consistent circular format throughout the system
6. THE System SHALL use consistent font sizes and spacing
7. THE System SHALL use consistent form field styling
8. THE System SHALL use consistent table styling for data display
9. THE System SHALL use consistent modal/dialog styling for confirmations
10. THE System SHALL maintain responsive design for mobile devices

### Requirement 12: Mobile Access Restrictions

**User Story:** As a system administrator, I want to restrict mobile access for regular employees while allowing HR, Admin, and Manager roles, so that attendance marking is controlled and onsite features are accessible to authorized personnel.

#### Acceptance Criteria

1. WHEN a regular employee accesses the system from a mobile device, THE System SHALL display a message indicating mobile access is restricted
2. WHEN an HR user accesses the system from a mobile device, THE System SHALL allow full access
3. WHEN an Admin user accesses the system from a mobile device, THE System SHALL allow full access
4. WHEN a Manager user accesses the system from a mobile device, THE System SHALL allow full access
5. THE System SHALL detect mobile devices using user agent strings
6. THE System SHALL allow regular employees to access the system from desktop browsers
7. THE System SHALL display an appropriate error message for blocked mobile access
8. THE System SHALL log mobile access attempts in the audit log
9. THE System SHALL provide a way for HR to temporarily override mobile restrictions if needed
10. THE System SHALL maintain mobile restrictions across all views and endpoints

### Requirement 13: Timezone Handling and IST Compliance

**User Story:** As a system administrator, I want all date and time operations to use Asia/Kolkata timezone (IST), so that attendance records and timestamps are accurate for the Indian office location.

#### Acceptance Criteria

1. THE System SHALL use Asia/Kolkata timezone for all datetime operations
2. WHEN displaying timestamps, THE System SHALL convert UTC times to IST
3. WHEN storing timestamps, THE System SHALL ensure timezone awareness
4. THE System SHALL display times in 12-hour format with AM/PM indicators
5. THE System SHALL validate that break time windows are enforced in IST
6. THE System SHALL calculate work hours using IST timestamps
7. THE System SHALL display dates in DD-MMM-YYYY format (e.g., 21-May-2026)
8. THE System SHALL handle daylight saving time transitions correctly (IST does not observe DST)
9. THE System SHALL ensure all date pickers use IST as the default timezone
10. THE System SHALL display timezone information (IST) in relevant UI elements

### Requirement 14: Audit Logging for New Features

**User Story:** As a system administrator, I want all actions related to new features to be logged in the audit log, so that I can track system usage and troubleshoot issues.

#### Acceptance Criteria

1. WHEN an employee submits a multi-date leave request, THE System SHALL create an audit log entry with action 'leave_request'
2. WHEN an employee submits a multi-date WFH request, THE System SHALL create an audit log entry with action 'wfh_request'
3. WHEN a Team Leader adds a comment to a request, THE System SHALL create an audit log entry
4. WHEN a Manager approves or rejects a request, THE System SHALL create an audit log entry with action 'leave_approve' or 'leave_reject'
5. WHEN HR gives final approval, THE System SHALL create an audit log entry
6. WHEN an employee submits an onsite request, THE System SHALL create an audit log entry
7. WHEN a Manager or HR approves an onsite request, THE System SHALL create an audit log entry
8. WHEN an employee checks in or out for an onsite visit, THE System SHALL create an audit log entry
9. WHEN an employee takes a flexible break during an onsite visit, THE System SHALL create an audit log entry indicating flexible break usage
10. WHEN HR accesses the employee attendance dashboard, THE System SHALL create an audit log entry
11. WHEN HR exports attendance statistics, THE System SHALL create an audit log entry
12. THE System SHALL include IP address, timestamp, user, and description in all audit log entries
13. THE System SHALL include target_user in audit log entries where applicable
14. THE System SHALL allow HR to view audit logs filtered by action type and date range

### Requirement 15: Error Handling and Validation

**User Story:** As a user, I want the system to validate my inputs and provide clear error messages, so that I can correct mistakes and successfully complete my tasks.

#### Acceptance Criteria

1. WHEN an employee submits a leave request with invalid dates, THE System SHALL display an error message indicating the issue
2. WHEN an employee submits a WFH request with dates in the past, THE System SHALL reject the request with an error message
3. WHEN an employee submits an onsite request with missing required fields, THE System SHALL display field-specific error messages
4. WHEN a Manager attempts to approve a request without adding a comment, THE System SHALL require a comment before proceeding
5. WHEN an employee attempts to select overlapping dates for leave requests, THE System SHALL display a warning
6. WHEN an employee attempts to take a break without checking in, THE System SHALL display an error message
7. WHEN an employee attempts to check out with an active break, THE System SHALL display a warning and require break end first
8. WHEN a database error occurs, THE System SHALL display a user-friendly error message and log the technical details
9. WHEN a network error occurs during form submission, THE System SHALL display a retry option
10. THE System SHALL validate all date inputs to ensure they are in the correct format
11. THE System SHALL validate all JSON fields to ensure they contain valid JSON data
12. THE System SHALL prevent SQL injection and XSS attacks through input validation
13. THE System SHALL display validation errors inline with form fields
14. THE System SHALL maintain form data when validation errors occur (no data loss)
15. THE System SHALL log all validation errors for debugging purposes

### Requirement 16: Notification System Integration

**User Story:** As a user, I want to receive notifications for approval actions and status changes, so that I stay informed about my requests and team activities.

#### Acceptance Criteria

1. WHEN an employee submits a leave request, THE System SHALL notify the Team Leader
2. WHEN a Team Leader adds a comment, THE System SHALL notify the Manager
3. WHEN a Manager approves a leave request, THE System SHALL notify HR and the employee
4. WHEN a Manager rejects a leave request, THE System SHALL notify the employee
5. WHEN HR gives final approval, THE System SHALL notify the employee
6. WHEN HR rejects a request, THE System SHALL notify the employee and Manager
7. WHEN an employee submits a WFH request, THE System SHALL notify the Team Leader
8. WHEN a Manager approves a WFH request, THE System SHALL notify HR and the employee
9. WHEN an employee submits an onsite request, THE System SHALL notify the Manager
10. WHEN a Manager approves an onsite request, THE System SHALL notify HR and the employee
11. THE System SHALL display notification count in the dashboard header
12. THE System SHALL mark notifications as read when viewed
13. THE System SHALL display notifications in chronological order (newest first)
14. THE System SHALL include relevant details in notification messages (employee name, request type, dates)
15. THE System SHALL allow users to view notification history

### Requirement 17: Backward Compatibility and Data Migration

**User Story:** As a system administrator, I want all new features to be backward compatible with existing data, so that the system continues to function without disruption.

#### Acceptance Criteria

1. WHEN the system processes existing leave requests without selected_dates, THE System SHALL use start_date and end_date for calculations
2. WHEN the system processes existing WFH requests without selected_dates, THE System SHALL use start_date and end_date for calculations
3. WHEN the system displays existing leave requests, THE System SHALL show the date range correctly
4. WHEN the system displays existing WFH requests, THE System SHALL show the date range correctly
5. THE System SHALL maintain all existing leave request functionality
6. THE System SHALL maintain all existing WFH request functionality
7. THE System SHALL maintain all existing attendance marking functionality
8. THE System SHALL maintain all existing break time functionality
9. THE System SHALL not require data migration for existing records
10. THE System SHALL handle null values in new fields gracefully
11. THE System SHALL maintain API compatibility for existing integrations
12. THE System SHALL maintain URL structure for existing views
13. THE System SHALL maintain database indexes for performance
14. THE System SHALL maintain existing user roles and permissions
15. THE System SHALL ensure migration 0021 is applied before using new features

### Requirement 18: Testing and Quality Assurance

**User Story:** As a developer, I want comprehensive testing for all new features, so that the system is reliable and bug-free in production.

#### Acceptance Criteria

1. THE System SHALL include unit tests for multi-date selection logic
2. THE System SHALL include unit tests for hierarchical approval workflow
3. THE System SHALL include unit tests for onsite request creation and approval
4. THE System SHALL include unit tests for flexible break time logic
5. THE System SHALL include unit tests for employee attendance dashboard calculations
6. THE System SHALL include integration tests for the complete approval workflow
7. THE System SHALL include integration tests for onsite check-in and check-out
8. THE System SHALL include integration tests for flexible break times during onsite visits
9. THE System SHALL include UI tests for multi-date picker functionality
10. THE System SHALL include UI tests for approval workflow interface
11. THE System SHALL include performance tests for dashboard queries with large datasets
12. THE System SHALL include security tests for input validation and authorization
13. THE System SHALL include tests for timezone handling and IST compliance
14. THE System SHALL include tests for mobile access restrictions
15. THE System SHALL achieve at least 80% code coverage for new features

