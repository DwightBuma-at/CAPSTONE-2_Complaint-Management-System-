#!/usr/bin/env python3
"""
Remove dacbuma-at@addu.edu.ph from AdminProfile completely
Keep only as superuser for superadmin dashboard
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

print('===== REMOVING ADMIN ACCOUNT FOR SUPERADMIN =====\n')

try:
    superadmin = User.objects.get(email='dacbuma-at@addu.edu.ph')
    
    print(f'✅ Found superadmin user: {superadmin.email}')
    
    # Remove from AdminProfile (if exists)
    try:
        admin_profile = superadmin.admin_profile
        admin_profile.delete()
        print(f'✅ Removed AdminProfile for {superadmin.email}')
    except AdminProfile.DoesNotExist:
        print(f'ℹ️  No AdminProfile found (already removed)')
    
    # Ensure user is SUPERUSER but NOT STAFF (so can't login as admin)
    superadmin.is_staff = False
    superadmin.is_superuser = True
    superadmin.is_active = True
    superadmin.save()
    
    print(f'\n✅ User account configured correctly:')
    print(f'   Email: {superadmin.email}')
    print(f'   is_staff: {superadmin.is_staff} (NOT an admin account)')
    print(f'   is_superuser: {superadmin.is_superuser} (Can access superadmin dashboard)')
    print(f'   is_active: {superadmin.is_active}')
    
    print(f'\n✅ {superadmin.email} is NOW ONLY a Superadmin')
    print(f'   - Cannot login as regular admin')
    print(f'   - Can access superadmin dashboard')
    
except User.DoesNotExist:
    print('❌ Superadmin user not found!')
except Exception as e:
    print(f'❌ Error: {e}')
