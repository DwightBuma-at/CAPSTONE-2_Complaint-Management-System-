# PhilSMS Account Fix - Quick Checklist

## Step 1: Verify API Token in Railway ✓

1. Go to Railway: https://railway.app
2. Select your project
3. Go to **Variables** tab
4. Find `PHILSMS_API_TOKEN`
5. Compare with token in PhilSMS account dashboard

**Expected:** Token looks like: `3520|XXXXXXXXXXXXXXXXXXXXXXXXXX`

---

## Step 2: Log into PhilSMS Account

1. Go to: https://app.philsms.com
2. Log in with your credentials
3. Go to **API Settings** or **Sender IDs**

---

## Step 3: Check & Fix Sender ID

### Current Setup:
```
PHILSMS_SENDER_ID = "PHILSMS"
```

### Issue:
This generic sender ID might not be verified in PhilSMS account.

### Solution - Create Verified Sender ID:

1. **In PhilSMS Dashboard:**
   - Go to **Sender IDs** section
   - Click **Add New Sender ID**
   - Select **Phone Number** (recommended)
   - Enter your phone: `+639958744151` (example)
   - Click **Verify**
   - PhilSMS sends verification code to your phone
   - Enter code to complete verification

2. **In Railway Variables:**
   - Update `PHILSMS_SENDER_ID = "+639958744151"`
   - OR use any other verified sender ID from your account

---

## Step 4: Verify API Token is Fresh

1. **In PhilSMS Dashboard:**
   - Go to **API Settings**
   - Check if token is still active (not expired)
   - If expired or suspicious → **Regenerate Token**

2. **Copy New Token:**
   - Copy the new token
   - Paste into Railway Variables as `PHILSMS_API_TOKEN`

---

## Step 5: Check Account Credits

1. **In PhilSMS Dashboard:**
   - Go to **Account** or **Balance**
   - Verify you have SMS credits
   - If zero → **Add credits** (usually PHP 500+ minimum)

---

## Step 6: Test SMS Locally

After making changes, run diagnostic:

```bash
python diagnose_sms.py
```

**Expected output:**
```
✅ PhilSMS: SMS sent successfully!
```

**If still seeing 403 errors:**
- Save changes and wait 2-3 minutes
- PhilSMS might cache settings
- Try again

---

## Step 7: Deploy to Production

```bash
git add .
git commit -m "Update PhilSMS sender ID to verified account"
git push origin main
```

Railway will auto-redeploy with new variables.

---

## Step 8: Test in Production

1. Go to: https://dvobarangaycms.vip
2. Create a test complaint
3. Provide phone number: `09958744151`
4. As admin, change status from "Pending" → "In Progress"
5. **Check phone** - Should receive SMS within 5-10 seconds

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| 403 - Telco Issues | API token expired, try regenerating |
| 403 - Could not interpret numbers | Sender ID not verified, create new one |
| No SMS received | Phone number format wrong or account has no credits |
| API working but no SMS | Check phone number, check if country code is set |

---

## Quick Reference

**File to check:**
- [myapp/sms_utils.py](myapp/sms_utils.py) - SMS sending code (phone format fixed ✅)

**Variables to update in Railway:**
```
PHILSMS_API_TOKEN = "your-new-token-here"
PHILSMS_SENDER_ID = "verified-sender-id-from-account"
```

**Test command:**
```bash
python diagnose_sms.py
```

---

**Questions?** Check Railway logs for detailed error messages:
```
Look for: "PhilSMS Error:" in logs
```

---

**Status:** Code is fixed (✅ commit f9f7e18), awaiting PhilSMS account configuration
