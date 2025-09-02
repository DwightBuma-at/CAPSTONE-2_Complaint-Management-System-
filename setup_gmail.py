#!/usr/bin/env python3
"""
Gmail SMTP Setup Script for Complaint Management System

This script helps you configure Gmail SMTP for sending verification emails.

Steps to set up Gmail App Password:
1. Go to your Google Account settings: https://myaccount.google.com/
2. Enable 2-Factor Authentication if not already enabled
3. Go to Security > 2-Step Verification > App passwords
4. Generate a new app password for "Mail"
5. Use that 16-character password in your settings

After getting your app password, update the settings in myproject/settings.py:
- Replace "your-email@gmail.com" with your actual Gmail address
- Replace "your-app-password" with your 16-character app password
"""

import os
import sys

def main():
    print("=" * 60)
    print("GMAIL SMTP SETUP FOR COMPLAINT MANAGEMENT SYSTEM")
    print("=" * 60)
    print()
    print("To enable real email sending, you need to:")
    print()
    print("1. Set up Gmail App Password:")
    print("   - Go to: https://myaccount.google.com/")
    print("   - Enable 2-Factor Authentication")
    print("   - Go to Security > 2-Step Verification > App passwords")
    print("   - Generate app password for 'Mail'")
    print()
    print("2. Update settings.py:")
    print("   - Open: myproject/settings.py")
    print("   - Find the Gmail SMTP Configuration section")
    print("   - Replace 'your-email@gmail.com' with your Gmail")
    print("   - Replace 'your-app-password' with your 16-char app password")
    print()
    print("3. Test the configuration:")
    print("   - Restart your Django server")
    print("   - Try signing up with a user account")
    print("   - Check if verification email is received")
    print()
    print("Current settings:")
    print(f"   EMAIL_HOST_USER: {os.getenv('EMAIL_HOST_USER', 'Not set')}")
    print(f"   EMAIL_BACKEND: {os.getenv('EMAIL_BACKEND', 'smtp')}")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
