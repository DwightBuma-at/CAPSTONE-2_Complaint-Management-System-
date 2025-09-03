from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from myapp.models import AdminProfile
import hashlib
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup production environment with admin user and admin profile'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Setting up production environment...'))
        
        # Create superuser if doesn't exist
        if not User.objects.filter(is_superuser=True).exists():
            try:
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@complaintmanagement.com',
                    password='ComplaintAdmin2025!'
                )
                self.stdout.write(self.style.SUCCESS('✅ Created superuser: admin'))
                self.stdout.write(self.style.WARNING('   Username: admin'))
                self.stdout.write(self.style.WARNING('   Password: ComplaintAdmin2025!'))
                
                # Create AdminProfile for the superuser
                admin_profile = AdminProfile.objects.create(
                    user=admin_user,
                    barangay='Central Admin',
                    access_key_hash=hashlib.sha256('admin2025'.encode()).hexdigest()
                )
                self.stdout.write(self.style.SUCCESS('✅ Created AdminProfile for superuser'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error creating superuser: {e}'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Superuser already exists'))
        
        # Display setup information
        self.stdout.write(self.style.SUCCESS('\n🎉 Production setup complete!'))
        self.stdout.write(self.style.SUCCESS('📋 Admin Login Details:'))
        self.stdout.write(self.style.WARNING('   URL: /admin/'))
        self.stdout.write(self.style.WARNING('   Username: admin'))
        self.stdout.write(self.style.WARNING('   Password: ComplaintAdmin2025!'))
        self.stdout.write(self.style.SUCCESS('\n📱 Your app is ready to use!'))
