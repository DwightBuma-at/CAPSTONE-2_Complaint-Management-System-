#!/usr/bin/env python3
"""
Test SendGrid domain authentication for dvobarangaycms.vip
Run this script to test if SendGrid is properly configured
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from myapp.sendgrid_email import send_email_via_sendgrid

def test_sendgrid_domain():
    """Test SendGrid email sending with domain authentication"""
    
    # Test email content
    test_email = "dwightanthonyb@gmail.com"  # Your email for testing
    subject = "SendGrid Domain Test - dvobarangaycms.vip"
    
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            .success {{ color: #4CAF50; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ SendGrid Domain Test</h1>
            </div>
            <div class="content">
                <p>Hello!</p>
                <p class="success">This email confirms that SendGrid domain authentication is working properly for dvobarangaycms.vip!</p>
                <p><strong>Domain:</strong> dvobarangaycms.vip</p>
                <p><strong>From:</strong> complaintmanagementsystem5@gmail.com</p>
                <p><strong>Timestamp:</strong> {timestamp}</p>
                <p>If you received this email, your SendGrid configuration is working correctly.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    print("Testing SendGrid domain authentication...")
    print(f"Sending test email to: {test_email}")
    print(f"Domain: dvobarangaycms.vip")
    
    # Test email sending
    success = send_email_via_sendgrid(test_email, subject, html_content)
    
    if success:
        print("SUCCESS: SendGrid domain authentication is working!")
        print("Check your email inbox for the test message")
        print("Your OTP emails should now work properly")
    else:
        print("FAILED: SendGrid domain authentication needs to be configured")
        print("Please complete the DNS setup in SendGrid dashboard")
        print("Make sure all DNS records are added and verified")
    
    return success

if __name__ == "__main__":
    test_sendgrid_domain()
