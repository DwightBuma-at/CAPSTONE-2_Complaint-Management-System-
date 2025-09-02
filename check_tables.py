#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'myapp_%'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print("✅ Found myapp tables:", tables)
        
        # Check if EmailOTP table exists
        if 'myapp_emailotp' in tables:
            print("✅ EmailOTP table exists!")
        else:
            print("❌ EmailOTP table missing!")
            
        if 'myapp_userprofile' in tables:
            print("✅ UserProfile table exists!")
        else:
            print("❌ UserProfile table missing!")
            
except Exception as e:
    print(f"❌ Error checking tables: {e}")
