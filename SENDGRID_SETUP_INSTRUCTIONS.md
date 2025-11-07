# SendGrid Setup Instructions for New Account
## dwightanthonyb@gmail.com

### ✅ Completed Steps:
1. ✅ Created new SendGrid account with `dwightanthonyb@gmail.com`
2. ✅ Verified sender email in SendGrid dashboard
3. ✅ Free trial active until **January 6, 2026**
4. ✅ Updated codebase to use new sender email

---

## 🔧 Next Steps: Configure Railway Environment

### Step 1: Get Your SendGrid API Key

1. Go to SendGrid Dashboard: https://app.sendgrid.com
2. Navigate to: **Settings** → **API Keys** (left sidebar)
3. Click **"Create API Key"** button
4. Configure the API Key:
   - **Name:** `Railway Production API Key` (or any name you prefer)
   - **API Key Permissions:** Select **"Full Access"** or **"Restricted Access"** with **"Mail Send"** enabled
5. Click **"Create & View"**
6. **COPY THE API KEY** - You'll only see it once! It starts with `SG.`
   - Example format: `SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 2: Add API Key to Railway

1. Go to your Railway dashboard: https://railway.app
2. Select your project: **Complaint Management System**
3. Select your service (the Django app)
4. Go to the **"Variables"** tab
5. Click **"New Variable"**
6. Add the following:

```
Variable Name: SENDGRID_API_KEY
Variable Value: [Paste your API key here - starts with SG.]
```

7. Click **"Add"** or **"Save"**
8. Railway will automatically **redeploy** your application

### Step 3: Verify Deployment (Optional but Recommended)

You can also add the sender email as an environment variable (optional):

```
Variable Name: SENDGRID_SENDER_EMAIL
Variable Value: dwightanthonyb@gmail.com
```

This allows you to change the sender email without modifying code in the future.

---

## 🧪 Testing After Deployment

### Option 1: Test via Your Application

1. Go to your production URL: `https://[your-railway-url].up.railway.app`
2. Try to register a new user or login
3. Check if OTP email is received at the test email address
4. Check your SendGrid dashboard - "EMAILS TODAY" should show 1+ requests

### Option 2: Check Railway Logs

1. Go to Railway Dashboard → Your Service → **"Deployments"** tab
2. Click on the latest deployment
3. Check the logs for:
   - ✅ `📧 SendGrid: Sending email to [email]`
   - ✅ `✅ SendGrid: Email sent successfully! Status: 202`
   - ❌ `❌ SENDGRID_API_KEY not found` (if this appears, API key wasn't added correctly)

### Option 3: Check SendGrid Dashboard

1. Go to: https://app.sendgrid.com
2. Dashboard should show:
   - **EMAILS TODAY:** Should be > 0 after testing
   - **REQUESTS:** Should increment with each email
   - **DELIVERED:** Should show 100% if emails are successfully sent

---

## 📋 What Changed in the Code

### Files Updated:

1. **`myapp/sendgrid_email.py`** (Line 40)
   - Changed from: `complaintmanagementsystem5.new@gmail.com`
   - Changed to: `dwightanthonyb@gmail.com`

2. **`env.example`**
   - Added `SENDGRID_API_KEY` documentation
   - Added `SENDGRID_SENDER_EMAIL` documentation

### What Stays the Same:

1. **OTP email format** - Unchanged
2. **Status notification format** - Unchanged
3. **All email templates** - Unchanged
4. **Superadmin login** - Still uses `complaintmanagementsystem5@gmail.com` (intentional)
5. **Local SMTP settings** - Still uses `complaintmanagementsystem5@gmail.com` for development

---

## 🔍 Troubleshooting

### Issue: "EMAILS TODAY 0" in SendGrid Dashboard

**Cause:** `SENDGRID_API_KEY` not set in Railway environment variables

**Solution:**
1. Go to Railway → Variables tab
2. Add `SENDGRID_API_KEY` with your API key
3. Redeploy

### Issue: "401 Unauthorized" in Railway Logs

**Cause:** Invalid or incorrect API key

**Solution:**
1. Verify API key is correct (starts with `SG.`)
2. Check for extra spaces or characters
3. Regenerate API key in SendGrid if needed

### Issue: "403 Forbidden" in Railway Logs

**Cause:** Sender email not verified in SendGrid

**Solution:**
1. Go to SendGrid → Settings → Sender Authentication
2. Verify that `dwightanthonyb@gmail.com` shows as "Verified"
3. If not, click "Resend Verification" and check your inbox

### Issue: Emails Going to Spam

**Solution:**
1. This is normal for new SendGrid accounts
2. Over time, your sender reputation will improve
3. Users should check spam folder and mark as "Not Spam"
4. Consider setting up domain authentication (advanced) for better deliverability

---

## 📊 Email Sending Limits

### Free Trial (Until January 6, 2026):
- **100 emails per day**
- Full SendGrid features
- No credit card required

### After Trial Ends (Free Forever Tier):
- **100 emails per day** (same as trial)
- Continues forever at no cost
- Sufficient for most barangay complaint systems

### If You Need More:
- Upgrade to paid plan (starting at $19.95/month)
- Increase daily limit to 40,000+ emails

---

## ✅ Quick Reference

| Configuration | Value |
|--------------|-------|
| **SendGrid Account** | dwightanthonyb@gmail.com |
| **Sender Email** | dwightanthonyb@gmail.com |
| **Trial Expires** | January 6, 2026 |
| **Daily Limit** | 100 emails/day |
| **Environment Variable** | SENDGRID_API_KEY |
| **API Key Format** | Starts with `SG.` |

---

## 🎯 Summary

**You're all set!** Once you add the `SENDGRID_API_KEY` to Railway:

✅ OTP emails will work again  
✅ Status notifications will work  
✅ All email services will resume  
✅ Fresh trial until January 6, 2026  
✅ 100 emails per day limit  

**Just add the API key to Railway and you're done!** 🚀

---

## 📞 Support

If you encounter issues:
1. Check Railway logs for error messages
2. Verify SendGrid dashboard shows verified sender
3. Confirm API key is correctly set in Railway
4. Check SendGrid "Activity" tab for email delivery status

**SendGrid Dashboard:** https://app.sendgrid.com  
**Railway Dashboard:** https://railway.app

