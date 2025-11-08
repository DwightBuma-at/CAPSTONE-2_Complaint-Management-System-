#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Profile Pictures for Survey Users
Debug tool to see what profile pictures are stored for each user
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

from myapp.models import UserProfile

def check_all_profile_pictures():
    """
    Check all profile pictures in the database
    """
    print("=" * 70)
    print("PROFILE PICTURES DATABASE CHECK")
    print("=" * 70)
    print()
    
    # Get all user profiles
    profiles = UserProfile.objects.all().order_by('email')
    
    if not profiles.exists():
        print("No user profiles found in database.")
        return
    
    print(f"Found {profiles.count()} user profiles:")
    print()
    print(f"{'#':<3} {'Email':<35} {'Full Name':<20} {'Has Picture':<12} {'Picture Length':<15}")
    print("-" * 90)
    
    for idx, profile in enumerate(profiles, 1):
        has_picture = "✅ Yes" if profile.profile_picture else "❌ No"
        picture_length = len(profile.profile_picture) if profile.profile_picture else 0
        
        print(f"{idx:<3} {profile.email:<35} {profile.full_name:<20} {has_picture:<12} {picture_length:<15}")
    
    print()
    print("=" * 70)
    
    # Check for duplicate profile pictures
    print("CHECKING FOR DUPLICATE PROFILE PICTURES...")
    print()
    
    picture_map = {}
    for profile in profiles:
        if profile.profile_picture:
            if profile.profile_picture in picture_map:
                picture_map[profile.profile_picture].append(profile.email)
            else:
                picture_map[profile.profile_picture] = [profile.email]
    
    duplicates_found = False
    for picture_data, emails in picture_map.items():
        if len(emails) > 1:
            duplicates_found = True
            print(f"⚠️  DUPLICATE FOUND:")
            print(f"   Picture length: {len(picture_data)} characters")
            print(f"   Shared by: {', '.join(emails)}")
            print()
    
    if not duplicates_found:
        print("✅ No duplicate profile pictures found.")
    
    print("=" * 70)


def check_specific_user(email):
    """
    Check profile picture for a specific user
    """
    email = email.strip().lower()
    
    print("=" * 70)
    print("SPECIFIC USER PROFILE PICTURE CHECK")
    print("=" * 70)
    print(f"Email: {email}")
    print()
    
    try:
        profile = UserProfile.objects.get(email__iexact=email)
        
        print(f"✅ User found: {profile.full_name}")
        print(f"📍 Barangay: {profile.barangay}")
        print()
        
        if profile.profile_picture:
            print(f"📷 Profile Picture Status: ✅ Has picture")
            print(f"📏 Picture Length: {len(profile.profile_picture)} characters")
            print(f"🔍 First 50 chars: {profile.profile_picture[:50]}...")
            print(f"🔍 Last 50 chars: ...{profile.profile_picture[-50:]}")
            
            # Check if this picture is used by other users
            same_picture_users = UserProfile.objects.filter(profile_picture=profile.profile_picture)
            if same_picture_users.count() > 1:
                print()
                print("⚠️  WARNING: This picture is shared with other users:")
                for user in same_picture_users:
                    if user.email != email:
                        print(f"   - {user.email} ({user.full_name})")
            else:
                print()
                print("✅ This picture is unique to this user.")
        else:
            print(f"📷 Profile Picture Status: ❌ No picture")
            print("   User will see default avatar.")
        
    except UserProfile.DoesNotExist:
        print(f"❌ No user found with email: {email}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        # Check specific user
        email = sys.argv[1]
        check_specific_user(email)
    else:
        # Check all users
        check_all_profile_pictures()
