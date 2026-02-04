#!/usr/bin/env python3
"""
Fix superadmin user status and ensure proper setup
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
from myapp.models import AdminProfile

User = get_user_model()

try:
    superadmin = User.objects.get(email='dacbuma-at@addu.edu.ph')
    
    # Ensure superadmin is properly configured
    superadmin.is_staff = True
    superadmin.is_superuser = True
    superadmin.save()
    
    print('✅ Superadmin user status updated:')
    print(f'   Email: {superadmin.email}')
    print(f'   Username: {superadmin.username}')
    print(f'   is_staff: {superadmin.is_staff}')
    print(f'   is_superuser: {superadmin.is_superuser}')
    
    # Check AdminProfile
    try:
        admin_profile = superadmin.admin_profile
        print(f'   Admin Profile Barangay: {admin_profile.barangay}')
    except AdminProfile.DoesNotExist:
        print('   ⚠️  Creating new Admin Profile...')
        admin_profile = AdminProfile.objects.create(
            user=superadmin,
            barangay='Poblacion 36-D'
        )
        print(f'   ✅ Admin Profile created: {admin_profile.barangay}')
    
except User.DoesNotExist:
    print('❌ Superadmin not found!')
except Exception as e:
    print(f'❌ Error: {e}')
