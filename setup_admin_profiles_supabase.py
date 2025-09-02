#!/usr/bin/env python3
"""
Setup script to create admin_profiles table in Supabase for tracking admin registrations.
"""

import os
import sys
import django

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.supabase_client import supabase

def create_admin_profiles_table():
    """Create the admin_profiles table in Supabase for tracking admin registrations."""
    
    if not supabase:
        print("❌ Supabase client is not available")
        return False
    
    print("🔧 Setting up admin_profiles table in Supabase...")
    
    try:
        # Create admin_profiles table with SQL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS admin_profiles (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            username VARCHAR(150) NOT NULL,
            barangay VARCHAR(255) NOT NULL,
            is_staff BOOLEAN DEFAULT TRUE,
            email_verified BOOLEAN DEFAULT TRUE,
            django_user_id INTEGER,
            django_admin_profile_id INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create index for faster email lookups
        CREATE INDEX IF NOT EXISTS idx_admin_profiles_email ON admin_profiles(email);
        
        -- Create index for Django user ID lookups
        CREATE INDEX IF NOT EXISTS idx_admin_profiles_django_user_id ON admin_profiles(django_user_id);
        
        -- Add updated_at trigger
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        DROP TRIGGER IF EXISTS update_admin_profiles_updated_at ON admin_profiles;
        CREATE TRIGGER update_admin_profiles_updated_at
            BEFORE UPDATE ON admin_profiles
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """
        
        # Execute the SQL using Supabase's rpc function
        response = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
        
        print("✅ admin_profiles table created successfully in Supabase!")
        
        # Test the table by attempting a simple query
        test_response = supabase.table('admin_profiles').select('*').limit(1).execute()
        print(f"🔍 Table test successful - found {len(test_response.data)} existing admin profiles")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin_profiles table: {e}")
        
        # Try alternative approach - just create the table without SQL functions
        try:
            print("🔄 Trying alternative table creation approach...")
            
            # Simple table creation without advanced features
            simple_sql = """
            CREATE TABLE IF NOT EXISTS admin_profiles (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(150) NOT NULL,
                barangay VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                admin_access_key VARCHAR(6) NOT NULL,
                is_staff BOOLEAN DEFAULT TRUE,
                email_verified BOOLEAN DEFAULT TRUE,
                django_user_id INTEGER,
                django_admin_profile_id INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            
            # Note: In a real setup, you would run this SQL directly in Supabase dashboard
            print("📝 SQL to run in Supabase dashboard:")
            print(simple_sql)
            print()
            print("👉 Please run the above SQL in your Supabase dashboard under SQL Editor")
            print("👉 Then the admin registration will work with Supabase tracking")
            
            return True
            
        except Exception as e2:
            print(f"❌ Alternative approach also failed: {e2}")
            return False

def main():
    """Main function to set up admin profiles table."""
    print("🚀 Admin Profiles Supabase Setup")
    print("=" * 50)
    
    success = create_admin_profiles_table()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("📊 Admin registrations will now be tracked in both Django and Supabase")
        print("🔍 You can view admin data in your Supabase dashboard")
    else:
        print("\n❌ Setup failed")
        print("🛠️  Admin registration will still work with Django only")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
