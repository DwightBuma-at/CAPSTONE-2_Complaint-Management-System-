#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        # Check current table structure
        cursor.execute("""
            SELECT column_name, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'myapp_userprofile'
            ORDER BY column_name;
        """)
        columns = cursor.fetchall()
        print("Current UserProfile table structure:")
        for col in columns:
            print(f"  {col[0]}: nullable={col[1]}, default={col[2]}")
        
        # Add email column if it doesn't exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'myapp_userprofile'
            AND column_name = 'email';
        """)
        email_exists = cursor.fetchone()
        
        if not email_exists:
            print("Adding email column...")
            cursor.execute("""
                ALTER TABLE myapp_userprofile 
                ADD COLUMN email VARCHAR(254) UNIQUE;
            """)
            print("✅ Added email column")
        else:
            print("✅ email column already exists")
        
        # Add password column if it doesn't exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'myapp_userprofile'
            AND column_name = 'password';
        """)
        password_exists = cursor.fetchone()
        
        if not password_exists:
            print("Adding password column...")
            cursor.execute("""
                ALTER TABLE myapp_userprofile 
                ADD COLUMN password VARCHAR(128);
            """)
            print("✅ Added password column")
        else:
            print("✅ password column already exists")
        
        # Ensure full_name column exists and is properly configured
        cursor.execute("""
            ALTER TABLE myapp_userprofile 
            ALTER COLUMN full_name SET NOT NULL;
        """)
        print("✅ Set full_name as NOT NULL")
        
        # Ensure barangay column exists and is properly configured
        cursor.execute("""
            ALTER TABLE myapp_userprofile 
            ALTER COLUMN barangay SET NOT NULL;
        """)
        print("✅ Set barangay as NOT NULL")
        
        # Show final table structure
        cursor.execute("""
            SELECT column_name, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'myapp_userprofile'
            ORDER BY column_name;
        """)
        columns = cursor.fetchall()
        print("\nFinal UserProfile table structure:")
        for col in columns:
            print(f"  {col[0]}: nullable={col[1]}, default={col[2]}")
        
        print("\n✅ UserProfile table now stores: Full Name, Email, Barangay, Password")
        
except Exception as e:
    print(f"❌ Error: {e}")
