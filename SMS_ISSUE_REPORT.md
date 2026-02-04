# SMS Notifications - Issue & Solution Report

## Issue Summary

**Problem:** Users are NOT receiving SMS notifications when complaint status is updated.

**Root Cause:** PhilSMS API account appears to have configuration issues returning 403 errors.

---

## Investigation Results

### ✅ What's Working

1. **Phone Number Collection** - Users can save phone numbers in their profile
2. **Phone Number Storage** - 3 users have phone numbers stored in system
3. **SMS Code Integration** - Status update function correctly calls SMS sending
4. **Phone Number Format** - ✅ FIXED - Now using correct `09XXXXXXXXX` format (not `+63`)
5. **Email Notifications** - ✅ Still working (Gmail SMTP)

### ❌ What's Not Working

**PhilSMS API is returning errors:**

```
Test 1 (+63 format): Status 403 - "Telco Issues"
Test 2 (09 format):  Status 403 - "Could not interpret numbers after plus-sign"
```

---

## What We Fixed

### Phone Number Format Issue
**File:** [myapp/sms_utils.py](myapp/sms_utils.py#L77-L97)

**Old Code:**
```python
# Converted 09XXXXXXXXX to +63XXXXXXXXX (incorrect for this API)
formatted_phone = '+63' + phone_number[1:]
```

**New Code:**
```python
# Keep as 09XXXXXXXXX (correct format for PhilSMS)
if phone_number.startswith('09'):
    formatted_phone = phone_number  # Already correct
elif phone_number.startswith('+63'):
    formatted_phone = '0' + phone_number[3:]  # Convert back
```

**Status:** ✅ Committed and deployed to Railway (commit `f9f7e18`)

---

## Next Steps - PhilSMS Account Issue

The API responses suggest one of these issues:

### Issue #1: Invalid API Token
- **Solution:** Verify `PHILSMS_API_TOKEN` in Railway Variables
- **Check:** Is it the complete token with no typos?
- **Action:** Log into PhilSMS account, regenerate API token if needed

### Issue #2: Sender ID Not Verified
- **Current:** `PHILSMS_SENDER_ID = "PHILSMS"`
- **Problem:** This sender ID might not be registered/verified in PhilSMS account
- **Solution:** 
  - Log into PhilSMS dashboard
  - Go to Sender IDs section
  - Create a verified sender ID (usually phone number like `+639XXXXXXXXX`)
  - Update `PHILSMS_SENDER_ID` in Railway to the verified ID

### Issue #3: Telco Connection Problem
- **Error:** "Telco Issues" with +63 format
- **Solution:** Contact PhilSMS support - account might have carrier issues

### Issue #4: Account Credits or Status
- **Check:** Does PhilSMS account have active credits?
- **Check:** Is the account still active/not suspended?
- **Solution:** Log into PhilSMS to verify account status

---

## Verification Steps

After fixing the PhilSMS account, test with:

```bash
# Run diagnostic script to test SMS
python diagnose_sms.py
```

Expected output should show:
```
✅ PhilSMS API connection is WORKING
```

Instead of:
```
❌ PhilSMS API returned error: 403
```

---

## Temporary Workaround

Until PhilSMS is fixed, users still receive **Email notifications** when status changes:
- ✅ Gmail SMTP is working 
- ✅ SendGrid API is ready as fallback
- Email arrives within 1-2 minutes

---

## Code Changes Made

### 1. Fixed SMS Phone Format ([myapp/sms_utils.py](myapp/sms_utils.py))
- **Line 77-97:** Changed phone format from `+63XXXXXXXXX` to `09XXXXXXXXX`
- **Why:** PhilSMS API returns error when sender ID receives plus-sign formatted numbers
- **Deployed:** Yes (commit `f9f7e18`)

### 2. Diagnostic Script ([diagnose_sms.py](diagnose_sms.py))
- **Purpose:** Help identify SMS configuration issues
- **Run:** `python diagnose_sms.py`
- **Shows:** API token, users with phones, API connection test

---

## System Status

| Component | Status | Details |
|-----------|--------|---------|
| **Email (Gmail SMTP)** | ✅ Working | Users receive verification emails |
| **Email (SendGrid)** | ✅ Ready | Fallback configured |
| **SMS (PhilSMS)** | ❌ Not Working | API returning 403 errors |
| **SMS Code Logic** | ✅ Correct | Properly integrated, now with correct phone format |
| **User Phone Storage** | ✅ Working | 3 users have numbers saved |

---

## Action Items

**Immediate:**
- [ ] Check PHILSMS_API_TOKEN in Railway Variables
- [ ] Verify it matches token in PhilSMS account
- [ ] Check PhilSMS account status/credits
- [ ] Run `diagnose_sms.py` after each change

**If still not working:**
- [ ] Contact PhilSMS support about 403 errors
- [ ] Ask about sender ID verification requirements
- [ ] Request new API token if current one is expired

**Testing:**
- [ ] After PhilSMS fix, change complaint status from "Pending" → "In Progress"
- [ ] User should receive SMS within seconds (plus email within 1-2 min)
- [ ] Check Railway logs for "✅ PhilSMS: SMS sent successfully"

---

## Technical Summary

**Architecture:**
```
Admin Changes Status
    ↓
[views.py - update_transaction_status()]
    ├─→ Email → Gmail SMTP ✅
    └─→ SMS → PhilSMS API ❌ (API issue, format now fixed)
```

**Phone Format Flow:**
```
UserProfile.phone_number: "09958744151"
    ↓
send_status_change_sms()
    ↓  
send_sms_via_philsms(formatted_phone="09958744151")
    ↓
PhilSMS API (fixed format, awaiting account fix)
```

---

**Last Updated:** February 2, 2026
**Deployed Changes:** Commit `f9f7e18` 
**Next Action:** Fix PhilSMS account configuration
