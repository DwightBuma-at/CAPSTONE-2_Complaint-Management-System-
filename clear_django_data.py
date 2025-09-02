#!/usr/bin/env python3
"""
Script to clear all complaints and transactions from Django database
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import Complaint

def clear_django_data():
    """Clear all complaints and transactions from Django database"""
    
    try:
        print("🗑️  Clearing Django database...")
        
        # Get counts before deletion
        complaint_count = Complaint.objects.count()
        
        print(f"📝 Found {complaint_count} complaints")
        
        # Clear complaints
        if complaint_count > 0:
            print("📝 Deleting complaints...")
            Complaint.objects.all().delete()
            print(f"✅ Deleted {complaint_count} complaints")
        
        print("🎉 Django database cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing Django data: {e}")

def check_django_status():
    """Check current data in Django database"""
    
    try:
        print("🔍 Checking Django database status...")
        
        complaint_count = Complaint.objects.count()
        
        print(f"📝 Complaints: {complaint_count} records")
        
        if complaint_count > 0:
            print("\n📝 Recent complaints:")
            for complaint in Complaint.objects.all()[:5]:
                print(f"  - {complaint.tracking_id} ({complaint.complaint_type}) - {complaint.status}")
                
    except Exception as e:
        print(f"❌ Error checking Django status: {e}")

if __name__ == "__main__":
    print("🚀 Django Data Management Tool")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "clear":
            # Ask for confirmation
            response = input("⚠️  Are you sure you want to delete ALL complaints and transactions? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                clear_django_data()
            else:
                print("❌ Operation cancelled")
        elif command == "status":
            check_django_status()
        else:
            print("❌ Unknown command. Use 'clear' or 'status'")
    else:
        print("📋 Available commands:")
        print("  python clear_django_data.py status  - Check current data")
        print("  python clear_django_data.py clear   - Clear all data")
        print()
        check_django_status()
