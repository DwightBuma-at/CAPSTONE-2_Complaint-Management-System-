#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        # Check the current structure of the UserProfile table
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
        
        # Fix the is_verified column to allow NULL values and set default
        cursor.execute("""
            ALTER TABLE myapp_userprofile 
            ALTER COLUMN is_verified DROP NOT NULL;
        """)
        print("✅ Removed NOT NULL constraint from is_verified")
        
        cursor.execute("""
            ALTER TABLE myapp_userprofile 
            ALTER COLUMN is_verified SET DEFAULT FALSE;
        """)
        print("✅ Set default value for is_verified to FALSE")
        
        # Also ensure email_verified has proper default
        cursor.execute("""
            ALTER TABLE myapp_userprofile 
            ALTER COLUMN email_verified SET DEFAULT FALSE;
        """)
        print("✅ Set default value for email_verified to FALSE")
        
        print("✅ UserProfile table constraints are now fixed!")
        
except Exception as e:
    print(f"❌ Error: {e}")
