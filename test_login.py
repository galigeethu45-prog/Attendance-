"""
Quick test script to verify login functionality
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Create test client
client = Client()

# Test 1: Check if login page is accessible
print("Test 1: Accessing login page...")
response = client.get('/login/')
print(f"Status Code: {response.status_code}")
print(f"✓ Login page accessible!" if response.status_code == 200 else "✗ Login page error!")

# Test 2: Check if root redirects to login
print("\nTest 2: Accessing root URL...")
response = client.get('/')
print(f"Status Code: {response.status_code}")
print(f"✓ Root URL accessible!" if response.status_code == 200 else "✗ Root URL error!")

# Test 3: Check if dashboard requires login
print("\nTest 3: Accessing dashboard without login...")
response = client.get('/attendance/')
print(f"Status Code: {response.status_code}")
print(f"✓ Dashboard redirects to login!" if response.status_code == 302 else "✗ Dashboard accessible without login!")

# Test 4: Test login with demo user
print("\nTest 4: Testing login with demo user...")
response = client.post('/login/', {
    'username': 'employee1',
    'password': 'emp123'
})
print(f"Status Code: {response.status_code}")
print(f"✓ Login successful!" if response.status_code == 302 else "✗ Login failed!")

# Test 5: Check if dashboard is accessible after login
print("\nTest 5: Accessing dashboard after login...")
response = client.get('/attendance/')
print(f"Status Code: {response.status_code}")
print(f"✓ Dashboard accessible after login!" if response.status_code == 200 else "✗ Dashboard not accessible!")

# Test 6: Test logout
print("\nTest 6: Testing logout...")
response = client.get('/logout/')
print(f"Status Code: {response.status_code}")
print(f"✓ Logout successful!" if response.status_code == 302 else "✗ Logout failed!")

print("\n" + "="*50)
print("All tests completed!")
print("="*50)
