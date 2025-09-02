#!/usr/bin/env python3
"""
Test Email Functionality for Complaint Management System

This script tests the email sending functionality.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_sending():
    """Test email sending functionality"""
    print("=" * 50)
    print("TESTING EMAIL FUNCTIONALITY")
    print("=" * 50)
    
    # Check current email settings
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    # Test email
    test_email = input("Enter your email address to test: ").strip()
    
    if not test_email:
        print("No email provided. Exiting.")
        return
    
    try:
        # Send test email
        subject = "Test Email - Complaint Management System"
        message = """
Hello!

This is a test email from your Complaint Management System.

If you received this email, your Gmail SMTP configuration is working correctly!

Best regards,
CMS Team
        """.strip()
        
        print(f"Sending test email to: {test_email}")
        print("Please wait...")
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        print("✅ Test email sent successfully!")
        print("Check your inbox (and spam folder) for the test email.")
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print()
        print("Troubleshooting tips:")
        print("1. Make sure you've updated the Gmail credentials in settings.py")
        print("2. Verify your Gmail App Password is correct")
        print("3. Check that 2-Factor Authentication is enabled on your Google Account")
        print("4. Make sure you're using an App Password, not your regular password")

if __name__ == "__main__":
    test_email_sending()
