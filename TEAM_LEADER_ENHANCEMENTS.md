# Team Leader Dashboard Enhancements

## Issues to Fix

### 1. Profile Page - Add Team Leader Badge
**File**: `templates/profile.html`
**Change**: Add badge showing "Team Leader" if user leads any teams

### 2. Leave/WFH Approval Pages - Filter for Team Leaders
**Files**: 
- `attendance/views.py` - `leave_approval`, `wfh_approval`, `overtime_approval`, `onsite_approval`
**Change**: Filter requests to show only team member requests for Team Leaders (HR sees all)

### 3. Pending Requests Page - Add Status Tabs
**File**: `templates/team_pending_requests.html`
**Change**: Add tabs for Pending/Approved/Rejected like the approval pages

### 4. Team Member List Page - Enhance Cards
**Files**:
- `templates/team_member_list.html`
- `attendance/team_views.py` - `team_member_list`
**Changes**:
- Make existing cards clickable (Total Members, Present Today, Team Leader)
- Add new cards: Absent, On Leave, WFH, Late Arrivals
- Each card click filters the member list below

## Implementation Plan

### Phase 1: Profile Badge (Quick Fix)
- Check if user is team leader of any team
- Display badge in profile sidebar

### Phase 2: Filter Approvals (Medium Priority)
- Modify approval views to detect team leaders
- Get team member IDs for the TL's teams
- Filter requests by team membership
- HR/Admin continue to see all requests

### Phase 3: Pending Requests Tabs (Medium Complexity)
- Add tab navigation to pending requests page
- Query for approved/rejected requests
- Display with proper status badges

### Phase 4: Enhanced Team Member List (Complex)
- Calculate attendance statistics for team
- Add clickable cards with counts
- Filter member list based on card clicked
- Use URL parameters or JavaScript for filtering

## Status: READY TO IMPLEMENT
