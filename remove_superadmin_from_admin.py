#!/usr/bin/env python3
"""
Remove dacbuma-at@addu.edu.ph from AdminProfile and verify data
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

print('===== REMOVING SUPERADMIN FROM ADMIN PROFILE =====\n')

try:
    superadmin = User.objects.get(email='dacbuma-at@addu.edu.ph')
    
    # Remove from AdminProfile
    try:
        admin_profile = superadmin.admin_profile
        barangay = admin_profile.barangay
        admin_profile.delete()
        print(f'✅ Removed Admin Profile for {superadmin.email}')
        print(f'   Barangay: {barangay}')
    except AdminProfile.DoesNotExist:
        print(f'⚠️  No AdminProfile found for {superadmin.email}')
    
    # Ensure user is still superuser but not staff admin
    superadmin.is_staff = False
    superadmin.is_superuser = True
    superadmin.save()
    
    print(f'\n✅ Updated user status:')
    print(f'   Email: {superadmin.email}')
    print(f'   is_staff: {superadmin.is_staff}')
    print(f'   is_superuser: {superadmin.is_superuser}')
    
except User.DoesNotExist:
    print('❌ Superadmin not found!')

print('\n===== VERIFYING DATA IN SUPABASE =====\n')

print(f'✅ Total Admins (AdminProfile): {AdminProfile.objects.count()}')
print(f'✅ Total Users: {User.objects.count()}')
print(f'✅ Total User Profiles: {UserProfile.objects.count()}')
print(f'✅ Total Complaints: {Complaint.objects.count()}')

print('\n===== SAMPLE ADMIN DATA =====')
for admin in AdminProfile.objects.all()[:5]:
    print(f'  - {admin.user.email} ({admin.barangay})')

print('\n===== SAMPLE COMPLAINTS =====')
for complaint in Complaint.objects.all()[:5]:
    print(f'  - {complaint.tracking_id} ({complaint.status}) - {complaint.barangay}')
