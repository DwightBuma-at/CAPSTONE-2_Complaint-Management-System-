#!/usr/bin/env python3
"""
Test script to verify security middleware functionality
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_unauthenticated_admin_access():
    """Test that unauthenticated users cannot access admin pages"""
    print("🔒 Testing unauthenticated access to admin pages...")
    
    admin_pages = [
        "/admin-dashboard.html",
        "/admin-dashboard.html/",
        "/admin-complaints.html",
        "/admin-complaints.html/",
        "/admin-user.html",
        "/admin-user.html/"
    ]
    
    for page in admin_pages:
        print(f"\nTesting: {page}")
        try:
            response = requests.get(f"{BASE_URL}{page}", allow_redirects=False)
            print(f"  Status Code: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                print(f"  Redirect Location: {location}")
                if 'show_login=true' in location:
                    print("  ✅ SUCCESS: Correctly redirected to login")
                else:
                    print("  ❌ FAIL: Redirected but not to login")
            elif response.status_code == 200:
                print("  ❌ FAIL: Page accessible without authentication")
            else:
                print(f"  ⚠️  UNEXPECTED: Status {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ ERROR: {e}")

def test_authenticated_admin_access():
    """Test that authenticated admins can access admin pages"""
    print("\n🔓 Testing authenticated admin access...")
    
    # First, login as admin
    login_data = {
        "email": "dwightanthonyb@gmail.com",
        "password": "your_password_here"  # Replace with actual password
    }
    
    try:
        # Step 1: Login
        response = requests.post(f"{BASE_URL}/api/admin/login/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('requires_access_key'):
                print("  ✅ Login successful, requires access key")
                
                # Step 2: Verify access key
                access_key_data = {
                    "email": login_data["email"],
                    "access_key": "123456"  # Replace with actual access key
                }
                
                response = requests.post(f"{BASE_URL}/api/admin/verify-access-key/", json=access_key_data)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print("  ✅ Access key verified")
                        
                        # Step 3: Test accessing admin page
                        response = requests.get(f"{BASE_URL}/admin-dashboard.html/")
                        if response.status_code == 200:
                            print("  ✅ Authenticated admin can access admin page")
                        else:
                            print(f"  ❌ Authenticated admin cannot access admin page: {response.status_code}")
                    else:
                        print(f"  ❌ Access key verification failed: {data.get('error')}")
                else:
                    print(f"  ❌ Access key verification failed: {response.status_code}")
            else:
                print(f"  ❌ Login failed: {data.get('error')}")
        else:
            print(f"  ❌ Login failed: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

if __name__ == "__main__":
    print("🚀 Security Middleware Test")
    print("=" * 50)
    
    test_unauthenticated_admin_access()
    # test_authenticated_admin_access()  # Uncomment if you want to test authenticated access
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
