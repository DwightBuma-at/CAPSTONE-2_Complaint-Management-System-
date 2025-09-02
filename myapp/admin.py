from django.contrib import admin
from .models import Complaint, AdminProfile, UserProfile, EmailOTP, ChatConversation, ChatMessage

# Register your models here.
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['tracking_id', 'user_full_name', 'barangay', 'complaint_type', 'status', 'created_at']
    list_filter = ['status', 'barangay', 'complaint_type', 'created_at']
    search_fields = ['tracking_id', 'user_full_name', 'description']
    readonly_fields = ['tracking_id', 'created_at']
    ordering = ['-created_at']


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'barangay', 'created_at']
    list_filter = ['barangay', 'created_at']
    search_fields = ['user__username', 'user__email', 'barangay']
    readonly_fields = ['created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'barangay', 'email_verified', 'created_at']
    list_filter = ['barangay', 'email_verified', 'created_at']
    search_fields = ['full_name', 'email', 'barangay']
    readonly_fields = ['created_at']


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ['email', 'otp_code', 'is_used', 'created_at', 'expires_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['email']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'admin', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['complaint__tracking_id', 'admin__email', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'is_admin_message', 'content', 'created_at']
    list_filter = ['is_admin_message', 'created_at']
    search_fields = ['content', 'sender__email']
    readonly_fields = ['created_at']
