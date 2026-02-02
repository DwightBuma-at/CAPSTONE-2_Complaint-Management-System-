#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SMS Notification Diagnostic Script
Helps identify why SMS notifications aren't being sent
"""
import os
import sys
import django

# Fix Unicode encoding on Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import UserProfile, Complaint
from myapp.sms_utils import send_sms_via_philsms, send_status_change_sms
import requests

print("\n" + "="*60)
print("📱 SMS NOTIFICATION DIAGNOSTIC REPORT")
print("="*60)

# 1. Check PhilSMS API Token
print("\n1️⃣  PHILSMS API CREDENTIALS")
print("-" * 60)
philsms_token = os.getenv('PHILSMS_API_TOKEN')
philsms_sender = os.getenv('PHILSMS_SENDER_ID', 'CMS')

if philsms_token:
    print(f"✅ PHILSMS_API_TOKEN is set")
    print(f"   Token (first 20 chars): {philsms_token[:20]}...")
else:
    print(f"❌ PHILSMS_API_TOKEN is NOT set - SMS WILL NOT WORK")

print(f"✅ PHILSMS_SENDER_ID: {philsms_sender}")

# 2. Check Users with Phone Numbers
print("\n2️⃣  USERS WITH PHONE NUMBERS")
print("-" * 60)
users_with_phone = UserProfile.objects.exclude(phone_number__isnull=True).exclude(phone_number='')
print(f"Total users with phone numbers: {users_with_phone.count()}")

if users_with_phone.exists():
    for user_profile in users_with_phone[:5]:  # Show first 5
        print(f"   - {user_profile.full_name} ({user_profile.email}): {user_profile.phone_number}")
else:
    print("⚠️  NO USERS WITH PHONE NUMBERS - Users need to provide phone number!")

# 3. Check Complaints and Their Users
print("\n3️⃣  COMPLAINTS AND USER PHONE NUMBERS")
print("-" * 60)
recent_complaints = Complaint.objects.all().order_by('-created_at')[:5]
print(f"Total complaints: {Complaint.objects.count()}")
print(f"Recent complaints:")

for complaint in recent_complaints:
    try:
        # Try to find user by email stored in complaint or user relation
        user_email = complaint.user.email if complaint.user else "No user relation"
        
        # Try to find UserProfile
        user_profile = None
        if complaint.user:
            try:
                user_profile = complaint.user.user_profile
            except:
                pass
        
        if not user_profile:
            # Try by email lookup
            user_profile = UserProfile.objects.filter(email__iexact=user_email).first()
        
        phone = user_profile.phone_number if user_profile and user_profile.phone_number else "❌ NO PHONE"
        
        print(f"\n   Complaint: {complaint.tracking_id}")
        print(f"   Type: {complaint.complaint_type}")
        print(f"   Status: {complaint.status}")
        print(f"   User Email: {user_email}")
        print(f"   Phone: {phone}")
    except Exception as e:
        print(f"   Error processing complaint: {e}")

# 4. Test PhilSMS API Connection
print("\n4️⃣  PHILSMS API CONNECTION TEST")
print("-" * 60)
if philsms_token:
    try:
        # Test 1: Try with +63 format
        test_payload_1 = {
            'recipient': '+639123456789',  
            'sender_id': philsms_sender,
            'type': 'plain',
            'message': 'SMS Test - Format 1: +63'
        }
        
        # Test 2: Try with 09 format
        test_payload_2 = {
            'recipient': '09123456789',  
            'sender_id': philsms_sender,
            'type': 'plain',
            'message': 'SMS Test - Format 2: 09'
        }
        
        headers = {
            'Authorization': f'Bearer {philsms_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        print("\n📌 Test 1: Sending with +63 format...")
        response1 = requests.post(
            'https://app.philsms.com/api/v3/sms/send',
            json=test_payload_1,
            headers=headers,
            timeout=5
        )
        print(f"   Status: {response1.status_code}, Response: {response1.text}")
        
        print("\n📌 Test 2: Sending with 09 format...")
        response2 = requests.post(
            'https://app.philsms.com/api/v3/sms/send',
            json=test_payload_2,
            headers=headers,
            timeout=5
        )
        print(f"   Status: {response2.status_code}, Response: {response2.text}")
        
        if response1.status_code == 200 or response2.status_code == 200:
            print("\n✅ PhilSMS API connection is WORKING")
        else:
            print("\n❌ PhilSMS API returned errors")
            print(f"\n🔧 POSSIBLE SOLUTIONS:")
            print(f"   1. Check if PHILSMS_API_TOKEN is correct")
            print(f"   2. Check if sender_id '{philsms_sender}' is verified in PhilSMS account")
            print(f"   3. Check if PhilSMS account has active credits")
            print(f"   4. Check if phone number {test_payload_1['recipient']} is valid")
            
    except Exception as e:
        print(f"❌ PhilSMS API connection failed: {e}")
else:
    print("⚠️  Skipping API test - PHILSMS_API_TOKEN not set")

# 5. Simulate SMS Sending
print("\n5️⃣  SIMULATE SMS SENDING")
print("-" * 60)
if users_with_phone.exists() and philsms_token:
    user_profile = users_with_phone.first()
    print(f"\nSimulating SMS to: {user_profile.full_name} ({user_profile.phone_number})")
    
    try:
        result = send_sms_via_philsms(
            recipient=user_profile.phone_number,
            message=f"Test SMS from CMS - This is a test notification to verify SMS is working"
        )
        
        if result:
            print(f"✅ SMS simulation SUCCESSFUL")
        else:
            print(f"❌ SMS simulation FAILED")
    except Exception as e:
        print(f"❌ Error during SMS simulation: {e}")
else:
    print("⚠️  Cannot simulate - Missing users with phones or API token")

# 6. Check Status Update Function
print("\n6️⃣  STATUS UPDATE FUNCTION CHECK")
print("-" * 60)
if recent_complaints.exists():
    complaint = recent_complaints.first()
    print(f"Testing with complaint: {complaint.tracking_id}")
    print(f"Current status: {complaint.status}")
    
    try:
        user_profile = None
        if complaint.user:
            try:
                user_profile = complaint.user.user_profile
            except:
                user_profile = UserProfile.objects.filter(email__iexact=complaint.user.email).first()
        
        if user_profile and user_profile.phone_number:
            print(f"✅ User has phone number: {user_profile.phone_number}")
            print(f"   Ready for SMS notification on status change")
        else:
            print(f"❌ User has NO phone number")
            print(f"   User must provide phone number for SMS notifications")
    except Exception as e:
        print(f"❌ Error checking user: {e}")

# 7. Recommendations
print("\n7️⃣  RECOMMENDATIONS")
print("-" * 60)

issues = []

if not philsms_token:
    issues.append("❌ PHILSMS_API_TOKEN not set in environment - ADD IT TO RAILWAY VARIABLES")

users_no_phone = UserProfile.objects.filter(phone_number__isnull=True) | UserProfile.objects.filter(phone_number='')
if users_no_phone.exists():
    issues.append(f"❌ {users_no_phone.count()} users have NO phone number - They must add phone in profile")

complaints_no_status_change = Complaint.objects.filter(status='Pending')
if complaints_no_status_change.exists():
    issues.append(f"⚠️  {complaints_no_status_change.count()} complaints still 'Pending' - Change status to test SMS")

if issues:
    print("\n🔧 ISSUES FOUND:")
    for issue in issues:
        print(f"   {issue}")
else:
    print("\n✅ All checks passed! SMS should be working.")
    print("   Next steps:")
    print("   1. Change a complaint status from Pending to In Progress")
    print("   2. Check Railway logs for SMS sending messages")
    print("   3. User should receive SMS on their phone")

print("\n" + "="*60)
print("📝 LOGS TO CHECK IN RAILWAY:")
print("="*60)
print("   - Look for: '📱 PhilSMS: Sending SMS to'")
print("   - Look for: '✅ PhilSMS: SMS sent successfully'")
print("   - Look for: '⚠️ Failed to send SMS notification'")
print("   - Look for: 'PHILSMS_API_TOKEN not found'")
print("\n")
