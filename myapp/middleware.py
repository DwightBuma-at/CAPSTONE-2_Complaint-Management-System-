from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
import json

class RoleBasedAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of admin pages that require admin authentication (both with and without trailing slashes)
        admin_pages = [
            '/admin-dashboard.html/',
            '/admin-dashboard.html',
            '/admin-complaints.html/',
            '/admin-complaints.html',
            '/admin-user.html/',
            '/admin-user.html',
        ]
        
        # List of user pages that require user authentication (both with and without trailing slashes)
        user_pages = [
            '/user.html/',
            '/user.html',
            '/user-submit.html/',
            '/user-submit.html',
            '/user-view.html/',
            '/user-view.html',
        ]
        
        # Check if the current path is an admin page
        if request.path in admin_pages:
            # Only block if user is authenticated as a regular user (not admin)
            # This prevents regular users from accessing admin pages via URL
            # Safety check: ensure request.user exists (should be added by AuthenticationMiddleware)
            if hasattr(request, 'user') and request.user.is_authenticated and not request.session.get('admin_authenticated'):
                print(f"🚫 Regular user blocked from accessing admin page {request.path}")
                # If it's an AJAX request, return JSON response
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Access denied. Regular users cannot access admin pages.',
                        'redirect': '/index.html',
                        'show_login': True
                    }, status=403)
                else:
                    # For regular requests, redirect to index with login modal
                    return redirect('/index.html?show_login=true')
            else:
                print(f"✅ Access granted for {request.path}")
        
        # Check if the current path is a user page
        elif request.path in user_pages:
            # Only block if user is authenticated as admin
            # This prevents admins from accessing user pages via URL
            if request.session.get('admin_authenticated'):
                print(f"🚫 Admin blocked from accessing user page {request.path}")
                # If it's an AJAX request, return JSON response
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Access denied. Admins cannot access user pages.',
                        'redirect': '/index.html',
                        'show_login': True
                    }, status=403)
                else:
                    # For regular requests, redirect to index with login modal
                    return redirect('/index.html?show_login=true')
            else:
                print(f"✅ Access granted for {request.path}")
        
        response = self.get_response(request)
        return response
