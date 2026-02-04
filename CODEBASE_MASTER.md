# Davao City Barangay Complaint Management System - Codebase Master Guide

**Last Updated:** February 2, 2026  
**Live Site:** https://dvobarangaycms.vip  
**Framework:** Django 5.1.6 | **Language:** Python 3.12.7 | **Database:** PostgreSQL (Supabase/Railway)

---

## 📋 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Database Schema](#database-schema)
6. [Key Components](#key-components)
7. [Authentication & Authorization](#authentication--authorization)
8. [API Endpoints](#api-endpoints)
9. [Frontend Templates](#frontend-templates)
10. [External Services Integration](#external-services-integration)
11. [Deployment](#deployment)
12. [Development Workflow](#development-workflow)

---

## 🎯 SYSTEM OVERVIEW

### Purpose
A comprehensive web-based complaint management system for barangay-level governance in Davao City, Philippines that enables citizens to:
- Submit complaints with images and location details
- Track complaint status in real-time
- Communicate with barangay officials via live chat
- Receive SMS/Email notifications

### User Roles
- **Citizens (Users):** Submit and track complaints, chat with admins
- **Barangay Admins:** Manage complaints, respond to users, forward to agencies
- **Superadmin:** System-wide oversight, admin management, statistics

### Key Features
- Email OTP-based registration & login
- Real-time complaint status tracking
- Live chat between users and admins
- Admin activity logging & audit trail
- SMS & Email notifications
- Multi-barangay support (182 barangays in Davao City)
- Profile pictures & phone numbers

---

## 🏗 ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                     Web Browser (Frontend)                       │
│  HTML5 + CSS3 + JavaScript (Vanilla) - Responsive Mobile-First  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/HTTPS
┌──────────────────────────▼──────────────────────────────────────┐
│                    Django Web Server                             │
│  - URL Routing (myproject/urls.py → myapp/urls.py)             │
│  - Views (myapp/views.py - 3196 lines)                          │
│  - Middleware (Role-based access control)                       │
│  - Models & ORM (myapp/models.py)                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐    ┌────────▼────────┐   ┌────▼──────┐
   │Database │    │External Services│   │ Static    │
   │         │    │                 │   │ Files     │
   └────┬────┘    └────────┬────────┘   └───────────┘
        │                  │
   ┌────▼────────┐    ┌────┴────────────────┬──────────┐
   │PostgreSQL   │    │ SendGrid (Email)    │ PhilSMS  │
   │(Supabase/   │    │ Gmail SMTP (Dev)    │ (SMS)    │
   │ Railway)    │    │ WhiteNoise (CDN)    │          │
   └─────────────┘    └─────────────────────┴──────────┘
```

---

## 🛠 TECHNOLOGY STACK

### Backend
| Layer | Technology | Purpose |
|-------|-----------|---------|
| Framework | Django 5.1.6 | Web application framework |
| Language | Python 3.12.7 | Backend programming |
| Database | PostgreSQL | Relational database |
| ORM | Django ORM | Database abstraction |
| Authentication | Django Auth + Custom OTP | User & admin authentication |
| Hosting | Railway Platform | Production deployment |

### Database Hosting
- **Development:** Supabase PostgreSQL
- **Production:** Railway PostgreSQL

### Frontend
| Layer | Technology | Purpose |
|-------|-----------|---------|
| Markup | HTML5 | Page structure |
| Styling | CSS3 | Responsive design, gradients, animations |
| Scripting | JavaScript (Vanilla) | DOM manipulation, API calls |
| Approach | Mobile-first responsive | Works on all devices |

### External Services
| Service | Purpose | Configuration |
|---------|---------|---|
| **SendGrid** | Email delivery (Production) | SENDGRID_API_KEY, SENDGRID_DOMAIN |
| **Gmail SMTP** | Email delivery (Development) | EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD |
| **PhilSMS API** | SMS notifications | PHILSMS_API_TOKEN, PHILSMS_SENDER_ID |
| **WhiteNoise** | Static file serving | Middleware in production |
| **Supabase** | Database (Development) | SUPABASE_URL, SUPABASE_KEY |

### Key Dependencies
```
Django>=5.1.6
psycopg2-binary>=2.9.9
python-dotenv>=1.0.0
supabase>=2.0.0
gunicorn>=21.2.0
whitenoise>=6.6.0
sendgrid>=6.10.0
requests>=2.31.0
Pillow>=10.0.0
pytz>=2023.3
twilio>=8.10.0
django-cors-headers>=4.3.1
```

---

## 📁 PROJECT STRUCTURE

```
Complaint Management System/
│
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── Procfile                           # Railway deployment config
├── runtime.txt                        # Python version for Railway
├── db.sqlite3                         # Local development database
├── README.md                          # Project documentation
├── CODEBASE_MASTER.md                 # This file (NEW)
│
├── myproject/                         # Django project settings
│   ├── __init__.py
│   ├── settings.py                    # Django configuration (371 lines)
│   ├── urls.py                        # Main URL routing
│   ├── asgi.py                        # ASGI config
│   ├── wsgi.py                        # WSGI config
│   └── __pycache__/
│
├── myapp/                             # Main Django application
│   ├── models.py                      # Database models (161 lines)
│   ├── views.py                       # Business logic (3196 lines)
│   ├── urls.py                        # API endpoint routing (108 lines)
│   ├── admin.py                       # Django admin configuration
│   ├── apps.py                        # App configuration
│   ├── tests.py                       # Unit tests
│   ├── middleware.py                  # Role-based access control (72 lines)
│   │
│   ├── supabase_client.py             # Supabase client initialization
│   ├── email_utils.py                 # Email & OTP functionality (247 lines)
│   ├── sendgrid_email.py              # SendGrid integration
│   ├── sms_utils.py                   # SMS notifications via PhilSMS (163 lines)
│   │
│   ├── migrations/                    # Database migrations
│   │   ├── 0001_initial.py
│   │   ├── 0016_initial.py
│   │   ├── 0020_adminprofile.py
│   │   ├── 0021_emailotp_userprofile.py
│   │   ├── 0022_add_profile_picture_only.py
│   │   ├── 0023_fix_profile_picture_field.py
│   │   ├── 0024_force_profile_picture_text.py
│   │   └── ... (more migrations)
│   │
│   ├── static/                        # Static files (CSS, JS, images)
│   │   └── (compiled assets)
│   │
│   ├── templates/                     # HTML templates
│   │   ├── index.html                 # Home page / Login page
│   │   ├── user.html                  # User dashboard
│   │   ├── user-submit.html           # Submit complaint form
│   │   ├── user-view.html             # View single complaint
│   │   ├── user-history.html          # User's complaint history
│   │   ├── admin-dashboard.html       # Admin main dashboard
│   │   ├── admin-complaints.html      # Admin complaint management
│   │   ├── admin-history.html         # Admin complaint history
│   │   ├── admin-user.html            # Admin user management
│   │   ├── admin-chat.html            # Admin chat interface
│   │   └── superadmin.html            # Superadmin dashboard
│   │
│   ├── management/                    # Custom Django commands
│   │   └── commands/
│   │
│   └── __pycache__/
│
├── davao_city_182_barangays_official.json    # Barangay list (182 entries)
├── davao_city_barangays.json                 # Alternative barangay data
├── davao_city_barangays_complete.txt         # Text format barangay list
│
├── Utility Scripts/                   # Development & debugging scripts
│   ├── add_email_verified_column.py
│   ├── admin_recovery_tool.py
│   ├── check_admin_profiles.py
│   ├── check_database_status.py
│   ├── check_otp_code.py
│   ├── check_tables.py
│   ├── create_182_barangays.py
│   ├── delete_user.py
│   ├── generate_test_otp.py
│   ├── migrate_admin_to_supabase.py
│   ├── setup_admin_profiles_supabase.py
│   ├── setup_gmail.py
│   ├── setup_supabase.py
│   ├── test_admin_endpoint.py
│   ├── test_email.py
│   ├── test_gmail_setup.py
│   ├── test_philsms.py
│   ├── test_sendgrid_domain.py
│   └── ... (20+ utility scripts)
│
└── Documentation/
    ├── ANALYSIS_OF_RESULTS.md
    ├── CAPSTONE_2_MANUSCRIPT_REVISION.md
    ├── PRESENTATION_DATA_SUMMARY.md
    ├── SECURITY_IMPLEMENTATION.md
    ├── SENDGRID_SETUP_INSTRUCTIONS.md
    ├── SMS_SETUP.md
    └── env.example                     # Environment variables template
```

---

## 🗄 DATABASE SCHEMA

### Entity Relationship Diagram

```
User (Django Auth)
    │
    ├─── UserProfile (1:1)
    │    ├── user_id (FK)
    │    ├── full_name
    │    ├── email
    │    ├── barangay
    │    ├── email_verified
    │    ├── profile_picture (base64)
    │    ├── phone_number
    │    └── created_at
    │
    ├─── Complaint (1:N)
    │    ├── user_id (FK)
    │    ├── tracking_id (unique)
    │    ├── barangay
    │    ├── complaint_type
    │    ├── description
    │    ├── location
    │    ├── image_base64
    │    ├── admin_update
    │    ├── resolution_image
    │    ├── status (enum)
    │    ├── forwarded_to_agency
    │    ├── forward_reason
    │    ├── forward_date
    │    ├── created_at
    │    └── updated_at
    │
    ├─── ChatConversation (many)
    │    ├── complaint_id (FK)
    │    ├── admin_id (FK → User)
    │    ├── user_id (FK → User)
    │    ├── created_at
    │    └── updated_at
    │
    ├─── ChatMessage (many)
    │    ├── conversation_id (FK)
    │    ├── sender_id (FK → User)
    │    ├── content
    │    ├── is_admin_message (bool)
    │    ├── is_read (bool)
    │    ├── admin_name
    │    └── created_at
    │
    ├─── AdminProfile (1:1, only for admins)
    │    ├── user_id (FK)
    │    ├── barangay
    │    ├── access_key_hash
    │    ├── barangay_captain
    │    ├── barangay_secretary
    │    ├── barangay_kagawad
    │    ├── sk_chairman
    │    ├── term_start_year
    │    ├── term_end_year
    │    └── created_at
    │
    └─── AdminActivityLog (many)
         ├── complaint_id (FK, nullable)
         ├── admin_user_id (FK → User)
         ├── admin_name
         ├── admin_barangay
         ├── action_type (enum)
         ├── description
         └── created_at

EmailOTP (standalone)
├── email
├── otp_code
├── is_used (bool)
├── created_at
└── expires_at
```

### Key Models

#### 1. **Complaint**
- Core model for all complaints
- Status workflow: Pending → In Progress → Resolved/Declined/Forwarded
- Supports image storage as base64 (no MEDIA directory needed)
- Tracks resolution images and admin updates
- Supports forwarding to higher agencies

#### 2. **UserProfile**
- Extends Django User model with profile information
- Email verification tracking
- Profile pictures (base64 encoded)
- Phone numbers for SMS notifications

#### 3. **AdminProfile**
- Extends Django User model for admin-specific data
- Access key hash for 6-digit PIN authentication
- Stores barangay officials information

#### 4. **ChatConversation & ChatMessage**
- Real-time communication between users and admins
- One conversation per complaint per admin-user pair
- Message read tracking
- Admin name storage for display

#### 5. **EmailOTP**
- Time-limited OTP codes for email verification
- Expires after 10 minutes
- Marked as used after successful verification

#### 6. **AdminActivityLog**
- Audit trail for all admin actions
- Tracks status changes, messages, forwarding, etc.
- Includes action description and timestamp

---

## 🔑 KEY COMPONENTS

### 1. **Authentication System**

#### User Registration Flow
```
User → Send Verification Code
    ↓
    → Check Email Not Registered
    ↓
    → Generate OTP (6 digits)
    ↓
    → Send via SendGrid/Gmail
    ↓
    → User Receives Email
    ↓
User → Verify Email with OTP
    ↓
    → Check OTP Valid & Not Expired
    ↓
    → Create Django User
    ↓
    → Create UserProfile
    ↓
    → Mark Email OTP as Used
    ↓
    → Registration Complete
```

#### User Login Flow
```
User → Enter Email
    ↓
    → Check User Exists
    ↓
    → Generate OTP
    ↓
    → Send via Email
    ↓
User → Verify Login OTP
    ↓
    → Check OTP Valid
    ↓
    → Create Session
    ↓
    → User Authenticated
```

#### Admin Registration Flow
```
Admin → Enter Email, Password, Barangay
    ↓
    → Send Verification Code
    ↓
    → Verify Email with OTP
    ↓
    → Create Admin User
    ↓
    → Verify Access Key (F32024)
    ↓
    → Create AdminProfile
    ↓
    → Registration Complete
```

#### Admin Login Flow
```
Admin → Enter Email & Access Key
    ↓
    → Check Email Exists
    ↓
    → Generate OTP
    ↓
    → Send via Email
    ↓
Admin → Verify OTP
    ↓
    → Create Admin Session
    ↓
    → Set admin_authenticated = True
    ↓
    → Redirect to Admin Dashboard
```

### 2. **Views Layer (myapp/views.py - 3196 lines)**

#### View Categories

**Page Views (Template Rendering)**
- `home()` - Home/index page
- `user_page()` - User dashboard
- `user_submit()` - Submit complaint form
- `user_view()` - View complaint detail
- `user_history()` - User complaint history
- `admin_dashboard()` - Admin main page
- `admin_complaints()` - Admin complaint management
- `admin_user()` - User management
- `admin_chat()` - Chat interface
- `superadmin_dashboard()` - Superadmin overview

**User Auth APIs**
- `send_verification_code()` - Send OTP for registration
- `verify_email_and_register()` - Complete registration with OTP
- `user_login()` - Initiate login with OTP
- `verify_login_otp()` - Verify login OTP
- `resend_verification_code()` - Resend OTP
- `check_user_auth()` - Check if user is authenticated
- `save_profile_picture()` - Upload profile image (base64)
- `get_profile_picture()` - Retrieve profile image
- `save_phone_number()` - Store phone for SMS
- `get_phone_number()` - Retrieve phone number

**Admin Auth APIs**
- `admin_login()` - Admin email login
- `admin_logout()` - Admin logout
- `admin_me()` - Get current admin info
- `admin_register()` - Admin registration
- `admin_send_verification_code()` - Send email OTP
- `admin_verify_email_and_register()` - Verify email with OTP
- `admin_verify_access_key()` - Verify 6-digit PIN
- `admin_recovery_info()` - Recover admin account

**Complaint Management APIs**
- `create_complaint()` - Submit new complaint
- `list_complaints()` - Get user's complaints
- `list_complaints_history()` - Get complaint history
- `complaint_detail()` - Get single complaint
- `fetch_complaints()` - Fetch all complaints (admin)
- `update_transaction_status()` - Update complaint status
- `list_transactions()` - Transaction list (complaints)
- `transaction_detail()` - Transaction detail

**Admin Management APIs**
- `list_users_for_admin()` - List all users
- `delete_user_for_admin()` - Delete user account
- `get_registered_barangays()` - Get barangays with admins
- `update_admin_officials()` - Update barangay officials info

**Chat APIs**
- `send_chat_message()` - Admin sends message
- `get_chat_messages()` - Retrieve chat history
- `delete_admin_chat()` - Delete chat conversation
- `get_admin_chat_list()` - Get admin's chat list
- `get_user_chat_list()` - Get user's chat list
- `get_user_chat_messages()` - Get user chat messages
- `send_user_chat_message()` - User sends message

**Superadmin APIs**
- `superadmin_list_admins()` - List all barangay admins
- `superadmin_list_users()` - List all registered users
- `superadmin_stats()` - System-wide statistics
- `superadmin_admin_details()` - Get admin details

**Utility APIs**
- `contact_form_submission()` - Contact form
- `get_admin_data()` - Get admin recovery data
- `get_complaint_activity_log()` - Audit trail for complaint
- `test_chat_delete()` - Debug endpoint

### 3. **URL Routing (myapp/urls.py - 108 lines)**

All routes are documented in urls.py with patterns for:
- Page rendering (template views)
- RESTful API endpoints
- Admin operations
- Superadmin operations
- Chat functionality
- Profile management

### 4. **Middleware (myapp/middleware.py - 72 lines)**

**RoleBasedAuthMiddleware**
- Prevents users from accessing admin pages
- Prevents admins from accessing user pages
- Returns JSON or redirect based on request type
- Works with session-based authentication

### 5. **Email & OTP System (myapp/email_utils.py - 247 lines)**

**Key Functions**
- `generate_otp()` - Generate random 6-digit code
- `send_verification_email()` - Send email via SendGrid (prod) or Gmail (dev)
- `create_otp_for_email()` - Store OTP in database
- `verify_otp()` - Check OTP validity and expiration
- `send_status_notification()` - Send complaint status updates

**Email Templates**
- Email verification with OTP
- Status update notifications
- Complaint assignment notifications
- Forwarding notifications

### 6. **SMS System (myapp/sms_utils.py - 163 lines)**

**PhilSMS Integration**
- `send_sms_via_philsms()` - Send SMS notifications
- Phone validation
- Message formatting
- Error handling & logging

**SMS Types**
- Status change notifications
- Complaint assignment alerts
- Forwarding notifications
- Complaint resolution updates

### 7. **Utilities & Helpers**

**Timezone Handling**
```python
get_ph_timezone()       # Get Asia/Manila timezone
format_ph_datetime()    # Convert to PH time format
get_current_ph_time()   # Get current PH time
```

**Authentication Decorator**
```python
@require_admin_auth     # Wrapper to check admin session
```

**Error Handling**
- JSON error responses
- HTTP status codes (400, 403, 404, 500)
- Detailed logging for debugging

---

## 🔐 AUTHENTICATION & AUTHORIZATION

### Session Management
- Django session framework
- `admin_authenticated` flag in session
- Cross-role access prevention

### Role-Based Access Control (RBAC)
| Role | Access | Page Access |
|------|--------|------------|
| **User** | User-only pages | user.html, user-submit.html, user-view.html, user-history.html |
| **Admin** | Admin pages | admin-dashboard.html, admin-complaints.html, admin-user.html, admin-chat.html |
| **Superadmin** | System-wide | superadmin.html + admin access |
| **Anonymous** | Public | index.html (login/register) |

### Security Features
- OTP-based verification (no passwords stored as plaintext)
- 6-digit admin PIN (access_key_hash)
- Email verification for account registration
- Session-based authentication
- CSRF protection enabled
- CORS configuration for API requests
- Password hashing using Django's `make_password()`

---

## 📡 API ENDPOINTS

### Base URL: `http://localhost:8000` or `https://dvobarangaycms.vip`

### User Authentication Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/user/send-verification/` | Send registration OTP |
| POST | `/api/user/verify-email/` | Verify email & register |
| POST | `/api/user/login/` | Start login process |
| POST | `/api/user/verify-login-otp/` | Verify login OTP |
| POST | `/api/user/resend-verification/` | Resend OTP |
| GET | `/api/user/check-auth/` | Check user authentication status |

### User Profile Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/user/save-profile-picture/` | Upload profile picture (base64) |
| GET | `/api/user/get-profile-picture/` | Retrieve profile picture |
| POST | `/api/user/save-phone-number/` | Save phone number |
| GET | `/api/user/get-phone-number/` | Get phone number |

### Complaint Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/complaints/create/` | Submit new complaint |
| GET | `/api/complaints/` | List user's complaints |
| GET | `/api/complaints/history/` | Get complaint history |
| GET | `/api/complaints/<tracking_id>/` | Get complaint detail |
| GET | `/api/transactions/` | List transactions (complaints) |
| GET | `/api/transactions/<tracking_id>/` | Transaction detail |
| PATCH | `/api/transactions/<tracking_id>/status/` | Update status |

### Admin Authentication Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/admin/login/` | Admin login |
| POST | `/api/admin/logout/` | Admin logout |
| GET | `/api/admin/me/` | Get current admin info |
| POST | `/api/admin/register/` | Admin registration |
| POST | `/api/admin/send-verification/` | Send email OTP |
| POST | `/api/admin/verify-email/` | Verify email & create account |
| POST | `/api/admin/verify-access-key/` | Verify admin PIN |

### Admin Management Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/admin/users/` | List all users (admin view) |
| DELETE | `/api/admin/users/<user_id>/delete/` | Delete user |
| GET | `/api/barangays/registered/` | Get registered barangays |
| POST | `/api/superadmin/update-officials/` | Update barangay officials |

### Chat Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/admin/chat/send/` | Admin sends message |
| GET | `/api/admin/chat/<complaint_id>/messages/` | Get admin chat history |
| DELETE | `/api/admin/chat/<complaint_id>/delete/` | Delete chat |
| GET | `/api/admin/chat/list/` | Get admin's chat list |
| GET | `/api/user/chat/list/` | Get user's chat list |
| GET | `/api/user/chat/<complaint_id>/messages/` | Get user chat messages |
| POST | `/api/user/chat/send/` | User sends message |

### Superadmin Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/superadmin/admins/` | List all admins |
| GET | `/api/superadmin/users/` | List all users |
| GET | `/api/superadmin/stats/` | Get system statistics |
| GET | `/api/superadmin/admin/<admin_id>/` | Get admin details |

### Activity & Logging Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/admin/complaint/<tracking_id>/activity/` | Get activity log |
| GET | `/api/contact/` | Contact form submission |

### Health Check
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/health/` | Server health check (Railway) |

---

## 🎨 FRONTEND TEMPLATES

### Template Files (11 HTML files)

#### User-Facing Templates

**1. index.html** - Home/Login Page
- Login section for users
- Registration section for new users
- Navigation between user/admin areas
- Responsive design with gradient UI
- OTP verification modal

**2. user.html** - User Dashboard
- Displays user welcome
- Quick actions (submit complaint, view complaint)
- Recent complaints preview
- Profile section with picture and phone number
- Logout button

**3. user-submit.html** - Submit Complaint Form
- Form with fields:
  - Complaint type (dropdown)
  - Description (textarea)
  - Location (text)
  - Image upload (camera/file)
  - Barangay selection
- Real-time validation
- Image preview
- Success message with tracking ID
- Image stored as base64

**4. user-view.html** - View Complaint Detail
- Complaint information display
- Status badge with color coding
- Images (original + resolution)
- Admin updates/notes
- Chat interface
- Forward information (if applicable)
- Status timeline

**5. user-history.html** - Complaint History
- Table/list of all user complaints
- Sorting by status, date
- Search functionality
- Status badges
- Quick view links
- Filtering options

#### Admin-Facing Templates

**6. admin-dashboard.html** - Admin Main Dashboard
- Barangay information display
- Quick statistics:
  - Total complaints
  - Pending count
  - In progress count
  - Resolved count
- Recent complaints list
- Shortcuts to management sections
- Admin profile info
- Logout button

**7. admin-complaints.html** - Complaint Management
- Table of barangay complaints
- Filtering by status
- Search functionality
- Sorting by date, type
- Quick actions:
  - View complaint
  - Update status
  - Send message
  - Forward complaint
- Bulk actions option
- Activity indicators

**8. admin-history.html** - Complaint History View
- Complete history of barangay complaints
- Advanced filtering
- Export options
- Resolved/declined statistics
- Forward tracking
- Pagination

**9. admin-user.html** - User Management
- List of registered users in barangay
- User search
- User details (name, email, phone)
- User's complaint count
- Delete user action
- Verification status
- Profile picture view

**10. admin-chat.html** - Chat Management
- Chat conversations list
- Real-time messaging interface
- User information display
- Complaint context
- Message read status
- Emoji/formatting support (if enabled)
- Delete conversation option
- Notification indicators

#### Superadmin Template

**11. superadmin.html** - Superadmin Dashboard
- System-wide statistics:
  - Total barangays with admins
  - Total users registered
  - Total complaints
  - Overall resolution rate
- Admin list with barangay assignments
- User statistics
- System status
- Admin management options
- Barangay officials management

### Frontend Technology Stack
- **HTML5** - Semantic markup
- **CSS3** - Responsive grid/flexbox, gradients, animations
- **Vanilla JavaScript** - AJAX requests, DOM manipulation
- **No Framework** - Lightweight, fast, no build required
- **Responsive** - Mobile-first design
- **Base64 Images** - No external image hosting needed

---

## 🔗 EXTERNAL SERVICES INTEGRATION

### 1. **Email Service**

#### Production (Railway) - SendGrid
```python
# sendgrid_email.py
- send_otp_email_sendgrid(email, otp_code)
- Uses SENDGRID_API_KEY
- Uses SENDGRID_DOMAIN for sender
- Reliable delivery with 99.9% uptime
```

#### Development - Gmail SMTP
```python
# email_utils.py
- Uses EMAIL_HOST: smtp.gmail.com
- EMAIL_HOST_USER: Gmail address
- EMAIL_HOST_PASSWORD: App password
- Timeout handling (5 seconds on Railway)
```

**Emails Sent**
- Email verification OTP
- Login OTP
- Complaint status updates
- Admin notifications
- Forwarding confirmations

### 2. **SMS Service**

#### PhilSMS API Integration
```python
# sms_utils.py
- send_sms_via_philsms(recipient, message)
- Requires: PHILSMS_API_TOKEN
- Optional: PHILSMS_SENDER_ID (default: "CMS")
- Phone format: 09123456789
```

**SMS Types**
- Status change notifications
- Complaint assigned alerts
- Resolution confirmations
- Forwarding notifications

### 3. **Database Services**

#### Supabase (Development)
- PostgreSQL database
- Real-time capabilities
- Authentication (not used, custom auth)
- Storage (not used, base64 images)
- Configuration:
  - SUPABASE_URL
  - SUPABASE_KEY

#### Railway PostgreSQL (Production)
- Managed PostgreSQL
- Environment variable: DATABASE_URL
- Auto-backup enabled
- Connection pooling

### 4. **Static File Serving**

#### WhiteNoise
- CSS, JS, Images served efficiently
- No separate CDN needed
- Configured in middleware (production only)
- STATIC_FILES_STORAGE setting

#### Local Development
- Django development server serves directly
- No STATIC_ROOT configuration

---

## 🚀 DEPLOYMENT

### Current Deployment
**Platform:** Railway  
**URL:** https://dvobarangaycms.vip  
**Environment:** Production (DEBUG=False recommended)

### Railway Configuration

**Procfile**
```
web: gunicorn myproject.wsgi
```

**Runtime.txt**
```
python-3.12.7
```

### Environment Variables (Production)

```env
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=dvobarangaycms.vip,www.dvobarangaycms.vip

# Database
DATABASE_URL=postgresql://...

# Email (SendGrid)
SENDGRID_API_KEY=...
SENDGRID_DOMAIN=...
DEFAULT_FROM_EMAIL=noreply@dvobarangaycms.vip

# SMS (PhilSMS)
PHILSMS_API_TOKEN=...
PHILSMS_SENDER_ID=CMS

# Supabase (if used)
SUPABASE_URL=...
SUPABASE_KEY=...

# CSRF & Security
CSRF_TRUSTED_ORIGINS=https://dvobarangaycms.vip

# Railway
RAILWAY_ENVIRONMENT=true
```

### Database Migrations on Deploy
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### Local Development Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd "Complaint Management System"

# 2. Create virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows
# or: source .venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file from env.example
cp env.example .env
# Edit .env with local values

# 5. Run migrations
python manage.py migrate

# 6. Create superuser (optional, for Django admin)
python manage.py createsuperuser

# 7. Start development server
python manage.py runserver

# 8. Access at http://localhost:8000
```

---

## 📊 DEVELOPMENT WORKFLOW

### Code Organization Best Practices
1. **Keep views.py focused** - Consider splitting into modules if exceeds 5000 lines
2. **Reusable utilities** - Create helper functions in utils.py
3. **Middleware first** - Use middleware for cross-cutting concerns
4. **DRY principle** - Don't repeat authentication/authorization logic

### Common Development Tasks

#### Adding a New Complaint Status
1. Update `Complaint.Status` in models.py
2. Update views that handle status updates
3. Update frontend templates for new status display
4. Add corresponding notification logic
5. Test status workflow

#### Adding a New API Endpoint
1. Create view function in views.py
2. Add URL pattern in urls.py
3. Create request/response handler
4. Add CSRF exemption if needed
5. Add error handling
6. Document in this file
7. Test with frontend

#### Modifying Models
1. Update model definition in models.py
2. Create migration: `python manage.py makemigrations`
3. Apply migration: `python manage.py migrate`
4. Update Django admin if needed
5. Update related views if affected
6. Update frontend templates if UI changes

#### Adding New Email Template
1. Create function in email_utils.py
2. Use either SendGrid or Gmail depending on environment
3. Test with dummy data
4. Add to appropriate workflow

### Testing
- Unit tests in tests.py
- Manual testing via Django admin
- Frontend testing via browser
- API testing via curl/Postman

### Debugging Tips
```python
# Print to console
print(f"Debug: {variable}")

# Check database state
python manage.py shell
>>> from myapp.models import *
>>> Complaint.objects.filter(...).values()

# Check session data
print(request.session.get('admin_authenticated'))

# View Django logs
# Check terminal output from manage.py runserver

# Check email logs
# Look for print statements in email_utils.py
```

---

## 📝 IMPORTANT CONSTANTS & CONFIGURATIONS

### Admin Constants
```python
ADMIN_ACTIVATION_KEY = "F32024"  # 6-digit PIN for admin registration
```

### OTP Configuration
```python
OTP_LENGTH = 6                   # Digits
OTP_EXPIRY = 10                  # Minutes
```

### Complaint Status Choices
```python
PENDING = "Pending"
IN_PROGRESS = "In Progress"
RESOLVED = "Resolved"
DECLINED = "Declined/Spam"
FORWARDED = "Forwarded to Agency"
RESOLVED_BY_AGENCY = "Resolved by Agency"
```

### Admin Activity Log Actions
```python
STATUS_CHANGE = "status_change"
CHAT_MESSAGE = "chat_message"
COMPLAINT_VIEW = "complaint_view"
USER_MANAGEMENT = "user_management"
COMPLAINT_FORWARD = "complaint_forward"
```

### Barangay Data
- **Total Barangays:** 182 (Davao City)
- **Data Sources:**
  - davao_city_182_barangays_official.json
  - davao_city_barangays.json
  - davao_city_barangays_complete.txt

---

## 🔍 UTILITY SCRIPTS

The workspace includes 20+ utility scripts for development, testing, and migration:

### Database Management
- `check_database_status.py` - Verify DB connection
- `check_tables.py` - List all tables
- `clear_django_data.py` - Reset local database
- `clear_supabase_data.py` - Clear production data

### Testing
- `test_email.py` - Test email sending
- `test_gmail_setup.py` - Test Gmail SMTP
- `test_sendgrid_domain.py` - Test SendGrid
- `test_philsms.py` - Test SMS API
- `test_admin_endpoint.py` - Test admin APIs
- `test_auth_security.py` - Test auth system
- `generate_test_otp.py` - Generate dummy OTP

### Admin Tools
- `admin_recovery_tool.py` - Recover admin accounts
- `check_admin_profiles.py` - Verify admin data
- `reset_admin_password.py` - Reset admin password
- `remove_superadmin_admin_account.py` - Admin cleanup

### Setup & Migration
- `setup_gmail.py` - Configure Gmail
- `setup_supabase.py` - Setup Supabase connection
- `setup_admin_profiles_supabase.py` - Migrate admin data
- `migrate_admin_to_supabase.py` - Admin migration
- `create_182_barangays.py` - Populate barangay list

---

## 📚 RELATED DOCUMENTATION

- **README.md** - Project overview & features
- **SECURITY_IMPLEMENTATION.md** - Security details
- **SENDGRID_SETUP_INSTRUCTIONS.md** - Email setup
- **SMS_SETUP.md** - SMS configuration
- **ANALYSIS_OF_RESULTS.md** - Testing results
- **CAPSTONE_2_MANUSCRIPT_REVISION.md** - Academic documentation

---

## 🎓 QUICK REFERENCE

### Most Important Files
| File | Size | Purpose |
|------|------|---------|
| views.py | 3196 | All business logic |
| models.py | 161 | Database schema |
| urls.py | 108 | URL routing |
| settings.py | 371 | Django configuration |
| email_utils.py | 247 | Email & OTP system |
| sms_utils.py | 163 | SMS integration |
| middleware.py | 72 | Access control |

### Most Used Functions
- `send_verification_code()` - Registration flow
- `verify_email_and_register()` - Complete registration
- `user_login()` - User authentication
- `admin_login()` - Admin authentication
- `create_complaint()` - Submit complaint
- `send_chat_message()` - Admin messaging
- `update_transaction_status()` - Change status

---

**This document serves as the master reference for the entire codebase. Update it when making significant architectural changes.**

Last Updated: February 2, 2026  
Maintained by: Development Team
