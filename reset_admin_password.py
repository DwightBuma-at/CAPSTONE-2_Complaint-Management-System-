#!/usr/bin/env python3
"""
Reset Admin Password Tool
"""

import os
import sys
import django

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

def reset_admin_password(email, new_password):
    """Reset admin password"""
    try:
        # Find the admin user
        admin = User.objects.get(email=email)
        
        # Set new password
        admin.set_password(new_password)
        admin.save()
        
        print("✅ Password reset successful!")
        print(f"📧 Email: {admin.email}")
        print(f"👤 Username: {admin.username}")
        print(f"🔑 New Password: {new_password}")
        print("=" * 50)
        print("You can now login with these credentials.")
        
    except User.DoesNotExist:
        print(f"❌ Admin not found with email: {email}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🔐 Admin Password Reset Tool")
    print("=" * 40)
    
    email = "33dpoblacion@gmail.com"
    new_password = "admin8"  # You can change this to any password you want
    
    print(f"🔍 Resetting password for: {email}")
    print(f"🔑 New password will be: {new_password}")
    print()
    
    reset_admin_password(email, new_password)

if __name__ == "__main__":
    main()
