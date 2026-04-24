"""
Middleware for blocking mobile device access
"""
from django.shortcuts import render
from django.conf import settings
import re


class BlockMobileMiddleware:
    """
    Middleware to block mobile device access to the attendance system.
    Only allows desktop/laptop browsers.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Mobile user agent patterns
        self.mobile_patterns = [
            r'Android',
            r'webOS',
            r'iPhone',
            r'iPad',
            r'iPod',
            r'BlackBerry',
            r'IEMobile',
            r'Opera Mini',
            r'Mobile',
            r'mobile',
            r'CriOS',  # Chrome on iOS
        ]
        
        # Compile regex patterns for better performance
        self.mobile_regex = re.compile('|'.join(self.mobile_patterns), re.IGNORECASE)
    
    def __call__(self, request):
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Check if it's a mobile device
        is_mobile = self.mobile_regex.search(user_agent)
        
        # Block mobile devices
        if is_mobile:
            # Allow static files and media files
            if request.path.startswith('/static/') or request.path.startswith('/media/'):
                return self.get_response(request)
            
            # Show mobile blocked page
            return render(request, 'mobile_blocked.html', status=403)
        
        # Allow desktop access
        response = self.get_response(request)
        return response
