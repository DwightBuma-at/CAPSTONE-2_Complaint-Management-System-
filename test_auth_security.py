#!/usr/bin/env python3
"""
Test script to verify authentication security for admin pages
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_unauthorized_access():
    """Test that unauthorized users cannot access admin pages"""
    print("🔒 Testing unauthorized access to admin pages...")
    
    admin_pages = [
        "/admin-dashboard.html/",
        "/admin-complaints.html/",
        "/admin-user.html/"
    ]
    
    for page in admin_pages:
        try:
            response = requests.get(f"{BASE_URL}{page}", allow_redirects=False)
            print(f"  {page}: Status {response.status_code}")
            
            if response.status_code == 302:
                # Should redirect to index with login modal
                redirect_url = response.headers.get('Location', '')
                if 'show_login=true' in redirect_url:
                    print(f"    ✅ Correctly redirects to login: {redirect_url}")
                else:
                    print(f"    ❌ Incorrect redirect: {redirect_url}")
            elif response.status_code == 401:
                print(f"    ✅ Returns 401 Unauthorized")
            else:
                print(f"    ❌ Unexpected status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"    ❌ Error accessing {page}: {e}")
    
    print()

def test_api_endpoints():
    """Test that API endpoints require authentication"""
    print("🔒 Testing API endpoint security...")
    
    api_endpoints = [
        "/api/admin/me/",
        "/api/transactions/",
    ]
    
    for endpoint in api_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"  {endpoint}: Status {response.status_code}")
            
            if response.status_code == 401:
                print(f"    ✅ Correctly requires authentication")
            else:
                print(f"    ❌ Should require authentication")
                
        except requests.exceptions.RequestException as e:
            print(f"    ❌ Error accessing {endpoint}: {e}")
    
    print()

def test_session_management():
    """Test session management"""
    print("🔒 Testing session management...")
    
    # Create a session
    session = requests.Session()
    
    # Try to access admin page without authentication
    try:
        response = session.get(f"{BASE_URL}/admin-dashboard.html/", allow_redirects=False)
        print(f"  Without auth: Status {response.status_code}")
        
        if response.status_code == 302:
            print(f"    ✅ Correctly redirects unauthorized users")
        else:
            print(f"    ❌ Should redirect unauthorized users")
            
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Error: {e}")
    
    print()

if __name__ == "__main__":
    print("🚀 Testing Authentication Security System")
    print("=" * 50)
    
    test_unauthorized_access()
    test_api_endpoints()
    test_session_management()
    
    print("✅ Security tests completed!")
    print("\n📋 Summary:")
    print("- Admin pages should redirect to login modal when accessed without authentication")
    print("- API endpoints should return 401 for unauthorized requests")
    print("- Session management should prevent unauthorized access")
    print("\n🔐 To test admin login:")
    print("1. Go to http://127.0.0.1:8000/")
    print("2. Click 'Login' and select 'Admin' role")
    print("3. Enter admin credentials and 6-digit access key")
    print("4. You should be redirected to admin dashboard")
