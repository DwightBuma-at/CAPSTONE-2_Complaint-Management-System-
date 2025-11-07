"""
SendGrid Email Integration for Railway Production
Handles all email sending via SendGrid API instead of SMTP
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings


def send_email_via_sendgrid(to_email, subject, html_content, from_email=None):
    """
    Send email using SendGrid API
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        html_content (str): HTML email content
        from_email (str): Sender email (optional)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        # Get SendGrid API key from environment - try multiple sources
        sendgrid_api_key = (
            os.getenv('SENDGRID_API_KEY') or 
            os.environ.get('SENDGRID_API_KEY') or
            None
        )
        
        if not sendgrid_api_key:
            print("❌ SENDGRID_API_KEY not found in environment variables")
            print("🔍 Environment variables available:", list(os.environ.keys()))
            print("🔍 RAILWAY_ENVIRONMENT:", os.getenv('RAILWAY_ENVIRONMENT'))
            return False
        
        # Default sender email - use system email (must be verified in SendGrid)
        if not from_email:
            from_email = 'dwightanthonyb@gmail.com'  # SendGrid verified sender
        
        print(f"📧 SendGrid: Sending email to {to_email}")
        print(f"📧 Subject: {subject}")
        print(f"📧 From: {from_email}")
        
        # Create SendGrid mail object
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        # Send email via SendGrid API
        sg = SendGridAPIClient(api_key=sendgrid_api_key)
        response = sg.send(message)
        
        print(f"✅ SendGrid: Email sent successfully! Status: {response.status_code}")
        print(f"🔍 SendGrid Response Headers: {dict(response.headers)}")
        return True
        
    except Exception as e:
        print(f"❌ SendGrid Error: {e}")
        print(f"🔍 SendGrid Error Type: {type(e).__name__}")
        import traceback
        print(f"🔍 SendGrid Traceback: {traceback.format_exc()}")
        return False


def send_otp_email_sendgrid(email, otp_code):
    """
    Send OTP verification email using SendGrid
    """
    subject = "Your Login Code - Complaint Management System"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            .otp-code {{ font-size: 24px; font-weight: bold; color: #4CAF50; text-align: center; padding: 20px; background: white; border-radius: 8px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #666; font-size: 12px; padding: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Email Verification</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>Here is your login code for the Complaint Management System:</p>
                <div class="otp-code">{otp_code}</div>
                <p><strong>This code expires in 10 minutes.</strong></p>
                <p>If you didn't request this code, please ignore this email.</p>
                <p><strong>📧 Can't find this email?</strong> Check your spam/junk folder and mark as "Not Spam".</p>
                <p>For assistance, contact us through the system.</p>
            </div>
            <div class="footer">
                <p>Best regards,<br>CMS Team</p>
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email_via_sendgrid(email, subject, html_content)


def send_status_notification_sendgrid(user_email, complaint_id, new_status, admin_barangay):
    """
    Send complaint status change notification using SendGrid
    """
    subject = f"Complaint Status Update - {complaint_id}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2196F3; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background: #f9f9f9; }}
            .status {{ font-size: 18px; font-weight: bold; color: #2196F3; text-align: center; padding: 15px; background: white; border-radius: 8px; margin: 15px 0; }}
            .footer {{ text-align: center; color: #666; font-size: 12px; padding: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Complaint Status Update</h1>
            </div>
            <div class="content">
                <p>Hello!</p>
                <p>Your complaint has been updated:</p>
                <p><strong>Complaint ID:</strong> {complaint_id}</p>
                <div class="status">Status: {new_status}</div>
                <p><strong>Updated by:</strong> {admin_barangay} Admin</p>
                <p>You can view your complaint details by logging into the system.</p>
            </div>
            <div class="footer">
                <p>Best regards,<br>CMS Team - {admin_barangay}</p>
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email_via_sendgrid(user_email, subject, html_content)
