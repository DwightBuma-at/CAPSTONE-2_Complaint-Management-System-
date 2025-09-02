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
    """Send verification email with OTP"""
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
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
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
    if send_verification_email(email, otp_code):
        return otp
    else:
        # If email sending fails, delete the OTP record
        otp.delete()
        return None


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
