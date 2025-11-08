#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick User Creation Script for Research Survey
Creates verified user accounts directly in the database
"""

import os
import sys
import django

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from myapp.models import UserProfile

User = get_user_model()

def create_survey_user(full_name, email, barangay, password):
    """
    Create a verified user account for survey purposes
    
    Args:
        full_name: User's full name
        email: User's email address
        barangay: User's barangay
        password: User's password (will be hashed)
    """
    email = email.strip().lower()
    
    print("=" * 70)
    print("CREATING SURVEY USER ACCOUNT")
    print("=" * 70)
    print(f"Full Name: {full_name}")
    print(f"Email: {email}")
    print(f"Barangay: {barangay}")
    print(f"Password: {'*' * len(password)}")
    print()
    
    # Check if user already exists
    if User.objects.filter(email__iexact=email).exists():
        print(f"❌ ERROR: Email '{email}' is already registered!")
        print(f"   Please use a different email address.")
        return False
    
    if UserProfile.objects.filter(email__iexact=email).exists():
        print(f"❌ ERROR: Email '{email}' already exists in UserProfile!")
        return False
    
    try:
        # Create username from email
        username = email.split('@')[0]
        base_username = username
        idx = 1
        while User.objects.filter(username=username).exists():
            idx += 1
            username = f"{base_username}{idx}"
        
        print(f"📝 Creating Django User with username: {username}")
        
        # Create Django User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        print(f"✅ Django User created successfully (ID: {user.id})")
        
        # Create UserProfile with verified email
        print(f"📝 Creating UserProfile...")
        user_profile = UserProfile.objects.create(
            user=user,
            full_name=full_name,
            email=email,
            barangay=barangay,
            password=make_password(password),
            email_verified=True  # Mark as verified to skip OTP
        )
        
        print(f"✅ UserProfile created successfully (ID: {user_profile.id})")
        print()
        print("=" * 70)
        print("✨ USER ACCOUNT CREATED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print("📋 Login Credentials:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print()
        print("🌐 The user can now login at: http://localhost:8000")
        print("   OR: https://your-railway-app.railway.app")
        print()
        print("✅ Email is already verified - no OTP required!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to create user account!")
        print(f"   Error details: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False


def create_multiple_users():
    """
    Interactive mode to create multiple users
    """
    print("\n" + "=" * 70)
    print("BULK USER CREATION FOR SURVEY")
    print("=" * 70)
    print("This tool helps you quickly create user accounts for your research survey.")
    print()
    
    users_created = 0
    
    while True:
        print("\n" + "-" * 70)
        print(f"Users created so far: {users_created}/50")
        print("-" * 70)
        print()
        
        full_name = input("Full Name (or 'q' to quit): ").strip()
        if full_name.lower() == 'q':
            break
        
        email = input("Email: ").strip().lower()
        if not email:
            print("❌ Email is required!")
            continue
        
        barangay = input("Barangay: ").strip()
        if not barangay:
            print("❌ Barangay is required!")
            continue
        
        password = input("Password: ").strip()
        if not password:
            print("❌ Password is required!")
            continue
        
        if len(password) < 6:
            print("❌ Password must be at least 6 characters!")
            continue
        
        # Create the user
        if create_survey_user(full_name, email, barangay, password):
            users_created += 1
        
        print()
        continue_prompt = input("Create another user? (y/n): ").strip().lower()
        if continue_prompt != 'y':
            break
    
    print()
    print("=" * 70)
    print(f"SUMMARY: {users_created} user(s) created successfully!")
    print("=" * 70)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("QUICK USER CREATION SCRIPT FOR RESEARCH SURVEY")
    print("=" * 70)
    print()
    
    # Check if command line arguments provided
    if len(sys.argv) == 5:
        # Direct creation mode
        full_name = sys.argv[1]
        email = sys.argv[2]
        barangay = sys.argv[3]
        password = sys.argv[4]
        
        create_survey_user(full_name, email, barangay, password)
    else:
        # Interactive mode
        print("MODE 1: Direct Command Line")
        print("  Usage: python create_survey_user.py \"Full Name\" \"email@example.com\" \"Barangay\" \"password\"")
        print()
        print("MODE 2: Interactive Mode (Current)")
        print("  Enter user details when prompted")
        print()
        
        create_multiple_users()

