from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest, Http404, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate, login as django_login, logout as django_logout, get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from functools import wraps
import json
import os
from datetime import datetime
import pytz

from .models import Complaint, AdminProfile, UserProfile, EmailOTP, ChatConversation, ChatMessage, AdminActivityLog
from .supabase_client import supabase
from .email_utils import create_otp_for_email, verify_otp

ADMIN_ACTIVATION_KEY = "F32024"

# Health check endpoint for Railway debugging
@csrf_exempt
def health_check(request):
    """Simple health check to test Railway deployment"""
    try:
        # Test database connection
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        db_status = "OK"
    except Exception as e:
        db_status = f"ERROR: {str(e)}"
    
    # Test model imports
    try:
        from .models import AdminActivityLog
        model_status = "OK - AdminActivityLog enabled"
    except Exception as e:
        model_status = f"ERROR: {str(e)}"
    
    # Test pytz import
    try:
        import pytz
        pytz_status = "OK"
    except Exception as e:
        pytz_status = f"ERROR: {str(e)}"
    
    return JsonResponse({
        "status": "OK",
        "database": db_status,
        "models": model_status,
        "pytz": pytz_status,
        "timestamp": timezone.now().isoformat()  # Use simple timezone.now() instead of custom function
    })

# Centralized time utility functions
def get_ph_timezone():
    """Get Philippine timezone object"""
    return pytz.timezone('Asia/Manila')

def format_ph_datetime(dt):
    """Convert any datetime to Philippine time and format as string"""
    if not dt:
        return ''
    
    ph_tz = get_ph_timezone()
    
    # Handle different input types
    if isinstance(dt, str):
        # Parse string datetime
        try:
            if 'T' in dt:
                # ISO format from Supabase
                if dt.endswith('Z'):
                    dt = dt.replace('Z', '+00:00')
                parsed_dt = datetime.fromisoformat(dt)
            else:
                # Django format
                parsed_dt = datetime.fromisoformat(dt)
            
            # If timezone-naive, assume UTC
            if parsed_dt.tzinfo is None:
                parsed_dt = pytz.UTC.localize(parsed_dt)
            
            # Convert to PH time
            ph_time = parsed_dt.astimezone(ph_tz)
            return ph_time.strftime("%Y-%m-%d %H:%M")
        except Exception as e:
            print(f"Error parsing datetime string: {dt}, error: {e}")
            return ''
    
    elif hasattr(dt, 'astimezone'):
        # Django timezone-aware datetime
        ph_time = dt.astimezone(ph_tz)
        return ph_time.strftime("%Y-%m-%d %H:%M")
    
    else:
        # Fallback for other types
        try:
            ph_time = timezone.localtime(dt)
            return ph_time.strftime("%Y-%m-%d %H:%M")
        except:
            return ''

def get_current_ph_time():
    """Get current time in Philippine timezone"""
    return timezone.now().astimezone(get_ph_timezone())

# Authentication decorator for admin pages
def require_admin_auth(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is authenticated as admin
        if not request.session.get('admin_authenticated'):
            # Check if user is authenticated as a regular user (block cross-role access)
            if request.user.is_authenticated:
                print(f"🚫 Regular user blocked from accessing admin page {request.path}")
                return redirect('/index.html?show_login=true')
            else:
                # User is not authenticated at all, allow access (will be handled by login system)
                print(f"✅ Unauthenticated user accessing admin page {request.path}")
                return view_func(request, *args, **kwargs)
        return view_func(request, *args, **kwargs)
    return wrapper

def home(request):
    return render(request, 'index.html')

def user_page(request):
    # Block admins from accessing user pages
    if request.session.get('admin_authenticated'):
        return redirect('/index.html?show_login=true')
    return render(request, 'user.html')

def user_submit(request):
    # Block admins from accessing user pages
    if request.session.get('admin_authenticated'):
        return redirect('/index.html?show_login=true')
    return render(request, 'user-submit.html')

def user_view(request):
    # Block admins from accessing user pages
    if request.session.get('admin_authenticated'):
        return redirect('/index.html?show_login=true')
    return render(request, 'user-view.html')

def user_history(request):
    # Block admins from accessing user pages
    if request.session.get('admin_authenticated'):
        return redirect('/index.html?show_login=true')
    return render(request, 'user-history.html')


# ==========================
# API: User Registration & Auth
# ==========================

@csrf_exempt
@require_http_methods(["POST"]) 
def send_verification_code(request):
    """Send verification code to user's email"""
    try:
        print(f"🔍 send_verification_code called with method: {request.method}")
        print(f"🔍 Request body: {request.body.decode('utf-8')[:200]}...")  # First 200 chars
        
        payload = json.loads(request.body.decode("utf-8"))
        print(f"🔍 Parsed payload successfully: {list(payload.keys())}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    except Exception as e:
        print(f"❌ Unexpected error in send_verification_code: {e}")
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)

    full_name = (payload.get("full_name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    barangay = (payload.get("barangay") or "").strip()
    password = (payload.get("password") or "").strip()
    confirm_password = (payload.get("confirm_password") or "").strip()

    # Debug logging
    print(f"Received payload: {payload}")
    print(f"Extracted values: email='{email}', full_name='{full_name}', barangay='{barangay}', password='{'*' * len(password) if password else 'empty'}', confirm_password='{'*' * len(confirm_password) if confirm_password else 'empty'}'")
    
    # Check which fields are missing
    missing_fields = []
    if not email: missing_fields.append("email")
    if not full_name: missing_fields.append("full_name")
    if not barangay: missing_fields.append("barangay")
    if not password: missing_fields.append("password")
    if not confirm_password: missing_fields.append("confirm_password")
    
    if missing_fields:
        print(f"Missing fields: {missing_fields}")
        return JsonResponse({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=400)

    if password != confirm_password:
        return JsonResponse({"error": "Passwords do not match"}, status=400)

    if len(password) < 6:
        return JsonResponse({"error": "Password must be at least 6 characters"}, status=400)

    # Check if email already exists
    try:
        print(f"🔍 Checking if email exists in database: {email}")
        if UserProfile.objects.filter(email__iexact=email).exists():
            return JsonResponse({"error": "Email already registered"}, status=400)
        print(f"✅ Database connection successful, email not found")
    except Exception as db_error:
        print(f"❌ Database connection failed: {db_error}")
        return JsonResponse({"error": "Database connection error. Please try again later."}, status=503)

    # Create OTP and send email
    try:
        print(f"📧 Attempting to create OTP for email: {email}")
        otp = create_otp_for_email(email)
        print(f"📧 create_otp_for_email returned: {otp}")
        if not otp:
            # If email sending fails, create OTP anyway for development/testing
            from .email_utils import generate_otp
            from datetime import timedelta
            
            # Delete any existing unused OTPs for this email
            EmailOTP.objects.filter(email=email, is_used=False).delete()
            
            # Generate new OTP without sending email
            otp_code = generate_otp()
            expires_at = timezone.now() + timedelta(minutes=10)
            
            # Create OTP record
            otp = EmailOTP.objects.create(
                email=email,
                otp_code=otp_code,
                expires_at=expires_at
            )
            
            return JsonResponse({
                "success": True, 
                "message": "Verification code generated. Check console for code: " + otp_code,
                "email": email
            })
        
        return JsonResponse({
            "success": True, 
            "message": "Verification code sent to your email",
            "email": email
        })
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR in send_verification_code: {e}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"]) 
def verify_email_and_register(request):
    """Verify OTP and create user account"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    email = (payload.get("email") or "").strip().lower()
    full_name = (payload.get("full_name") or "").strip()
    barangay = (payload.get("barangay") or "").strip()
    password = (payload.get("password") or "").strip()
    otp_code = (payload.get("otp_code") or "").strip()

    # Validation
    if not all([email, barangay, password, otp_code]):
        return JsonResponse({"error": "All fields are required"}, status=400)

    if len(otp_code) != 6:
        return JsonResponse({"error": "Invalid OTP code format"}, status=400)

    # Verify OTP
    is_valid, message = verify_otp(email, otp_code)
    if not is_valid:
        return JsonResponse({"error": message}, status=400)

    # Check if email already exists (double check)
    if UserProfile.objects.filter(email__iexact=email).exists():
        return JsonResponse({"error": "Email already registered"}, status=400)

    try:
        # Get User model
        User = get_user_model()
        
        # Create user
        username = email.split('@')[0]
        # Ensure unique username
        base_username = username
        idx = 1
        while User.objects.filter(username=username).exists():
            idx += 1
            username = f"{base_username}{idx}"

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create user profile with email and password
        from django.contrib.auth.hashers import make_password
        UserProfile.objects.create(
            user=user,
            full_name=full_name,
            email=email,
            barangay=barangay,
            password=make_password(password),  # Hash the password
            email_verified=True
        )

        return JsonResponse({
            "success": True,
            "message": "Account created successfully! You can now login.",
            "user_id": user.id
        }, status=201)

    except Exception as e:
        return JsonResponse({"error": f"Error creating account: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"]) 
def user_login(request):
    """User login with email and password - sends OTP for verification"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    email = (payload.get("email") or "").strip().lower()
    password = (payload.get("password") or "").strip()

    if not email or not password:
        return JsonResponse({"error": "Email and password are required"}, status=400)

    # Find user profile by email
    try:
        print(f"🔍 Attempting to find user profile for email: {email}")
        user_profile = UserProfile.objects.get(email__iexact=email)
        user = user_profile.user
        print(f"✅ User profile found successfully")
    except UserProfile.DoesNotExist:
        print(f"❌ User profile not found for email: {email}")
        return JsonResponse({"error": "Invalid credentials"}, status=401)
    except Exception as db_error:
        print(f"❌ Database connection failed in user_login: {db_error}")
        return JsonResponse({"error": "Database connection error. Please try again later."}, status=503)

    # Check if email is verified
    if not user_profile.email_verified:
        return JsonResponse({"error": "Please verify your email before logging in"}, status=401)

    # Verify password from UserProfile
    from django.contrib.auth.hashers import check_password
    if not check_password(password, user_profile.password):
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    # Create OTP for login verification
    try:
        print(f"📧 Creating OTP for user login: {email}")
        otp = create_otp_for_email(email)
        if not otp:
            # If email sending fails, create OTP anyway for development/testing
            from .email_utils import generate_otp
            from datetime import timedelta
            
            # Delete any existing unused OTPs for this email
            EmailOTP.objects.filter(email=email, is_used=False).delete()
            
            # Generate new OTP without sending email
            otp_code = generate_otp()
            expires_at = timezone.now() + timedelta(minutes=10)
            
            # Create OTP record
            otp = EmailOTP.objects.create(
                email=email,
                otp_code=otp_code,
                expires_at=expires_at
            )
            print(f"⚠️ Email sending failed, but OTP created for debugging: {otp_code}")
            
            return JsonResponse({
                "success": True, 
                "message": "Login verification code generated. Check console for code: " + otp_code,
                "email": email
            })
        
        print(f"✅ OTP created successfully")
        
        # Email sending is working - no need for debug mode
        return JsonResponse({
            "success": True,
            "message": "Verification code sent to your email",
            "email": email
        })
        
    except Exception as e:
        print(f"❌ Error in user login OTP creation: {e}")
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)

    return JsonResponse({
        "success": True,
        "message": "Please check your email for the verification code to complete login",
        "email": email,
        "requires_otp": True
    })


@csrf_exempt
@require_http_methods(["POST"]) 
def verify_login_otp(request):
    """Verify OTP for login and complete user authentication"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    email = (payload.get("email") or "").strip().lower()
    otp_code = (payload.get("otp_code") or "").strip()

    if not email or not otp_code:
        return JsonResponse({"error": "Email and OTP code are required"}, status=400)

    # Verify OTP
    is_valid, message = verify_otp(email, otp_code)
    if not is_valid:
        return JsonResponse({"error": message}, status=400)

    # Find user profile and login
    try:
        print(f"🔍 Attempting to find user profile for login verification: {email}")
        user_profile = UserProfile.objects.get(email__iexact=email)
        user = user_profile.user
        print(f"✅ User profile found for login verification")
    except UserProfile.DoesNotExist:
        print(f"❌ User profile not found for login verification: {email}")
        return JsonResponse({"error": "User not found"}, status=401)
    except Exception as db_error:
        print(f"❌ Database connection failed in verify_login_otp: {db_error}")
        return JsonResponse({"error": "Database connection error. Please try again later."}, status=503)

    # Login user
    django_login(request, user)
    
    return JsonResponse({
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user_profile.full_name,
            "barangay": user_profile.barangay
        },
        "redirect": "/user.html"
    })


@csrf_exempt
@require_http_methods(["POST"]) 
def resend_verification_code(request):
    """Resend verification code to user's email"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    email = (payload.get("email") or "").strip().lower()

    if not email:
        return JsonResponse({"error": "Email is required"}, status=400)

    # Check if email already exists
    if UserProfile.objects.filter(email__iexact=email).exists():
        return JsonResponse({"error": "Email already registered"}, status=400)

    # Create new OTP and send email
    otp = create_otp_for_email(email)
    if not otp:
        return JsonResponse({"error": "Failed to send verification email. Please try again."}, status=500)

    return JsonResponse({
        "success": True,
        "message": "Verification code resent to your email",
        "email": email
    })


# ==========================
# API: Admin Auth
# ==========================

@csrf_exempt
@require_http_methods(["POST"]) 
def admin_login(request):
    """First step of admin login - validate email and password"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    email = (payload.get("email") or "").strip().lower()
    password = (payload.get("password") or "").strip()
    admin_name = (payload.get("admin_name") or "").strip()

    if not email or not password:
        return JsonResponse({"error": "Email and password are required"}, status=400)

    # Find user by email
    User = get_user_model()
    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    # Check if user is staff/admin
    if not (user.is_staff or user.is_superuser):
        return JsonResponse({"error": "Not authorized as admin"}, status=403)

    # Verify password
    if not user.check_password(password):
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    # Check if admin profile exists
    try:
        admin_profile = user.admin_profile
    except AdminProfile.DoesNotExist:
        if not user.is_superuser:
            return JsonResponse({"error": "Admin profile not found"}, status=403)

    return JsonResponse({
        "success": True,
        "message": "Please enter your 6-digit admin access key",
        "email": email,
        "admin_name": admin_name,
        "requires_access_key": True
    })


@csrf_exempt
@require_http_methods(["POST"]) 
def admin_verify_access_key(request):
    """Second step of admin login - validate access key"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    email = (payload.get("email") or "").strip().lower()
    access_key = (payload.get("access_key") or "").strip()
    admin_name = (payload.get("admin_name") or "").strip()

    if not email or not access_key:
        return JsonResponse({"error": "Email and access key are required"}, status=400)

    # Validate access key format
    if not (access_key.isdigit() and len(access_key) == 6):
        return JsonResponse({"error": "Admin access key must be exactly 6 digits"}, status=400)

    # Find user by email
    User = get_user_model()
    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return JsonResponse({"error": "Invalid email"}, status=401)

    # Check if user is staff/admin
    if not (user.is_staff or user.is_superuser):
        return JsonResponse({"error": "Not authorized as admin"}, status=403)

    # Validate access key against AdminProfile
    try:
        admin_profile = user.admin_profile
        if not check_password(access_key, admin_profile.access_key_hash):
            return JsonResponse({"error": "Invalid admin access key"}, status=401)
    except AdminProfile.DoesNotExist:
        if not user.is_superuser:
            return JsonResponse({"error": "Admin profile not found"}, status=403)

    # Login successful
    django_login(request, user)
    
    # Get admin profile info
    display_name = admin_name if admin_name else "Admin"  # Use provided name or default
    admin_barangay = "Admin"
    try:
        admin_profile = user.admin_profile
        admin_barangay = admin_profile.barangay
    except AdminProfile.DoesNotExist:
        pass
    
    # Set admin authentication flag in session
    request.session['admin_authenticated'] = True
    request.session['admin_email'] = email
    request.session['admin_name'] = display_name
    request.session['admin_barangay'] = admin_barangay
    
    # Check if this is the superadmin email and redirect accordingly
    if email == 'complaintmanagementsystem5@gmail.com':
        redirect_url = "/superadmin.html/"
        success_message = "Superadmin login successful"
    else:
        redirect_url = "/admin-dashboard.html"
        success_message = "Admin login successful"
    
    return JsonResponse({
        "success": True,
        "message": success_message,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": display_name,
            "barangay": admin_barangay
        },
        "redirect": redirect_url
    })


@csrf_exempt
@require_http_methods(["POST"]) 
def admin_logout(request):
    django_logout(request)
    # Clear admin authentication session
    if 'admin_authenticated' in request.session:
        del request.session['admin_authenticated']
    if 'admin_email' in request.session:
        del request.session['admin_email']
    if 'admin_name' in request.session:
        del request.session['admin_name']
    if 'admin_barangay' in request.session:
        del request.session['admin_barangay']
    return JsonResponse({"ok": True})


@require_http_methods(["GET"]) 
def admin_me(request):
    # Check both Django authentication and our session flag
    user = getattr(request, "user", None)
    session_authenticated = request.session.get('admin_authenticated', False)
    
    if user and user.is_authenticated and (user.is_staff or user.is_superuser) and session_authenticated:
        # Get admin info from session (name from login, barangay from profile)
        full_name = request.session.get('admin_name', 'Admin')
        barangay = request.session.get('admin_barangay', None)
        
        # Get full admin profile data including officials
        admin_profile = None
        try:
            admin_profile = user.admin_profile
            if not barangay:
                barangay = admin_profile.barangay
        except:
            barangay = None
            
        return JsonResponse({
            "authenticated": True, 
            "username": user.get_username(),
            "email": user.email,
            "full_name": full_name,
            "barangay": barangay,
            # Include officials data if available
            "barangayCaptain": admin_profile.barangay_captain if admin_profile else None,
            "barangaySecretary": admin_profile.barangay_secretary if admin_profile else None,
            "barangayKagawad": admin_profile.barangay_kagawad if admin_profile else None,
            "skChairman": admin_profile.sk_chairman if admin_profile else None,
            "termStartYear": admin_profile.term_start_year if admin_profile else None,
            "termEndYear": admin_profile.term_end_year if admin_profile else None
        })
    return JsonResponse({"authenticated": False})


@csrf_exempt
@require_http_methods(["POST"]) 
def admin_register(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    email = (payload.get("email") or "").strip().lower()
    password = (payload.get("password") or "").strip()
    barangay = (payload.get("barangay") or "").strip()
    activation_key = (payload.get("activation_key") or "").strip()
    admin_access_key = (payload.get("admin_access_key") or "").strip()

    if not all([email, password, barangay, activation_key, admin_access_key]):
        return HttpResponseBadRequest("Missing fields")

    # Validate activation key (case-insensitive match to F32024)
    if activation_key.upper() != ADMIN_ACTIVATION_KEY:
        return JsonResponse({"error": "Invalid activation key"}, status=403)

    # Enforce 6-digit admin access key
    if not (admin_access_key.isdigit() and len(admin_access_key) == 6):
        return JsonResponse({"error": "Admin Access Key must be exactly 6 digits"}, status=400)

    User = get_user_model()
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({"error": "Email already registered"}, status=400)

    # Create user
    username = email.split('@')[0]
    # Ensure unique username
    base_username = username
    idx = 1
    while User.objects.filter(username=username).exists():
        idx += 1
        username = f"{base_username}{idx}"

    user = User.objects.create_user(username=username, email=email, password=password)
    user.is_staff = True
    user.save()

    AdminProfile.objects.create(
        user=user,
        barangay=barangay,
        access_key_hash=make_password(admin_access_key)
    )

    return JsonResponse({"ok": True, "message": "Admin registered successfully. You can now login as Admin."}, status=201)


@csrf_exempt
@require_http_methods(["POST"]) 
def admin_send_verification_code(request):
    """Send verification code to admin's email"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    email = (payload.get("email") or "").strip().lower()
    barangay = (payload.get("barangay") or "").strip()
    password = (payload.get("password") or "").strip()
    confirm_password = (payload.get("confirm_password") or "").strip()
    activation_key = (payload.get("activation_key") or "").strip()
    admin_access_key = (payload.get("admin_access_key") or "").strip()

    # Validation
    if not all([email, barangay, password, confirm_password, activation_key, admin_access_key]):
        return JsonResponse({"error": "All fields are required"}, status=400)

    if password != confirm_password:
        return JsonResponse({"error": "Passwords do not match"}, status=400)

    if len(password) < 6:
        return JsonResponse({"error": "Password must be at least 6 characters"}, status=400)

    # Validate activation key (case-insensitive match to F32024)
    if activation_key.upper() != ADMIN_ACTIVATION_KEY:
        return JsonResponse({"error": "Invalid activation key"}, status=403)

    # Enforce 6-digit admin access key
    if not (admin_access_key.isdigit() and len(admin_access_key) == 6):
        return JsonResponse({"error": "Admin Access Key must be exactly 6 digits"}, status=400)

    # Check if email already exists in both Django and Supabase
    User = get_user_model()
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({"error": "Email already registered"}, status=400)

    # Check Supabase admin_profiles table
    if supabase:
        try:
            response = supabase.table('admin_profiles').select('*').eq('email', email).execute()
            if response.data:
                return JsonResponse({"error": "Email already registered"}, status=400)
        except Exception as e:
            print(f"Supabase check error: {e}")

    # Create OTP and send email
    otp = create_otp_for_email(email)
    if not otp:
        return JsonResponse({"error": "Failed to send verification email. Please try again."}, status=500)

    return JsonResponse({
        "success": True, 
        "message": "Verification code sent to your email",
        "email": email
    })


@csrf_exempt
@require_http_methods(["POST"]) 
def admin_verify_email_and_register(request):
    """Verify OTP and create admin account"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    email = (payload.get("email") or "").strip().lower()
    barangay = (payload.get("barangay") or "").strip()
    password = (payload.get("password") or "").strip()
    activation_key = (payload.get("activation_key") or "").strip()
    admin_access_key = (payload.get("admin_access_key") or "").strip()
    otp_code = (payload.get("otp_code") or "").strip()
    
    # Barangay officials data (from superadmin registration)
    barangay_captain = (payload.get("barangay_captain") or "").strip()
    barangay_secretary = (payload.get("barangay_secretary") or "").strip()
    barangay_kagawad = (payload.get("barangay_kagawad") or "").strip()
    sk_chairman = (payload.get("sk_chairman") or "").strip()
    term_start_year = payload.get("term_start_year")
    term_end_year = payload.get("term_end_year")

    if not all([email, barangay, password, activation_key, admin_access_key, otp_code]):
        return JsonResponse({"error": "All fields are required"}, status=400)

    # Verify OTP
    is_valid, message = verify_otp(email, otp_code)
    if not is_valid:
        return JsonResponse({"error": message}, status=400)

    # Validate activation key
    if activation_key.upper() != ADMIN_ACTIVATION_KEY:
        return JsonResponse({"error": "Invalid activation key"}, status=403)

    # Enforce 6-digit admin access key
    if not (admin_access_key.isdigit() and len(admin_access_key) == 6):
        return JsonResponse({"error": "Admin Access Key must be exactly 6 digits"}, status=400)

    try:
        # Create user
        User = get_user_model()
        username = email.split('@')[0]
        # Ensure unique username
        base_username = username
        idx = 1
        while User.objects.filter(username=username).exists():
            idx += 1
            username = f"{base_username}{idx}"

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = True
        user.save()

        # Create AdminProfile in Django with officials data
        admin_profile = AdminProfile.objects.create(
            user=user,
            barangay=barangay,
            access_key_hash=make_password(admin_access_key),
            barangay_captain=barangay_captain,
            barangay_secretary=barangay_secretary,
            barangay_kagawad=barangay_kagawad,
            sk_chairman=sk_chairman,
            term_start_year=int(term_start_year) if term_start_year else None,
            term_end_year=int(term_end_year) if term_end_year else None
        )

        # Also store in Supabase for tracking
        if supabase:
            try:
                admin_data = {
                    "email": email,
                    "username": username,
                    "barangay": barangay,
                    "is_staff": True,
                    "email_verified": True,
                    "django_user_id": user.id,
                    "django_admin_profile_id": admin_profile.id
                }
                
                supabase_response = supabase.table('admin_profiles').insert(admin_data).execute()
                print(f"Admin profile created in Supabase: {email}")
            except Exception as e:
                print(f"Failed to store admin profile in Supabase: {e}")
                # Continue anyway - Django profile is created

        return JsonResponse({
            "success": True,
            "message": "Admin account created successfully! You can now login.",
            "user_id": user.id
        }, status=201)

    except Exception as e:
        return JsonResponse({"error": f"Error creating admin account: {str(e)}"}, status=500)

# ==========================
# API: Contact Form
# ==========================

@csrf_exempt
@require_http_methods(["POST"]) 
def contact_form_submission(request):
    """Handle contact form submissions and send email to admin"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    message = (payload.get("msg") or "").strip()

    # Validation
    if not all([name, email, message]):
        return JsonResponse({"error": "All fields are required"}, status=400)

    if not email or '@' not in email:
        return JsonResponse({"error": "Please enter a valid email address"}, status=400)

    try:
        # Send email to admin
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f"New Contact Form Submission from {name}"
        
        email_body = f"""
New contact form submission received:

Name: {name}
Email: {email}
Message:
{message}

---
This message was sent from the CMS Contact Form.
        """.strip()
        
        try:
            # Try to send email to admin
            send_mail(
                subject=subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["complaintmanagementsystem5@gmail.com"],
                fail_silently=False,
            )
            
            return JsonResponse({
                "success": True,
                "message": "Thank you! Your message has been sent successfully. We'll get back to you within 24 hours."
            })
        except Exception as email_error:
            print(f"Email sending failed: {email_error}")
            # Even if email fails, we can still log the contact form submission
            print(f"Contact form submission (email failed): Name={name}, Email={email}, Message={message}")
            
            return JsonResponse({
                "success": True,
                "message": "Thank you! Your message has been received. We'll get back to you within 24 hours. (Note: Email service temporarily unavailable)"
            })
        
    except Exception as e:
        print(f"Error processing contact form: {e}")
        return JsonResponse({
            "error": f"Server error: {str(e)}"
        }, status=500)


# ==========================
# API: Complaints
# ==========================
@require_admin_auth
def admin_dashboard(request):
    return render(request, 'admin-dashboard.html')


@require_admin_auth
def admin_complaints(request):
    complaints = Complaint.objects.all()
    return render(request, 'admin-complaints.html', {"complaints": complaints})

@require_admin_auth
def admin_history(request):
    return render(request, 'admin-history.html')

@require_admin_auth
def admin_user(request):
    return render(request, 'admin-user.html')

def _generate_tracking_id() -> str:
    # 6 digits tracking number, prefixed with TXN-
    return f"TXN-{get_random_string(length=6, allowed_chars='0123456789')}"


@require_http_methods(["GET"]) 
def list_complaints(request):
    # Check if user is authenticated
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    # Try Supabase first, fallback to Django ORM
    if supabase:
        try:
            # Filter complaints by user_id for regular users, show all for admins
            # Exclude resolved complaints from the main view (they go to transaction history)
            if user.is_staff or user.is_superuser:
                response = supabase.table('complaints').select('*').neq('status', 'Resolved').neq('status', 'Resolved by Agency').neq('status', 'Declined/Spam').order('created_at', desc=True).execute()
            else:
                # For regular users, show all complaints they submitted except resolved and declined ones
                response = supabase.table('complaints').select('*').eq('user_id', user.id).neq('status', 'Resolved').neq('status', 'Resolved by Agency').neq('status', 'Declined/Spam').order('created_at', desc=True).execute()
            
            complaints = response.data
            data = []
            for c in complaints:
                # Use centralized time formatting
                formatted_date = format_ph_datetime(c.get('created_at'))
                
                data.append({
                    "id": c.get('id'),
                    "tracking_id": c.get('tracking_id'),
                    "date": formatted_date,
                    "barangay": c.get('barangay'),
                    "type": c.get('complaint_type'),
                    "status": c.get('status'),
                    "description": c.get('description'),
                    "location": c.get('location'),
                    "image": c.get('image_base64'),
                    "resolution_image": c.get('resolution_image'),
                    "admin_update": c.get('admin_update'),
                })
            print(f"Found {len(data)} complaints in Supabase")  # Debug logging
            return JsonResponse({"results": data})
        except Exception as e:
            print(f"Supabase error: {e}, falling back to Django ORM")  # Debug logging
    
    # Fallback to Django ORM
    if user.is_staff or user.is_superuser:
        # Exclude resolved and declined complaints from the main view (they go to transaction history)
        complaints = Complaint.objects.exclude(status__in=['Resolved', 'Resolved by Agency', 'Declined/Spam'])
    else:
        # For regular users, show all complaints they submitted except resolved and declined ones
        complaints = Complaint.objects.filter(user=user).exclude(status__in=['Resolved', 'Resolved by Agency', 'Declined/Spam'])
    
    print(f"Found {complaints.count()} complaints in Django database")  # Debug logging
    data = [
        {
            "id": c.id,
            "tracking_id": c.tracking_id,
            "date": format_ph_datetime(c.created_at),
            "barangay": c.barangay,
            "type": c.complaint_type,
            "status": c.status,
            "description": c.description,
            "location": c.location,
            "image": c.image_base64 or None,
            "resolution_image": c.resolution_image or None,
            "admin_update": c.admin_update or None,
        }
        for c in complaints
    ]
    print(f"Returning {len(data)} complaints")  # Debug logging
    return JsonResponse({"results": data})


@require_http_methods(["GET"]) 
def list_complaints_history(request):
    """Get resolved complaints for transaction history"""
    # Check if user is authenticated
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    # Get admin's barangay if they are an admin
    admin_barangay = None
    if user.is_staff or user.is_superuser:
        try:
            # Get admin's barangay from their profile
            admin_profile = AdminProfile.objects.get(user=user)
            admin_barangay = admin_profile.barangay
            print(f"Admin barangay: {admin_barangay}")  # Debug logging
        except AdminProfile.DoesNotExist:
            print("Admin profile not found")  # Debug logging
            return JsonResponse({"error": "Admin profile not found"}, status=404)
    
    # Try Supabase first, fallback to Django ORM
    if supabase:
        try:
            # Filter resolved and declined complaints by user_id for regular users, by barangay for admins
            if user.is_staff or user.is_superuser:
                if admin_barangay:
                    response = supabase.table('complaints').select('*').in_('status', ['Resolved', 'Resolved by Agency', 'Declined/Spam']).eq('barangay', admin_barangay).order('updated_at', desc=True).execute()
                else:
                    response = supabase.table('complaints').select('*').in_('status', ['Resolved', 'Resolved by Agency', 'Declined/Spam']).order('updated_at', desc=True).execute()
            else:
                # For regular users, show only their resolved and declined complaints
                response = supabase.table('complaints').select('*').eq('user_id', user.id).in_('status', ['Resolved', 'Resolved by Agency', 'Declined/Spam']).order('updated_at', desc=True).execute()
            
            complaints = response.data
            data = []
            for c in complaints:
                # Use centralized time formatting
                formatted_date = format_ph_datetime(c.get('created_at'))
                
                data.append({
                    "id": c.get('id'),
                    "tracking_id": c.get('tracking_id'),
                    "date": formatted_date,
                    "user_name": c.get('user_full_name') or 'Unknown User',
                    "barangay": c.get('barangay'),
                    "type": c.get('complaint_type'),
                    "status": c.get('status'),
                    "description": c.get('description'),
                    "location": c.get('location'),
                    "image": c.get('image_base64'),
                    "resolution_image": c.get('resolution_image'),
                    "admin_update": c.get('admin_update'),
                    "forwarded_to_agency": c.get('forwarded_to_agency'),
                    "resolved_date": format_ph_datetime(c.get('updated_at')),  # Use updated_at as resolved_date
                })
            print(f"Found {len(data)} resolved complaints in Supabase")  # Debug logging
            return JsonResponse({"results": data})
        except Exception as e:
            print(f"Supabase error: {e}, falling back to Django ORM")  # Debug logging
    
    # Fallback to Django ORM
    if user.is_staff or user.is_superuser:
        if admin_barangay:
            complaints = Complaint.objects.filter(status__in=['Resolved', 'Resolved by Agency', 'Declined/Spam'], barangay=admin_barangay).order_by('-updated_at')
        else:
            complaints = Complaint.objects.filter(status__in=['Resolved', 'Resolved by Agency', 'Declined/Spam']).order_by('-updated_at')
    else:
        # For regular users, show only their resolved and declined complaints
        complaints = Complaint.objects.filter(user=user, status__in=['Resolved', 'Resolved by Agency', 'Declined/Spam']).order_by('-updated_at')
    
    print(f"Found {complaints.count()} resolved complaints in Django database")  # Debug logging
    data = [
        {
            "id": c.id,
            "tracking_id": c.tracking_id,
            "date": format_ph_datetime(c.created_at),
            "user_name": c.user_full_name or 'Unknown User',
            "barangay": c.barangay,
            "type": c.complaint_type,
            "status": c.status,
            "description": c.description,
            "location": c.location,
            "image": c.image_base64 or None,
            "resolution_image": c.resolution_image or None,
            "admin_update": c.admin_update or None,
            "forwarded_to_agency": c.forwarded_to_agency or None,
            "resolved_date": format_ph_datetime(c.updated_at),  # Use updated_at as resolved_date
        }
        for c in complaints
    ]
    print(f"Returning {len(data)} resolved complaints")  # Debug logging
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"]) 
def create_complaint(request):
    # Expect JSON body from the front-end
    try:
        payload = json.loads(request.body.decode("utf-8"))
        print(f"Received payload: {payload}")  # Debug logging
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")  # Debug logging
        return HttpResponseBadRequest("Invalid JSON body")

    required_fields = ["barangay", "complaint_type", "description", "location"]
    missing = [f for f in required_fields if not payload.get(f)]
    if missing:
        print(f"Missing fields: {missing}")  # Debug logging
        return HttpResponseBadRequest(f"Missing fields: {', '.join(missing)}")

    # Get user information from session or request
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"error": "User must be authenticated"}, status=401)
    
    # Get user profile for full name and barangay
    try:
        user_profile = user.user_profile
        user_full_name = user_profile.full_name
        user_barangay = user_profile.barangay
    except:
        return JsonResponse({"error": "User profile not found"}, status=400)

    # Validate that the selected barangay has a registered admin
    # Note: Users can now submit complaints to any barangay that has a registered admin
    # The frontend will only show barangays with registered admins

    # Validate image data if provided
    image_data = payload.get("image")
    if image_data:
        # Check if it's a valid base64 data URL
        if not isinstance(image_data, str) or not image_data.startswith('data:image/'):
            print("Invalid image data format")  # Debug logging
            return HttpResponseBadRequest("Invalid image data format")
        
        # Check image data size (max 5MB)
        import base64
        try:
            # Remove data URL prefix to get base64 data
            if ',' in image_data:
                base64_data = image_data.split(',')[1]
            else:
                base64_data = image_data
            
            # Calculate size in bytes
            image_size = len(base64_data) * 3 // 4  # Approximate size
            if image_size > 5 * 1024 * 1024:  # 5MB
                print(f"Image too large: {image_size} bytes")  # Debug logging
                return HttpResponseBadRequest("Image file is too large (max 5MB)")
        except Exception as e:
            print(f"Error processing image data: {e}")  # Debug logging
            return HttpResponseBadRequest("Invalid image data")

    # Ensure unique tracking id
    tracking_id = _generate_tracking_id()
    while Complaint.objects.filter(tracking_id=tracking_id).exists():
        tracking_id = _generate_tracking_id()

    # Try to save to Supabase first
    if supabase:
        try:
            complaint_data = {
                "tracking_id": tracking_id,
                "user_id": user.id,
                "user_full_name": user_full_name,
                "user_barangay": user_barangay,  # Add user's barangay
                "barangay": payload["barangay"],
                "complaint_type": payload["complaint_type"],
                "description": payload["description"],
                "location": payload["location"],
                "image_base64": image_data,
                "status": "Pending"
            }
            
            response = supabase.table('complaints').insert(complaint_data).execute()
            created_complaint = response.data[0] if response.data else None
            
            if created_complaint:
                print(f"Complaint created successfully in Supabase: {tracking_id}")  # Debug logging
                
                return JsonResponse(
                    {
                        "id": created_complaint.get('id'),
                        "tracking_id": created_complaint.get('tracking_id'),
                        "status": created_complaint.get('status'),
                        "date": format_ph_datetime(timezone.now()),
                    },
                    status=201,
                )
        except Exception as e:
            print(f"Supabase error: {e}, falling back to Django ORM")  # Debug logging

    # Fallback to Django ORM
    try:
        complaint = Complaint.objects.create(
            tracking_id=tracking_id,
            user=user,
            user_full_name=user_full_name,
            user_barangay=user_barangay,  # Add user's barangay
            barangay=payload["barangay"],
            complaint_type=payload["complaint_type"],
            description=payload["description"],
            location=payload["location"],
            image_base64=image_data,
        )
        print(f"Complaint created successfully in Django: {complaint.tracking_id}")  # Debug logging
        
        return JsonResponse(
            {
                "id": complaint.id,
                "tracking_id": complaint.tracking_id,
                "status": complaint.status,
                "date": format_ph_datetime(complaint.created_at),
            },
            status=201,
        )
    except Exception as e:
        print(f"Error creating complaint: {e}")  # Debug logging
        return HttpResponseBadRequest(f"Error creating complaint: {str(e)}")


@require_http_methods(["GET"]) 
def complaint_detail(request, tracking_id: str):
    try:
        c = Complaint.objects.get(tracking_id=tracking_id)
    except Complaint.DoesNotExist:
        raise Http404("Complaint not found")

    return JsonResponse(
        {
            "id": c.id,
            "tracking_id": c.tracking_id,
            "date": format_ph_datetime(c.created_at),
            "barangay": c.barangay,
            "type": c.complaint_type,
            "status": c.status,
            "description": c.description,
            "location": c.location,
            "image": c.image_base64 or None,
        }
    )


@require_http_methods(["GET"])
def fetch_complaints(request):
    complaints = Complaint.objects.all().values(
        "tracking_id", "created_at", "barangay", "complaint_type", "status", "description"
    )
    return JsonResponse(list(complaints), safe=False)


@require_http_methods(["GET"]) 
def list_transactions(request):
    """API endpoint to fetch complaints for admin view (renamed from transactions)"""
    # Check if user is authenticated as admin
    user = request.user
    if not user.is_authenticated or not (user.is_staff or user.is_superuser):
        return JsonResponse({"error": "Admin authentication required"}, status=401)
    
    # Get admin's barangay for filtering
    try:
        admin_profile = user.admin_profile
        admin_barangay = admin_profile.barangay
    except:
        return JsonResponse({"error": "Admin profile not found"}, status=400)
    
    # Check if this is a dashboard request (include resolved complaints)
    include_resolved = request.GET.get('include_resolved', 'false').lower() == 'true'
    
    # Try Supabase first, fallback to Django ORM
    if supabase:
        try:
            # Filter complaints by admin's barangay
            if include_resolved:
                # Include all complaints (for dashboard statistics)
                response = supabase.table('complaints').select('*').eq('barangay', admin_barangay).order('created_at', desc=True).execute()
            else:
                # Exclude resolved and declined complaints (for active complaints view)
                response = supabase.table('complaints').select('*').eq('barangay', admin_barangay).neq('status', 'Resolved').neq('status', 'Resolved by Agency').neq('status', 'Declined/Spam').order('created_at', desc=True).execute()
            complaints = response.data
            data = []
            for c in complaints:
                # Use centralized time formatting
                formatted_date = format_ph_datetime(c.get('created_at'))
                
                data.append({
                    "id": c.get('tracking_id'),
                    "date": formatted_date,
                    "user_name": c.get('user_full_name', 'N/A'),  # Use user_full_name field
                    "user": c.get('user_full_name', 'N/A'),  # Keep for backward compatibility
                    "user_barangay": c.get('user_barangay', 'N/A'),  # Add user's barangay
                    "user_profile_picture": c.get('user_profile_picture'),  # Add user's profile picture
                    "type": c.get('complaint_type'),
                    "status": c.get('status'),
                    "description": c.get('description'),
                    "barangay": c.get('barangay'),
                    "location": c.get('location'),
                    "image": c.get('image_base64'),
                    "resolution_image": c.get('resolution_image'),
                    "admin_update": c.get('admin_update'),
                    "forwarded_to_agency": c.get('forwarded_to_agency'),
                    "forward_reason": c.get('forward_reason'),
                    "forward_date": c.get('forward_date'),
                })
            print(f"Found {len(data)} complaints in Supabase for barangay {admin_barangay}")  # Debug logging
            return JsonResponse({"results": data})
        except Exception as e:
            print(f"Supabase error: {e}, falling back to Django ORM")  # Debug logging
    
    # Fallback to Django ORM
    if include_resolved:
        # Include all complaints (for dashboard statistics)
        complaints = Complaint.objects.filter(barangay=admin_barangay)
        print(f"Found {complaints.count()} complaints in Django database for barangay {admin_barangay} (including resolved and declined)")  # Debug logging
    else:
        # Exclude resolved and declined complaints (for active complaints view)
        complaints = Complaint.objects.filter(barangay=admin_barangay).exclude(status__in=['Resolved', 'Resolved by Agency', 'Declined/Spam'])
        print(f"Found {complaints.count()} complaints in Django database for barangay {admin_barangay} (excluding resolved and declined)")  # Debug logging
    data = [
        {
            "id": c.tracking_id,
            "date": format_ph_datetime(c.created_at),
            "user_name": c.user_full_name or 'N/A',  # Use user_full_name field
            "user": c.user_full_name or 'N/A',  # Keep for backward compatibility
            "user_barangay": c.user_barangay or 'N/A',  # Add user's barangay
            "user_profile_picture": c.user.user_profile.profile_picture if hasattr(c.user, 'user_profile') and c.user.user_profile.profile_picture else None,  # Add user's profile picture
            "type": c.complaint_type,
            "status": c.status,
            "description": c.description,
            "barangay": c.barangay,
            "location": c.location,
            "image": c.image_base64 or None,
            "resolution_image": c.resolution_image or None,
            "admin_update": c.admin_update or None,
            "forwarded_to_agency": c.forwarded_to_agency or None,
            "forward_reason": c.forward_reason or None,
            "forward_date": c.forward_date.isoformat() if c.forward_date else None,
        }
        for c in complaints
    ]
    print(f"Returning {len(data)} complaints")  # Debug logging
    return JsonResponse({"results": data})


@require_http_methods(["GET"]) 
def transaction_detail(request, tracking_id: str):
    """Get specific complaint details (renamed from transaction)"""
    # Check if user is authenticated as admin
    user = request.user
    if not user.is_authenticated or not (user.is_staff or user.is_superuser):
        return JsonResponse({"error": "Admin authentication required"}, status=401)
    
    # Get admin's barangay for filtering
    try:
        admin_profile = user.admin_profile
        admin_barangay = admin_profile.barangay
    except:
        return JsonResponse({"error": "Admin profile not found"}, status=400)
    
    try:
        # Only allow access to complaints from admin's barangay
        complaint = Complaint.objects.get(tracking_id=tracking_id, barangay=admin_barangay)
    except Complaint.DoesNotExist:
        raise Http404("Complaint not found")

    return JsonResponse(
        {
            "id": complaint.tracking_id,
            "date": format_ph_datetime(complaint.created_at),
            "user": complaint.user_full_name or 'N/A',  # Use user_full_name field
            "type": complaint.complaint_type,
            "status": complaint.status,
            "description": complaint.description,
            "barangay": complaint.barangay,
            "location": complaint.location,
            "image": complaint.image_base64 or None,
        }
    )


@csrf_exempt
@require_http_methods(["PATCH"]) 
def update_transaction_status(request, tracking_id: str):
    """Update complaint status (renamed from transaction)"""
    # Check if user is authenticated as admin
    user = request.user
    if not user.is_authenticated or not (user.is_staff or user.is_superuser):
        return JsonResponse({"error": "Admin authentication required"}, status=401)
    
    # Get admin's barangay for filtering
    try:
        admin_profile = user.admin_profile
        admin_barangay = admin_profile.barangay
    except:
        return JsonResponse({"error": "Admin profile not found"}, status=400)
    
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    new_status = payload.get("status")
    if not new_status:
        return HttpResponseBadRequest("Status is required")

    # Get admin update if provided
    admin_update = payload.get("admin_update", "").strip()
    
    # Get admin information for personalized messages
    admin_name = request.session.get('admin_name', 'Admin')
    admin_barangay_name = admin_profile.barangay
    
    # Get forwarding details if provided
    forwarded_to_agency = payload.get("forwarded_to_agency", "").strip()
    forward_reason = payload.get("forward_reason", "").strip()
    
    # If status is being set to "In Progress", require admin update
    if new_status == "In Progress" and not admin_update:
        return JsonResponse({"error": "Admin update is required when setting status to In Progress"}, status=400)
    
    # Format admin update with admin name and barangay
    if admin_update:
        formatted_admin_update = f"Hello, this is {admin_name} from Barangay {admin_barangay_name}. {admin_update}"
    else:
        formatted_admin_update = f"Hello, this is {admin_name} from Barangay {admin_barangay_name}. Your complaint status has been updated."

    # If status is being set to "Forwarded to Agency", require agency and reason
    if new_status == "Forwarded to Agency":
        if not forwarded_to_agency:
            return JsonResponse({"error": "Agency selection is required when forwarding complaint"}, status=400)
        if not forward_reason:
            return JsonResponse({"error": "Forward reason is required when forwarding complaint"}, status=400)

    # If status is being set to "Resolved" or "Resolved by Agency", require resolution image
    resolution_image = payload.get("resolution_image")
    if (new_status == "Resolved" or new_status == "Resolved by Agency") and not resolution_image:
        return JsonResponse({"error": "Resolution image is required when setting status to Resolved or Resolved by Agency"}, status=400)

    # Try Supabase first, fallback to Django ORM
    if supabase:
        try:
            # Get current complaint data from Supabase
            response = supabase.table('complaints').select('*').eq('tracking_id', tracking_id).eq('barangay', admin_barangay).execute()
            
            if not response.data:
                raise Http404("Complaint not found")
            
            complaint_data = response.data[0]
            old_status = complaint_data.get('status')
            user_email = complaint_data.get('user_email')  # Assuming user email is stored in complaints table
            
            # Update complaint in Supabase
            update_data = {'status': new_status}
            if admin_update:
                update_data['admin_update'] = formatted_admin_update
            if resolution_image:
                update_data['resolution_image'] = resolution_image
            if forwarded_to_agency:
                update_data['forwarded_to_agency'] = forwarded_to_agency
            if forward_reason:
                update_data['forward_reason'] = forward_reason
            if new_status == "Forwarded to Agency":
                update_data['forward_date'] = timezone.now().isoformat()
            
            update_response = supabase.table('complaints').update(update_data).eq('tracking_id', tracking_id).eq('barangay', admin_barangay).execute()
            
            if not update_response.data:
                return JsonResponse({"error": "Failed to update complaint"}, status=500)
            
            # Send email notification if status changed
            if old_status != new_status and user_email:
                from .email_utils import send_status_change_notification
                try:
                    send_status_change_notification(
                        user_email=user_email,
                        tracking_id=tracking_id,
                        complaint_type=complaint_data.get('complaint_type', 'Unknown'),
                        old_status=old_status,
                        new_status=new_status,
                        admin_barangay=admin_barangay
                    )
                    print(f"📧 Notification sent to {user_email} for complaint {tracking_id}")
                except Exception as e:
                    print(f"⚠️ Failed to send notification email: {e}")
            
            return JsonResponse({"ok": True, "status": new_status})
            
        except Exception as e:
            print(f"Supabase error: {e}, falling back to Django ORM")
    
    # Fallback to Django ORM
    try:
        # Only allow updating complaints from admin's barangay
        complaint = Complaint.objects.get(tracking_id=tracking_id, barangay=admin_barangay)
        old_status = complaint.status  # Store old status for notification
        complaint.status = new_status
        
        # Save admin update if provided
        if admin_update:
            complaint.admin_update = formatted_admin_update
        
        # Save resolution image if provided
        if resolution_image:
            complaint.resolution_image = resolution_image
            
        # Save forwarding details if provided
        if forwarded_to_agency:
            complaint.forwarded_to_agency = forwarded_to_agency
        if forward_reason:
            complaint.forward_reason = forward_reason
        if new_status == "Forwarded to Agency":
            complaint.forward_date = timezone.now()
            
        complaint.save()
        
        # Log admin activity for audit trail with personalized message
        admin_display_name = request.session.get('admin_name', 'Admin')
        
        # Create personalized status change description
        status_descriptions = {
            'Reported': f"Hello! This is {admin_display_name} from barangay {admin_barangay}. Your complaint has been received and is now in review for processing.",
            'In Progress': f"Hello! This is {admin_display_name} from barangay {admin_barangay}. We are now working on your complaint. {admin_update if admin_update else 'Our team is actively addressing this issue.'}",
            'Forwarded to Agency': f"Hello! This is {admin_display_name} from barangay {admin_barangay}. Your complaint has been forwarded to {forwarded_to_agency} for further investigation. Reason: {forward_reason}",
            'Resolved by Agency': f"Hello! This is {admin_display_name} from barangay {admin_barangay}. Your complaint has been successfully resolved by {forwarded_to_agency}. Thank you for reporting this issue.",
            'Resolved': f"Hello! This is {admin_display_name} from barangay {admin_barangay}. Your complaint has been successfully resolved. Thank you for reporting this issue.",
            'Declined/Spam': f"Hello! This is {admin_display_name} from barangay {admin_barangay}. After review, this complaint has been declined. If you believe this is an error, please contact our office directly."
        }
        
        personalized_description = status_descriptions.get(new_status, f"Hello! This is {admin_display_name} from barangay {admin_barangay}. Status changed from '{old_status}' to '{new_status}'.")
        
        # Log admin activity for audit trail
        try:
            # Use different action type for forwarding
            action_type = AdminActivityLog.ActionType.COMPLAINT_FORWARD if new_status == "Forwarded to Agency" else AdminActivityLog.ActionType.STATUS_CHANGE
            
            AdminActivityLog.objects.create(
                complaint=complaint,
                admin_user=user,
                admin_name=admin_display_name,
                admin_barangay=admin_barangay,
                action_type=action_type,
                description=personalized_description,
                old_value=old_status,
                new_value=new_status
            )
            print(f"📋 Audit log created: {admin_display_name} changed status of {tracking_id} from {old_status} to {new_status}")
        except Exception as e:
            # Log the error but don't crash the status update
            print(f"Warning: Could not log admin activity: {e}")
        print(f"📋 Audit log created: {admin_display_name} changed status of {tracking_id} from {old_status} to {new_status}")
        
        # Send email notification to user if status changed
        if old_status != new_status:
            # Get user email from complaint
            user_email = None
            
            # Try to get user email from UserProfile if complaint has user
            if complaint.user:
                try:
                    from .models import UserProfile
                    user_profile = UserProfile.objects.get(user=complaint.user)
                    user_email = user_profile.email
                except UserProfile.DoesNotExist:
                    print(f"UserProfile not found for user {complaint.user.id}")
            
            # If we have user email, send notification
            if user_email:
                from .email_utils import send_status_change_notification
                try:
                    send_status_change_notification(
                        user_email=user_email,
                        tracking_id=complaint.tracking_id,
                        complaint_type=complaint.complaint_type,
                        old_status=old_status,
                        new_status=new_status,
                        admin_barangay=admin_barangay
                    )
                    print(f"📧 Notification sent to {user_email} for complaint {tracking_id}")
                except Exception as e:
                    print(f"⚠️ Failed to send notification email: {e}")
            else:
                print(f"⚠️ No user email found for complaint {tracking_id}")
        
        return JsonResponse({"ok": True, "status": complaint.status})
    except Complaint.DoesNotExist:
        raise Http404("Complaint not found")


@csrf_exempt
@require_http_methods(["POST"])
def admin_recovery_info(request):
    """Get admin recovery information (for admin use only)"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    email = (payload.get("email") or "").strip().lower()

    if not email:
        return JsonResponse({"error": "Email is required"}, status=400)

    # Check Supabase admin_profiles table
    if supabase:
        try:
            response = supabase.table('admin_profiles').select('*').eq('email', email).execute()
            if response.data:
                admin_data = response.data[0]
                return JsonResponse({
                    "success": True,
                    "admin_info": {
                        "email": admin_data.get('email'),
                        "barangay": admin_data.get('barangay'),
                        "password": admin_data.get('password'),
                        "admin_access_key": admin_data.get('admin_access_key'),
                        "created_at": admin_data.get('created_at')
                    }
                })
            else:
                return JsonResponse({"error": "Admin not found"}, status=404)
        except Exception as e:
            print(f"Supabase recovery check error: {e}")
            return JsonResponse({"error": "Database error"}, status=500)
    else:
        return JsonResponse({"error": "Supabase not available"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def get_admin_data(request):
    """Get admin data from database for dashboard display"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    email = (payload.get("email") or "").strip().lower()

    if not email:
        return JsonResponse({"error": "Email is required"}, status=400)

    # Try Supabase first, fallback to Django ORM
    if supabase:
        try:
            response = supabase.table('admin_profiles').select('email, barangay, username').eq('email', email).execute()
            if response.data:
                admin_data = response.data[0]
                return JsonResponse({
                    "success": True,
                    "admin_data": {
                        "email": admin_data.get('email'),
                        "barangay": admin_data.get('barangay'),
                        "username": admin_data.get('username')
                    }
                })
            else:
                print(f"Admin not found in Supabase: {email}, falling back to Django ORM")
        except Exception as e:
            print(f"Supabase admin data check error: {e}, falling back to Django ORM")

    # Fallback to Django ORM
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Find user by email
        user = User.objects.filter(email=email).first()
        if user and hasattr(user, 'admin_profile'):
            admin_profile = user.admin_profile
            return JsonResponse({
                "success": True,
                "admin_data": {
                    "email": user.email,
                    "barangay": admin_profile.barangay,
                    "username": user.username
                }
            })
        else:
            return JsonResponse({"error": "Admin not found"}, status=404)
    except Exception as e:
        print(f"Django ORM admin data check error: {e}")
        return JsonResponse({"error": "Database error"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def save_profile_picture(request):
    """Save user profile picture to database"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    email = (payload.get("email") or "").strip().lower()
    profile_picture = payload.get("profile_picture", "")

    if not email:
        return JsonResponse({"error": "Email is required"}, status=400)

    if not profile_picture:
        return JsonResponse({"error": "Profile picture data is required"}, status=400)

    # Try Supabase first, fallback to Django ORM
    if supabase:
        try:
            # Check if user exists in user_profiles table
            response = supabase.table('user_profiles').select('email').eq('email', email).execute()
            if response.data:
                # Update existing user profile
                update_response = supabase.table('user_profiles').update({
                    'profile_picture': profile_picture,
                    'updated_at': timezone.now().isoformat()
                }).eq('email', email).execute()
                
                if update_response.data:
                    return JsonResponse({
                        "success": True,
                        "message": "Profile picture saved successfully"
                    })
                else:
                    return JsonResponse({"error": "Failed to update profile picture"}, status=500)
            else:
                return JsonResponse({"error": "User not found"}, status=404)
        except Exception as e:
            print(f"Supabase profile picture save error: {e}, falling back to Django ORM")

    # Fallback to Django ORM
    try:
        user_profile = UserProfile.objects.filter(email__iexact=email).first()
        if user_profile:
            user_profile.profile_picture = profile_picture
            user_profile.save()
            return JsonResponse({
                "success": True,
                "message": "Profile picture saved successfully"
            })
        else:
            # Try to find a User with this email and create a UserProfile
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.filter(email__iexact=email).first()
            
            if user:
                # Create a UserProfile for this user
                user_profile = UserProfile.objects.create(
                    user=user,
                    full_name=user.get_full_name() or user.username,
                    email=email,
                    barangay="Unknown",  # Will be updated when user completes profile
                    profile_picture=profile_picture
                )
                return JsonResponse({
                    "success": True,
                    "message": "Profile picture saved successfully (profile created)"
                })
            else:
                # No user found, return error
                return JsonResponse({
                    "error": "User not found in database",
                    "details": "Please ensure you are logged in with a valid account."
                }, status=404)
    except Exception as e:
        print(f"Django ORM profile picture save error: {e}")
        return JsonResponse({
            "error": "Database error", 
            "details": str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def get_profile_picture(request):
    """Get user profile picture from database"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    email = (payload.get("email") or "").strip().lower()

    if not email:
        return JsonResponse({"error": "Email is required"}, status=400)

    # Try Supabase first, fallback to Django ORM
    if supabase:
        try:
            response = supabase.table('user_profiles').select('profile_picture').eq('email', email).execute()
            if response.data and response.data[0].get('profile_picture'):
                return JsonResponse({
                    "success": True,
                    "profile_picture": response.data[0]['profile_picture']
                })
            else:
                return JsonResponse({
                    "success": True,
                    "profile_picture": None
                })
        except Exception as e:
            print(f"Supabase profile picture get error: {e}, falling back to Django ORM")

    # Fallback to Django ORM
    try:
        user_profile = UserProfile.objects.filter(email__iexact=email).first()
        if user_profile and user_profile.profile_picture:
            return JsonResponse({
                "success": True,
                "profile_picture": user_profile.profile_picture
            })
        else:
            return JsonResponse({
                "success": True,
                "profile_picture": None
            })
    except Exception as e:
        print(f"Django ORM profile picture get error: {e}")
        return JsonResponse({"error": "Database error"}, status=500)


@require_http_methods(["GET"]) 
def check_user_auth(request):
    """API endpoint to check if user is authenticated and get user info"""
    user = request.user
    
    if not user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    try:
        # Try to get user profile
        user_profile = user.user_profile
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": user_profile.full_name,
            "role": "user",
            "barangay": user_profile.barangay,
            "profile_picture": user_profile.profile_picture
        }
    except:
        # User exists but no profile, check if admin
        try:
            admin_profile = user.admin_profile
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": f"Admin - {admin_profile.barangay}",
                "role": "admin",
                "barangay": admin_profile.barangay
            }
        except:
            # Fallback for users without profiles
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": user.get_full_name() or user.username,
                "role": "user" if not user.is_staff else "admin"
            }
    
    return JsonResponse(user_data)


@require_http_methods(["GET"]) 
def list_users_for_admin(request):
    """API endpoint to fetch users filtered by admin's barangay"""
    # Check if user is authenticated as admin
    user = request.user
    if not user.is_authenticated or not (user.is_staff or user.is_superuser):
        return JsonResponse({"error": "Admin authentication required"}, status=401)
    
    # Get admin's barangay for filtering
    try:
        admin_profile = user.admin_profile
        admin_barangay = admin_profile.barangay
    except:
        return JsonResponse({"error": "Admin profile not found"}, status=400)
    
    # Try Supabase first, fallback to Django ORM
    if supabase:
        try:
            # Get users from the same barangay as admin
            response = supabase.table('user_profiles').select('*').eq('barangay', admin_barangay).order('created_at', desc=True).execute()
            users = response.data
            data = []
            
            for user_data in users:
                data.append({
                    "id": user_data.get('id'),
                    "email": user_data.get('email'),
                    "full_name": user_data.get('full_name'),
                    "barangay": user_data.get('barangay'),
                    "joined_date": user_data.get('created_at', '').split('T')[0] if user_data.get('created_at') else 'N/A',
                    "status": "Active"  # Default status for Supabase users
                })
            
            print(f"Found {len(data)} users in Supabase for barangay {admin_barangay}")
            return JsonResponse({"users": data})
        except Exception as e:
            print(f"Supabase error: {e}, falling back to Django ORM")
    
    # Fallback to Django ORM
    try:
        # Get all UserProfile objects for the admin's barangay
        user_profiles = UserProfile.objects.filter(barangay=admin_barangay).order_by('-created_at')
        data = []
        
        for profile in user_profiles:
            data.append({
                "id": profile.id,
                "email": profile.email,
                "full_name": profile.full_name,
                "barangay": profile.barangay,
                "joined_date": profile.created_at.strftime('%Y-%m-%d') if profile.created_at else 'N/A',
                "status": "Active"  # Default status for Django users
            })
        
        print(f"Found {len(data)} users in Django database for barangay {admin_barangay}")
        return JsonResponse({"users": data})
    except Exception as e:
        print(f"Django ORM error: {e}")
        return JsonResponse({"error": "Database error"}, status=500)


@require_http_methods(["DELETE"]) 
def delete_user_for_admin(request, user_id):
    """API endpoint to delete a user (admin only)"""
    # Check if user is authenticated as admin
    user = request.user
    if not user.is_authenticated or not (user.is_staff or user.is_superuser):
        return JsonResponse({"error": "Admin authentication required"}, status=401)
    
    # Get admin's barangay for filtering
    try:
        admin_profile = user.admin_profile
        admin_barangay = admin_profile.barangay
    except:
        return JsonResponse({"error": "Admin profile not found"}, status=400)
    
    # Try Supabase first, fallback to Django ORM
    if supabase:
        try:
            # Check if user exists and belongs to admin's barangay
            response = supabase.table('user_profiles').select('*').eq('id', user_id).eq('barangay', admin_barangay).execute()
            if response.data:
                # Delete the user
                delete_response = supabase.table('user_profiles').delete().eq('id', user_id).execute()
                if delete_response.data:
                    print(f"Deleted user {user_id} from Supabase")
                    return JsonResponse({"success": True, "message": "User deleted successfully"})
                else:
                    return JsonResponse({"error": "Failed to delete user"}, status=500)
            else:
                return JsonResponse({"error": "User not found or not in your barangay"}, status=404)
        except Exception as e:
            print(f"Supabase delete error: {e}, falling back to Django ORM")
    
    # Fallback to Django ORM
    try:
        # Check if user exists and belongs to admin's barangay
        user_profile = UserProfile.objects.filter(id=user_id, barangay=admin_barangay).first()
        if user_profile:
            user_profile.delete()
            print(f"Deleted user {user_id} from Django database")
            return JsonResponse({"success": True, "message": "User deleted successfully"})
        else:
            return JsonResponse({"error": "User not found or not in your barangay"}, status=404)
    except Exception as e:
        print(f"Django ORM delete error: {e}")
        return JsonResponse({"error": "Database error"}, status=500)


@require_http_methods(["GET"]) 
def get_registered_barangays(request):
    """API endpoint to get all barangays that have registered admins"""
    # Try Supabase first, fallback to Django ORM
    if supabase:
        try:
            # Get all unique barangays from admin_profiles table
            response = supabase.table('admin_profiles').select('barangay').execute()
            barangays = []
            
            # Extract unique barangays, excluding SYSTEM_SUPERADMIN
            seen_barangays = set()
            for admin_data in response.data:
                barangay = admin_data.get('barangay')
                if barangay and barangay not in seen_barangays and barangay != 'SYSTEM_SUPERADMIN':
                    barangays.append(barangay)
                    seen_barangays.add(barangay)
            
            print(f"Found {len(barangays)} barangays with admins in Supabase (excluding superadmin)")
            
            # If Supabase has data, return it
            if barangays:
                return JsonResponse({
                    "success": True,
                    "barangays": sorted(barangays)  # Sort alphabetically
                })
            else:
                print("No barangays found in Supabase, falling back to Django ORM")
        except Exception as e:
            print(f"Supabase error: {e}, falling back to Django ORM")
    
    # Fallback to Django ORM
    try:
        # Get all unique barangays from AdminProfile model, excluding SYSTEM_SUPERADMIN
        barangays = list(AdminProfile.objects.exclude(barangay='SYSTEM_SUPERADMIN').values_list('barangay', flat=True).distinct())
        
        print(f"Found {len(barangays)} barangays with admins in Django database (excluding superadmin)")
        return JsonResponse({
            "success": True,
            "barangays": sorted(barangays)  # Sort alphabetically
        })
    except Exception as e:
        print(f"Django ORM error: {e}")
        return JsonResponse({"error": "Database error"}, status=500)


@require_http_methods(["GET"]) 
def admin_chat(request):
    """Render admin chat page"""
    return render(request, 'admin-chat.html')

def superadmin_dashboard(request):
    """Render superadmin dashboard page - only accessible for the specific superadmin email"""
    # Check if user is authenticated and is the specific superadmin
    if not request.session.get('admin_authenticated', False):
        # Redirect to login if not authenticated
        return redirect('/?show_login=true')
    
    # Check if this is the superadmin email
    admin_email = request.session.get('admin_email', '')
    if admin_email != 'complaintmanagementsystem5@gmail.com':
        # Regular admins shouldn't access superadmin page, redirect to admin dashboard
        return redirect('/admin-dashboard.html/')
    
    return render(request, 'superadmin.html')


# ==========================
# API: Chat Functionality
# ==========================

@csrf_exempt
@require_http_methods(["POST"]) 
def send_chat_message(request):
    """Send a chat message from admin to user"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    # Check if user is authenticated as admin
    user = request.user
    if not user.is_authenticated or not (user.is_staff or user.is_superuser):
        return JsonResponse({"error": "Admin authentication required"}, status=401)

    complaint_id = payload.get("complaintId")
    message_content = payload.get("message", "").strip()

    if not complaint_id or not message_content:
        return JsonResponse({"error": "Complaint ID and message are required"}, status=400)

    try:
        # Get the complaint
        complaint = Complaint.objects.get(tracking_id=complaint_id)
        
        # Get or create chat conversation
        conversation, created = ChatConversation.objects.get_or_create(
            complaint=complaint,
            admin=user,
            user=complaint.user,
            defaults={'created_at': timezone.now()}
        )

        # Get admin display name from session
        admin_display_name = request.session.get('admin_name', 'Admin')
        
        # Create the message with admin name
        chat_message = ChatMessage.objects.create(
            conversation=conversation,
            sender=user,
            content=message_content,
            is_admin_message=True,
            admin_name=admin_display_name
        )

        # Log admin activity for audit trail
        try:
            admin_profile = user.admin_profile
            admin_barangay = admin_profile.barangay
        except:
            admin_barangay = "Unknown"
            
        # Log admin activity for audit trail
        try:
            AdminActivityLog.objects.create(
                complaint=complaint,
                admin_user=user,
                admin_name=admin_display_name,
                admin_barangay=admin_barangay,
                action_type=AdminActivityLog.ActionType.CHAT_MESSAGE,
                description=f"Sent chat message: {message_content[:50]}{'...' if len(message_content) > 50 else ''}",
                new_value=message_content
            )
            print(f"📋 Audit log created: {admin_display_name} sent chat message to {tracking_id}")
        except Exception as e:
            # Log the error but don't crash the chat message
            print(f"Warning: Could not log chat activity: {e}")

        # Update conversation timestamp to move it to top of list
        conversation.update_timestamp()

        return JsonResponse({
            "success": True,
            "message": "Message sent successfully",
            "message_id": chat_message.id,
            "timestamp": chat_message.created_at.isoformat()
        })

    except Complaint.DoesNotExist:
        return JsonResponse({"error": "Complaint not found"}, status=404)
    except Exception as e:
        print(f"Error sending chat message: {e}")
        return JsonResponse({"error": "Failed to send message"}, status=500)


@require_http_methods(["GET"]) 
def get_chat_messages(request, complaint_id):
    """Get chat messages for a specific complaint"""
    # Check if user is authenticated as admin
    user = request.user
    if not user.is_authenticated or not (user.is_staff or user.is_superuser):
        return JsonResponse({"error": "Admin authentication required"}, status=401)

    try:
        # Get the complaint
        complaint = Complaint.objects.get(tracking_id=complaint_id)
        
        # Get the conversation
        try:
            conversation = ChatConversation.objects.get(
                complaint=complaint,
                admin=user,
                user=complaint.user
            )
        except ChatConversation.DoesNotExist:
            # Return empty messages if no conversation exists yet
            return JsonResponse({
                "success": True,
                "messages": [],
                "conversation_id": None
            })

        # Get all messages for this conversation
        messages = conversation.messages.all()
        
        # Mark all user messages as read when admin opens the chat
        unread_messages = conversation.messages.filter(is_admin_message=False, is_read=False)
        unread_messages.update(is_read=True)
        
        message_data = []
        for msg in messages:
            # Determine sender name based on message type
            if msg.is_admin_message:
                # For admin messages, use the stored admin name or fallback to barangay admin
                if msg.admin_name:
                    sender_name = msg.admin_name
                else:
                    try:
                        admin_profile = AdminProfile.objects.get(user=msg.sender)
                        sender_name = f"{admin_profile.barangay} Admin"
                    except AdminProfile.DoesNotExist:
                        sender_name = "Admin"
            else:
                # For user messages, use their full name or email
                sender_name = msg.sender.user_profile.full_name if hasattr(msg.sender, 'user_profile') else msg.sender.email
            
            message_data.append({
                "id": msg.id,
                "content": msg.content,
                "sender": msg.sender.email,
                "sender_name": sender_name,
                "is_admin_message": msg.is_admin_message,
                "timestamp": msg.created_at.isoformat(),
                "formatted_time": msg.created_at.strftime("%Y-%m-%d %H:%M")
            })

        return JsonResponse({
            "success": True,
            "messages": message_data,
            "conversation_id": conversation.id
        })

    except Complaint.DoesNotExist:
        return JsonResponse({"error": "Complaint not found"}, status=404)
    except Exception as e:
        print(f"Error getting chat messages: {e}")
        return JsonResponse({"error": "Failed to get messages"}, status=500)


@require_http_methods(["GET"]) 
def get_admin_chat_list(request):
    """Get list of all chat conversations for the admin"""
    # Check if user is authenticated as admin
    user = request.user
    if not user.is_authenticated or not (user.is_staff or user.is_superuser):
        return JsonResponse({"error": "Admin authentication required"}, status=401)

    try:
        # Get all conversations for this admin
        conversations = ChatConversation.objects.filter(admin=user).select_related(
            'complaint', 'user', 'user__user_profile'
        ).prefetch_related('messages')
        
        chat_list = []
        for conv in conversations:
            # Get the last message
            last_message = conv.messages.last()
            
            # Get user info
            user_name = conv.user.user_profile.full_name if hasattr(conv.user, 'user_profile') else conv.user.email
            user_barangay = conv.user.user_profile.barangay if hasattr(conv.user, 'user_profile') else 'Unknown'
            
            # Get user profile picture
            user_profile_picture = None
            if hasattr(conv.user, 'user_profile') and conv.user.user_profile.profile_picture:
                user_profile_picture = conv.user.user_profile.profile_picture
            
            # Count unread messages (messages from user that haven't been read by admin)
            unread_count = conv.messages.filter(is_admin_message=False, is_read=False).count()
            
            chat_list.append({
                "conversation_id": conv.id,
                "complaint_id": conv.complaint.tracking_id,
                "complaint_type": conv.complaint.complaint_type,
                "user_name": user_name,
                "user_email": conv.user.email,
                "user_barangay": user_barangay,
                "user_profile_picture": user_profile_picture,
                "last_message": last_message.content if last_message else "No messages yet",
                "last_activity": last_message.created_at.isoformat() if last_message else conv.created_at.isoformat(),
                "message_count": conv.messages.count(),
                "unread_count": unread_count,
                "created_at": conv.created_at.isoformat()
            })

        # Sort by last activity (most recent first)
        chat_list.sort(key=lambda x: x['last_activity'], reverse=True)

        return JsonResponse({
            "success": True,
            "chats": chat_list
        })

    except Exception as e:
        print(f"Error getting admin chat list: {e}")
        return JsonResponse({"error": "Failed to get chat list"}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_admin_chat(request, complaint_id):
    """Delete a chat conversation for admin"""
    print(f"🗑️ DELETE request received for complaint_id: {complaint_id}")
    
    # Check if user is authenticated as admin using session-based auth
    if not request.session.get('admin_authenticated'):
        print("❌ Admin authentication failed - session not authenticated")
        return JsonResponse({"error": "Admin authentication required"}, status=401)
    
    print("✅ Admin authentication successful")
    
    try:
        # Parse request body to get conversation ID if needed
        data = {}
        if request.body:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                pass
        
        conversation_id = data.get('conversationId')
        print(f"📋 Request data: {data}")
        print(f"🔗 Conversation ID: {conversation_id}")
        
        # Try Supabase first
        if supabase:
            print("🌐 Using Supabase for deletion")
            try:
                # Delete all messages in the conversation from Supabase
                print(f"🗑️ Deleting messages for complaint_id: {complaint_id}")
                delete_messages_response = supabase.table('chat_messages').delete().eq('complaint_id', complaint_id).execute()
                print(f"📤 Messages deletion response: {delete_messages_response}")
                
                # Delete the conversation from Supabase
                print(f"🗑️ Deleting conversation for complaint_id: {complaint_id}")
                delete_conversation_response = supabase.table('chat_conversations').delete().eq('complaint_id', complaint_id).execute()
                print(f"📤 Conversation deletion response: {delete_conversation_response}")
                
                print("✅ Supabase deletion successful")
                return JsonResponse({"success": True, "message": "Chat deleted successfully"})
                
            except Exception as supabase_error:
                print(f"❌ Supabase error deleting chat: {supabase_error}")
                print("🔄 Falling back to Django ORM")
        else:
            print("🗄️ Supabase not available, using Django ORM")
        
        # Django ORM fallback
        from myapp.models import ChatConversation, ChatMessage
        
        print(f"🔍 Looking for conversation with complaint_id: {complaint_id}")
        
        # Find the conversation by complaint_id
        try:
            conversation = ChatConversation.objects.get(complaint_id=complaint_id)
            print(f"📝 Found conversation: {conversation.id}")
            
            # Delete all messages in this conversation
            messages_count = ChatMessage.objects.filter(conversation=conversation).count()
            print(f"🗑️ Deleting {messages_count} messages")
            ChatMessage.objects.filter(conversation=conversation).delete()
            
            # Delete the conversation itself
            print(f"🗑️ Deleting conversation: {conversation.id}")
            conversation.delete()
            
            print("✅ Django ORM deletion successful")
            return JsonResponse({"success": True, "message": "Chat deleted successfully"})
            
        except ChatConversation.DoesNotExist:
            print(f"⚠️ Chat conversation not found for complaint_id: {complaint_id} - treating as already deleted")
            return JsonResponse({"success": True, "message": "Chat already deleted or not found"})
        
    except Exception as e:
        print(f"❌ Error deleting admin chat: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": "Failed to delete chat"}, status=500)


def test_chat_delete(request):
    """Test endpoint to verify routing and authentication"""
    print("🧪 Test endpoint called")
    admin_auth = request.session.get('admin_authenticated')
    print(f"🔐 Admin auth status: {admin_auth}")
    return JsonResponse({"success": True, "message": "Test endpoint working", "admin_auth": admin_auth})


# ==========================
# API: User Chat Functionality
# ==========================

@require_http_methods(["GET"]) 
def get_user_chat_list(request):
    """Get list of all chat conversations for the user"""
    # Check if user is authenticated
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({
            "success": False,
            "error": "Authentication required",
            "redirect": True
        }, status=401)

    try:
        # Get all conversations for this user
        conversations = ChatConversation.objects.filter(user=user).select_related(
            'complaint', 'admin', 'admin__admin_profile'
        ).prefetch_related('messages')
        
        chat_list = []
        for conv in conversations:
            # Get the last message
            last_message = conv.messages.last()
            
            # Get admin info
            try:
                admin_profile = AdminProfile.objects.get(user=conv.admin)
                admin_name = f"{admin_profile.barangay} Admin"
                admin_barangay = admin_profile.barangay
            except AdminProfile.DoesNotExist:
                admin_name = "Admin"
                admin_barangay = "Unknown"
            
            # Count unread messages (messages from admin that haven't been read by user)
            unread_count = conv.messages.filter(is_admin_message=True, is_read=False).count()
            
            chat_list.append({
                "conversation_id": conv.id,
                "complaint_id": conv.complaint.tracking_id,
                "complaint_type": conv.complaint.complaint_type,
                "admin_name": admin_name,
                "admin_barangay": admin_barangay,
                "last_message": last_message.content if last_message else "No messages yet",
                "last_activity": last_message.created_at.isoformat() if last_message else conv.created_at.isoformat(),
                "message_count": conv.messages.count(),
                "unread_count": unread_count,
                "created_at": conv.created_at.isoformat()
            })

        # Sort by last activity (most recent first)
        chat_list.sort(key=lambda x: x['last_activity'], reverse=True)

        return JsonResponse({
            "success": True,
            "chats": chat_list
        })

    except Exception as e:
        print(f"Error getting user chat list: {e}")
        return JsonResponse({
            "success": False,
            "error": "Failed to get chat list"
        }, status=500)


@require_http_methods(["GET"]) 
def get_user_chat_messages(request, complaint_id):
    """Get chat messages for a specific complaint (user view)"""
    # Check if user is authenticated
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({
            "success": False,
            "error": "Authentication required",
            "redirect": True
        }, status=401)

    try:
        # Get the complaint
        complaint = Complaint.objects.get(tracking_id=complaint_id, user=user)
        
        # Get the conversation
        try:
            conversation = ChatConversation.objects.get(
                complaint=complaint,
                user=user
            )
        except ChatConversation.DoesNotExist:
            # Return empty messages if no conversation exists yet
            return JsonResponse({
                "success": True,
                "messages": [],
                "conversation_id": None
            })

        # Get all messages for this conversation
        messages = conversation.messages.all()
        
        # Mark all admin messages as read when user opens the chat
        unread_admin_messages = conversation.messages.filter(is_admin_message=True, is_read=False)
        unread_admin_messages.update(is_read=True)
        
        message_data = []
        for msg in messages:
            # Determine sender name based on message type
            if msg.is_admin_message:
                # For admin messages, use the stored admin name or fallback to barangay admin
                if msg.admin_name:
                    sender_name = msg.admin_name
                else:
                    try:
                        admin_profile = AdminProfile.objects.get(user=msg.sender)
                        sender_name = f"{admin_profile.barangay} Admin"
                    except AdminProfile.DoesNotExist:
                        sender_name = "Admin"
            else:
                # For user messages, use their full name or email
                sender_name = msg.sender.user_profile.full_name if hasattr(msg.sender, 'user_profile') else msg.sender.email
            
            message_data.append({
                "id": msg.id,
                "content": msg.content,
                "sender": msg.sender.email,
                "sender_name": sender_name,
                "is_admin_message": msg.is_admin_message,
                "timestamp": msg.created_at.isoformat(),
                "formatted_time": msg.created_at.strftime("%Y-%m-%d %H:%M")
            })

        return JsonResponse({
            "success": True,
            "messages": message_data,
            "conversation_id": conversation.id
        })

    except Complaint.DoesNotExist:
        return JsonResponse({"error": "Complaint not found"}, status=404)
    except Exception as e:
        print(f"Error getting user chat messages: {e}")
        return JsonResponse({"error": "Failed to get messages"}, status=500)


@csrf_exempt
@require_http_methods(["POST"]) 
def send_user_chat_message(request):
    """Send a chat message from user to admin"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    # Check if user is authenticated
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    complaint_id = payload.get("complaintId")
    message_content = payload.get("message", "").strip()

    if not complaint_id or not message_content:
        return JsonResponse({"error": "Complaint ID and message are required"}, status=400)

    try:
        # Get the complaint
        complaint = Complaint.objects.get(tracking_id=complaint_id, user=user)
        
        # Get or create chat conversation
        conversation, created = ChatConversation.objects.get_or_create(
            complaint=complaint,
            user=user,
            defaults={'created_at': timezone.now()}
        )

        # If conversation was created, we need to find an admin to assign
        if created:
            # Find an admin from the same barangay as the complaint
            try:
                admin_profile = AdminProfile.objects.get(barangay=complaint.barangay)
                conversation.admin = admin_profile.user
                conversation.save()
            except AdminProfile.DoesNotExist:
                # If no admin found for this barangay, use the first available admin
                try:
                    admin_profile = AdminProfile.objects.first()
                    if admin_profile:
                        conversation.admin = admin_profile.user
                        conversation.save()
                except:
                    pass

        # Create the message
        chat_message = ChatMessage.objects.create(
            conversation=conversation,
            sender=user,
            content=message_content,
            is_admin_message=False
        )

        # Update conversation timestamp to move it to top of list
        conversation.update_timestamp()

        return JsonResponse({
            "success": True,
            "message": "Message sent successfully",
            "message_id": chat_message.id,
            "timestamp": chat_message.created_at.isoformat()
        })

    except Complaint.DoesNotExist:
        return JsonResponse({"error": "Complaint not found"}, status=404)
    except Exception as e:
        print(f"Error sending user chat message: {e}")
        return JsonResponse({"error": "Failed to send message"}, status=500)


@require_http_methods(["GET"]) 
def get_complaint_activity_log(request, tracking_id):
    """Get activity log for a specific complaint"""
    # Check if user is authenticated as admin
    user = request.user
    if not user.is_authenticated or not (user.is_staff or user.is_superuser):
        return JsonResponse({"error": "Admin authentication required"}, status=401)
    
    try:
        # Get the complaint
        complaint = Complaint.objects.get(tracking_id=tracking_id)
        
        # Get all activity logs for this complaint
        log_data = []
        try:
            activity_logs = AdminActivityLog.objects.filter(complaint=complaint).order_by('-created_at')
            
            for log in activity_logs:
                log_data.append({
                    "id": log.id,
                    "admin_name": log.admin_name,
                    "admin_barangay": log.admin_barangay,
                    "action_type": log.action_type,
                    "description": log.description,
                    "old_value": log.old_value,
                    "new_value": log.new_value,
                    "timestamp": log.created_at.isoformat(),
                    "formatted_time": format_ph_datetime(log.created_at)
                })
            print(f"📋 Retrieved {len(activity_logs)} activity log entries for complaint {tracking_id}")
        except Exception as e:
            print(f"Warning: Could not retrieve activity logs: {e}")
            # Return empty log data if AdminActivityLog is not available

        return JsonResponse({
            "success": True,
            "activity_logs": log_data
        })

    except Complaint.DoesNotExist:
        return JsonResponse({"error": "Complaint not found"}, status=404)
    except Exception as e:
        print(f"Error getting activity log: {e}")
        return JsonResponse({"error": "Failed to get activity log"}, status=500)


@require_http_methods(["GET"]) 
def get_user_complaint_activity(request, tracking_id):
    """Get activity log for a specific complaint (user view)"""
    # Check if user is authenticated
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    try:
        # Get the complaint (only if it belongs to the user)
        complaint = Complaint.objects.get(tracking_id=tracking_id, user=user)
        
        # Get all activity logs for this complaint (status changes only for users)
        log_data = []
        try:
            activity_logs = AdminActivityLog.objects.filter(
                complaint=complaint, 
                action_type=AdminActivityLog.ActionType.STATUS_CHANGE
            ).order_by('created_at')
            
            for log in activity_logs:
                log_data.append({
                    "status": log.new_value,
                    "description": log.description,
                    "admin_name": log.admin_name,
                    "admin_barangay": log.admin_barangay,
                    "timestamp": log.created_at.isoformat(),
                    "formatted_time": format_ph_datetime(log.created_at)
                })
            print(f"📋 Retrieved {len(activity_logs)} status change logs for user view of complaint {tracking_id}")
        except Exception as e:
            print(f"Warning: Could not retrieve user activity logs: {e}")
            # Return empty log data if AdminActivityLog is not available

        return JsonResponse({
            "success": True,
            "activity_logs": log_data
        })

    except Complaint.DoesNotExist:
        return JsonResponse({"error": "Complaint not found"}, status=404)
    except Exception as e:
        print(f"Error getting user complaint activity: {e}")
        return JsonResponse({"error": "Failed to get complaint activity"}, status=500)


# ================================
# SUPERADMIN API ENDPOINTS
# ================================

@csrf_exempt
def superadmin_list_admins(request):
    """API endpoint to list all registered admins for superadmin dashboard"""
    if request.method != 'GET':
        return JsonResponse({"error": "Method not allowed"}, status=405)
        
    # Check if user is authenticated as superadmin
    if not request.session.get('admin_authenticated', False):
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    admin_email = request.session.get('admin_email', '')
    if admin_email != 'complaintmanagementsystem5@gmail.com':
        return JsonResponse({"error": "Superadmin access required"}, status=403)

    try:
        # Get all admin profiles except superadmin
        admin_profiles = AdminProfile.objects.exclude(
            user__email='complaintmanagementsystem5@gmail.com'
        ).select_related('user')
        
        admins_data = []
        for admin_profile in admin_profiles:
            user = admin_profile.user
            
            # Count users in this barangay (exact match)
            user_count = UserProfile.objects.filter(barangay=admin_profile.barangay).count()
            print(f"👥 Admin {user.email} ({admin_profile.barangay}) has {user_count} users")
            
            admin_data = {
                "id": admin_profile.id,
                "email": user.email,
                "barangay": admin_profile.barangay,
                "userCount": user_count,
                "isActive": user.is_active,
                "registrationDate": admin_profile.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "officials": {
                    "barangayCaptain": admin_profile.barangay_captain or "",
                    "barangaySecretary": admin_profile.barangay_secretary or "",
                    "barangayKagawad": admin_profile.barangay_kagawad or "",
                    "skChairman": admin_profile.sk_chairman or "",
                    "termStartYear": admin_profile.term_start_year,
                    "termEndYear": admin_profile.term_end_year
                }
            }
            admins_data.append(admin_data)
        
        return JsonResponse({
            "admins": admins_data,
            "totalCount": len(admins_data)
        })

    except Exception as e:
        print(f"Error listing admins: {e}")
        return JsonResponse({"error": "Failed to retrieve admins"}, status=500)


@csrf_exempt
def superadmin_list_users(request):
    """API endpoint to list all registered users for superadmin dashboard"""
    if request.method != 'GET':
        return JsonResponse({"error": "Method not allowed"}, status=405)
        
    # Check if user is authenticated as superadmin
    if not request.session.get('admin_authenticated', False):
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    admin_email = request.session.get('admin_email', '')
    if admin_email != 'complaintmanagementsystem5@gmail.com':
        return JsonResponse({"error": "Superadmin access required"}, status=403)

    try:
        # Get all user profiles
        user_profiles = UserProfile.objects.all()
        
        users_data = []
        for user_profile in user_profiles:
            # Count complaints submitted by this user
            complaint_count = Complaint.objects.filter(user=user_profile.user).count()
            
            # Debug profile picture data
            print(f"User {user_profile.email} profile picture: {user_profile.profile_picture[:50] if user_profile.profile_picture else 'None'}...")
            
            user_data = {
                "id": user_profile.id,
                "email": user_profile.email,
                "fullName": user_profile.full_name,
                "barangay": user_profile.barangay,
                "complaintsSubmitted": complaint_count,
                "isEmailVerified": user_profile.email_verified,
                "registrationDate": user_profile.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "profilePicture": user_profile.profile_picture
            }
            users_data.append(user_data)
        
        return JsonResponse({
            "users": users_data,
            "totalCount": len(users_data)
        })

    except Exception as e:
        print(f"Error listing users: {e}")
        return JsonResponse({"error": "Failed to retrieve users"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_admin_officials(request):
    """API endpoint to update admin officials information"""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")
    
    # Check if user is authenticated as superadmin
    if not request.session.get('admin_authenticated', False):
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    admin_email = request.session.get('admin_email', '')
    if admin_email != 'complaintmanagementsystem5@gmail.com':
        return JsonResponse({"error": "Superadmin access required"}, status=403)

    admin_id = payload.get("admin_id")
    barangay_captain = payload.get("barangayCaptain", "").strip()
    barangay_secretary = payload.get("barangaySecretary", "").strip()
    barangay_kagawad = payload.get("barangayKagawad", "").strip()
    sk_chairman = payload.get("skChairman", "").strip()
    term_start_year = payload.get("termStartYear")
    term_end_year = payload.get("termEndYear")

    print(f"Received update request for admin_id: {admin_id}")
    print(f"Payload: {payload}")

    if not admin_id:
        print("Error: No admin_id provided")
        return JsonResponse({"error": "Admin ID is required"}, status=400)

    try:
        # Debug: List all available admin IDs
        all_admins = AdminProfile.objects.all()
        print(f"Available admin IDs in database: {[admin.id for admin in all_admins]}")
        print(f"Looking for admin_id: {admin_id} (type: {type(admin_id)})")
        
        # Find the admin profile
        admin_profile = AdminProfile.objects.get(id=admin_id)
        print(f"Updating officials for admin {admin_id}: {admin_profile.barangay}")
        
        # Update officials information
        admin_profile.barangay_captain = barangay_captain
        admin_profile.barangay_secretary = barangay_secretary
        admin_profile.barangay_kagawad = barangay_kagawad
        admin_profile.sk_chairman = sk_chairman
        
        if term_start_year:
            admin_profile.term_start_year = int(term_start_year)
        if term_end_year:
            admin_profile.term_end_year = int(term_end_year)
        
        admin_profile.save()
        print(f"Officials updated successfully for {admin_profile.barangay}")
        
        return JsonResponse({
            "success": True,
            "message": "Officials information updated successfully"
        })
        
    except AdminProfile.DoesNotExist:
        return JsonResponse({"error": "Admin not found"}, status=404)
    except Exception as e:
        print(f"Error updating officials: {e}")
        return JsonResponse({"error": "Failed to update officials"}, status=500)


@csrf_exempt
def superadmin_stats(request):
    """API endpoint to get stats for superadmin dashboard"""
    if request.method != 'GET':
        return JsonResponse({"error": "Method not allowed"}, status=405)
        
    # Check if user is authenticated as superadmin
    if not request.session.get('admin_authenticated', False):
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    admin_email = request.session.get('admin_email', '')
    if admin_email != 'complaintmanagementsystem5@gmail.com':
        return JsonResponse({"error": "Superadmin access required"}, status=403)

    try:
        # Count admins (excluding superadmin)
        total_admins = AdminProfile.objects.exclude(
            user__email='complaintmanagementsystem5@gmail.com'
        ).count()
        
        # Count users
        total_users = UserProfile.objects.count()
        
        return JsonResponse({
            "totalBarangayAdmins": total_admins,
            "totalRegisteredUsers": total_users
        })

    except Exception as e:
        print(f"Error getting stats: {e}")
        return JsonResponse({"error": "Failed to retrieve stats"}, status=500)


@csrf_exempt
def superadmin_admin_details(request, admin_id):
    """Get detailed information for a specific admin"""
    try:
        # Check if user is authenticated as superadmin
        if not request.session.get('admin_authenticated') or request.session.get('admin_email') != 'complaintmanagementsystem5@gmail.com':
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Get admin profile
        try:
            admin_profile = AdminProfile.objects.get(id=admin_id)
        except AdminProfile.DoesNotExist:
            return JsonResponse({'error': 'Admin not found'}, status=404)
        
        user = admin_profile.user
        
        # Count users in the same barangay
        user_count_same_barangay = UserProfile.objects.filter(barangay=admin_profile.barangay).count()
        
        # Get last login info
        last_login = user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
        
        # Calculate total logins (this is a simplified approach)
        total_logins = 1 if user.last_login else 0
        
        # Account created date
        account_created = user.date_joined.strftime('%Y-%m-%d')
        
        # Account age in days
        from datetime import datetime
        account_age = (datetime.now().date() - user.date_joined.date()).days
        
        admin_data = {
            'id': admin_profile.id,
            'email': user.email,
            'barangay': admin_profile.barangay,
            'userCount': user_count_same_barangay,
            'lastLogin': last_login,
            'totalLogins': total_logins,
            'accountCreated': account_created,
            'accountAge': account_age,
            'systemInfo': {
                'accessKey': 'Set (Hidden)' if admin_profile.access_key else 'Not set',
                'accountCreated': account_created,
                'accountAge': f"{account_age} days"
            },
            'officials': {
                'barangay_captain': admin_profile.barangay_captain or 'Not set',
                'barangay_secretary': admin_profile.barangay_secretary or 'Not set',
                'barangay_kagawad': admin_profile.barangay_kagawad or 'Not set',
                'sk_chairman': admin_profile.sk_chairman or 'Not set',
                'term_start_year': admin_profile.term_start_year or 'Not set',
                'term_end_year': admin_profile.term_end_year or 'Not set'
            }
        }
        
        return JsonResponse({
            'success': True,
            'admin': admin_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
