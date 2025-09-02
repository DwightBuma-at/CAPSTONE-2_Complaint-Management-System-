import os
from django.conf import settings
from supabase import create_client, Client

# Get Supabase credentials from Django settings
SUPABASE_URL = getattr(settings, 'SUPABASE_URL', os.getenv("SUPABASE_URL"))
SUPABASE_KEY = getattr(settings, 'SUPABASE_KEY', os.getenv("SUPABASE_KEY"))

# Initialize Supabase client
supabase: Client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Supabase client: {e}")
        supabase = None
else:
    print("⚠️  Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
    supabase = None
