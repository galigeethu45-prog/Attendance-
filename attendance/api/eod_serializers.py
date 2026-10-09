"""
EOD API Integration - Read-Only Serializers
Purpose: Provide minimal employee and attendance data to EOD system
Security: Only expose non-sensitive fields
"""

from rest_framework import serializers
from attendance.models import EmployeeMasterData


class EODEmployeeSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for employee master data → EOD
    
    Exposes ONLY:
    - employee_id
    - first_name
    - last_name
    - department
    - designation
    
    Does NOT expose sensitive fields like:
    - Aadhaar, PAN, email, phone, address, DOB, gender, bank details, salary
    """
    
    class Meta:
        model = EmployeeMasterData
        fields = ['employee_id', 'first_name', 'last_name', 'department', 'designation']
        read_only_fields = ['employee_id', 'first_name', 'last_name', 'department', 'designation']


class EODAttendanceSerializer(serializers.Serializer):
    """
    Read-only serializer for attendance status → EOD
    
    Returns:
    - employee_id: str
    - status: str (PRESENT | ABSENT | WFH | LEAVE)
    
    Status normalization:
    - present → PRESENT
    - late → PRESENT
    - half-day → PRESENT
    - absent → ABSENT
    - Approved WFH → WFH
    - Approved Leave → LEAVE
    """
    
    employee_id = serializers.CharField(read_only=True)
    status = serializers.ChoiceField(choices=['PRESENT', 'ABSENT', 'WFH', 'LEAVE'], read_only=True)
