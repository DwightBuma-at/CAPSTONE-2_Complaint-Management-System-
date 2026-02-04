"""
Check SMS setup for specific user
"""
import os
import django
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import UserProfile

print("=" * 60)
print("Checking SMS Setup for Users")
print("=" * 60)

# Check the specific user
users = UserProfile.objects.filter(email__icontains='dwightanthonyb@gmail.com')

if users.exists():
    for user_profile in users:
        print(f"\n✅ User Found: {user_profile.full_name}")
        print(f"   Email: {user_profile.email}")
        print(f"   Phone Number: {user_profile.phone_number}")
        print(f"   Phone Type: {type(user_profile.phone_number)}")
        print(f"   Phone Empty?: {not user_profile.phone_number}")
        
        if user_profile.phone_number:
            phone = user_profile.phone_number
            if phone.startswith('09'):
                formatted = '+63' + phone[1:]
                print(f"   Formatted: {formatted}")
                print(f"   ✅ Phone format is correct!")
            else:
                print(f"   ⚠️ Phone format may be incorrect")
        else:
            print(f"   ❌ No phone number saved!")
else:
    print("❌ User not found!")
    
print("\n" + "=" * 60)
print("All users with phone numbers:")
print("=" * 60)

all_users = UserProfile.objects.exclude(phone_number__isnull=True).exclude(phone_number='')
for user in all_users:
    print(f"- {user.full_name}: {user.phone_number} (Email: {user.email})")

print("\n" + "=" * 60)
print("Checking Environment Variables:")
print("=" * 60)
print(f"PHILSMS_API_TOKEN: {'✅ Set' if os.getenv('PHILSMS_API_TOKEN') else '❌ Not set'}")
print(f"PHILSMS_SENDER_ID: {os.getenv('PHILSMS_SENDER_ID', 'Not set')}")
