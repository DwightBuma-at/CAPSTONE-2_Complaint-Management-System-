from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # http://127.0.0.1:8000/
    path('index.html', views.home, name='index'),  # Alias for home
    path('user.html', views.user_page, name='user'),
    path('user-submit.html', views.user_submit, name='user_submit'),
    path('user-view.html', views.user_view, name='user_view'),
    path('user-history.html', views.user_history, name='user_history'),
    # API endpoints
    path('api/complaints/', views.list_complaints, name='complaints_list'),
    path('api/complaints/history/', views.list_complaints_history, name='complaints_history'),
    path('api/complaints/create/', views.create_complaint, name='complaints_create'),
    path('api/complaints/<str:tracking_id>/', views.complaint_detail, name='complaint_detail'),
    path('api/complaints/', views.fetch_complaints, name='fetch_complaints'),
    
    # User Registration & Auth API endpoints
    path('api/user/send-verification/', views.send_verification_code, name='send_verification_code'),
    path('api/user/verify-email/', views.verify_email_and_register, name='verify_email_and_register'),
    path('api/user/login/', views.user_login, name='user_login'),
    path('api/user/verify-login-otp/', views.verify_login_otp, name='verify_login_otp'),
    path('api/user/resend-verification/', views.resend_verification_code, name='resend_verification_code'),
    
    # Transaction API endpoints (now using complaints)
    path('api/transactions/', views.list_transactions, name='transactions_list'),
    path('api/transactions/<str:tracking_id>/', views.transaction_detail, name='transaction_detail'),
    path('api/transactions/<str:tracking_id>/status/', views.update_transaction_status, name='update_transaction_status'),

    # Admin auth
    path('api/admin/login/', views.admin_login, name='admin_login'),
    path('api/admin/logout/', views.admin_logout, name='admin_logout'),
    path('api/admin/me/', views.admin_me, name='admin_me'),
    path('api/admin/register/', views.admin_register, name='admin_register'),
    
    # Admin Registration & Auth API endpoints
    path('api/admin/send-verification/', views.admin_send_verification_code, name='admin_send_verification_code'),
    path('api/admin/verify-email/', views.admin_verify_email_and_register, name='admin_verify_email_and_register'),
    path('api/admin/verify-access-key/', views.admin_verify_access_key, name='admin_verify_access_key'),

    # Admin dashboard
    path('admin-dashboard.html/', views.admin_dashboard, name='admin_dashboard'),
    
    # Superadmin dashboard
    path('superadmin.html/', views.superadmin_dashboard, name='superadmin_dashboard'),
    
    # Superadmin API endpoints
    path('api/superadmin/admins/', views.superadmin_list_admins, name='superadmin_list_admins'),
    path('api/superadmin/users/', views.superadmin_list_users, name='superadmin_list_users'),
    path('api/superadmin/stats/', views.superadmin_stats, name='superadmin_stats'),
    path('api/superadmin/admin/<int:admin_id>/', views.superadmin_admin_details, name='superadmin_admin_details'),
    path('api/superadmin/update-officials/', views.update_admin_officials, name='update_admin_officials'),

    # Admin complaints and users management
    path('admin-complaints.html/', views.admin_complaints, name='admin_complaints'),
    path('admin-history.html/', views.admin_history, name='admin_history'),
    path('admin-user.html/', views.admin_user, name='admin_user'),
    path('admin-chat.html/', views.admin_chat, name='admin_chat'),
    
    # Contact form
    path('api/contact/', views.contact_form_submission, name='contact_form_submission'),
    
    # Admin recovery
    path('api/admin/recovery-info/', views.admin_recovery_info, name='admin_recovery_info'),
    path('api/admin/get-data/', views.get_admin_data, name='get_admin_data'),
    
    # Profile picture API endpoints
    path('api/user/save-profile-picture/', views.save_profile_picture, name='save_profile_picture'),
    path('api/user/get-profile-picture/', views.get_profile_picture, name='get_profile_picture'),
    
    # User authentication check
    path('api/user/check-auth/', views.check_user_auth, name='check_user_auth'),
    
    # Registered barangays endpoint
    path('api/barangays/registered/', views.get_registered_barangays, name='get_registered_barangays'),
    
    # Admin users management
    path('api/admin/users/', views.list_users_for_admin, name='list_users_for_admin'),
    path('api/admin/users/<int:user_id>/delete/', views.delete_user_for_admin, name='delete_user_for_admin'),
    
    # Chat functionality
    path('api/admin/chat/send/', views.send_chat_message, name='send_chat_message'),
    path('api/admin/chat/<str:complaint_id>/messages/', views.get_chat_messages, name='get_chat_messages'),
    path('api/admin/chat/<str:complaint_id>/delete/', views.delete_admin_chat, name='delete_admin_chat'),
    path('api/admin/chat/list/', views.get_admin_chat_list, name='get_admin_chat_list'),
    
    # Debug endpoint
    path('api/admin/chat/test/', views.test_chat_delete, name='test_chat_delete'),
    
    # User chat functionality
    path('api/user/chat/list/', views.get_user_chat_list, name='get_user_chat_list'),
    path('api/user/chat/<str:complaint_id>/messages/', views.get_user_chat_messages, name='get_user_chat_messages'),
    path('api/user/chat/send/', views.send_user_chat_message, name='send_user_chat_message'),
    
    # Admin activity log
    path('api/admin/complaint/<str:tracking_id>/activity/', views.get_complaint_activity_log, name='get_complaint_activity_log'),
    
    # User complaint activity
    path('api/user/complaint/<str:tracking_id>/activity/', views.get_user_complaint_activity, name='get_user_complaint_activity'),
    
    # Health check for Railway debugging
    path('health/', views.health_check, name='health_check'),
]
