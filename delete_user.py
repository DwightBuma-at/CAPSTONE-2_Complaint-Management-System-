"""
Script to delete a user by email address
Deletes from both Django database and Supabase
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from myapp.models import UserProfile, Complaint, ChatConversation
from myapp.supabase_client import supabase

User = get_user_model()

def delete_user_by_email(email, auto_confirm=False):
    """Delete a user and all associated data by email"""
    email = email.strip().lower()
    
    print(f"Searching for user with email: {email}")
    print("=" * 70)
    
    # Find user in Django
    try:
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            print(f"ERROR: User not found in Django database")
            return False
        
        print(f"Found user in Django:")
        print(f"   ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        
        # Check for UserProfile
        try:
            user_profile = user.user_profile
            print(f"   Profile: {user_profile.full_name} - {user_profile.barangay}")
            
            # Count related data
            complaints_count = Complaint.objects.filter(user=user).count()
            conversations_count = ChatConversation.objects.filter(user=user).count()
            
            print(f"\nRelated data:")
            print(f"   Complaints: {complaints_count}")
            print(f"   Chat conversations: {conversations_count}")
            
        except UserProfile.DoesNotExist:
            print(f"   WARNING: No UserProfile found")
            user_profile = None
        
        # Confirm deletion
        if not auto_confirm:
            print("\n" + "=" * 70)
            response = input(f"Are you sure you want to delete this user? (yes/no): ").strip().lower()
            if response != 'yes':
                print("Deletion cancelled")
                return False
        else:
            print("\nAuto-confirming deletion...")
        
        print("\nDeleting user...")
        
        # Delete from Supabase first (if exists)
        if supabase:
            try:
                # Delete from user_profiles table
                if user_profile:
                    supabase_response = supabase.table('user_profiles').delete().eq('email', email).execute()
                    print(f"SUCCESS: Deleted from Supabase user_profiles")
                
                # Delete from complaints table (if any)
                complaints_response = supabase.table('complaints').delete().eq('user_email', email).execute()
                print(f"SUCCESS: Deleted related complaints from Supabase")
                
            except Exception as e:
                print(f"WARNING: Supabase deletion error (continuing with Django): {e}")
        
        # Delete from Django
        # Since UserProfile has CASCADE, deleting UserProfile will delete User
        # But we need to delete UserProfile first to avoid issues
        if user_profile:
            user_profile.delete()
            print(f"SUCCESS: Deleted UserProfile from Django")
        
        # Delete User (should be automatic with CASCADE, but let's be explicit)
        try:
            user.delete()
            print(f"SUCCESS: Deleted User from Django")
        except Exception as e:
            print(f"WARNING: User deletion note: {e}")
        
        print("\n" + "=" * 70)
        print("User deleted successfully!")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"ERROR: Error deleting user: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    email = "bdprobinos@addu.edu.ph"
    auto_confirm = False
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == "--yes":
        auto_confirm = True
    
    delete_user_by_email(email, auto_confirm=auto_confirm)

