# SendGrid & SMS Configuration for Railway Production

## 📊 Current Status

| Service | Type | Status | Configuration |
|---------|------|--------|---|
| **Gmail SMTP** | Email (Primary) | ✅ **WORKING** | Hardcoded in settings.py |
| **SendGrid** | Email (Fallback) | ⚠️ **NOT CONFIGURED** | Needs API key in Railway |
| **PhilSMS** | SMS Notifications | ⚠️ **NOT CONFIGURED** | Needs API token in Railway |
| **Twilio** | SMS (Alternative) | ❌ **NOT USED** | Code includes but not implemented |

---

## 🚀 Quick Setup Guide

### What You Need

**For SendGrid (Email Fallback):**
- Free SendGrid account (100 emails/day free)
- 1 API key to add to Railway

**For SMS (PhilSMS):**
- PhilSMS account with credits
- 1 API token to add to Railway

---

## 1️⃣ SETUP SendGrid (Email Fallback)

### Why SendGrid?
- Improves email reliability if Gmail SMTP fails
- Better deliverability tracking
- Higher volume limits than Gmail

### Step-by-Step Setup

**Step 1: Create SendGrid Account (If Not Done)**
```
1. Go to: https://sendgrid.com/free
2. Sign up with: dwightanthonyb@gmail.com
3. Click "Create Free Account"
4. Verify email
```

**Step 2: Get API Key**
```
1. Login to SendGrid: https://app.sendgrid.com
2. Left sidebar → Settings → API Keys
3. Click "Create API Key" button
4. Name: "Railway Production"
5. Permissions: Select "Full Access"
6. Click "Create & View"
7. COPY THE KEY (starts with "SG.")
8. Save it somewhere safe - you won't see it again!
```

**Step 3: Add to Railway**
```
1. Go to Railway Dashboard: https://railway.app
2. Select your project: "Complaint Management System"
3. Select the "web" service (your Django app)
4. Click "Variables" tab
5. Add new variable:
   Name:  SENDGRID_API_KEY
   Value: SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
6. Save/Deploy
```

**Step 4: Verify Sender Email (In SendGrid)**
```
SendGrid Dashboard → Settings → Sender Authentication
- Check if dwightanthonyb@gmail.com is verified
- If not, SendGrid will send verification email
- Verify it before using
```

**After Setup:**
- ✅ Email sending will try Gmail first
- ✅ If Gmail fails, SendGrid fallback activates automatically
- ✅ No code changes needed

---

## 2️⃣ SETUP SMS (PhilSMS)

### Why PhilSMS?
- Specifically for Philippine phone numbers
- Reliable SMS delivery in PH
- Integrated in codebase already

### Step-by-Step Setup

**Step 1: Create PhilSMS Account**
```
1. Go to: https://app.philsms.com
2. Sign up or log in
3. Complete profile verification
4. Add SMS credits (pricing varies)
   - Usually PHP 1-2 per SMS
   - Minimum topup varies
```

**Step 2: Get API Token**
```
1. Login to PhilSMS Dashboard
2. Settings → API Keys or Account Settings
3. Generate/View API Token
4. Copy the token (long string of characters)
```

**Step 3: Add to Railway**
```
1. Go to Railway Dashboard
2. Select your project
3. Select "web" service
4. Click "Variables" tab
5. Add TWO variables:

   Variable 1:
   Name:  PHILSMS_API_TOKEN
   Value: [Your PhilSMS API token]

   Variable 2:
   Name:  PHILSMS_SENDER_ID
   Value: CMS  (or your preferred sender name)

6. Save/Deploy
```

**After Setup:**
- ✅ SMS sent when complaints change status
- ✅ User receives SMS to their registered phone
- ✅ SMS logs appear in Railway logs

---

## 3️⃣ (OPTIONAL) TWILIO Setup

### Note: PhilSMS is preferred for PH numbers
- Twilio works but costs more
- PhilSMS is already configured
- Only use Twilio if you want international SMS support

**If you want Twilio:**
```
1. Sign up at: https://www.twilio.com
2. Get Account SID and Auth Token
3. Add to Railway Variables:
   TWILIO_ACCOUNT_SID=...
   TWILIO_AUTH_TOKEN=...
   TWILIO_FROM=+1234567890 (your Twilio number)
```

---

## 📝 Environment Variables Checklist

### Copy this and add to Railway Variables:

```
SENDGRID_API_KEY=[Your SendGrid API Key - starts with SG.]
PHILSMS_API_TOKEN=[Your PhilSMS API Token]
PHILSMS_SENDER_ID=CMS
```

### Optional (for Twilio):
```
TWILIO_ACCOUNT_SID=[Your Twilio Account SID]
TWILIO_AUTH_TOKEN=[Your Twilio Auth Token]
TWILIO_FROM=[Your Twilio Phone Number]
```

---

## 🧪 How to Test

### Test SendGrid (After Adding API Key)

**Local Testing:**
```bash
python test_email_send.py
# Should show: ✅ Email sent successfully
```

**On Railway:**
- Trigger email send (user login)
- Check Railway Logs
- Look for: "✅ Email sent successfully via Gmail SMTP"
  OR "✅ Email sent via SendGrid fallback"

### Test PhilSMS (After Adding API Token)

**Create Test Script:**
```bash
cat > test_sms_send.py << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.sms_utils import send_sms_via_philsms

# Test SMS
result = send_sms_via_philsms(
    recipient="09123456789",  # Replace with your number
    message="Test SMS from Complaint Management System"
)

if result:
    print("✅ SMS sent successfully!")
else:
    print("❌ SMS failed - check API token and credits")
EOF

python test_sms_send.py
```

**On Railway:**
- Submit a complaint and update its status
- User gets SMS notification if phone is registered
- Check Railway Logs for SMS send status

---

## ✅ Verification Checklist

### For SendGrid
- [ ] Account created at sendgrid.com
- [ ] API Key generated
- [ ] Sender email verified in SendGrid
- [ ] SENDGRID_API_KEY added to Railway Variables
- [ ] Railway redeployed
- [ ] Test email received

### For PhilSMS
- [ ] Account created at philsms.com
- [ ] SMS credits purchased
- [ ] API Token copied
- [ ] PHILSMS_API_TOKEN added to Railway Variables
- [ ] PHILSMS_SENDER_ID added to Railway Variables
- [ ] Railway redeployed
- [ ] Test SMS received on phone

---

## 📊 Email Flow (With SendGrid Fallback)

```
User needs email
    ↓
Try Gmail SMTP (Primary - Always Works)
    ├─ Success → Email sent ✅
    ├─ Timeout/Error → Try SendGrid fallback
    │   ├─ SendGrid API key configured?
    │   │   ├─ YES → Try SendGrid
    │   │   │   ├─ Success → Email sent ✅
    │   │   │   └─ Error → Log error
    │   │   └─ NO → Log "API key not configured"
    │   └─ Both failed → Email not delivered ❌
```

---

## 📊 SMS Flow (PhilSMS)

```
Complaint status changes
    ↓
Check user phone number registered
    ├─ YES → Prepare SMS message
    │   └─ Send via PhilSMS
    │       ├─ API token configured?
    │       │   ├─ YES → SMS sent ✅
    │       │   └─ NO → Log "API token not configured"
    │       └─ API credits available?
    │           ├─ YES → SMS delivered ✅
    │           └─ NO → SMS failed (out of credits)
    └─ NO → No SMS sent (user didn't provide phone)
```

---

## 🔍 Where to Check Logs

### Railway Logs
```
1. Go to Railway Dashboard
2. Select your project
3. Select "web" service
4. Click "Logs" tab
5. Search for:
   - "Email sent successfully" (Gmail success)
   - "Email sent via SendGrid" (SendGrid fallback)
   - "SENDGRID_API_KEY not found" (SendGrid not configured)
   - "PhilSMS: SMS sent successfully" (SMS success)
   - "PHILSMS_API_TOKEN not found" (SMS not configured)
```

---

## 🆘 Troubleshooting

### Email Issues

**Problem:** "Email sent successfully via Gmail SMTP" but user doesn't receive
- **Solution:** Check spam folder, mark as not spam, retry

**Problem:** "SENDGRID_API_KEY not found" in logs
- **Solution:** Add SENDGRID_API_KEY to Railway Variables (optional but recommended)

**Problem:** Both Gmail and SendGrid fail
- **Solution:** Check Railway logs for specific error, verify credentials

### SMS Issues

**Problem:** "PHILSMS_API_TOKEN not found" in logs
- **Solution:** Add PHILSMS_API_TOKEN to Railway Variables

**Problem:** SMS fails even with token configured
- **Solution 1:** Check PhilSMS account has SMS credits
- **Solution 2:** Verify phone number format: 09123456789 (with leading 0)
- **Solution 3:** Check PhilSMS API token is correct and not expired

**Problem:** User doesn't receive SMS
- **Solution 1:** User must register phone number in profile
- **Solution 2:** Phone must be valid Philippine number (09xxx)
- **Solution 3:** PhilSMS account must have credits
- **Solution 4:** Check PhilSMS dashboard for delivery reports

---

## 💰 Cost Estimation

### SendGrid
- **Free tier:** 100 emails/day
- **Recommended:** Free or $9.95/month (unlimited)

### PhilSMS
- **SMS Rate:** Usually PHP 1-2 per SMS
- **For ~100 users:** ~PHP 100-200/month
- **For ~1000 users:** ~PHP 1000-2000/month

### Twilio (Alternative)
- **SMS Rate:** $0.0075 per SMS (more expensive)
- **For ~100 users:** ~$7-15/month
- **For ~1000 users:** ~$75-150/month

**Recommendation:** Use PhilSMS for local Philippine users (cheaper)

---

## 📞 Support Resources

- **SendGrid Docs:** https://docs.sendgrid.com
- **PhilSMS Docs:** https://app.philsms.com/docs (if available)
- **Railway Docs:** https://docs.railway.app
- **Django Email:** https://docs.djangoproject.com/en/5.1/topics/email/

---

## 🎯 Next Steps

1. **Add SendGrid (Recommended):** Takes 5 minutes, improves email reliability
2. **Add PhilSMS (Required for SMS):** If you need SMS notifications
3. **Test Both:** Use provided scripts to verify
4. **Monitor Logs:** Watch Railway logs for any issues

**Start with SendGrid first** - it's faster and improves email reliability with just one API key!

