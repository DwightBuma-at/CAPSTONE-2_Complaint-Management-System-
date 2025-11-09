# Davao City Barangay Complaint Management System

A comprehensive web-based complaint management system designed for barangay-level governance in Davao City, Philippines. This system enables citizens to submit, track, and manage complaints while providing barangay officials with powerful administrative tools.

[![Live Site](https://img.shields.io/badge/Live-dvobarangaycms.vip-blue)](https://dvobarangaycms.vip)
[![Python](https://img.shields.io/badge/Python-3.12.7-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1.6-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Features

### For Citizens (Users)
- **Account Registration & Login** with email OTP verification
- **Submit Complaints** with images and location details
- **Real-time Tracking** of complaint status with unique tracking IDs
- **Live Chat** with barangay officials for each complaint
- **Email & SMS Notifications** for status updates
- **Complaint History** view with resolution details
- **Profile Management** with profile pictures and phone numbers

### For Barangay Admins
- **Secure Admin Dashboard** with 6-digit access key protection
- **Complaint Management** with status updates and filtering
- **Direct Messaging** with citizens through integrated chat
- **Status Updates** with admin notes and resolution images
- **Forward Complaints** to higher agencies when needed
- **User Management** - view and manage registered users
- **Activity Logging** - complete audit trail of all admin actions
- **Statistics Dashboard** - view complaint trends and resolution rates

### For Superadmin
- **System-wide Overview** of all barangays
- **Admin Management** - view and manage all barangay admins
- **User Statistics** - total registered users and admins
- **Barangay Officials Management** - update official information

## 🚀 Live Demo

Visit the live system: **[https://dvobarangaycms.vip](https://dvobarangaycms.vip)**

### Test Credentials
**User Account:**
- Register with your email and verify via OTP

**Admin Account:**
- Contact system administrator for admin credentials
- Activation Key: Contact administrator

## 📋 Table of Contents

- [Technology Stack](#-technology-stack)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Security Features](#-security-features)
- [Contributing](#-contributing)
- [License](#-license)

## 🛠 Technology Stack

### Backend
- **Framework:** Django 5.1.6
- **Language:** Python 3.12.7
- **Database:** PostgreSQL (Supabase + Railway)
- **ORM:** Django ORM with Supabase integration
- **Authentication:** Django Auth + Custom OTP System

### Frontend
- **HTML5, CSS3, JavaScript (Vanilla)**
- **Responsive Design** - Mobile-first approach
- **Modern UI/UX** with gradient effects and animations

### External Services
- **Email:** SendGrid (Production) / Gmail SMTP (Development)
- **SMS:** PhilSMS API for SMS notifications
- **Database:** Supabase PostgreSQL (Development) / Railway PostgreSQL (Production)
- **Hosting:** Railway Platform
- **Static Files:** WhiteNoise

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
```

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  (HTML/CSS/JS - Responsive Web Application)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Django Application Layer                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Views      │  │  Middleware  │  │    Models    │     │
│  │ (Business    │  │  (Auth &     │  │  (Data       │     │
│  │  Logic)      │  │  Security)   │  │  Structure)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    External Services Layer                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  PostgreSQL  │  │   SendGrid   │  │   PhilSMS    │     │
│  │  (Database)  │  │   (Email)    │  │    (SMS)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

**Main Models:**
- `Complaint` - Core complaint entity with status tracking
- `UserProfile` - Citizen user profiles with verification
- `AdminProfile` - Barangay admin profiles with access control
- `EmailOTP` - OTP codes for email verification
- `ChatConversation` - Admin-user conversations
- `ChatMessage` - Individual chat messages
- `AdminActivityLog` - Audit trail for admin actions

## 📦 Installation

### Prerequisites
- Python 3.12.7 or higher
- PostgreSQL database
- Git

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/DwightBuma-at/CAPSTONE-2_Complaint-Management-System-.git
cd "CAPSTONE-2_Complaint-Management-System-"
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the project root:
```env
# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (Supabase for development)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Email Configuration (Gmail SMTP for development)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# SendGrid Configuration (Production)
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_SENDER_EMAIL=your-verified-sender@domain.com

# PhilSMS Configuration (Optional)
PHILSMS_API_TOKEN=your-philsms-api-token
PHILSMS_SENDER_ID=PHILSMS
```

5. **Run database migrations**
```bash
python manage.py migrate
```

6. **Create superuser (optional)**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

8. **Access the application**
- Main site: http://127.0.0.1:8000/
- Django admin: http://127.0.0.1:8000/admin/

## ⚙️ Configuration

### Email Configuration

**Development (Gmail SMTP):**
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password
3. Add credentials to `.env` file

**Production (SendGrid):**
1. Create a SendGrid account
2. Verify your sender email/domain
3. Generate API key
4. Add to Railway environment variables

### SMS Configuration (PhilSMS)

1. Sign up at [PhilSMS](https://www.philsms.com/)
2. Get your API token
3. Add to environment variables
4. Configure sender ID

### Database Configuration

**Development:** Uses Supabase PostgreSQL
**Production:** Uses Railway PostgreSQL (auto-configured)

## 📖 Usage

### For Citizens

1. **Register an Account**
   - Click "Sign Up" on the homepage
   - Enter your details (name, email, barangay, password)
   - Verify your email with the OTP code sent

2. **Submit a Complaint**
   - Log in to your account
   - Click "Submit Complaint"
   - Fill in complaint details, location, and upload image
   - Receive tracking ID for your complaint

3. **Track Your Complaint**
   - View real-time status updates
   - Chat with barangay officials
   - Receive email/SMS notifications

### For Barangay Admins

1. **Register as Admin**
   - Use the admin registration form
   - Provide activation key (contact superadmin)
   - Set your 6-digit access key
   - Verify email with OTP

2. **Manage Complaints**
   - View all complaints for your barangay
   - Update complaint status with notes
   - Upload resolution images
   - Forward complaints to higher agencies

3. **Communicate with Citizens**
   - Use the chat feature for each complaint
   - Send updates and ask for clarifications

## 🔌 API Documentation

### User Authentication

**Send Verification Code**
```http
POST /api/user/send-verification/
Content-Type: application/json

{
  "email": "user@example.com",
  "full_name": "John Doe",
  "barangay": "Barangay Name",
  "password": "password123",
  "confirm_password": "password123"
}
```

**User Login**
```http
POST /api/user/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### Complaint Management

**Create Complaint**
```http
POST /api/complaints/create/
Content-Type: application/json
Authorization: Session

{
  "barangay": "Barangay Name",
  "complaint_type": "Infrastructure",
  "description": "Road damage description",
  "location": "Street Address",
  "image": "data:image/jpeg;base64,..."
}
```

**List Complaints**
```http
GET /api/complaints/
Authorization: Session
```

### Admin Operations

**Admin Login**
```http
POST /api/admin/login/
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "password123",
  "admin_name": "Admin Name"
}
```

**Update Complaint Status**
```http
PATCH /api/transactions/{tracking_id}/status/
Content-Type: application/json
Authorization: Session

{
  "status": "In Progress",
  "admin_update": "Working on this issue",
  "resolution_image": "data:image/jpeg;base64,..."
}
```

## 🚢 Deployment

### Railway Deployment

This project is configured for automatic deployment on Railway.

1. **Connect GitHub Repository**
   - Link your GitHub repo to Railway
   - Railway auto-detects Django configuration

2. **Configure Environment Variables**
   - Add all required environment variables in Railway dashboard
   - Set `RAILWAY_ENVIRONMENT=production`

3. **Add PostgreSQL Service**
   - Add PostgreSQL plugin in Railway
   - Database URL is auto-configured

4. **Deploy**
   - Push to `main` branch
   - Railway automatically builds and deploys
   - Migrations run automatically via `Procfile`

### Custom Domain Setup

1. Add your domain in Railway settings
2. Configure DNS records:
   - Type: CNAME
   - Name: @ or www
   - Value: Your Railway domain

## 🔒 Security Features

- **Role-Based Access Control** - Separate user and admin authentication
- **Email OTP Verification** - Two-factor authentication for registration and login
- **Password Hashing** - Django's built-in password hashing (PBKDF2)
- **Access Key Protection** - 6-digit access keys for admin accounts
- **CSRF Protection** - Django's CSRF middleware enabled
- **Session Security** - Secure session cookies in production
- **Activity Logging** - Complete audit trail of admin actions
- **Input Validation** - Comprehensive validation on all inputs
- **SQL Injection Protection** - Django ORM prevents SQL injection
- **XSS Protection** - Django's template escaping

## 📊 System Requirements

### Minimum Requirements
- **Server:** 512MB RAM, 1 CPU core
- **Database:** PostgreSQL 12+
- **Python:** 3.12.7+
- **Storage:** 1GB (for base64 image storage)

### Recommended Requirements
- **Server:** 1GB RAM, 2 CPU cores
- **Database:** PostgreSQL 14+
- **Storage:** 5GB+
- **Bandwidth:** 10GB/month

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check database credentials in .env
# Ensure PostgreSQL is running
python manage.py migrate --check
```

**Email Not Sending**
```bash
# Verify email credentials
# Check SendGrid/Gmail configuration
# Review logs for SMTP errors
```

**Static Files Not Loading**
```bash
# Collect static files
python manage.py collectstatic --noinput
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

**Dwight Anthony C. Buma-at**
- GitHub: [@DwightBuma-at](https://github.com/DwightBuma-at)
- Project: Capstone 2 - Complaint Management System

## 🙏 Acknowledgments

- Davao City Government for the inspiration
- Barangay officials for their feedback and support
- All contributors and testers

## 📞 Support

For support, email: complaintmanagementsystem5@gmail.com

## 🗺️ Roadmap

- [ ] Mobile application (iOS/Android)
- [ ] Advanced analytics dashboard
- [ ] Multi-language support (Tagalog, Cebuano)
- [ ] Push notifications
- [ ] Document attachment support
- [ ] Complaint categorization with AI
- [ ] Public complaint map view
- [ ] Integration with social media platforms

## 📸 Screenshots

### Homepage
![Homepage](docs/screenshots/homepage.png)

### User Dashboard
![User Dashboard](docs/screenshots/user-dashboard.png)

### Admin Dashboard
![Admin Dashboard](docs/screenshots/admin-dashboard.png)

### Chat Interface
![Chat Interface](docs/screenshots/chat-interface.png)

---

**Made with ❤️ for the citizens of Davao City**

*Last Updated: November 2025*

