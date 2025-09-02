#!/usr/bin/env python3
"""
Simple script to logout and test unauthenticated access
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

def logout_and_test():
    print("🚪 Logging out...")
    
    # Try to logout
    try:
        response = requests.post(f"{BASE_URL}/api/admin/logout/")
        print(f"Logout response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Logged out successfully")
        else:
            print("⚠️  Logout may have failed")
    except Exception as e:
        print(f"❌ Logout error: {e}")
    
    print("\n🔒 Now testing unauthenticated access to admin pages...")
    
    # Test admin pages
    admin_pages = [
        "/admin-dashboard.html",
        "/admin-dashboard.html/",
        "/admin-complaints.html",
        "/admin-complaints.html/"
    ]
    
    for page in admin_pages:
        print(f"\nTesting: {page}")
        try:
            response = requests.get(f"{BASE_URL}{page}", allow_redirects=False)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                print(f"  Redirect: {location}")
                if 'show_login=true' in location:
                    print("  ✅ CORRECT: Redirected to login")
                else:
                    print("  ❌ WRONG: Not redirected to login")
            elif response.status_code == 200:
                print("  ❌ SECURITY BREACH: Page accessible without login!")
            else:
                print(f"  ⚠️  Unexpected: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    print("🔐 Security Test - Unauthenticated Access")
    print("=" * 50)
    logout_and_test()
    print("\n" + "=" * 50)
    print("✅ Test completed!")
    print("\n💡 To test in browser:")
    print("1. Open incognito/private window")
    print("2. Go to: http://127.0.0.1:8000/admin-dashboard.html")
    print("3. Should redirect to: http://127.0.0.1:8000/index.html?show_login=true")
