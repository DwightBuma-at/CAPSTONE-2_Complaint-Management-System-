#!/usr/bin/env python3
"""
Admin Recovery Tool - Retrieve admin credentials from Supabase
"""

import os
import sys
import django
import requests
import json

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def recover_admin_info(email):
    """Recover admin information from the API"""
    
    url = "http://127.0.0.1:8000/api/admin/recovery-info/"
    
    data = {
        "email": email
    }
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                admin_info = result["admin_info"]
                
                print("🔍 Admin Recovery Results:")
                print("=" * 50)
                print(f"📧 Email: {admin_info['email']}")
                print(f"🏘️ Barangay: {admin_info['barangay']}")
                print(f"🔑 Password: {admin_info['password']}")
                print(f"🔐 Admin Access Key: {admin_info['admin_access_key']}")
                print(f"📅 Created: {admin_info['created_at']}")
                print("=" * 50)
                print("✅ Recovery successful!")
                
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
        elif response.status_code == 404:
            print(f"❌ Admin not found with email: {email}")
        else:
            print(f"❌ Server error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Django is running on http://127.0.0.1:8000/")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🔐 Admin Recovery Tool")
    print("=" * 30)
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = input("Enter admin email: ").strip()
    
    if not email:
        print("❌ Email is required")
        return
    
    print(f"🔍 Searching for admin: {email}")
    print()
    
    recover_admin_info(email)

if __name__ == "__main__":
    main()
