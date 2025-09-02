#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        # Check if the old table exists
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'myapp_otpcode';
        """)
        old_table = cursor.fetchone()
        
        if old_table:
            print("Found old table: myapp_otpcode")
            
            # Check if the new table exists
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'myapp_emailotp';
            """)
            new_table = cursor.fetchone()
            
            if not new_table:
                print("Creating new table: myapp_emailotp")
                # Create the new table with the same structure
                cursor.execute("""
                    CREATE TABLE myapp_emailotp (
                        id BIGSERIAL PRIMARY KEY,
                        email VARCHAR(254) NOT NULL,
                        otp_code VARCHAR(6) NOT NULL,
                        is_used BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        expires_at TIMESTAMP WITH TIME ZONE NOT NULL
                    );
                """)
                print("✅ Created myapp_emailotp table")
            else:
                print("✅ myapp_emailotp table already exists")
                
        else:
            print("No old table found")
            
except Exception as e:
    print(f"❌ Error: {e}")
