#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        # Check if email_verified column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'myapp_userprofile'
            AND column_name = 'email_verified';
        """)
        email_verified_exists = cursor.fetchone()
        
        if not email_verified_exists:
            print("Adding email_verified column...")
            cursor.execute("""
                ALTER TABLE myapp_userprofile 
                ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
            """)
            print("✅ Added email_verified column")
        else:
            print("✅ email_verified column already exists")
        
        # Check if created_at column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'myapp_userprofile'
            AND column_name = 'created_at';
        """)
        created_at_exists = cursor.fetchone()
        
        if not created_at_exists:
            print("Adding created_at column...")
            cursor.execute("""
                ALTER TABLE myapp_userprofile 
                ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            """)
            print("✅ Added created_at column")
        else:
            print("✅ created_at column already exists")
        
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
        
        print("\n✅ UserProfile table is now complete!")
        
except Exception as e:
    print(f"❌ Error: {e}")
