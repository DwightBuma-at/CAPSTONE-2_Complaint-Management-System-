#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OTP Code Checker for Testing
Quickly retrieve OTP codes for testing survey accounts
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

from myapp.models import EmailOTP
from django.utils import timezone

def check_otp(email):
    """
    Check the most recent OTP code for an email address
    """
    email = email.strip().lower()
    
    print("=" * 70)
    print("OTP CODE CHECKER")
    print("=" * 70)
    print(f"Email: {email}")
    print()
    
    # Get all unused OTPs for this email
    otps = EmailOTP.objects.filter(email__iexact=email, is_used=False).order_by('-created_at')
    
    if not otps.exists():
        print("❌ No unused OTP codes found for this email.")
        print()
        print("Possible reasons:")
        print("  1. User hasn't tried to login yet")
        print("  2. OTP code has already been used")
        print("  3. Email address is incorrect")
        return
    
    # Get the most recent OTP
    latest_otp = otps.first()
    
    # Check if expired
    is_expired = latest_otp.is_expired()
    
    print("✅ OTP Code Found!")
    print()
    print("=" * 70)
    print(f"📧 OTP CODE: {latest_otp.otp_code}")
    print("=" * 70)
    print()
    print(f"Created at: {latest_otp.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Expires at: {latest_otp.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Status: {'❌ EXPIRED' if is_expired else '✅ VALID'}")
    print()
    
    if is_expired:
        print("⚠️ This OTP has expired. User needs to request a new one.")
    else:
        time_left = (latest_otp.expires_at - timezone.now()).total_seconds() / 60
        print(f"⏰ Time remaining: {time_left:.1f} minutes")
    
    print()
    
    # Show all OTP codes for this email
    if otps.count() > 1:
        print(f"📝 Total unused OTP codes for this email: {otps.count()}")
        print()
        print("All OTP codes (most recent first):")
        for idx, otp in enumerate(otps, 1):
            status = "EXPIRED" if otp.is_expired() else "VALID"
            print(f"  {idx}. {otp.otp_code} - {otp.created_at.strftime('%H:%M:%S')} - {status}")
    
    print()
    print("=" * 70)


def list_all_recent_otps():
    """
    List all recent OTP codes (last 10)
    """
    print("=" * 70)
    print("RECENT OTP CODES (Last 10)")
    print("=" * 70)
    print()
    
    otps = EmailOTP.objects.filter(is_used=False).order_by('-created_at')[:10]
    
    if not otps.exists():
        print("No unused OTP codes found in the system.")
        return
    
    print(f"{'Email':<40} {'OTP Code':<10} {'Status':<10} {'Created'}")
    print("-" * 90)
    
    for otp in otps:
        status = "EXPIRED" if otp.is_expired() else "VALID"
        created = otp.created_at.strftime('%H:%M:%S')
        print(f"{otp.email:<40} {otp.otp_code:<10} {status:<10} {created}")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        # Check specific email
        email = sys.argv[1]
        check_otp(email)
    else:
        # Interactive mode
        print("\n" + "=" * 70)
        print("OTP CODE CHECKER FOR SURVEY TESTING")
        print("=" * 70)
        print()
        print("This tool helps you retrieve OTP codes for testing purposes.")
        print()
        
        choice = input("1. Check OTP for specific email\n2. List all recent OTPs\n\nChoice (1 or 2): ").strip()
        
        if choice == "1":
            print()
            email = input("Enter email address: ").strip()
            print()
            check_otp(email)
        elif choice == "2":
            print()
            list_all_recent_otps()
        else:
            print("Invalid choice!")

