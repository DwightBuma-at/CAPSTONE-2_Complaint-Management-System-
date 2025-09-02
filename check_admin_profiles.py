#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import AdminProfile
from django.contrib.auth import get_user_model

User = get_user_model()
from myapp.supabase_client import supabase

print("🔍 Checking Admin Profiles...")
print("=" * 50)

# Check Django AdminProfile model
print("\n📋 Django AdminProfile records:")
try:
    admin_profiles = AdminProfile.objects.all()
    if admin_profiles:
        for profile in admin_profiles:
            print(f"  - ID: {profile.id}")
            print(f"    User: {profile.user.username}")
            print(f"    Email: {profile.user.email}")
            print(f"    Barangay: {profile.barangay}")
            print(f"    Admin Access Key: {profile.access_key_hash}")
            print()
    else:
        print("  No AdminProfile records found in Django database")
except Exception as e:
    print(f"  Error accessing Django AdminProfile: {e}")

# Check Supabase admin_profiles table
print("\n📋 Supabase admin_profiles table:")
try:
    if supabase:
        response = supabase.table('admin_profiles').select('*').execute()
        if response.data:
            for profile in response.data:
                print(f"  - Email: {profile.get('email')}")
                print(f"    Barangay: {profile.get('barangay')}")
                print(f"    Username: {profile.get('username')}")
                print(f"    Password: {profile.get('password')}")
                print(f"    Admin Access Key: {profile.get('admin_access_key')}")
                print(f"    Created At: {profile.get('created_at')}")
                print()
        else:
            print("  No records found in Supabase admin_profiles table")
    else:
        print("  Supabase client not available")
except Exception as e:
    print(f"  Error accessing Supabase admin_profiles: {e}")

print("\n" + "=" * 50)
print("✅ Check complete!")
