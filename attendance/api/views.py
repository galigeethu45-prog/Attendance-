from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from functools import wraps
import json

from attendance.models import EmployeeProfile, Team, TeamMembership


# =========================
# PERMISSION DECORATORS (TEAM-007)
# =========================
def hr_required(view_func):
    """
    Decorator to restrict access to HR/Admin users only
    Checks: is_authenticated AND (is_superuser OR is_hr flag OR role in ['hr', 'manager'])
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        
        # Superusers always have access
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Check HR profile
        try:
            profile = request.user.employeeprofile
            if profile.is_hr or profile.role in ['hr', 'manager']:
                return view_func(request, *args, **kwargs)
        except EmployeeProfile.DoesNotExist:
            pass
        
        return JsonResponse({"error": "HR/Admin access required"}, status=403)
    
    return wrapper


def team_leader_or_hr_required(view_func):
    """
    Decorator to restrict access to Team Leaders, HR, or Admin
    Checks: is_authenticated AND (is_superuser OR is_hr OR is_team_leader)
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        
        # Superusers always have access
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Check profile permissions
        try:
            profile = request.user.employeeprofile
            if profile.is_hr or profile.is_team_leader or profile.role in ['hr', 'manager', 'team_leader']:
                return view_func(request, *args, **kwargs)
        except EmployeeProfile.DoesNotExist:
            pass
        
        return JsonResponse({"error": "Team Leader, HR, or Admin access required"}, status=403)
    
    return wrapper


@csrf_exempt
@require_http_methods(["POST"])
def register_api(request):
    # This can be implemented later if needed
    return JsonResponse({"error": "Not implemented"}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    data = json.loads(request.body)
    identifier = data.get('identifier')  # employee_id OR email
    password = data.get('password')

    if not identifier or not password:
        return JsonResponse(
            {"error": "Identifier and password required"}, 
            status=400
        )

    # Determine login type
    if '@' in identifier:
        try:
            user = User.objects.get(email=identifier)
            username = user.username
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "Invalid credentials"}, 
                status=401
            )
    else:
        username = identifier  # employee_id stored as username

    user = authenticate(username=username, password=password)

    if user is None:
        return JsonResponse(
            {"error": "Invalid credentials"}, 
            status=401
        )

    login(request, user)

    profile = EmployeeProfile.objects.get(user=user)

    return JsonResponse({
        "message": "Login successful",
        "employee_id": profile.employee_id,
        "is_hr": profile.is_hr,
        "profile_completed": hasattr(profile, 'profile_completed') and profile.profile_completed
    })




@require_http_methods(["GET"])
def test_auth_api(request):
    """Test endpoint to check authentication status"""
    if not request.user.is_authenticated:
        return JsonResponse({
            "authenticated": False,
            "user": "Anonymous"
        })
    
    try:
        profile = request.user.employeeprofile
        return JsonResponse({
            "authenticated": True,
            "user": request.user.username,
            "is_superuser": request.user.is_superuser,
            "employee_id": profile.employee_id,
            "is_hr": profile.is_hr,
            "role": profile.role
        })
    except EmployeeProfile.DoesNotExist:
        return JsonResponse({
            "authenticated": True,
            "user": request.user.username,
            "is_superuser": request.user.is_superuser,
            "employee_id": "NO_PROFILE",
            "is_hr": False,
            "role": "NO_PROFILE"
        })


@require_http_methods(["GET"])
def missing_checkouts_api(request):
    """Get missing checkouts for employee(s) - only for dates before today"""
    from django.utils import timezone
    from attendance.models import Attendance, LeaveRequest, WFHRequest
    from datetime import timedelta
    
    # Authentication and authorization check
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    # Allow superusers OR HR users
    is_authorized = False
    if request.user.is_superuser:
        is_authorized = True
        print(f"DEBUG: Superuser {request.user.username} granted access")
    else:
        try:
            profile = request.user.employeeprofile
            print(f"DEBUG: User {request.user.username}, is_hr: {profile.is_hr}, role: {profile.role}")
            if profile.is_hr:
                is_authorized = True
        except EmployeeProfile.DoesNotExist:
            pass
    
    if not is_authorized:
        return JsonResponse({"error": "HR access only"}, status=403)
    
    
    today = timezone.localtime(timezone.now()).date()
    yesterday = today - timedelta(days=1)
    
    mode = request.GET.get('mode', 'specific')
    
    if request.GET.get('all'):
        # All employees with missing checkouts
        all_missing = Attendance.objects.filter(
            check_in__isnull=False,
            check_out__isnull=True,
            date__lte=yesterday  # Only up to yesterday
        ).select_related('employee', 'employee__employeeprofile').order_by('-date')
        
        results = []
        total_to_assign = 0
        
        for att in all_missing:
            # Check if employee is on leave/WFH
            is_on_leave = LeaveRequest.objects.filter(
                employee=att.employee,
                status='approved',
                start_date__lte=att.date,
                end_date__gte=att.date
            ).exists()
            
            is_on_wfh = WFHRequest.objects.filter(
                employee=att.employee,
                status='approved',
                start_date__lte=att.date,
                end_date__gte=att.date
            ).exists()
            
            skip_reason = None
            if is_on_leave:
                skip_reason = "On Leave"
            elif is_on_wfh:
                skip_reason = "On WFH"
            else:
                total_to_assign += 1
            
            results.append({
                'employee_name': att.employee.get_full_name() or att.employee.username,
                'employee_id': att.employee.employeeprofile.employee_id,
                'date': att.date.strftime('%Y-%m-%d'),
                'date_display': att.date.strftime('%b %d, %Y'),
                'check_in_time': att.check_in.strftime('%I:%M %p'),
                'skip_reason': skip_reason
            })
        
        return JsonResponse({
            'missing_checkouts': results,
            'total_records': len(results),
            'total_employees': len(set(a['employee_id'] for a in results)),
            'total_to_assign': total_to_assign
        })
    else:
        # Specific employee
        employee_id = request.GET.get('employee_id')
        if not employee_id:
            return JsonResponse({"error": "Employee ID is required"}, status=400)
        
        try:
            emp = User.objects.get(id=employee_id)
        except User.DoesNotExist:
            return JsonResponse({"error": f"Employee with ID {employee_id} not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Error fetching employee: {str(e)}"}, status=500)
        
        missing_for_emp = Attendance.objects.filter(
            employee=emp,
            check_in__isnull=False,
            check_out__isnull=True,
            date__lte=yesterday  # Only up to yesterday
        ).order_by('-date')
        
        results = []
        for att in missing_for_emp:
            is_on_leave = LeaveRequest.objects.filter(
                employee=emp,
                status='approved',
                start_date__lte=att.date,
                end_date__gte=att.date
            ).exists()
            
            is_on_wfh = WFHRequest.objects.filter(
                employee=emp,
                status='approved',
                start_date__lte=att.date,
                end_date__gte=att.date
            ).exists()
            
            skip_reason = None
            if is_on_leave:
                skip_reason = "On Leave"
            elif is_on_wfh:
                skip_reason = "On WFH"
            
            results.append({
                'employee_name': emp.get_full_name() or emp.username,
                'date': att.date.strftime('%Y-%m-%d'),
                'date_display': att.date.strftime('%b %d, %Y'),
                'check_in_time': att.check_in.strftime('%I:%M %p'),
                'skip_reason': skip_reason
            })
        
        return JsonResponse({
            'missing_checkouts': results,
            'total_records': len(results)
        })


@csrf_exempt
@require_http_methods(["POST"])
def assign_missing_checkouts_api(request):
    """Assign missing checkouts for employee(s)"""
    from django.utils import timezone
    from datetime import time, timedelta, datetime
    from attendance.models import Attendance, LeaveRequest, WFHRequest, AuditLog
    
    # Authentication and authorization check
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    # Allow superusers OR HR users
    is_authorized = False
    if request.user.is_superuser:
        is_authorized = True
        print(f"DEBUG: Superuser {request.user.username} granted access to assign")
    else:
        try:
            profile = request.user.employeeprofile
            if profile.is_hr:
                is_authorized = True
        except EmployeeProfile.DoesNotExist:
            pass
    
    if not is_authorized:
        return JsonResponse({"error": "HR access only"}, status=403)
    
    data = json.loads(request.body)
    today = timezone.localtime(timezone.now()).date()
    yesterday = today - timedelta(days=1)
    checkout_time = time(19, 0)  # 7 PM
    
    mode = data.get('mode')
    employee_id = data.get('employee_id')
    
    # Validation
    if not mode or mode not in ['all', 'specific']:
        return JsonResponse({"error": "Valid mode ('all' or 'specific') is required"}, status=400)
    
    if mode == 'specific' and not employee_id:
        return JsonResponse({"error": "Employee ID is required for specific mode"}, status=400)
    
    assigned_count = 0
    skipped_count = 0
    results = []
    
    if mode == 'all':
        # Get all employees with missing checkouts
        all_missing = Attendance.objects.filter(
            check_in__isnull=False,
            check_out__isnull=True,
            date__lte=yesterday
        ).select_related('employee').order_by('-date')
        
        for att in all_missing:
            # Check leave only (WFH employees still need checkout)
            is_on_leave = LeaveRequest.objects.filter(
                employee=att.employee,
                status='approved',
                start_date__lte=att.date,
                end_date__gte=att.date
            ).exists()
            
            # WFH check removed - WFH employees need checkout assigned
            # is_on_wfh = WFHRequest.objects.filter(
            #     employee=att.employee,
            #     status='approved',
            #     start_date__lte=att.date,
            #     end_date__gte=att.date
            # ).exists()
            
            if is_on_leave:
                skipped_count += 1
                results.append({
                    'employee_name': att.employee.get_full_name() or att.employee.username,
                    'date': att.date.strftime('%b %d, %Y'),
                    'check_in_time': att.check_in.strftime('%I:%M %p'),
                    'success': False,
                    'reason': 'On Leave'
                })
            # elif is_on_wfh:  # REMOVED - WFH should not skip checkout
            #     skipped_count += 1
            #     results.append({
            #         'employee_name': att.employee.get_full_name() or att.employee.username,
            #         'date': att.date.strftime('%b %d, %Y'),
            #         'check_in_time': att.check_in.strftime('%I:%M %p'),
            #         'success': False,
            #         'reason': 'On WFH'
            #     })
            else:
                # Assign checkout
                try:
                    checkout_datetime = timezone.make_aware(
                        datetime.combine(att.date, checkout_time)
                    )
                    att.check_out = checkout_datetime
                    att.calculate_work_hours()
                    att.save()
                    
                    # Create audit log
                    AuditLog.objects.create(
                        user=request.user,
                        action='check_out',
                        description=f'Bulk checkout assignment: 7 PM for {att.employee.username} on {att.date}',
                        target_user=att.employee
                    )
                    
                    assigned_count += 1
                    results.append({
                        'employee_name': att.employee.get_full_name() or att.employee.username,
                        'date': att.date.strftime('%b %d, %Y'),
                        'check_in_time': att.check_in.strftime('%I:%M %p'),
                        'success': True,
                        'reason': 'Assigned'
                    })
                except Exception as e:
                    skipped_count += 1
                    results.append({
                        'employee_name': att.employee.get_full_name() or att.employee.username,
                        'date': att.date.strftime('%b %d, %Y'),
                        'check_in_time': att.check_in.strftime('%I:%M %p'),
                        'success': False,
                        'reason': str(e)
                    })
    
    else:
        employee_id = data.get('employee_id')
        if not employee_id or employee_id == 'undefined':
            return JsonResponse({"error": "Valid employee ID is required"}, status=400)
        
        try:
            emp = User.objects.get(id=employee_id)
        except User.DoesNotExist:
            return JsonResponse({"error": f"Employee with ID {employee_id} not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Error fetching employee: {str(e)}"}, status=500)
        
        missing_for_emp = Attendance.objects.filter(
            employee=emp,
            check_in__isnull=False,
            check_out__isnull=True,
            date__lte=yesterday
        ).order_by('-date')
        
        for att in missing_for_emp:
            # Check leave only (WFH employees still need checkout)
            is_on_leave = LeaveRequest.objects.filter(
                employee=emp,
                status='approved',
                start_date__lte=att.date,
                end_date__gte=att.date
            ).exists()
            
            # WFH check removed - WFH employees need checkout assigned
            # is_on_wfh = WFHRequest.objects.filter(
            #     employee=emp,
            #     status='approved',
            #     start_date__lte=att.date,
            #     end_date__gte=att.date
            # ).exists()
            
            if is_on_leave:
                skipped_count += 1
                results.append({
                    'employee_name': emp.get_full_name() or emp.username,
                    'date': att.date.strftime('%b %d, %Y'),
                    'check_in_time': att.check_in.strftime('%I:%M %p'),
                    'success': False,
                    'reason': 'On Leave'
                })
            # elif is_on_wfh:  # REMOVED - WFH should not skip checkout
            #     skipped_count += 1
            #     results.append({
            #         'employee_name': emp.get_full_name() or emp.username,
            #         'date': att.date.strftime('%b %d, %Y'),
            #         'check_in_time': att.check_in.strftime('%I:%M %p'),
            #         'success': False,
            #         'reason': 'On WFH'
            #     })
            else:
                try:
                    checkout_datetime = timezone.make_aware(
                        datetime.combine(att.date, checkout_time)
                    )
                    att.check_out = checkout_datetime
                    att.calculate_work_hours()
                    att.save()
                    
                    AuditLog.objects.create(
                        user=request.user,
                        action='check_out',
                        description=f'Bulk checkout assignment: 7 PM for {att.employee.username} on {att.date}',
                        target_user=att.employee
                    )
                    
                    assigned_count += 1
                    results.append({
                        'employee_name': emp.get_full_name() or emp.username,
                        'date': att.date.strftime('%b %d, %Y'),
                        'check_in_time': att.check_in.strftime('%I:%M %p'),
                        'success': True,
                        'reason': 'Assigned'
                    })
                except Exception as e:
                    skipped_count += 1
                    results.append({
                        'employee_name': emp.get_full_name() or emp.username,
                        'date': att.date.strftime('%b %d, %Y'),
                        'check_in_time': att.check_in.strftime('%I:%M %p'),
                        'success': False,
                        'reason': str(e)
                    })
    
    return JsonResponse({
        'assigned_count': assigned_count,
        'skipped_count': skipped_count,
        'results': results
    })



# =========================
# TEAM MANAGEMENT APIs (TEAM-005, TEAM-006)
# =========================

@require_http_methods(["GET"])
@hr_required
def teams_list_api(request):
    """
    TEAM-010: List all teams (HR sees all details, others see names only)
    GET /api/teams/
    """
    from attendance.api.serializers import TeamListSerializer
    
    # Check if user is HR for detailed view
    is_hr_user = request.user.is_superuser
    if not is_hr_user:
        try:
            profile = request.user.employeeprofile
            is_hr_user = profile.is_hr or profile.role in ['hr', 'manager']
        except EmployeeProfile.DoesNotExist:
            pass
    
    if is_hr_user:
        # HR sees all teams with full details
        teams = Team.objects.filter(is_active=True).select_related('team_leader').order_by('department', 'name')
    else:
        # Others see only active teams (names only)
        teams = Team.objects.filter(is_active=True).only('id', 'name', 'department')
    
    serializer = TeamListSerializer(teams, many=True)
    return JsonResponse({
        'teams': serializer.data,
        'count': len(serializer.data)
    })


@require_http_methods(["GET"])
@team_leader_or_hr_required
def team_detail_api(request, team_id):
    """
    TEAM-011: Get team details with member list (role-based filtering)
    GET /api/teams/<team_id>/
    """
    from attendance.api.serializers import TeamSerializer
    from django.shortcuts import get_object_or_404
    
    team = get_object_or_404(Team, id=team_id, is_active=True)
    
    # Check permissions: HR/Admin see all, Team Leader sees only their teams
    is_hr_user = request.user.is_superuser
    if not is_hr_user:
        try:
            profile = request.user.employeeprofile
            is_hr_user = profile.is_hr or profile.role in ['hr', 'manager']
        except EmployeeProfile.DoesNotExist:
            pass
    
    if not is_hr_user:
        # Team Leader can only see their own teams
        if team.team_leader != request.user:
            return JsonResponse({"error": "You can only view teams you lead"}, status=403)
    
    serializer = TeamSerializer(team)
    return JsonResponse(serializer.data)


@csrf_exempt
@require_http_methods(["POST"])
@hr_required
def team_create_api(request):
    """
    TEAM-005: Create a new team (HR only)
    POST /api/teams/create/
    Body: {
        "name": "Frontend Team",
        "department": "Engineering",
        "team_leader": 5,  // User ID
        "description": "Optional description"
    }
    """
    from attendance.api.serializers import TeamSerializer
    from attendance.models import AuditLog
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    # Validate team_leader if provided
    if 'team_leader' in data and data['team_leader']:
        try:
            leader = User.objects.get(id=data['team_leader'])
        except User.DoesNotExist:
            return JsonResponse({"error": "Team leader not found"}, status=400)
    
    serializer = TeamSerializer(data=data)
    if serializer.is_valid():
        team = serializer.save(created_by=request.user)
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action='user_create',
            description=f"Created team: {team.name} in {team.department} department"
        )
        
        return JsonResponse({
            'message': 'Team created successfully',
            'team': TeamSerializer(team).data
        }, status=201)
    
    return JsonResponse({"errors": serializer.errors}, status=400)


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
@hr_required
def team_update_api(request, team_id):
    """
    TEAM-005: Update team details (HR only)
    PUT/PATCH /api/teams/<team_id>/update/
    """
    from attendance.api.serializers import TeamSerializer
    from attendance.models import AuditLog
    from django.shortcuts import get_object_or_404
    
    team = get_object_or_404(Team, id=team_id)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    # Validate team_leader if being updated
    if 'team_leader' in data and data['team_leader']:
        try:
            leader = User.objects.get(id=data['team_leader'])
        except User.DoesNotExist:
            return JsonResponse({"error": "Team leader not found"}, status=400)
    
    serializer = TeamSerializer(team, data=data, partial=True)
    if serializer.is_valid():
        team = serializer.save()
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action='user_create',
            description=f"Updated team: {team.name}"
        )
        
        return JsonResponse({
            'message': 'Team updated successfully',
            'team': TeamSerializer(team).data
        })
    
    return JsonResponse({"errors": serializer.errors}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
@hr_required
def team_delete_api(request, team_id):
    """
    TEAM-005: Delete (deactivate) a team (HR only)
    DELETE /api/teams/<team_id>/delete/
    """
    from attendance.models import AuditLog
    from django.shortcuts import get_object_or_404
    
    team = get_object_or_404(Team, id=team_id)
    
    # Soft delete
    team.is_active = False
    team.save()
    
    # Deactivate all memberships
    TeamMembership.objects.filter(team=team, is_active=True).update(is_active=False)
    
    # Create audit log
    AuditLog.objects.create(
        user=request.user,
        action='user_delete',
        description=f"Deactivated team: {team.name}"
    )
    
    return JsonResponse({'message': 'Team deactivated successfully'})


@csrf_exempt
@require_http_methods(["POST"])
@hr_required
def team_add_member_api(request, team_id):
    """
    TEAM-006: Add a single member to team (HR only)
    POST /api/teams/<team_id>/add-member/
    Body: {"employee_id": 10}
    """
    from attendance.models import AuditLog
    from django.shortcuts import get_object_or_404
    
    team = get_object_or_404(Team, id=team_id, is_active=True)
    
    try:
        data = json.loads(request.body)
        employee_id = data.get('employee_id')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    if not employee_id:
        return JsonResponse({"error": "employee_id is required"}, status=400)
    
    try:
        employee = User.objects.get(id=employee_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "Employee not found"}, status=404)
    
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
        
        return JsonResponse({
            'message': message,
            'membership_id': membership.id
        }, status=201)
    
    return JsonResponse({"error": message}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
@hr_required
def team_remove_member_api(request, team_id):
    """
    TEAM-006: Remove a member from team (HR only)
    POST /api/teams/<team_id>/remove-member/
    Body: {"employee_id": 10}
    """
    from attendance.models import AuditLog
    from django.shortcuts import get_object_or_404
    
    team = get_object_or_404(Team, id=team_id, is_active=True)
    
    try:
        data = json.loads(request.body)
        employee_id = data.get('employee_id')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    if not employee_id:
        return JsonResponse({"error": "employee_id is required"}, status=400)
    
    try:
        employee = User.objects.get(id=employee_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "Employee not found"}, status=404)
    
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
        
        return JsonResponse({'message': message})
    
    return JsonResponse({"error": message}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
@hr_required
def team_bulk_add_members_api(request):
    """
    TEAM-006: Bulk add members to a team (HR only)
    POST /api/teams/bulk-add-members/
    Body: {
        "team_id": 1,
        "employee_ids": [5, 10, 15, 20]
    }
    """
    from attendance.api.serializers import BulkMemberAssignmentSerializer
    from attendance.models import AuditLog
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    serializer = BulkMemberAssignmentSerializer(data=data)
    if not serializer.is_valid():
        return JsonResponse({"errors": serializer.errors}, status=400)
    
    team_id = serializer.validated_data['team_id']
    employee_ids = serializer.validated_data['employee_ids']
    
    try:
        team = Team.objects.get(id=team_id, is_active=True)
    except Team.DoesNotExist:
        return JsonResponse({"error": "Team not found or inactive"}, status=404)
    
    # Bulk add members
    added = []
    skipped = []
    errors = []
    
    for emp_id in employee_ids:
        try:
            employee = User.objects.get(id=emp_id)
            success, message, membership = team.add_member(employee, added_by=request.user)
            
            if success:
                added.append({
                    'employee_id': emp_id,
                    'name': employee.get_full_name() or employee.username
                })
                
                # Create audit log for each addition
                AuditLog.objects.create(
                    user=request.user,
                    action='user_create',
                    description=f"Bulk add: Added {employee.get_full_name() or employee.username} to team {team.name}",
                    target_user=employee
                )
            else:
                skipped.append({
                    'employee_id': emp_id,
                    'name': employee.get_full_name() or employee.username,
                    'reason': message
                })
        except User.DoesNotExist:
            errors.append({
                'employee_id': emp_id,
                'reason': 'Employee not found'
            })
    
    return JsonResponse({
        'message': f'Bulk operation completed',
        'added_count': len(added),
        'skipped_count': len(skipped),
        'error_count': len(errors),
        'added': added,
        'skipped': skipped,
        'errors': errors
    })


@require_http_methods(["GET"])
@team_leader_or_hr_required
def my_teams_api(request):
    """
    Get teams where the logged-in user is the team leader
    GET /api/teams/my-teams/
    """
    from attendance.api.serializers import TeamSerializer
    
    teams = Team.objects.filter(
        team_leader=request.user,
        is_active=True
    ).select_related('team_leader', 'created_by').prefetch_related('memberships__employee')
    
    serializer = TeamSerializer(teams, many=True)
    return JsonResponse({
        'teams': serializer.data,
        'count': len(serializer.data)
    })


@require_http_methods(["GET"])
def team_members_api(request, team_id):
    """
    Get all active members of a team
    GET /api/teams/<team_id>/members/
    """
    from attendance.api.serializers import UserBasicSerializer
    from django.shortcuts import get_object_or_404
    
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    team = get_object_or_404(Team, id=team_id, is_active=True)
    members = team.get_active_members()
    
    serializer = UserBasicSerializer(members, many=True)
    return JsonResponse({
        'team_name': team.name,
        'members': serializer.data,
        'count': len(serializer.data)
    })
