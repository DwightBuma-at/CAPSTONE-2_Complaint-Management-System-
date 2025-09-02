#!/usr/bin/env python
"""
Supabase Database Setup Script
This script helps you configure Supabase as your main Django database
"""
import os
import sys

def create_env_file():
    """Create .env file with Supabase database credentials"""
    print("🔧 Setting up Supabase as main database...")
    print("\nPlease provide your Supabase database credentials:")
    
    # Get Supabase URL (for API)
    supabase_url = input("Enter your Supabase Project URL (e.g., https://dfcaiybfnrhyitofdxug.supabase.co): ").strip()
    if not supabase_url:
        print("❌ Supabase URL is required!")
        return False
    
    # Get Supabase Key (for API)
    supabase_key = input("Enter your Supabase Anon Key (starts with 'eyJ...'): ").strip()
    if not supabase_key:
        print("❌ Supabase Key is required!")
        return False
    
    # Get Database Password
    print("\n📋 From your Supabase connection dialog, copy the password from:")
    print("postgresql://postgres:[YOUR-PASSWORD]@db.dfcaiybfnrhyitofdxug.supabase.co")
    db_password = input("Enter your Supabase Database Password: ").strip()
    if not db_password:
        print("❌ Database password is required!")
        return False
    
    # Create .env file content
    env_content = f"""# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_KEY={supabase_key}

# Supabase Database Configuration (for Django ORM)
SUPABASE_DB_PASSWORD={db_password}
SUPABASE_DB_HOST=db.dfcaiybfnrhyitofdxug.supabase.co

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

def test_database_connection():
    """Test the Supabase database connection"""
    print("\n🧪 Testing Supabase database connection...")
    
    try:
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
        import django
        django.setup()
        
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Connected to PostgreSQL: {version[0]}")
        
        # Test if we can access the database
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()
            print(f"✅ Connected to database: {db_name[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing database connection: {e}")
        return False

def create_complaints_table():
    """Create the complaints table using Django migrations"""
    print("\n📋 Creating complaints table in Supabase...")
    
    try:
        # Run migrations
        os.system("python manage.py makemigrations")
        os.system("python manage.py migrate")
        print("✅ Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

def main():
    print("🚀 Supabase Database Setup for Complaint Management System")
    print("=" * 60)
    
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
    if test_database_connection():
        print("\n🎉 Database connection successful!")
        
        # Create table
        if create_complaints_table():
            print("\n🎉 Setup completed successfully!")
            print("\n✅ Now your models.py will directly control Supabase tables!")
            print("\nNext steps:")
            print("1. Run 'python manage.py runserver' to start your application")
            print("2. Any changes to models.py will now affect Supabase tables")
            print("3. Use 'python manage.py makemigrations' and 'python manage.py migrate' to update tables")
        else:
            print("\n❌ Failed to create tables. Please check your database permissions.")
    else:
        print("\n❌ Database connection failed. Please check your credentials.")

if __name__ == "__main__":
    main()
