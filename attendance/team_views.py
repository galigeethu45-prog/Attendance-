# =========================
# TEAM MANAGEMENT VIEWS (TEAM-012 to TEAM-024)
# =========================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
import json

from attendance.models import (
    Team, TeamMembership, EmployeeProfile, 
    LeaveRequest, WFHRequest, OnsiteRequest, Overtime,
    AuditLog, Notification, Attendance
)


# =========================
# PERMISSION DECORATORS
# =========================
def hr_only(view_func):
    """Decorator to restrict access to HR/Admin only"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page")
            return redirect('login')
        
        # Check if user is HR/Admin
        is_hr = request.user.is_superuser
        if not is_hr:
            try:
                profile = request.user.employeeprofile
                is_hr = profile.is_hr or profile.role in ['hr', 'manager']
            except EmployeeProfile.DoesNotExist:
                pass
        
        if not is_hr:
            messages.error(request, "HR/Admin access required")
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def team_leader_or_hr(view_func):
    """Decorator to restrict access to Team Leaders, HR, or Admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page")
            return redirect('login')
        
        # Check permissions
        is_authorized = request.user.is_superuser
        if not is_authorized:
            try:
                profile = request.user.employeeprofile
                is_authorized = (
                    profile.is_hr or 
                    profile.is_team_leader or 
                    profile.role in ['hr', 'manager', 'team_leader']
                )
            except EmployeeProfile.DoesNotExist:
                pass
        
        if not is_authorized:
            messages.error(request, "Team Leader, HR, or Admin access required")
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


# =========================
# HR TEAM MANAGEMENT (TEAM-012, TEAM-013, TEAM-014)
# =========================

@login_required
@hr_only
def team_management(request):
    """
    TEAM-012: HR Team Management Page
    Main page for creating, editing, and managing teams
    """
    teams = Team.objects.filter(is_active=True).select_related('team_leader').annotate(
        member_count=Count('memberships', filter=Q(memberships__is_active=True))
    ).order_by('department', 'name')
    
    # Get all potential team leaders
    potential_leaders = User.objects.filter(
        is_active=True
    ).select_related('employeeprofile').order_by('first_name', 'last_name')
    
    # Get all employees for member assignment
    all_employees = User.objects.filter(
        is_active=True
    ).select_related('employeeprofile').order_by('first_name', 'last_name')
    
    context = {
        'teams': teams,
        'potential_leaders': potential_leaders,
        'all_employees': all_employees,
    }
    
    return render(request, 'team_management.html', context)


@login_required
@hr_only
@require_http_methods(["POST"])
def create_team(request):
    """
    TEAM-012: Create a new team
    """
    try:
        name = request.POST.get('name', '').strip()
        department = request.POST.get('department', '').strip()
        team_leader_id = request.POST.get('team_leader')
        description = request.POST.get('description', '').strip()
        
        # Validation
        if not name:
            messages.error(request, "Team name is required")
            return redirect('team_management')
        
        if not department:
            messages.error(request, "Department is required")
            return redirect('team_management')
        
        # Check duplicate team name
        if Team.objects.filter(name__iexact=name, is_active=True).exists():
            messages.error(request, f"Team '{name}' already exists")
            return redirect('team_management')
        
        # Get team leader if provided
        team_leader = None
        if team_leader_id:
            try:
                team_leader = User.objects.get(id=team_leader_id)
            except User.DoesNotExist:
                messages.error(request, "Invalid team leader selected")
                return redirect('team_management')
        
        # Create team
        team = Team.objects.create(
            name=name,
            department=department,
            team_leader=team_leader,
            description=description,
            created_by=request.user
        )
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action='user_create',
            description=f"Created team: {team.name} in {team.department} department"
        )
        
        # TEAM-020: Notify team leader if assigned
        if team_leader:
            Notification.objects.create(
                employee=team_leader,
                message=f"You have been assigned as Team Leader of '{team.name}'"
            )
        
        messages.success(request, f"Team '{team.name}' created successfully!")
        return redirect('team_management')
        
    except Exception as e:
        messages.error(request, f"Error creating team: {str(e)}")
        return redirect('team_management')


@login_required
@hr_only
@require_http_methods(["POST"])
def update_team(request, team_id):
    """
    TEAM-012: Update team details
    """
    team = get_object_or_404(Team, id=team_id)
    
    try:
        name = request.POST.get('name', '').strip()
        department = request.POST.get('department', '').strip()
        team_leader_id = request.POST.get('team_leader')
        description = request.POST.get('description', '').strip()
        
        # Validation
        if not name:
            messages.error(request, "Team name is required")
            return redirect('team_management')
        
        if not department:
            messages.error(request, "Department is required")
            return redirect('team_management')
        
        # Check duplicate team name (excluding current team)
        if Team.objects.filter(name__iexact=name, is_active=True).exclude(id=team_id).exists():
            messages.error(request, f"Team '{name}' already exists")
            return redirect('team_management')
        
        # Update fields
        team.name = name
        team.department = department
        team.description = description
        
        # Update team leader
        if team_leader_id:
            try:
                team.team_leader = User.objects.get(id=team_leader_id)
            except User.DoesNotExist:
                messages.error(request, "Invalid team leader selected")
                return redirect('team_management')
        else:
            team.team_leader = None
        
        team.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action='user_create',
            description=f"Updated team: {team.name}"
        )
        
        messages.success(request, f"Team '{team.name}' updated successfully!")
        return redirect('team_management')
        
    except Exception as e:
        messages.error(request, f"Error updating team: {str(e)}")
        return redirect('team_management')


@login_required
@hr_only
@require_http_methods(["POST"])
def delete_team(request, team_id):
    """
    TEAM-012: Delete (deactivate) a team
    """
    team = get_object_or_404(Team, id=team_id)
    
    try:
        team_name = team.name
        
        # Soft delete
        team.is_active = False
        team.save()
        
        # Deactivate all memberships
        TeamMembership.objects.filter(team=team, is_active=True).update(is_active=False)
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action='user_delete',
            description=f"Deactivated team: {team_name}"
        )
        
        messages.success(request, f"Team '{team_name}' deactivated successfully!")
        
    except Exception as e:
        messages.error(request, f"Error deleting team: {str(e)}")
    
    return redirect('team_management')


@login_required
@hr_only
def team_members_view(request, team_id):
    """
    TEAM-013, TEAM-014: Team member management page
    Shows current members and allows adding/removing members
    """
    team = get_object_or_404(Team, id=team_id, is_active=True)
    
    # Get current members
    memberships = TeamMembership.objects.filter(
        team=team,
        is_active=True
    ).select_related('employee__employeeprofile').order_by('employee__first_name', 'employee__last_name')
    
    # Get available employees (not in team)
    current_member_ids = memberships.values_list('employee_id', flat=True)
    available_employees = User.objects.filter(
        is_active=True
    ).exclude(
        id__in=current_member_ids
    ).select_related('employeeprofile').order_by('first_name', 'last_name')
    
    context = {
        'team': team,
        'memberships': memberships,
        'available_employees': available_employees,
    }
    
    return render(request, 'team_members.html', context)


@login_required
@hr_only
@require_http_methods(["POST"])
def add_team_member(request, team_id):
    """
    TEAM-014: Add a single member to team
    """
    team = get_object_or_404(Team, id=team_id, is_active=True)
    
    try:
        employee_id = request.POST.get('employee_id')
        if not employee_id:
            messages.error(request, "Please select an employee")
            return redirect('team_members_view', team_id=team_id)
        
        employee = get_object_or_404(User, id=employee_id)
        
        # Add member using Team model method
        success, message, membership = team.add_member(employee, added_by=request.user)
        
        if success:
            # Create audit log
            AuditLog.objects.create(
                user=request.user,
                action='user_create',
                description=f"Added {employee.get_full_name() or employee.username} to team {team.name}",
                target_user=employee
            )
            
            # TEAM-020: Notify team leader
            if team.team_leader and team.team_leader != request.user:
                Notification.objects.create(
                    employee=team.team_leader,
                    message=f"New member added: {employee.get_full_name() or employee.username} joined your team '{team.name}'"
                )
            
            # Notify the employee
            Notification.objects.create(
                employee=employee,
                message=f"You have been added to team '{team.name}'"
            )
            
            messages.success(request, message)
        else:
            messages.warning(request, message)
            
    except Exception as e:
        messages.error(request, f"Error adding member: {str(e)}")
    
    return redirect('team_members_view', team_id=team_id)


@login_required
@hr_only
@require_http_methods(["POST"])
def remove_team_member(request, team_id, member_id):
    """
    TEAM-014: Remove a member from team
    """
    team = get_object_or_404(Team, id=team_id, is_active=True)
    employee = get_object_or_404(User, id=member_id)
    
    try:
        # Remove member using Team model method
        success, message = team.remove_member(employee)
        
        if success:
            # Create audit log
            AuditLog.objects.create(
                user=request.user,
                action='user_delete',
                description=f"Removed {employee.get_full_name() or employee.username} from team {team.name}",
                target_user=employee
            )
            messages.success(request, message)
        else:
            messages.error(request, message)
            
    except Exception as e:
        messages.error(request, f"Error removing member: {str(e)}")
    
    return redirect('team_members_view', team_id=team_id)


@login_required
@hr_only
@require_http_methods(["POST"])
def bulk_add_members(request, team_id):
    """
    TEAM-014: Bulk add members to team
    """
    team = get_object_or_404(Team, id=team_id, is_active=True)
    
    try:
        employee_ids = request.POST.getlist('employee_ids')
        
        if not employee_ids:
            messages.error(request, "Please select at least one employee")
            return redirect('team_members_view', team_id=team_id)
        
        added_count = 0
        skipped_count = 0
        
        for emp_id in employee_ids:
            try:
                employee = User.objects.get(id=emp_id)
                success, message, membership = team.add_member(employee, added_by=request.user)
                
                if success:
                    added_count += 1
                    # Create audit log
                    AuditLog.objects.create(
                        user=request.user,
                        action='user_create',
                        description=f"Bulk add: Added {employee.get_full_name() or employee.username} to team {team.name}",
                        target_user=employee
                    )
                else:
                    skipped_count += 1
            except User.DoesNotExist:
                skipped_count += 1
        
        if added_count > 0:
            messages.success(request, f"Successfully added {added_count} member(s) to team")
        if skipped_count > 0:
            messages.warning(request, f"{skipped_count} member(s) were skipped (already in team or not found)")
            
    except Exception as e:
        messages.error(request, f"Error adding members: {str(e)}")
    
    return redirect('team_members_view', team_id=team_id)


# =========================
# TEAM LEADER DASHBOARD (TEAM-015, TEAM-016, TEAM-017)
# =========================

@login_required
@team_leader_or_hr
def team_leader_dashboard(request):
    """
    TEAM-015: Team Leader Dashboard
    Shows teams where user is team leader
    If user is HR/Admin, redirect to team management page instead
    """
    # Check if user is HR/Admin - redirect to team management
    is_hr = request.user.is_superuser
    if not is_hr:
        try:
            profile = request.user.employeeprofile
            is_hr = profile.is_hr or profile.role in ['hr', 'manager']
        except EmployeeProfile.DoesNotExist:
            pass
    
    if is_hr:
        # HR should use Team Management page, not Team Leader Dashboard
        return redirect('team_management')
    
    # Get teams where user is team leader
    my_teams = Team.objects.filter(
        team_leader=request.user,
        is_active=True
    ).select_related('created_by').annotate(
        member_count=Count('memberships', filter=Q(memberships__is_active=True))
    ).order_by('name')
    
    context = {
        'my_teams': my_teams,
        'all_teams': my_teams,
        'is_hr': False,  # Set to False since HR users are redirected
    }
    
    return render(request, 'team_leader_dashboard.html', context)


@login_required
@team_leader_or_hr
def team_pending_requests(request, team_id):
    """
    TEAM-016: Team Pending Requests View
    Shows all requests from team members with status filtering (Pending/Approved/Rejected)
    """
    team = get_object_or_404(Team, id=team_id, is_active=True)
    
    # Permission check: only team leader or HR can view
    is_hr = request.user.is_superuser
    if not is_hr:
        try:
            profile = request.user.employeeprofile
            is_hr = profile.is_hr or profile.role in ['hr', 'manager']
        except EmployeeProfile.DoesNotExist:
            pass
    
    if not is_hr and team.team_leader != request.user:
        messages.error(request, "You can only view requests for teams you lead")
        return redirect('team_leader_dashboard')
    
    # Get team member IDs
    team_member_ids = TeamMembership.objects.filter(
        team=team,
        is_active=True
    ).values_list('employee_id', flat=True)
    
    # Get status filter (default: pending)
    status_filter = request.GET.get('status', 'pending')
    
    # Filter requests based on status
    if status_filter == 'pending':
        leave_requests = LeaveRequest.objects.filter(
            employee_id__in=team_member_ids,
            status='pending'
        ).select_related('employee__employeeprofile').order_by('-created_at')
        
        wfh_requests = WFHRequest.objects.filter(
            employee_id__in=team_member_ids,
            status='pending'
        ).select_related('employee__employeeprofile').order_by('-created_at')
        
        ot_requests = Overtime.objects.filter(
            employee_id__in=team_member_ids,
            status='pending'
        ).select_related('employee__employeeprofile').order_by('-requested_at')
        
        onsite_requests = OnsiteRequest.objects.filter(
            employee_id__in=team_member_ids,
            status='pending'
        ).select_related('employee__employeeprofile').order_by('-created_at')
    
    elif status_filter == 'approved':
        leave_requests = LeaveRequest.objects.filter(
            employee_id__in=team_member_ids,
            status='approved'
        ).select_related('employee__employeeprofile', 'tl_approver', 'manager_approver').order_by('-created_at')
        
        wfh_requests = WFHRequest.objects.filter(
            employee_id__in=team_member_ids,
            status='approved'
        ).select_related('employee__employeeprofile', 'tl_approver', 'manager_approver', 'hr_approver').order_by('-created_at')
        
        ot_requests = Overtime.objects.filter(
            employee_id__in=team_member_ids,
            status='approved'
        ).select_related('employee__employeeprofile', 'tl_approver').order_by('-requested_at')
        
        onsite_requests = OnsiteRequest.objects.filter(
            employee_id__in=team_member_ids,
            status='approved'
        ).select_related('employee__employeeprofile', 'tl_approver', 'manager_approver').order_by('-created_at')
    
    elif status_filter == 'rejected':
        leave_requests = LeaveRequest.objects.filter(
            employee_id__in=team_member_ids,
            status='rejected'
        ).select_related('employee__employeeprofile', 'tl_approver', 'manager_approver').order_by('-created_at')
        
        wfh_requests = WFHRequest.objects.filter(
            employee_id__in=team_member_ids,
            status='rejected'
        ).select_related('employee__employeeprofile', 'tl_approver', 'manager_approver').order_by('-created_at')
        
        ot_requests = Overtime.objects.filter(
            employee_id__in=team_member_ids,
            status='rejected'
        ).select_related('employee__employeeprofile', 'tl_approver').order_by('-requested_at')
        
        onsite_requests = OnsiteRequest.objects.filter(
            employee_id__in=team_member_ids,
            status='rejected'
        ).select_related('employee__employeeprofile', 'tl_approver', 'manager_approver').order_by('-created_at')
    
    else:  # 'all'
        leave_requests = LeaveRequest.objects.filter(
            employee_id__in=team_member_ids
        ).select_related('employee__employeeprofile', 'tl_approver', 'manager_approver').order_by('-created_at')
        
        wfh_requests = WFHRequest.objects.filter(
            employee_id__in=team_member_ids
        ).select_related('employee__employeeprofile', 'tl_approver', 'manager_approver', 'hr_approver').order_by('-created_at')
        
        ot_requests = Overtime.objects.filter(
            employee_id__in=team_member_ids
        ).select_related('employee__employeeprofile', 'tl_approver').order_by('-requested_at')
        
        onsite_requests = OnsiteRequest.objects.filter(
            employee_id__in=team_member_ids
        ).select_related('employee__employeeprofile', 'tl_approver', 'manager_approver').order_by('-created_at')
    
    # Count for badges
    pending_count = (
        LeaveRequest.objects.filter(employee_id__in=team_member_ids, status='pending').count() +
        WFHRequest.objects.filter(employee_id__in=team_member_ids, status='pending').count() +
        Overtime.objects.filter(employee_id__in=team_member_ids, status='pending').count() +
        OnsiteRequest.objects.filter(employee_id__in=team_member_ids, status='pending').count()
    )
    
    approved_count = (
        LeaveRequest.objects.filter(employee_id__in=team_member_ids, status='approved').count() +
        WFHRequest.objects.filter(employee_id__in=team_member_ids, status='approved').count() +
        Overtime.objects.filter(employee_id__in=team_member_ids, status='approved').count() +
        OnsiteRequest.objects.filter(employee_id__in=team_member_ids, status='approved').count()
    )
    
    rejected_count = (
        LeaveRequest.objects.filter(employee_id__in=team_member_ids, status='rejected').count() +
        WFHRequest.objects.filter(employee_id__in=team_member_ids, status='rejected').count() +
        Overtime.objects.filter(employee_id__in=team_member_ids, status='rejected').count() +
        OnsiteRequest.objects.filter(employee_id__in=team_member_ids, status='rejected').count()
    )
    
    context = {
        'team': team,
        'leave_requests': leave_requests,
        'wfh_requests': wfh_requests,
        'ot_requests': ot_requests,
        'onsite_requests': onsite_requests,
        'is_hr': is_hr,
        'status_filter': status_filter,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    
    return render(request, 'team_pending_requests.html', context)


@login_required
@team_leader_or_hr
def team_member_list(request, team_id):
    """
    TEAM-017: Team Member List View
    Shows team members with current status and enhanced statistics
    Supports filtering by status (all/present/absent/leave/wfh/late)
    """
    team = get_object_or_404(Team, id=team_id, is_active=True)
    
    # Permission check
    is_hr = request.user.is_superuser
    if not is_hr:
        try:
            profile = request.user.employeeprofile
            is_hr = profile.is_hr or profile.role in ['hr', 'manager']
        except EmployeeProfile.DoesNotExist:
            pass
    
    if not is_hr and team.team_leader != request.user:
        messages.error(request, "You can only view members for teams you lead")
        return redirect('team_leader_dashboard')
    
    # Get filter parameter
    status_filter = request.GET.get('filter', 'all')
    
    # Get team members
    today = timezone.now().date()
    memberships = TeamMembership.objects.filter(
        team=team,
        is_active=True
    ).select_related('employee__employeeprofile').order_by('employee__first_name', 'employee__last_name')
    
    # Get team member IDs
    team_member_ids = list(memberships.values_list('employee_id', flat=True))
    
    # Get today's attendance for all team members
    today_attendance = {
        att.employee_id: att 
        for att in Attendance.objects.filter(
            employee_id__in=team_member_ids,
            date=today
        ).select_related('employee')
    }
    
    # Get approved leaves for today
    approved_leaves_today = set(
        LeaveRequest.objects.filter(
            employee_id__in=team_member_ids,
            status='approved',
            start_date__lte=today,
            end_date__gte=today
        ).values_list('employee_id', flat=True)
    )
    
    # Get approved WFH for today
    approved_wfh_today = set(
        WFHRequest.objects.filter(
            employee_id__in=team_member_ids,
            status='approved',
            start_date__lte=today,
            end_date__gte=today
        ).values_list('employee_id', flat=True)
    )
    
    # Categorize members and prepare data
    members_data = []
    present_members = []
    absent_members = []
    leave_members = []
    wfh_members = []
    late_members = []
    
    for membership in memberships:
        employee = membership.employee
        emp_id = employee.id
        attendance = today_attendance.get(emp_id)
        
        # Determine status
        if emp_id in approved_leaves_today:
            status = 'on_leave'
            status_display = 'On Leave'
            status_class = 'primary'
            leave_members.append(membership)
        elif emp_id in approved_wfh_today:
            status = 'wfh'
            status_display = 'WFH'
            status_class = 'info'
            wfh_members.append(membership)
        elif attendance:
            if attendance.status == 'late':
                status = 'late'
                status_display = 'Late'
                status_class = 'warning'
                late_members.append(membership)
            elif attendance.status in ['present', 'half-day']:
                status = 'present'
                status_display = 'Present'
                status_class = 'success'
                present_members.append(membership)
            else:
                status = 'absent'
                status_display = 'Absent'
                status_class = 'danger'
                absent_members.append(membership)
        else:
            # Not checked in and no leave/wfh
            status = 'absent'
            status_display = 'Absent'
            status_class = 'danger'
            absent_members.append(membership)
        
        member_info = {
            'membership': membership,
            'employee': employee,
            'attendance': attendance,
            'status': status,
            'status_display': status_display,
            'status_class': status_class,
        }
        
        members_data.append(member_info)
    
    # Apply filter
    if status_filter == 'present':
        filtered_data = [m for m in members_data if m['status'] == 'present']
    elif status_filter == 'absent':
        filtered_data = [m for m in members_data if m['status'] == 'absent']
    elif status_filter == 'leave':
        filtered_data = [m for m in members_data if m['status'] == 'on_leave']
    elif status_filter == 'wfh':
        filtered_data = [m for m in members_data if m['status'] == 'wfh']
    elif status_filter == 'late':
        filtered_data = [m for m in members_data if m['status'] == 'late']
    else:  # 'all'
        filtered_data = members_data
    
    # Calculate counts
    total_members = len(members_data)
    present_count = len(present_members)
    absent_count = len(absent_members)
    leave_count = len(leave_members)
    wfh_count = len(wfh_members)
    late_count = len(late_members)
    
    context = {
        'team': team,
        'members_data': filtered_data,
        'today': today,
        'is_hr': is_hr,
        'status_filter': status_filter,
        'total_members': total_members,
        'present_count': present_count,
        'absent_count': absent_count,
        'leave_count': leave_count,
        'wfh_count': wfh_count,
        'late_count': late_count,
    }
    
    return render(request, 'team_member_list.html', context)


# =========================
# TEAM LEADER COMMENT FUNCTIONALITY (TEAM-018)
# =========================

@login_required
@team_leader_or_hr
@require_http_methods(["POST"])
def add_tl_comment_leave(request, leave_id):
    """
    TEAM-018: Add Team Leader comment on leave request
    """
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    
    try:
        comment = request.POST.get('tl_comment', '').strip()
        
        if not comment:
            messages.error(request, "Comment cannot be empty")
            return redirect(request.META.get('HTTP_REFERER', 'team_leader_dashboard'))
        
        # Update comment
        leave_request.tl_comment = comment
        leave_request.tl_approver = request.user
        leave_request.tl_approved_at = timezone.now()
        leave_request.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action='leave_approve',
            description=f"Team Leader commented on leave request for {leave_request.employee.get_full_name() or leave_request.employee.username}",
            target_user=leave_request.employee
        )
        
        # TEAM-020: Notify employee
        Notification.objects.create(
            employee=leave_request.employee,
            message=f"Team Leader added a comment on your leave request: {comment[:50]}..."
        )
        
        # Notify manager/HR that TL has commented
        from django.db.models import Q
        managers_hr = User.objects.filter(
            Q(employeeprofile__role__in=['manager', 'hr']) | 
            Q(employeeprofile__is_hr=True) | 
            Q(is_superuser=True)
        ).distinct()
        
        for user in managers_hr:
            Notification.objects.create(
                employee=user,
                message=f"Team Leader commented on leave request from {leave_request.employee.get_full_name() or leave_request.employee.username}"
            )
        
        messages.success(request, "Comment added successfully!")
        
    except Exception as e:
        messages.error(request, f"Error adding comment: {str(e)}")
    
    return redirect(request.META.get('HTTP_REFERER', 'team_leader_dashboard'))


@login_required
@team_leader_or_hr
@require_http_methods(["POST"])
def add_tl_comment_wfh(request, wfh_id):
    """
    TEAM-018: Add Team Leader comment on WFH request
    """
    wfh_request = get_object_or_404(WFHRequest, id=wfh_id)
    
    try:
        comment = request.POST.get('tl_comment', '').strip()
        
        if not comment:
            messages.error(request, "Comment cannot be empty")
            return redirect(request.META.get('HTTP_REFERER', 'team_leader_dashboard'))
        
        # Update comment
        wfh_request.tl_comment = comment
        wfh_request.tl_approver = request.user
        wfh_request.tl_approved_at = timezone.now()
        wfh_request.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action='wfh_approve',
            description=f"Team Leader commented on WFH request for {wfh_request.employee.get_full_name() or wfh_request.employee.username}",
            target_user=wfh_request.employee
        )
        
        # TEAM-020: Notify employee
        Notification.objects.create(
            employee=wfh_request.employee,
            message=f"Team Leader added a comment on your WFH request: {comment[:50]}..."
        )
        
        # Notify manager/HR
        from django.db.models import Q
        managers_hr = User.objects.filter(
            Q(employeeprofile__role__in=['manager', 'hr']) | 
            Q(employeeprofile__is_hr=True) | 
            Q(is_superuser=True)
        ).distinct()
        
        for user in managers_hr:
            Notification.objects.create(
                employee=user,
                message=f"Team Leader commented on WFH request from {wfh_request.employee.get_full_name() or wfh_request.employee.username}"
            )
        
        messages.success(request, "Comment added successfully!")
        
    except Exception as e:
        messages.error(request, f"Error adding comment: {str(e)}")
    
    return redirect(request.META.get('HTTP_REFERER', 'team_leader_dashboard'))


@login_required
@team_leader_or_hr
@require_http_methods(["POST"])
def add_tl_comment_ot(request, ot_id):
    """
    TEAM-018: Add Team Leader comment on OT request
    """
    ot_request = get_object_or_404(Overtime, id=ot_id)
    
    try:
        comment = request.POST.get('tl_comment', '').strip()
        
        if not comment:
            messages.error(request, "Comment cannot be empty")
            return redirect(request.META.get('HTTP_REFERER', 'team_leader_dashboard'))
        
        # Update comment
        ot_request.tl_comment = comment
        ot_request.tl_approver = request.user
        ot_request.tl_commented_at = timezone.now()
        ot_request.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action='overtime_approve',
            description=f"Team Leader commented on OT request for {ot_request.employee.get_full_name() or ot_request.employee.username}",
            target_user=ot_request.employee
        )
        
        # TEAM-020: Notify employee
        Notification.objects.create(
            employee=ot_request.employee,
            message=f"Team Leader added a comment on your overtime request: {comment[:50]}..."
        )
        
        # Notify HR (only HR can approve OT)
        from django.db.models import Q
        hr_users = User.objects.filter(
            Q(employeeprofile__is_hr=True) | Q(is_superuser=True)
        ).distinct()
        
        for user in hr_users:
            Notification.objects.create(
                employee=user,
                message=f"Team Leader commented on OT request from {ot_request.employee.get_full_name() or ot_request.employee.username}"
            )
        
        messages.success(request, "Comment added successfully!")
        
    except Exception as e:
        messages.error(request, f"Error adding comment: {str(e)}")
    
    return redirect(request.META.get('HTTP_REFERER', 'team_leader_dashboard'))


@login_required
@team_leader_or_hr
@require_http_methods(["POST"])
def add_tl_comment_onsite(request, onsite_id):
    """
    TEAM-018: Add Team Leader comment on Onsite request
    """
    onsite_request = get_object_or_404(OnsiteRequest, id=onsite_id)
    
    try:
        comment = request.POST.get('tl_comment', '').strip()
        
        if not comment:
            messages.error(request, "Comment cannot be empty")
            return redirect(request.META.get('HTTP_REFERER', 'team_leader_dashboard'))
        
        # Update comment
        onsite_request.tl_comment = comment
        onsite_request.tl_approver = request.user
        onsite_request.tl_commented_at = timezone.now()
        onsite_request.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action='user_create',
            description=f"Team Leader commented on Onsite request for {onsite_request.employee.get_full_name() or onsite_request.employee.username}",
            target_user=onsite_request.employee
        )
        
        # TEAM-020: Notify employee
        Notification.objects.create(
            employee=onsite_request.employee,
            message=f"Team Leader added a comment on your onsite request: {comment[:50]}..."
        )
        
        # Notify manager/HR
        from django.db.models import Q
        managers_hr = User.objects.filter(
            Q(employeeprofile__role__in=['manager', 'hr']) | 
            Q(employeeprofile__is_hr=True) | 
            Q(is_superuser=True)
        ).distinct()
        
        for user in managers_hr:
            Notification.objects.create(
                employee=user,
                message=f"Team Leader commented on Onsite request from {onsite_request.employee.get_full_name() or onsite_request.employee.username}"
            )
        
        messages.success(request, "Comment added successfully!")
        
    except Exception as e:
        messages.error(request, f"Error adding comment: {str(e)}")
    
    return redirect(request.META.get('HTTP_REFERER', 'team_leader_dashboard'))
