#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        # Check if the UserProfile table exists
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'myapp_userprofile';
        """)
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("Found myapp_userprofile table")
            
            # Check what columns exist
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'myapp_userprofile'
                ORDER BY column_name;
            """)
            columns = [row[0] for row in cursor.fetchall()]
            print("Current columns:", columns)
            
            # Add missing columns if they don't exist
            if 'full_name' not in columns:
                print("Adding full_name column...")
                cursor.execute("""
                    ALTER TABLE myapp_userprofile 
                    ADD COLUMN full_name VARCHAR(255);
                """)
                print("✅ Added full_name column")
            
            if 'barangay' not in columns:
                print("Adding barangay column...")
                cursor.execute("""
                    ALTER TABLE myapp_userprofile 
                    ADD COLUMN barangay VARCHAR(120);
                """)
                print("✅ Added barangay column")
                
            if 'email_verified' not in columns:
                print("Adding email_verified column...")
                cursor.execute("""
                    ALTER TABLE myapp_userprofile 
                    ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
                """)
                print("✅ Added email_verified column")
                
            if 'created_at' not in columns:
                print("Adding created_at column...")
                cursor.execute("""
                    ALTER TABLE myapp_userprofile 
                    ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
                """)
                print("✅ Added created_at column")
                
            print("✅ UserProfile table structure is now correct!")
            
        else:
            print("❌ myapp_userprofile table does not exist!")
            
except Exception as e:
    print(f"❌ Error: {e}")
