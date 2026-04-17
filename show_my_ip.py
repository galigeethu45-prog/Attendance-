"""
Quick script to show what IP address the system sees
Run this from office to find your Regus IP
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory
from attendance.views import get_client_ip

# Create a fake request
factory = RequestFactory()
request = factory.get('/')

# Simulate different scenarios
print("="*60)
print("IP ADDRESS DETECTION TEST")
print("="*60)

# Test 1: Direct connection
request.META['REMOTE_ADDR'] = '203.0.113.45'  # Example
print("\nScenario 1: Direct Connection")
print(f"IP detected: {get_client_ip(request)}")

# Test 2: Behind proxy/load balancer (AWS scenario)
request.META['HTTP_X_FORWARDED_FOR'] = '198.51.100.30, 10.0.0.1'
print("\nScenario 2: Behind Load Balancer (AWS)")
print(f"IP detected: {get_client_ip(request)}")
print("(First IP in X-Forwarded-For is the real client IP)")

print("\n" + "="*60)
print("TO FIND YOUR OFFICE IP:")
print("="*60)
print("\n1. Go to office and connect to Regus WiFi")
print("2. Visit: https://whatismyipaddress.com")
print("3. Copy the IP address shown")
print("4. Add it to attendance/views.py in ALLOWED_OFFICE_IPS")
print("\nSee GET_OFFICE_IP_GUIDE.txt for detailed instructions")
print("="*60)
