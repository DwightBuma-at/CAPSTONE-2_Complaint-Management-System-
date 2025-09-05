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
    """Send verification email with OTP - Railway $5 plan should support SMTP"""
    import os
    
    # Try to send email even on Railway since you have the paid plan
    print(f"📧 Attempting to send email to {email} (Railway $5 plan)")
    
    subject = "Email Verification - Complaint Management System"
    
    message = f"""
Hello!

Thank you for signing up for the Complaint Management System.

Your verification code is: {otp_code}

This code will expire in 10 minutes.

If you didn't request this verification, please ignore this email.

Best regards,
CMS Team
    """.strip()
    
    try:
        print(f"🔍 SMTP Config: Host={settings.EMAIL_HOST}, Port={settings.EMAIL_PORT}, TLS={settings.EMAIL_USE_TLS}")
        print(f"🔍 Sending from: {settings.DEFAULT_FROM_EMAIL} to: {email}")
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        print(f"✅ Email sent successfully via SMTP to {email}")
        return True
    except Exception as e:
        print(f"❌ SMTP Error sending email to {email}: {e}")
        print(f"🔍 SMTP Error Details: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"🔍 Full traceback: {traceback.format_exc()}")
        # Even on Railway $5 plan, if SMTP fails, continue with OTP fallback
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
    """Send email notification when complaint status changes"""
    
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