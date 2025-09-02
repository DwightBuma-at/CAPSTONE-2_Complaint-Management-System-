#!/usr/bin/env python
"""
Script to migrate existing admin profiles from Django to Supabase
"""

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
from myapp.supabase_client import supabase

User = get_user_model()

def migrate_admin_to_supabase():
    """Migrate existing admin profiles from Django to Supabase"""
    
    print("🔄 Migrating Admin Profiles from Django to Supabase...")
    print("=" * 60)
    
    if not supabase:
        print("❌ Supabase client is not available")
        return False
    
    try:
        # Get all admin profiles from Django
        admin_profiles = AdminProfile.objects.all()
        
        if not admin_profiles:
            print("📋 No admin profiles found in Django database")
            return True
        
        print(f"📋 Found {admin_profiles.count()} admin profile(s) in Django")
        
        for profile in admin_profiles:
            user = profile.user
            print(f"\n👤 Processing admin: {user.username} ({user.email})")
            print(f"   Barangay: {profile.barangay}")
            
            # Check if admin already exists in Supabase
            try:
                existing = supabase.table('admin_profiles').select('*').eq('email', user.email).execute()
                
                if existing.data:
                    print(f"   ⚠️  Admin already exists in Supabase, skipping...")
                    continue
                    
            except Exception as e:
                print(f"   ⚠️  Error checking existing admin in Supabase: {e}")
                print(f"   📝 This might be because the admin_profiles table doesn't exist yet")
                print(f"   💡 Please create the table in Supabase dashboard first")
                return False
            
            # Insert admin profile into Supabase
            try:
                admin_data = {
                    "email": user.email,
                    "username": user.username,
                    "barangay": profile.barangay,
                    "password": user.password,  # This is the hashed password
                    "admin_access_key": "123456",  # Default access key, admin can change later
                    "is_staff": user.is_staff,
                    "email_verified": True,
                    "django_user_id": user.id,
                    "django_admin_profile_id": profile.id
                }
                
                response = supabase.table('admin_profiles').insert(admin_data).execute()
                
                if response.data:
                    print(f"   ✅ Successfully migrated to Supabase")
                else:
                    print(f"   ❌ Failed to migrate to Supabase")
                    
            except Exception as e:
                print(f"   ❌ Error migrating to Supabase: {e}")
                return False
        
        print(f"\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Admin Profile Migration Tool")
    print("=" * 60)
    
    success = migrate_admin_to_supabase()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("📊 Admin profiles are now available in both Django and Supabase")
        print("🔍 The admin dashboard should now show the correct barangay information")
    else:
        print("\n❌ Migration failed")
        print("🛠️  Please check the error messages above")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
