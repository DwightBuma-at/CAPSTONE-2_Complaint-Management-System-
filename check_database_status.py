#!/usr/bin/env python3
"""
Check and restore Supabase database data
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
from myapp.models import AdminProfile, UserProfile, Complaint

User = get_user_model()

print('===== DATABASE STATUS CHECK =====\n')

print('USERS:')
user_count = User.objects.count()
print(f'  Total: {user_count}')
for user in User.objects.all()[:10]:
    print(f'    - {user.email} (staff: {user.is_staff}, superuser: {user.is_superuser})')

print('\nADMIN PROFILES:')
admin_count = AdminProfile.objects.count()
print(f'  Total: {admin_count}')
for admin in AdminProfile.objects.all()[:10]:
    print(f'    - {admin.user.email} ({admin.barangay})')

print('\nUSER PROFILES:')
user_profile_count = UserProfile.objects.count()
print(f'  Total: {user_profile_count}')
for userprofile in UserProfile.objects.all()[:10]:
    print(f'    - {userprofile.full_name} ({userprofile.email})')

print('\nCOMPLAINTS:')
complaint_count = Complaint.objects.count()
print(f'  Total: {complaint_count}')
for complaint in Complaint.objects.all()[:10]:
    print(f'    - {complaint.tracking_id} ({complaint.status})')

# Check if superadmin exists
print('\n===== SUPERADMIN CHECK =====')
try:
    superadmin = User.objects.get(email='dacbuma-at@addu.edu.ph')
    print(f'✅ Superadmin exists: {superadmin.email}')
    print(f'   - is_staff: {superadmin.is_staff}')
    print(f'   - is_superuser: {superadmin.is_superuser}')
    
    try:
        admin_profile = superadmin.admin_profile
        print(f'   - Admin Profile: {admin_profile.barangay}')
    except AdminProfile.DoesNotExist:
        print(f'   ⚠️  No Admin Profile found!')
except User.DoesNotExist:
    print('❌ Superadmin does not exist!')
