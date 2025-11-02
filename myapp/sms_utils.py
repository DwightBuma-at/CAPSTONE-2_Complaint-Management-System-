"""
PhilSMS SMS Integration for Complaint Management System
Handles sending SMS notifications for complaint status changes
"""
import os
import requests
from django.conf import settings


def send_sms_via_philsms(recipient, message):
    """
    Send SMS using PhilSMS API
    
    Args:
        recipient (str): Recipient phone number (format: 09123456789)
        message (str): SMS message content
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        # Get PhilSMS API credentials from environment variables
        philsms_api_token = os.getenv('PHILSMS_API_TOKEN')
        philsms_sender_id = os.getenv('PHILSMS_SENDER_ID', 'CMS')
        
        if not philsms_api_token:
            print("❌ PHILSMS_API_TOKEN not found in environment variables")
            return False
        
        # PhilSMS API endpoint
        url = "https://app.philsms.com/api/v3/sms/send"
        
        # Prepare headers
        headers = {
            'Authorization': f'Bearer {philsms_api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Prepare request body
        payload = {
            'recipient': recipient,
            'sender_id': philsms_sender_id,
            'type': 'plain',  # PhilSMS API expects 'plain' for SMS type
            'message': message
        }
        
        print(f"📱 PhilSMS: Sending SMS to {recipient}")
        print(f"📱 Message: {message[:50]}...")  # Log first 50 chars
        print(f"📱 Sender ID: {philsms_sender_id}")
        
        # Send SMS via PhilSMS API
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print(f"✅ PhilSMS: SMS sent successfully! Response: {result}")
            return True
        else:
            print(f"❌ PhilSMS Error: Status {response.status_code}, Response: {response.text}")
            return False
        
    except requests.exceptions.Timeout:
        print(f"❌ PhilSMS Error: Request timeout")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ PhilSMS Error: {e}")
        return False
    except Exception as e:
        print(f"❌ PhilSMS Error: {e}")
        import traceback
        print(f"📱 PhilSMS Traceback: {traceback.format_exc()}")
        return False


def send_status_change_sms(phone_number, tracking_id, complaint_type, old_status, new_status, admin_barangay):
    """
    Send SMS notification when complaint status changes
    
    Args:
        phone_number (str): User's phone number (format: 09123456789 or 09958744151)
        tracking_id (str): Complaint tracking ID
        complaint_type (str): Type of complaint
        old_status (str): Previous status
        new_status (str): New status
        admin_barangay (str): Barangay admin name
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        # Convert phone number to proper format for PhilSMS API
        # PhilSMS API expects +63XXXXXXXXXX format
        if phone_number.startswith('+63'):
            # Already in correct format
            formatted_phone = phone_number
        elif phone_number.startswith('09'):
            # Convert 09XXXXXXXXX to +63XXXXXXXXXX
            formatted_phone = '+63' + phone_number[1:]
        else:
            print(f"⚠️ Invalid phone number format: {phone_number}")
            return False
        
        # Create SMS message based on status - matching email notifications format and wording
        status_messages = {
            'Reported': f"""Hello! Your complaint has been updated:
Complaint ID: {tracking_id}
Status: Reported
Updated by: {admin_barangay} Admin
You can view your complaint details by logging into the system.
Best regards, CMS Team - {admin_barangay}""",
            'In Progress': f"""Hello! Your complaint has been updated:
Complaint ID: {tracking_id}
Status: In Progress
Updated by: {admin_barangay} Admin
You can view your complaint details by logging into the system.
Best regards, CMS Team - {admin_barangay}""",
            'Resolved': f"""Hello! Your complaint has been updated:
Complaint ID: {tracking_id}
Status: Resolved
Updated by: {admin_barangay} Admin
You can view your complaint details by logging into the system.
Best regards, CMS Team - {admin_barangay}""",
            'Declined/Spam': f"""Hello! Your complaint has been updated:
Complaint ID: {tracking_id}
Status: Declined/Spam
Updated by: {admin_barangay} Admin
You can view your complaint details by logging into the system.
Best regards, CMS Team - {admin_barangay}""",
            'Forwarded to Agency': f"""Hello! Your complaint has been updated:
Complaint ID: {tracking_id}
Status: Forwarded to Agency
Updated by: {admin_barangay} Admin
You can view your complaint details by logging into the system.
Best regards, CMS Team - {admin_barangay}""",
            'Resolved by Agency': f"""Hello! Your complaint has been updated:
Complaint ID: {tracking_id}
Status: Resolved by Agency
Updated by: {admin_barangay} Admin
You can view your complaint details by logging into the system.
Best regards, CMS Team - {admin_barangay}"""
        }
        
        # Get message for the status or use fallback
        message = status_messages.get(new_status)
        if not message:
            # Fallback message for any other status
            message = f"""Hello! Your complaint has been updated:
Complaint ID: {tracking_id}
Status: {new_status}
Updated by: {admin_barangay} Admin
You can view your complaint details by logging into the system.
Best regards, CMS Team - {admin_barangay}"""
        
        # Send SMS
        return send_sms_via_philsms(formatted_phone, message)
        
    except Exception as e:
        print(f"❌ Error creating SMS notification: {e}")
        return False

