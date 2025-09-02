#!/usr/bin/env python
"""
Test script for admin get-data endpoint
"""

import requests
import json

def test_admin_get_data():
    """Test the admin get-data endpoint"""
    
    url = "http://127.0.0.1:8000/api/admin/get-data/"
    data = {
        "email": "dwightanthonyb@gmail.com"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🧪 Testing admin get-data endpoint...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        print("-" * 50)
        
        response = requests.post(url, json=data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Success!")
            print(f"Admin Data: {json.dumps(result, indent=2)}")
            
            if result.get('success') and result.get('admin_data'):
                admin_data = result['admin_data']
                print(f"\n📋 Admin Information:")
                print(f"   Email: {admin_data.get('email')}")
                print(f"   Username: {admin_data.get('username')}")
                print(f"   Barangay: {admin_data.get('barangay')}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_admin_get_data()
