#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Test OTP for Survey Users
Creates an OTP code without needing to login through the website
"""

import os
import sys
import django

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import EmailOTP, UserProfile
from myapp.email_utils import generate_otp
from django.utils import timezone
from datetime import timedelta

def create_test_otp(email):
    """
    Generate a test OTP code for a user
    """
    email = email.strip().lower()
    
    print("=" * 70)
    print("GENERATE TEST OTP")
    print("=" * 70)
    print(f"Email: {email}")
    print()
    
    # Check if user exists
    try:
        user_profile = UserProfile.objects.get(email__iexact=email)
        print(f"✅ User found: {user_profile.full_name}")
    except UserProfile.DoesNotExist:
        print(f"❌ Error: No user found with email '{email}'")
        print("   Please create the user account first.")
        return
    
    # Delete any existing unused OTPs for this email
    old_otps = EmailOTP.objects.filter(email=email, is_used=False)
    if old_otps.exists():
        print(f"🗑️  Deleting {old_otps.count()} old unused OTP(s)...")
        old_otps.delete()
    
    # Generate new OTP
    otp_code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=10)
    
    # Create OTP record
    otp = EmailOTP.objects.create(
        email=email,
        otp_code=otp_code,
        expires_at=expires_at
    )
    
    print()
    print("=" * 70)
    print("✅ TEST OTP GENERATED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print(f"📧 Email: {email}")
    print(f"👤 User: {user_profile.full_name}")
    print(f"📍 Barangay: {user_profile.barangay}")
    print()
    print("=" * 70)
    print(f"🔑 OTP CODE: {otp_code}")
    print("=" * 70)
    print()
    print(f"⏰ Valid for: 10 minutes")
    print(f"   Expires at: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("📝 Use this OTP to login without going through the website.")
    print("   This is for TESTING ONLY - in production, users will")
    print("   receive OTP via email when they attempt to login.")
    print()
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        email = sys.argv[1]
        create_test_otp(email)
    else:
        print("\n" + "=" * 70)
        print("GENERATE TEST OTP FOR SURVEY USERS")
        print("=" * 70)
        print()
        email = input("Enter user email: ").strip()
        print()
        create_test_otp(email)

