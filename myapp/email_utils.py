import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import EmailOTP


def generate_otp():
    """Generate a random 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(email, otp_code):
    """Send verification email with OTP - Use Gmail SMTP (reliable), fallback to SendGrid"""
    import os
    
    subject = "Your Email Verification Code - Complaint Management System"
    
    html_message = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ padding: 30px; background: #f9f9f9; border: 1px solid #e0e0e0; }}
        .otp-box {{ font-size: 32px; font-weight: bold; color: #667eea; text-align: center; padding: 20px; background: white; border-radius: 8px; margin: 20px 0; letter-spacing: 4px; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; padding: 20px; background: #f0f0f0; border-radius: 0 0 8px 8px; }}
        .warning {{ color: #d9534f; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Email Verification</h1>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>Welcome to the <strong>Davao City Barangay Complaint Management System</strong>!</p>
            <p>Your 6-digit verification code is:</p>
            <div class="otp-box">{otp_code}</div>
            <p><strong>⏱️ This code expires in 10 minutes.</strong></p>
            <p>If you didn't request this code, please ignore this email.</p>
        </div>
        <div class="footer">
            <p><span class="warning">❌ Can't find this email?</span> Check your spam/junk folder and mark as "Not Spam".</p>
            <p>© 2026 Davao City Barangay CMS. All rights reserved.</p>
        </div>
    </div>
</body>
</html>"""
    
    text_message = f"""Hello!

Welcome to the Davao City Barangay Complaint Management System.

Your verification code is: {otp_code}

This code will expire in 10 minutes.

If you didn't request this verification, please ignore this email.

Best regards,
CMS Team"""
    
    # Try Gmail SMTP first (most reliable)
    try:
        print(f"📧 Attempting Gmail SMTP to {email}")
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"✅ Email sent successfully via Gmail SMTP to {email}")
        return True
        
    except Exception as smtp_error:
        print(f"⚠️ Gmail SMTP failed: {type(smtp_error).__name__}: {smtp_error}")
        
        # Fallback: Try SendGrid
        try:
            if os.getenv('SENDGRID_API_KEY'):
                from .sendgrid_email import send_email_via_sendgrid
                if send_email_via_sendgrid(email, subject, html_message):
                    print(f"✅ Email sent via SendGrid fallback to {email}")
                    return True
        except Exception as sendgrid_error:
            print(f"❌ SendGrid also failed: {sendgrid_error}")
        
        print(f"❌ All email methods failed for {email}")
        return False


def create_otp_for_email(email):
    """Create and store OTP for email verification"""
    # Delete any existing unused OTPs for this email
    EmailOTP.objects.filter(email=email, is_used=False).delete()
    
    # Generate new OTP
    otp_code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=10)
    
    # Create OTP record
    otp = EmailOTP.objects.create(
        email=email,
        otp_code=otp_code,
        expires_at=expires_at
    )
    
    # Send email
    try:
        if send_verification_email(email, otp_code):
            print(f"✅ Email sent successfully to {email}")
            return otp
        else:
            print(f"⚠️ Email sending failed for {email}, but OTP record preserved for fallback")
            # Keep the OTP record for fallback usage (don't delete it)
            return otp
    except Exception as e:
        print(f"❌ Email sending crashed for {email}: {e}")
        # Keep the OTP record for fallback usage
        return otp


def verify_otp(email, otp_code):
    """Verify OTP code for email"""
    try:
        otp = EmailOTP.objects.get(
            email=email,
            otp_code=otp_code,
            is_used=False
        )
        
        # Check if OTP is expired
        if otp.is_expired():
            return False, "OTP has expired"
        
        # Mark OTP as used
        otp.is_used = True
        otp.save()
        
        return True, "OTP verified successfully"
        
    except EmailOTP.DoesNotExist:
        return False, "Invalid OTP code"
    except Exception as e:
        return False, f"Error verifying OTP: {str(e)}"


def send_status_change_notification(user_email, tracking_id, complaint_type, old_status, new_status, admin_barangay):
    """Send email notification when complaint status changes - Use SendGrid on Railway"""
    import os
    
    # Use SendGrid on Railway for reliable delivery
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print(f"🚂 Railway detected - using SendGrid for status notification to {user_email}")
        from .sendgrid_email import send_status_notification_sendgrid
        return send_status_notification_sendgrid(user_email, tracking_id, new_status, admin_barangay)
    
    # Use Gmail SMTP for local development
    print(f"📧 Local development - using Gmail SMTP for status notification to {user_email}")
    
    # Status-specific messages
    status_messages = {
        'In Progress': {
            'subject': f'Update: Your complaint #{tracking_id} is now being processed',
            'message': f"""
Good news! Your complaint has been received and is now being processed by the {admin_barangay} Barangay Office.

Complaint Details:
- Tracking ID: {tracking_id}
- Type: {complaint_type}
- Status: {new_status}
- Barangay: {admin_barangay}

Our team is working on your complaint and will update you once it's resolved.

You can track your complaint status anytime by logging into your account at our complaint management portal.
            """.strip()
        },
        'Resolved': {
            'subject': f'Resolved: Your complaint #{tracking_id} has been resolved',
            'message': f"""
Great news! Your complaint has been successfully resolved by the {admin_barangay} Barangay Office.

Complaint Details:
- Tracking ID: {tracking_id}
- Type: {complaint_type}
- Status: {new_status}
- Barangay: {admin_barangay}

Thank you for using our complaint management system. If you have any concerns about this resolution, please don't hesitate to contact the {admin_barangay} Barangay Office directly.

You can view the resolution details by logging into your account.
            """.strip()
        },
        'Declined/Spam': {
            'subject': f'Update: Your complaint #{tracking_id} status has been updated',
            'message': f"""
We've reviewed your complaint and updated its status.

Complaint Details:
- Tracking ID: {tracking_id}
- Type: {complaint_type}
- Status: {new_status}
- Barangay: {admin_barangay}

If you believe this decision was made in error or if you have additional information to provide, please contact the {admin_barangay} Barangay Office directly.

You can view more details by logging into your account.
            """.strip()
        }
    }
    
    # Get the appropriate message for the new status
    notification_info = status_messages.get(new_status)
    if not notification_info:
        # Fallback for any other status
        notification_info = {
            'subject': f'Update: Your complaint #{tracking_id} status has changed',
            'message': f"""
Your complaint status has been updated by the {admin_barangay} Barangay Office.

Complaint Details:
- Tracking ID: {tracking_id}
- Type: {complaint_type}
- Previous Status: {old_status}
- New Status: {new_status}
- Barangay: {admin_barangay}

You can view more details by logging into your account at our complaint management portal.
            """.strip()
        }
    
    # Add footer to all messages
    full_message = notification_info['message'] + f"""

---
This is an automated notification from the {admin_barangay} Barangay Complaint Management System.
Please do not reply to this email.

For inquiries, please visit your local barangay office or use our complaint management portal.
    """
    
    try:
        send_mail(
            subject=notification_info['subject'],
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        print(f"✅ Status change notification sent to {user_email} for complaint {tracking_id}")
        return True
    except Exception as e:
        print(f"❌ Error sending status change notification to {user_email}: {e}")
        return False