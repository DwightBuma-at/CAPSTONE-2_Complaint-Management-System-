#!/usr/bin/env python3
"""
Update superadmin access key to 000000
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
from myapp.models import AdminProfile

User = get_user_model()

try:
    admin_user = User.objects.get(email='dacbuma-at@addu.edu.ph')
    
    # Update or create AdminProfile with new access key
    admin_profile, created = AdminProfile.objects.get_or_create(user=admin_user)
    admin_profile.access_key_hash = make_password('000000')
    admin_profile.save()
    
    print('✅ Admin Access Key updated successfully!')
    print(f'📧 Email: {admin_user.email}')
    print(f'🔑 New Admin Access Key: 000000')
    print(f'   Status: {"Created" if created else "Updated"} Admin Profile')
    
except User.DoesNotExist:
    print('❌ Admin user not found with email: dacbuma-at@addu.edu.ph')
except Exception as e:
    print(f'❌ Error: {e}')
