# PhilSMS SMS Integration Setup

## Overview
The Complaint Management System now supports SMS notifications via PhilSMS. Users receive SMS alerts when their complaint status changes, in addition to email notifications.

## Setup Instructions

### 1. Get PhilSMS API Credentials

1. Visit [PhilSMS](https://www.philsms.com/) and create an account
2. Complete the top-up process in your PhilSMS account (currently shows ₱0)
3. Go to "Developers" section in your PhilSMS dashboard
4. Copy your **API Token** from the dashboard
5. Note your **Sender ID** (or use default: "CMS")

**Your Current API Token:**
```
3520|K7ZJIDC5R4W0JnimXi4UWn0mWUlz5uu4P35ML2Ca
```

**API Endpoint:**
```
https://app.philsms.com/api/v3/
```

### 2. Configure Environment Variables

Add the following to your `.env` file or Railway environment variables:

```env
# PhilSMS Configuration (For SMS Notifications)
PHILSMS_API_TOKEN=your-philsms-api-token-here
PHILSMS_SENDER_ID=CMS
```

### 3. Install Dependencies

```bash
pip install requests>=2.31.0
```

Or update your `requirements.txt`:
```
requests>=2.31.0
```

### 4. Database Migration

Run the migration to add phone_number field to UserProfile:

```bash
python manage.py migrate
```

## How It Works

### User Experience

1. **User adds phone number**: 
   - User clicks "Add Phone Number" badge on their profile
   - Enters phone in format: `09958744151` (11 digits starting with 09)
   - Number is saved to database

2. **Admin updates complaint status**:
   - Admin changes complaint status to any of the following:
     - In Progress
     - Resolved
     - Declined/Spam
     - Forwarded to Agency
     - Resolved by Agency

3. **Automatic notifications**:
   - **Email notification** is sent to user's email
   - **SMS notification** is sent to user's phone number (if added)
   - Both notifications occur simultaneously

### SMS Message Format

Each status has a specific SMS message (matching email notification format):

- **In Progress**: "Update: Your complaint #{tracking_id} is now being processed. Good news! Your complaint has been received and is now being processed by the {admin_barangay} Barangay Office. Our team is working on your complaint and will update you once it's resolved. Track status in CMS app. -CMS"

- **Resolved**: "Resolved: Your complaint #{tracking_id} has been resolved. Great news! Your complaint has been successfully resolved by the {admin_barangay} Barangay Office. Thank you for using our complaint management system. -CMS"

- **Declined/Spam**: "Update: Your complaint #{tracking_id} status has been updated. We've reviewed your complaint and updated its status to {new_status}. If you believe this decision was made in error, please contact the {admin_barangay} Barangay Office directly. -CMS"

- **Forwarded to Agency**: "Update: Your complaint #{tracking_id} has been forwarded. Your complaint has been forwarded to a higher agency by {admin_barangay}. You'll be notified of updates. Track status in CMS app. -CMS"

- **Resolved by Agency**: "Update: Your complaint #{tracking_id} has been resolved by agency. Your complaint has been successfully resolved by the higher agency. Thank you for reporting this issue. View details in CMS app. -CMS"

## API Details

### PhilSMS API Endpoint
```
POST https://app.philsms.com/api/v3/sms/send
```

### Request Format
```json
{
  "recipient": "09958744151",
  "sender_id": "CMS",
  "type": "sms",
  "message": "Your complaint status has been updated."
}
```

### Headers Required
```
Authorization: Bearer {PHILSMS_API_TOKEN}
Content-Type: application/json
Accept: application/json
```

## Files Modified

### Backend
- `myapp/models.py`: Added `phone_number` field to UserProfile
- `myapp/views.py`: Added SMS notifications to status update function
- `myapp/urls.py`: Added phone number API endpoints
- `myapp/sms_utils.py`: **NEW FILE** - PhilSMS integration utilities
- `myproject/settings.py`: Added PhilSMS configuration
- `requirements.txt`: Added `requests` package

### Frontend
- `myapp/templates/user.html`: Added phone number UI, modal, and API integration

### Database
- Migration `0040_userprofile_phone_number`: Adds phone_number field

## Testing

### Test SMS Sending

1. Add your phone number to your user profile
2. Submit a test complaint
3. As admin, change the complaint status
4. Check your phone for SMS notification

### Verify Configuration

Check logs for:
- ✅ `📱 PhilSMS: SMS sent successfully!`
- ❌ `❌ PHILSMS_API_TOKEN not found` - Add token to environment
- ❌ `❌ PhilSMS Error` - Check token validity and top-up

## Troubleshooting

### No SMS Received

1. **Check PhilSMS top-up balance**: SMS requires credit (currently shows ₱0)
2. **Verify API token**: Ensure correct token in environment variables
3. **Check phone format**: Must be 11 digits starting with 09
4. **Check logs**: Look for PhilSMS error messages

### SMS Sending Fails

1. **Token issues**: 
   - Verify token is active in PhilSMS dashboard
   - Check for typos in environment variable

2. **Network issues**:
   - Check internet connectivity
   - Verify PhilSMS API is accessible

3. **Phone number format**:
   - Ensure format is correct (09XXXXXXXXX)
   - Remove any spaces or special characters

## Security Notes

- Phone numbers are stored in encrypted PostgreSQL database
- API tokens should never be committed to version control
- Use environment variables for all sensitive credentials
- SMS notifications only sent for status changes, not for OTP

## Future Enhancements

Potential improvements:
- SMS for chat notifications
- Bulk SMS for announcements
- SMS opt-in/opt-out settings
- Delivery status tracking

## Support

For PhilSMS support:
- Website: https://www.philsms.com/
- Documentation: https://app.philsms.com/developers/documentation

