#!/usr/bin/env python3
"""
Test Script for Status Change Email Notifications

This script helps you test the email notification system when admin changes complaint status.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_status_notification():
    """Test the status change notification email system"""
    print("=" * 60)
    print("STATUS CHANGE NOTIFICATION TEST")
    print("=" * 60)
    print()
    
    # Import after Django setup
    from myapp.email_utils import send_status_change_notification
    
    # Test data
    test_email = input("Enter test email address: ").strip()
    if not test_email:
        print("No email provided. Exiting.")
        return
    
    test_data = {
        'user_email': test_email,
        'tracking_id': 'TXN-TEST123',
        'complaint_type': 'Street Light Problem',
        'old_status': 'Reported',
        'new_status': 'In Progress',
        'admin_barangay': 'Test Barangay'
    }
    
    print(f"Testing with:")
    print(f"  Email: {test_data['user_email']}")
    print(f"  Tracking ID: {test_data['tracking_id']}")
    print(f"  Complaint Type: {test_data['complaint_type']}")
    print(f"  Status Change: {test_data['old_status']} → {test_data['new_status']}")
    print(f"  Admin Barangay: {test_data['admin_barangay']}")
    print()
    
    # Test different status changes
    status_changes = [
        ('Reported', 'In Progress'),
        ('In Progress', 'Resolved'),
        ('Reported', 'Declined/Spam')
    ]
    
    for old_status, new_status in status_changes:
        print(f"🧪 Testing {old_status} → {new_status}")
        
        success = send_status_change_notification(
            user_email=test_data['user_email'],
            tracking_id=test_data['tracking_id'],
            complaint_type=test_data['complaint_type'],
            old_status=old_status,
            new_status=new_status,
            admin_barangay=test_data['admin_barangay']
        )
        
        if success:
            print(f"✅ {new_status} notification sent successfully!")
        else:
            print(f"❌ Failed to send {new_status} notification")
        print()
    
    print("=" * 60)
    print("Test completed! Check your email inbox.")
    print("=" * 60)

if __name__ == "__main__":
    test_status_notification()
