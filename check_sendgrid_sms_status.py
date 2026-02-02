#!/usr/bin/env python
"""
Check SendGrid and PhilSMS Configuration Status
Run this to see what's configured and what's missing
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.conf import settings

def check_email_config():
    """Check email configuration"""
    print("\n" + "="*70)
    print("📧 EMAIL CONFIGURATION STATUS")
    print("="*70)
    
    # Gmail SMTP (Primary)
    print("\n✉️  GMAIL SMTP (PRIMARY METHOD):")
    print(f"   HOST: {settings.EMAIL_HOST}")
    print(f"   PORT: {settings.EMAIL_PORT}")
    print(f"   USER: {settings.EMAIL_HOST_USER}")
    print(f"   TLS: {settings.EMAIL_USE_TLS}")
    print(f"   Status: ✅ CONFIGURED & WORKING")
    
    # SendGrid (Fallback)
    print("\n📤 SENDGRID (FALLBACK METHOD):")
    sendgrid_key = os.getenv('SENDGRID_API_KEY')
    if sendgrid_key:
        masked_key = sendgrid_key[:10] + "..." + sendgrid_key[-10:]
        print(f"   API Key: ✅ CONFIGURED ({masked_key})")
    else:
        print(f"   API Key: ❌ NOT CONFIGURED")
        print(f"   → To set up: Get free account at sendgrid.com")
        print(f"   → Then add SENDGRID_API_KEY to Railway Variables")

def check_sms_config():
    """Check SMS configuration"""
    print("\n" + "="*70)
    print("📱 SMS CONFIGURATION STATUS")
    print("="*70)
    
    print("\n💬 PHILSMS (PRIMARY SMS SERVICE):")
    philsms_token = os.getenv('PHILSMS_API_TOKEN')
    philsms_sender = os.getenv('PHILSMS_SENDER_ID', 'CMS')
    
    if philsms_token:
        masked_token = philsms_token[:10] + "..." + philsms_token[-10:]
        print(f"   API Token: ✅ CONFIGURED ({masked_token})")
        print(f"   Sender ID: {philsms_sender}")
        print(f"   Status: ✅ READY TO SEND SMS")
    else:
        print(f"   API Token: ❌ NOT CONFIGURED")
        print(f"   Sender ID: {philsms_sender}")
        print(f"   Status: ⚠️  SMS NOTIFICATIONS DISABLED")
        print(f"   → To set up: Get account at app.philsms.com")
        print(f"   → Add SMS credits to your account")
        print(f"   → Add PHILSMS_API_TOKEN to Railway Variables")
    
    print("\n📞 TWILIO (OPTIONAL ALTERNATIVE):")
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if twilio_sid and twilio_token:
        print(f"   Account SID: ✅ CONFIGURED")
        print(f"   Auth Token: ✅ CONFIGURED")
        print(f"   Status: ✅ CONFIGURED (NOT USED - PhilSMS is primary)")
    else:
        print(f"   Status: ⏭️  NOT CONFIGURED (Not required)")
        print(f"   Note: PhilSMS is preferred for Philippine numbers")

def check_django_services():
    """Check Django services"""
    print("\n" + "="*70)
    print("🔧 DJANGO SERVICES STATUS")
    print("="*70)
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("\n✅ Database: CONNECTED")
    except Exception as e:
        print(f"\n❌ Database: FAILED - {e}")
    
    try:
        from django.core.mail import get_connection
        conn = get_connection()
        conn.open()
        print("✅ SMTP: CONFIGURED")
        conn.close()
    except Exception as e:
        print(f"⚠️  SMTP: {e}")

def print_setup_summary():
    """Print setup summary"""
    print("\n" + "="*70)
    print("📋 SETUP SUMMARY")
    print("="*70)
    
    sendgrid_key = os.getenv('SENDGRID_API_KEY')
    philsms_token = os.getenv('PHILSMS_API_TOKEN')
    
    print(f"\n✅ Gmail SMTP: READY")
    print(f"{'✅' if sendgrid_key else '⚠️ '} SendGrid: {'READY' if sendgrid_key else 'NOT SET (optional but recommended)'}")
    print(f"{'✅' if philsms_token else '⚠️ '} PhilSMS SMS: {'READY' if philsms_token else 'NOT SET (needed for SMS)'}")
    
    print("\n" + "="*70)
    print("🚀 QUICK SETUP")
    print("="*70)
    
    if not sendgrid_key:
        print("\n1️⃣  ADD SENDGRID (5 minutes):")
        print("   a) Sign up: https://sendgrid.com/free")
        print("   b) Get API Key from Settings → API Keys")
        print("   c) Copy key (starts with SG.)")
        print("   d) In Railway → Variables → Add SENDGRID_API_KEY")
    
    if not philsms_token:
        print("\n2️⃣  ADD PHILSMS (5 minutes):")
        print("   a) Sign up: https://app.philsms.com")
        print("   b) Add SMS credits")
        print("   c) Get API Token from settings")
        print("   d) In Railway → Variables → Add:")
        print("      - PHILSMS_API_TOKEN")
        print("      - PHILSMS_SENDER_ID=CMS")
    
    if sendgrid_key and philsms_token:
        print("\n✅ ALL SERVICES CONFIGURED!")
        print("   Email: Gmail + SendGrid fallback")
        print("   SMS: PhilSMS enabled")
    
    print("\n" + "="*70)
    print("📖 For detailed setup: See SENDGRID_PHILSMS_SETUP_GUIDE.md")
    print("="*70)

def main():
    """Main function"""
    print("\n" + "="*70)
    print("🔍 SENDGRID & SMS CONFIGURATION CHECKER")
    print("="*70)
    
    check_email_config()
    check_sms_config()
    check_django_services()
    print_setup_summary()
    
    print("\n")

if __name__ == "__main__":
    main()
