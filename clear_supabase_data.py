#!/usr/bin/env python3
"""
Script to clear all complaints and transactions from Supabase database
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.supabase_client import supabase

def clear_supabase_data():
    """Clear all complaints and transactions from Supabase"""
    
    if not supabase:
        print("❌ Supabase client not initialized")
        return
    
    try:
        print("🗑️  Clearing Supabase data...")
        
        # Clear complaints
        try:
            print("📝 Clearing complaints table...")
            result = supabase.table('complaints').delete().neq('id', 0).execute()
            print(f"✅ Deleted {len(result.data) if result.data else 0} complaints")
        except Exception as e:
            print(f"⚠️  Could not clear complaints: {e}")
        
        print("🎉 Supabase data cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing Supabase data: {e}")

def check_supabase_status():
    """Check if Supabase tables exist and show current data"""
    
    if not supabase:
        print("❌ Supabase client not initialized")
        return
    
    try:
        print("🔍 Checking Supabase status...")
        
        # Check complaints table
        try:
            result = supabase.table('complaints').select('count', count='exact').execute()
            complaint_count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
            print(f"📝 Complaints table: {complaint_count} records")
        except Exception as e:
            print(f"📝 Complaints table: ❌ Error - {e}")
        

            
    except Exception as e:
        print(f"❌ Error checking Supabase status: {e}")

if __name__ == "__main__":
    print("🚀 Supabase Data Management Tool")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "clear":
            clear_supabase_data()
        elif command == "status":
            check_supabase_status()
        else:
            print("❌ Unknown command. Use 'clear' or 'status'")
    else:
        print("📋 Available commands:")
        print("  python clear_supabase_data.py status  - Check current data")
        print("  python clear_supabase_data.py clear   - Clear all data")
        print()
        check_supabase_status()
