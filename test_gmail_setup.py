#!/usr/bin/env python3
"""
Gmail SMTP Test Script

This script helps you test your Gmail SMTP configuration before using it in the main application.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_gmail_configuration():
    """Test Gmail SMTP configuration"""
    print("=" * 60)
    print("GMAIL SMTP CONFIGURATION TEST")
    print("=" * 60)
    print()
    
    # Check current settings
    print("Current Email Settings:")
    print(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    # Check if credentials are set
    if "your-gmail@gmail.com" in settings.EMAIL_HOST_USER or "your-16-char-app-password" in settings.EMAIL_HOST_PASSWORD:
        print("❌ ERROR: You need to update your Gmail credentials!")
        print()
        print("Please update these lines in myproject/settings.py:")
        print("  EMAIL_HOST_USER = 'your-actual-gmail@gmail.com'")
        print("  EMAIL_HOST_PASSWORD = 'your-16-character-app-password'")
        print()
        print("Steps to get Gmail App Password:")
        print("1. Go to https://myaccount.google.com/")
        print("2. Enable 2-Factor Authentication")
        print("3. Go to Security > 2-Step Verification > App passwords")
        print("4. Generate app password for 'Mail'")
        print("5. Use that 16-character password")
        return False
    
    # Get test email
    test_email = input("Enter your email address to test: ").strip()
    
    if not test_email:
        print("No email provided. Exiting.")
        return False
    
    print()
    print(f"Sending test email to: {test_email}")
    print("Please wait...")
    
    try:
        # Send test email
        subject = "Test Email - Complaint Management System"
        message = """
Hello!

This is a test email from your Complaint Management System.

If you received this email, your Gmail SMTP configuration is working correctly!

You can now use the email verification system in your application.

Best regards,
CMS Team
        """.strip()
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        print("✅ SUCCESS! Test email sent successfully!")
        print("Check your inbox (and spam folder) for the test email.")
        print()
        print("🎉 Your Gmail SMTP configuration is working!")
        print("You can now use the email verification system in your application.")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to send email: {e}")
        print()
        print("Troubleshooting tips:")
        print("1. Make sure you've updated the Gmail credentials in settings.py")
        print("2. Verify your Gmail App Password is correct (16 characters)")
        print("3. Check that 2-Factor Authentication is enabled on your Google Account")
        print("4. Make sure you're using an App Password, not your regular password")
        print("5. Check if your Gmail account allows 'less secure app access'")
        return False

if __name__ == "__main__":
    test_gmail_configuration()
