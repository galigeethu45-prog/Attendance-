from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from attendance.models import EmployeeProfile
from .serializers import RegisterSerializer


@api_view(['POST'])
def register_api(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Registration successful"},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_api(request):
    identifier = request.data.get('identifier')  # employee_id OR email
    password = request.data.get('password')

    if not identifier or not password:
        return Response(
            {"error": "Identifier and password required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Determine login type
    if '@' in identifier:
        try:
            user = User.objects.get(email=identifier)
            username = user.username
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
    else:
        username = identifier  # employee_id stored as username

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    login(request, user)

    profile = EmployeeProfile.objects.get(user=user)

    return Response({
        "message": "Login successful",
        "employee_id": profile.employee_id,
        "is_hr": profile.is_hr,
        "profile_completed": hasattr(profile, 'profile_completed') and profile.profile_completed
    })