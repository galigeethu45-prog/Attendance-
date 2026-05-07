# Implementation Plan: Phase 3 Complete Implementation

## Overview

This implementation plan breaks down Phase 3 features into discrete, actionable tasks. The database models are already in place (migration 0021), so this focuses on implementing views, templates, and JavaScript integration for:

1. Multi-date selection for Leave/WFH requests
2. Hierarchical approval workflow (TL → Manager → HR)
3. Onsite/client visit requests with flexible breaks
4. Flexible break times during onsite visits
5. Employee attendance dashboard for HR
6. Manager role with HR-level access

**Technology Stack:** Django (Python), Bootstrap 5, Flatpickr.js, SQLite
**Timezone:** Asia/Kolkata (IST)

## Tasks

- [x] 1. Setup and Dependencies
  - Add Flatpickr.js library to static files (via CDN or download)
  - Verify Bootstrap 5 is available in base template
  - Create `static/js/multi-date-picker.js` file for date selection logic
  - Test that all static files are loading correctly
  - _Requirements: 1.1, 2.1, 11.1_

- [x] 2. Multi-Date Selection for Leave Requests
  - [x] 2.1 Update leave_request.html template with multi-date picker UI
    - Add date selection mode toggle (range vs specific dates)
    - Add Flatpickr calendar picker with `mode: "multiple"`
    - Add manual date entry textarea for comma-separated dates
    - Add hidden field for selected_dates JSON storage
    - Implement JavaScript to sync calendar picker and manual entry
    - Add mode toggle handler to show/hide appropriate fields
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [x] 2.2 Update leave_request view in attendance/views.py
    - Parse selected_dates from POST data
    - Validate date format (YYYY-MM-DD)
    - Validate dates are in the future
    - Store selected_dates as JSON in LeaveRequest model
    - Maintain backward compatibility with start_date/end_date
    - Calculate total_days using selected_dates if present
    - _Requirements: 1.4, 1.5, 1.6, 1.8, 1.9, 1.10_

  - [ ]* 2.3 Write unit tests for leave request multi-date selection
    - Test parsing of comma-separated dates
    - Test validation of future dates
    - Test JSON storage and retrieval
    - Test total_days calculation for selected dates
    - Test backward compatibility with date ranges
    - _Requirements: 18.1_

- [x] 3. Multi-Date Selection for WFH Requests
  - [x] 3.1 Update wfh_request.html template with multi-date picker UI
    - Add date selection mode toggle (range vs specific dates)
    - Add Flatpickr calendar picker with `mode: "multiple"`
    - Add manual date entry textarea for comma-separated dates
    - Add hidden field for selected_dates JSON storage
    - Implement JavaScript to sync calendar picker and manual entry
    - Add mode toggle handler to show/hide appropriate fields
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 3.2 Update wfh_request view in attendance/views.py
    - Parse selected_dates from POST data
    - Validate date format (YYYY-MM-DD)
    - Validate dates are in the future
    - Store selected_dates as JSON in WFHRequest model
    - Maintain backward compatibility with start_date/end_date
    - Calculate total_days using selected_dates if present
    - _Requirements: 2.4, 2.5, 2.6, 2.8, 2.9, 2.10_

  - [ ]* 3.3 Write unit tests for WFH request multi-date selection
    - Test parsing of comma-separated dates
    - Test validation of future dates
    - Test JSON storage and retrieval
    - Test total_days calculation for selected dates
    - Test backward compatibility with date ranges
    - _Requirements: 18.2_

- [x] 4. Checkpoint - Verify multi-date selection works
  - Test leave request with calendar picker
  - Test leave request with manual entry
  - Test WFH request with calendar picker
  - Test WFH request with manual entry
  - Verify backward compatibility with existing requests
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Hierarchical Approval Workflow for Leave Requests
  - [x] 5.1 Create leave_approval view in attendance/views.py
    - Filter pending requests based on user role (TL, Manager, HR)
    - TL sees requests without tl_comment
    - Manager sees requests with tl_comment but not manager_approved
    - HR sees requests with manager_approved=True
    - Pass user_role to template for conditional rendering
    - _Requirements: 4.1, 4.2, 4.4, 4.7_

  - [x] 5.2 Create leave_action view in attendance/views.py
    - Handle TL comment submission (store in tl_comment, set tl_approver and timestamp)
    - Handle Manager approve/reject (set manager_approved, store comment, notify HR or employee)
    - Handle HR final approve/reject (set status, notify employee and manager)
    - Create notifications for each step
    - Create audit log entries for each action
    - _Requirements: 4.3, 4.5, 4.6, 4.8, 4.9, 4.10_

  - [x] 5.3 Create leave_approval.html template
    - Display pending requests table with employee, type, dates, reason
    - Show TL comment column for Manager and HR
    - Show Manager decision column for HR
    - Add action button (Add Comment for TL, Approve/Reject for Manager/HR)
    - Create action modal with comment field and approve/reject buttons
    - Display approval chain status indicators (TL → Manager → HR)
    - _Requirements: 4.11, 4.12_

  - [x] 5.4 Update employee leave request history view
    - Display approval chain (TL comment → Manager approval → HR decision)
    - Show status indicators for each step
    - Display comments from TL, Manager, and HR
    - Show approver names and timestamps
    - _Requirements: 4.11_

  - [ ]* 5.5 Write unit tests for leave approval workflow
    - Test TL comment submission
    - Test Manager approval flow
    - Test Manager rejection flow
    - Test HR final approval
    - Test HR rejection of manager-approved request
    - Test notification creation at each step
    - Test audit log entries
    - _Requirements: 18.2, 18.6_

- [x] 6. Hierarchical Approval Workflow for WFH Requests
  - [x] 6.1 Create wfh_approval view in attendance/views.py
  - [x] 6.2 Create wfh_action view in attendance/views.py
  - [x] 6.3 Create wfh_approval.html template
  - [x] 6.4 Update employee WFH request history view

  - [ ]* 6.5 Write unit tests for WFH approval workflow
    - Test TL comment submission
    - Test Manager approval flow
    - Test Manager rejection flow
    - Test HR final approval
    - Test HR rejection of manager-approved request
    - Test notification creation at each step
    - Test audit log entries
    - _Requirements: 18.2, 18.6_

- [ ] 7. Checkpoint - Verify approval workflows work
  - Test leave approval as TL (add comment)
  - Test leave approval as Manager (approve/reject)
  - Test leave approval as HR (final decision)
  - Test WFH approval as TL (add comment)
  - Test WFH approval as Manager (approve/reject)
  - Test WFH approval as HR (final decision)
  - Verify notifications are sent correctly
  - Verify audit logs are created
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Manager Role Access and Permissions
  - [x] 8.1 Update EmployeeProfile model save method
    - When role is set to 'manager', automatically set is_hr=True
    - Ensure managers have HR dashboard access
    - _Requirements: 3.2_

  - [x] 8.2 Update dashboard view for manager access
    - Allow managers to access HR dashboard features
    - Display manager's profile photo in dashboard header
    - Show pending leave/WFH requests requiring manager approval
    - Show employee attendance statistics
    - _Requirements: 3.1, 3.3, 3.4, 3.5, 3.7_

  - [x] 8.3 Update mobile access restrictions
    - Allow managers to access system from mobile devices
    - Update is_mobile_device check to include manager role
    - _Requirements: 3.6_

  - [ ]* 8.4 Write unit tests for manager role
    - Test is_hr flag is set when role is 'manager'
    - Test manager can access HR dashboard
    - Test manager can access from mobile
    - Test manager approval authority
    - _Requirements: 18.2_

- [x] 9. Onsite Request Feature
  - [x] 9.1 Create onsite_request view in attendance/views.py
  - [x] 9.2 Create onsite_request.html template
  - [x] 9.3 Create onsite_approval view in attendance/views.py
  - [x] 9.4 Create onsite_action view in attendance/views.py
  - [x] 9.5 Create onsite_approval.html template

  - [ ]* 9.6 Write unit tests for onsite request creation and approval
    - Test onsite request creation
    - Test validation of future dates
    - Test Manager approval flow
    - Test HR final approval
    - Test notification creation
    - Test audit log entries
    - _Requirements: 18.3, 18.7_

- [x] 10. Onsite Visit Check-In and Check-Out
  - [x] 10.1 Create onsite_check_in view in attendance/views.py
  - [x] 10.2 Create onsite_check_out view in attendance/views.py
  - [x] 10.3 Update dashboard.html to show onsite check-in/check-out buttons

  - [ ]* 10.4 Write unit tests for onsite check-in and check-out
    - Test check-in for approved onsite request
    - Test check-out after check-in
    - Test validation (can't check-out before check-in)
    - Test location restrictions (allowed from anywhere)
    - Test audit log entries
    - _Requirements: 18.7_

- [ ] 11. Flexible Break Times for Onsite Visits
  - [x] 11.1 Update start_break view in attendance/views.py
    - Check for active approved onsite request for today
    - If onsite request exists, bypass time window validation
    - Still enforce 5 PM cutoff for all breaks
    - Still enforce break count limits (2 tea, 1 lunch)
    - Still enforce break duration limits (15 min tea, 45 min lunch)
    - Mark break with 'flexible' time_slot indicator
    - Create audit log entry indicating flexible break usage
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.7, 9.8, 9.9_

  - [x] 11.2 Update dashboard.html to show flexible break message
    - Display message when onsite request is active
    - Show "Flexible break times enabled for onsite visit" indicator
    - Update break button labels to indicate flexibility
    - _Requirements: 9.10_

  - [ ]* 11.3 Write unit tests for flexible break times
    - Test break allowed outside normal windows with approved onsite request
    - Test break denied outside normal windows without onsite request
    - Test 5 PM cutoff still enforced
    - Test break count limits still enforced
    - Test break duration limits still enforced
    - Test audit log entries for flexible breaks
    - _Requirements: 18.4, 18.8_

- [ ] 12. Checkpoint - Verify onsite features work
  - Test onsite request creation
  - Test onsite request approval (Manager → HR)
  - Test onsite check-in and check-out
  - Test flexible break times during onsite visit
  - Test that normal break restrictions apply without onsite request
  - Verify audit logs are created
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Employee Attendance Dashboard for HR
  - [x] 13.1 Create employee_attendance_dashboard view in attendance/views.py
    - Restrict access to HR and Manager roles only
    - Parse filter parameters (employee_id, department, start_date, end_date)
    - Query attendance records with filters applied
    - Calculate statistics per employee (present days, absent days, late arrivals, half-days, total hours)
    - Get list of departments for filter dropdown
    - Handle CSV export if requested
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.8, 10.9, 10.10, 10.11_

  - [x] 13.2 Create employee_attendance_dashboard.html template
    - Display filter form (employee, department, date range)
    - Display employee statistics table with profile photos
    - Show present days, absent days, late arrivals, half-days, total hours
    - Add export to CSV button
    - Display summary statistics for all employees
    - Allow drill-down into individual employee details
    - Show date range for statistics
    - _Requirements: 10.1, 10.7, 10.12, 10.13, 10.14, 10.15_

  - [x] 13.3 Add CSV export functionality
    - Generate CSV with columns: Employee ID, Name, Department, Present Days, Absent Days, Late Arrivals, Half Days, Total Hours
    - Set appropriate headers for file download
    - Create audit log entry for export
    - _Requirements: 10.6, 14.11_

  - [ ]* 13.4 Write unit tests for employee attendance dashboard
    - Test statistics calculation (present, absent, late, half-days, total hours)
    - Test filtering by employee
    - Test filtering by department
    - Test filtering by date range
    - Test CSV export
    - Test access restrictions (HR/Manager only)
    - _Requirements: 18.5, 18.11_

- [ ] 14. UI Integration and Dark Theme Consistency
  - [x] 14.1 Apply dark theme CSS to all new templates
    - Use existing dark theme classes from base.html
    - Apply consistent card layouts (glass-card class)
    - Use consistent button styles (btn-primary, btn-success, btn-danger)
    - Use consistent form field styling
    - _Requirements: 11.1, 11.2, 11.3, 11.7_

  - [x] 14.2 Add status indicators with consistent colors
    - Green badges for approved status
    - Red badges for rejected status
    - Yellow badges for pending status
    - Consistent badge styling across all templates
    - _Requirements: 11.4_

  - [x] 14.3 Display profile photos consistently
    - Use circular format for all profile photos
    - Consistent size across all views
    - Fallback to default avatar if no photo
    - _Requirements: 11.5_

  - [x] 14.4 Ensure responsive design for mobile
    - Test all new templates on mobile devices
    - Ensure tables are responsive (horizontal scroll if needed)
    - Ensure forms are mobile-friendly
    - Ensure modals work on mobile
    - _Requirements: 11.10_

  - [ ]* 14.5 Write UI integration tests
    - Test dark theme is applied to all new pages
    - Test status indicators display correctly
    - Test profile photos display correctly
    - Test responsive design on mobile
    - _Requirements: 18.9_

- [ ] 15. URL Routes and Navigation
  - [x] 15.1 Add new URL routes to attendance/urls.py
  - [x] 15.2 Update navigation menu in base.html
    - Add "Leave Approval" link for TL, Manager, HR
    - Add "WFH Approval" link for TL, Manager, HR
    - Add "Onsite Request" link for all employees
    - Add "Onsite Approval" link for Manager, HR
    - Add "Employee Dashboard" link for HR, Manager
    - Use role-based visibility for menu items
    - _Requirements: All features_

- [ ] 16. Notification System Integration
  - [x] 16.1 Update notification creation for all new features
    - Create notifications when leave request is submitted (notify TL)
    - Create notifications when TL adds comment (notify Manager)
    - Create notifications when Manager approves/rejects (notify HR/employee)
    - Create notifications when HR gives final decision (notify employee/manager)
    - Create notifications for WFH requests (same flow as leave)
    - Create notifications for onsite requests (notify Manager, then HR)
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8, 16.9, 16.10_

  - [x] 16.2 Update notification display in dashboard
    - Show notification count in header
    - Display recent notifications
    - Mark notifications as read when viewed
    - Display notifications in chronological order
    - Include relevant details (employee name, request type, dates)
    - _Requirements: 16.11, 16.12, 16.13, 16.14_

  - [ ]* 16.3 Write unit tests for notification system
    - Test notification creation at each approval step
    - Test notification display
    - Test mark as read functionality
    - Test notification history
    - _Requirements: 18.2_

- [ ] 17. Error Handling and Validation
  - [x] 17.1 Add client-side validation to all forms
    - Validate date formats in JavaScript
    - Validate required fields before submission
    - Validate date ranges (start before end)
    - Validate future dates for requests
    - Display inline error messages
    - _Requirements: 15.1, 15.2, 15.10, 15.13_

  - [x] 17.2 Add server-side validation to all views
    - Validate date formats in views
    - Validate required fields
    - Validate future dates
    - Validate overlapping requests
    - Validate user permissions
    - Return user-friendly error messages
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.12_

  - [x] 17.3 Add error logging and debugging
    - Log all validation errors to audit log
    - Log database errors with technical details
    - Display user-friendly error messages to users
    - Maintain form data when validation errors occur
    - _Requirements: 15.8, 15.14, 15.15_

  - [ ]* 17.4 Write unit tests for error handling
    - Test validation of invalid dates
    - Test validation of past dates
    - Test validation of missing required fields
    - Test validation of overlapping requests
    - Test error message display
    - Test form data preservation on error
    - _Requirements: 18.12_

- [ ] 18. Audit Logging for New Features
  - [x] 18.1 Add audit log entries for all new actions
    - Log multi-date leave request submission
    - Log multi-date WFH request submission
    - Log TL comment addition
    - Log Manager approval/rejection
    - Log HR final decision
    - Log onsite request submission
    - Log onsite request approval
    - Log onsite check-in and check-out
    - Log flexible break usage during onsite visits
    - Log HR dashboard access
    - Log CSV export
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9, 14.10, 14.11_

  - [x] 18.2 Update audit log view for HR
    - Add filter by action type
    - Add filter by date range
    - Display IP address, timestamp, user, description
    - Display target_user where applicable
    - _Requirements: 14.12, 14.13, 14.14_

  - [ ]* 18.3 Write unit tests for audit logging
    - Test audit log creation for each action type
    - Test audit log filtering
    - Test audit log display
    - _Requirements: 18.2_

- [ ] 19. Backward Compatibility and Data Migration
  - [x] 19.1 Test backward compatibility with existing data
    - Test existing leave requests without selected_dates
    - Test existing WFH requests without selected_dates
    - Test existing attendance records
    - Test existing break logs
    - Verify all existing functionality still works
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8_

  - [x] 19.2 Handle null values in new fields gracefully
    - Check for null selected_dates before processing
    - Use start_date/end_date as fallback
    - Handle null approval fields (tl_comment, manager_comment, etc.)
    - _Requirements: 17.9, 17.10_

  - [ ]* 19.3 Write integration tests for backward compatibility
    - Test processing of old leave requests
    - Test processing of old WFH requests
    - Test display of old requests
    - Test calculations with old data
    - _Requirements: 18.2_

- [ ] 20. Final Integration and Testing
  - [ ] 20.1 Run all unit tests
    - Verify all unit tests pass
    - Fix any failing tests
    - Achieve at least 80% code coverage
    - _Requirements: 18.15_

  - [ ] 20.2 Run integration tests
    - Test complete leave approval workflow (Employee → TL → Manager → HR)
    - Test complete WFH approval workflow (Employee → TL → Manager → HR)
    - Test complete onsite workflow (Employee → Manager → HR → Check-in → Check-out)
    - Test flexible breaks during onsite visits
    - Test employee attendance dashboard with real data
    - _Requirements: 18.6, 18.7, 18.8_

  - [ ] 20.3 Perform manual testing
    - Test multi-date picker in different browsers
    - Test approval workflows with different roles
    - Test onsite features end-to-end
    - Test mobile access restrictions
    - Test CSV export
    - Test all error scenarios
    - _Requirements: All features_

  - [ ] 20.4 Security testing
    - Test input validation and XSS prevention
    - Test CSRF protection on all forms
    - Test role-based access control
    - Test SQL injection prevention
    - _Requirements: 15.12, 18.12_

  - [ ] 20.5 Performance testing
    - Test dashboard queries with large datasets
    - Test CSV export with large datasets
    - Verify database indexes are used
    - Optimize slow queries if needed
    - _Requirements: 18.11_

- [ ] 21. Final Checkpoint - Complete system verification
  - Verify all features are implemented and working
  - Verify all tests pass
  - Verify backward compatibility
  - Verify security measures are in place
  - Verify performance is acceptable
  - Verify documentation is complete
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- The implementation follows the existing Django project structure
- All new features integrate with existing authentication, authorization, and audit logging
- Dark theme and UI consistency are maintained throughout
- Backward compatibility is ensured for all existing data
- Security and performance are considered in all implementations

## Implementation Order

The tasks are ordered to minimize dependencies and allow for incremental testing:

1. **Setup** (Task 1) - Foundation for all features
2. **Multi-date selection** (Tasks 2-4) - Core functionality used by multiple features
3. **Approval workflows** (Tasks 5-7) - Core business logic
4. **Manager role** (Task 8) - Required for approval workflows
5. **Onsite features** (Tasks 9-12) - New feature with dependencies on approval workflows
6. **Employee dashboard** (Task 13) - Reporting feature
7. **UI/UX** (Tasks 14-15) - Polish and consistency
8. **Supporting features** (Tasks 16-19) - Notifications, error handling, audit logging, backward compatibility
9. **Testing and verification** (Tasks 20-21) - Final validation

This order allows for early testing of core features and ensures that dependencies are implemented before dependent features.
