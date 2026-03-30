from django.contrib.auth.models import User
from rest_framework import serializers
from attendance.models import EmployeeProfile


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

