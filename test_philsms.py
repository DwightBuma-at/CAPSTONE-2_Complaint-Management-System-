"""
PhilSMS Diagnostic Test Script
Tests the PhilSMS SMS functionality to identify issues
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("PhilSMS Diagnostic Test")
print("=" * 60)

# 1. Check Environment Variables
print("\n1. Checking Environment Variables...")
philsms_token = os.getenv('PHILSMS_API_TOKEN')
philsms_sender = os.getenv('PHILSMS_SENDER_ID', 'CMS')

if philsms_token:
    print(f"✅ PHILSMS_API_TOKEN found: {philsms_token[:10]}...{philsms_token[-10:]}")
else:
    print("❌ PHILSMS_API_TOKEN not found!")
    sys.exit(1)

print(f"✅ PHILSMS_SENDER_ID: {philsms_sender}")

# 2. Test API Connection
print("\n2. Testing PhilSMS API Connection...")
import requests

url = "https://app.philsms.com/api/v3/sms/send"
headers = {
    'Authorization': f'Bearer {philsms_token}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

print(f"   API Endpoint: {url}")
print(f"   Authorization: Bearer {philsms_token[:20]}...")

# 3. Get User Phone Number from Database
print("\n3. Checking User Phone Numbers in Database...")
try:
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    django.setup()
    
    from myapp.models import UserProfile
    
    users_with_phone = UserProfile.objects.exclude(phone_number__isnull=True).exclude(phone_number='')
    
    if users_with_phone.exists():
        print(f"✅ Found {users_with_phone.count()} users with phone numbers:")
        for user_profile in users_with_phone[:5]:  # Show first 5
            print(f"   - {user_profile.full_name}: {user_profile.phone_number}")
    else:
        print("❌ No users have phone numbers saved!")
        print("   → Users need to add their phone number in their profile")
        print("   → Phone number format should be: 09123456789")
except Exception as e:
    print(f"⚠️ Could not check database: {e}")

# 4. Test SMS Send (if user provides phone number)
print("\n4. Test SMS Send")
test_phone = input("Enter phone number to test (09XXXXXXXXX) or press Enter to skip: ").strip()

if test_phone:
    # Format phone number
    if test_phone.startswith('09'):
        formatted_phone = '+63' + test_phone[1:]
    elif test_phone.startswith('+63'):
        formatted_phone = test_phone
    else:
        print(f"❌ Invalid format! Use 09XXXXXXXXX format")
        sys.exit(1)
    
    print(f"   Formatted phone: {formatted_phone}")
    
    # Test message
    test_message = """Hello! Your complaint has been updated:
Complaint ID: TEST123
Status: Test Message
This is a test SMS from Complaint Management System.
Best regards, CMS Team"""
    
    payload = {
        'recipient': formatted_phone,
        'sender_id': philsms_sender,
        'type': 'plain',
        'message': test_message
    }
    
    print("\n   Sending test SMS...")
    print(f"   To: {formatted_phone}")
    print(f"   Sender ID: {philsms_sender}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        print(f"\n   Response Status: {response.status_code}")
        print(f"   Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ SMS SENT SUCCESSFULLY!")
            print("   Check your phone for the message.")
        elif response.status_code == 401:
            print("\n❌ AUTHENTICATION FAILED!")
            print("   → Check if your API token is correct")
            print("   → Token may have expired or been revoked")
        elif response.status_code == 400:
            print("\n❌ BAD REQUEST!")
            print("   → Check phone number format")
            print("   → Check if you have sufficient credits")
            response_data = response.json()
            if 'message' in response_data:
                print(f"   → Error: {response_data['message']}")
        elif response.status_code == 402:
            print("\n❌ INSUFFICIENT CREDITS!")
            print("   → Your PhilSMS account has ₱0 balance")
            print("   → You need to top up your account at https://app.philsms.com/")
            print("   → Go to 'Credits' or 'Top Up' section")
        else:
            print(f"\n❌ UNEXPECTED ERROR!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n❌ REQUEST TIMEOUT!")
        print("   → PhilSMS API took too long to respond")
        print("   → Check your internet connection")
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR!")
        print("   → Cannot connect to PhilSMS API")
        print("   → Check your internet connection")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        print(traceback.format_exc())
else:
    print("   Skipped test SMS send")

# 5. Summary and Recommendations
print("\n" + "=" * 60)
print("DIAGNOSTIC SUMMARY")
print("=" * 60)

print("\n📋 Common Issues and Solutions:")
print()
print("Issue 1: 'Insufficient Credits' (402 Error)")
print("   → Your PhilSMS account balance is ₱0")
print("   → Solution: Top up at https://app.philsms.com/credits")
print()
print("Issue 2: No phone number in user profile")
print("   → Users must add phone number (09XXXXXXXXX format)")
print("   → Solution: Go to user profile page and save phone number")
print()
print("Issue 3: SMS not triggered on status update")
print("   → SMS only sent when admin updates complaint status")
print("   → Check console logs for 'SMS notification sent' message")
print()
print("Issue 4: Phone number format error")
print("   → Use format: 09123456789 (Philippine mobile)")
print("   → System converts to +63123456789 automatically")
print()
print("Issue 5: API Token invalid")
print("   → Token may have expired or been revoked")
print("   → Get new token from https://app.philsms.com/developers")

print("\n" + "=" * 60)
