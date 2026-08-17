from django.contrib.auth.models import User
from rest_framework import serializers
from attendance.models import EmployeeProfile, Team, TeamMembership


class RegisterSerializer(serializers.Serializer):
    employee_id = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if not value.endswith('@arraafiinfotech.com'):
            raise serializers.ValidationError(
                "Only @arraafiinfotech.com email is allowed"
            )
        return value

    def validate_employee_id(self, value):
        if EmployeeProfile.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError(
                "Employee ID already exists"
            )
        return value

    def create(self, validated_data):
        # Create User
        user = User.objects.create_user(
            username=validated_data['employee_id'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Create Employee Profile
        EmployeeProfile.objects.create(
            user=user,
            employee_id=validated_data['employee_id']
        )

        return user


# =========================
# TEAM MANAGEMENT SERIALIZERS
# =========================
class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for team displays"""
    employee_id = serializers.CharField(source='employeeprofile.employee_id', read_only=True)
    department = serializers.CharField(source='employeeprofile.department', read_only=True)
    designation = serializers.CharField(source='employeeprofile.designation', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'employee_id', 'department', 'designation']


class TeamMembershipSerializer(serializers.ModelSerializer):
    """Serializer for team membership with employee details"""
    employee = UserBasicSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True)
    added_by_name = serializers.CharField(source='added_by.get_full_name', read_only=True)
    
    class Meta:
        model = TeamMembership
        fields = ['id', 'employee', 'employee_id', 'is_active', 'added_at', 'added_by', 'added_by_name', 'removed_at']
        read_only_fields = ['id', 'added_at', 'added_by', 'removed_at']


class TeamSerializer(serializers.ModelSerializer):
    """Full team serializer with all details"""
    team_leader_details = UserBasicSerializer(source='team_leader', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    member_count = serializers.IntegerField(source='get_member_count', read_only=True)
    members = TeamMembershipSerializer(source='memberships', many=True, read_only=True)
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'department', 'team_leader', 'team_leader_details',
            'description', 'is_active', 'created_at', 'updated_at',
            'created_by', 'created_by_name', 'member_count', 'members'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def validate_name(self, value):
        """Ensure team name is unique (case-insensitive)"""
        team_id = self.instance.id if self.instance else None
        existing = Team.objects.filter(name__iexact=value)
        if team_id:
            existing = existing.exclude(id=team_id)
        if existing.exists():
            raise serializers.ValidationError("A team with this name already exists")
        return value


class TeamListSerializer(serializers.ModelSerializer):
    """Lightweight team serializer for list views"""
    team_leader_name = serializers.CharField(source='team_leader.get_full_name', read_only=True)
    member_count = serializers.IntegerField(source='get_member_count', read_only=True)
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'department', 'team_leader', 'team_leader_name', 'member_count', 'is_active']


class BulkMemberAssignmentSerializer(serializers.Serializer):
    """Serializer for bulk member assignment"""
    team_id = serializers.IntegerField()
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of employee (User) IDs to add to the team"
    )
    
    def validate_team_id(self, value):
        """Ensure team exists and is active"""
        try:
            team = Team.objects.get(id=value, is_active=True)
        except Team.DoesNotExist:
            raise serializers.ValidationError("Team not found or inactive")
        return value
    
    def validate_employee_ids(self, value):
        """Ensure all employees exist"""
        existing_count = User.objects.filter(id__in=value).count()
        if existing_count != len(value):
            raise serializers.ValidationError("One or more employee IDs are invalid")
        return value


