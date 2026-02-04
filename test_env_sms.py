"""
Test if environment variables are loaded correctly
"""
import os
from dotenv import load_dotenv

# Force reload .env
load_dotenv(override=True)

print("=" * 60)
print("Current Environment Variables")
print("=" * 60)
print(f"PHILSMS_API_TOKEN: {os.getenv('PHILSMS_API_TOKEN', 'NOT SET')[:30]}...")
print(f"PHILSMS_SENDER_ID: {os.getenv('PHILSMS_SENDER_ID', 'NOT SET')}")
print("=" * 60)

# Test SMS sending directly
from myapp.sms_utils import send_sms_via_philsms

phone = input("\nEnter phone number to test (09XXXXXXXXX): ").strip()

if phone:
    if phone.startswith('09'):
        formatted = '+63' + phone[1:]
    else:
        formatted = phone
    
    message = "TEST: This is a test message from Complaint Management System"
    
    print(f"\nTesting SMS to {formatted}...")
    result = send_sms_via_philsms(formatted, message)
    
    if result:
        print("\n✅ SMS sent successfully!")
    else:
        print("\n❌ SMS failed to send")
