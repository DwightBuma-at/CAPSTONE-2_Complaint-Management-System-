#!/usr/bin/env python
"""
Test script to verify Gmail SMTP email sending works
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_gmail_smtp():
    """Test Gmail SMTP connection and email sending"""
    print("=" * 60)
    print("🧪 TESTING GMAIL SMTP EMAIL SENDING")
    print("=" * 60)
    
    # Test configuration
    print("\n📋 Configuration Check:")
    print(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"  EMAIL_TIMEOUT: {settings.EMAIL_TIMEOUT}")
    print(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # Test recipient
    test_email = "dwightanthonyb@gmail.com"
    otp_code = "123456"
    
    print(f"\n📧 Test Details:")
    print(f"  Recipient: {test_email}")
    print(f"  OTP Code: {otp_code}")
    
    # Try sending
    print(f"\n⏳ Attempting to send test email via Gmail SMTP...")
    
    try:
        html_message = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .otp-box {{ font-size: 32px; font-weight: bold; color: #667eea; text-align: center; padding: 20px; background: white; border-radius: 8px; margin: 20px 0; letter-spacing: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Email Verification Test</h1>
        </div>
        <div class="content">
            <p>This is a test email for the Complaint Management System.</p>
            <p>Test OTP Code:</p>
            <div class="otp-box">{otp_code}</div>
            <p>If you received this, email is working!</p>
        </div>
    </div>
</body>
</html>"""
        
        result = send_mail(
            subject="🧪 TEST: Email Configuration Working",
            message="This is a test email. If you received this, Gmail SMTP is configured correctly!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"✅ SUCCESS! Email sent successfully!")
        print(f"   Send result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED! Error sending email:")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Message: {str(e)}")
        import traceback
        print(f"\n📋 Full Traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gmail_smtp()
    print("\n" + "=" * 60)
    if success:
        print("✅ EMAIL TEST PASSED - System can send emails!")
    else:
        print("❌ EMAIL TEST FAILED - Check configuration above")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
