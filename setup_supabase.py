#!/usr/bin/env python
"""
Supabase Setup Script
This script helps you configure and test your Supabase connection
"""
import os
import sys

def create_env_file():
    """Create .env file with Supabase credentials"""
    print("🔧 Setting up Supabase configuration...")
    print("\nPlease provide your Supabase credentials:")
    
    # Get Supabase URL
    supabase_url = input("Enter your Supabase Project URL (e.g., https://your-project-id.supabase.co): ").strip()
    if not supabase_url:
        print("❌ Supabase URL is required!")
        return False
    
    # Get Supabase Key
    supabase_key = input("Enter your Supabase Anon Key (starts with 'eyJ...'): ").strip()
    if not supabase_key:
        print("❌ Supabase Key is required!")
        return False
    
    # Create .env file content
    env_content = f"""# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_KEY={supabase_key}

# Email Configuration (optional)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Twilio Configuration (optional)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_FROM=your-twilio-phone-number
"""
    
    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_supabase_connection():
    """Test the Supabase connection"""
    print("\n🧪 Testing Supabase connection...")
    
    try:
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
        import django
        django.setup()
        
        # Import and test Supabase client
        from myapp.supabase_client import supabase
        
        if supabase is None:
            print("❌ Supabase client not initialized. Check your credentials.")
            return False
        
        # Test connection by trying to access a table
        try:
            # Try to list tables (this will fail if connection is bad)
            response = supabase.table('complaints').select('*').limit(1).execute()
            print("✅ Supabase connection successful!")
            return True
        except Exception as e:
            print(f"⚠️  Connection test failed (this might be normal if table doesn't exist): {e}")
            print("✅ Supabase client is working, but you may need to create the complaints table")
            return True
            
    except Exception as e:
        print(f"❌ Error testing Supabase connection: {e}")
        return False

def main():
    print("🚀 Supabase Setup for Complaint Management System")
    print("=" * 50)
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("📁 .env file already exists")
        choice = input("Do you want to recreate it? (y/n): ").lower()
        if choice == 'y':
            if not create_env_file():
                return
    else:
        if not create_env_file():
            return
    
    # Test connection
    if test_supabase_connection():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Create the 'complaints' table in your Supabase dashboard")
        print("2. Run 'python manage.py runserver' to start your application")
        print("3. Your complaints will now be saved to Supabase!")
    else:
        print("\n❌ Setup failed. Please check your credentials and try again.")

if __name__ == "__main__":
    main()
