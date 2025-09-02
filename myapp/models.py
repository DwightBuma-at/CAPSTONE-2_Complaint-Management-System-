from django.db import models
from django.contrib.auth import get_user_model


class Complaint(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        IN_PROGRESS = "In Progress", "In Progress"
        RESOLVED = "Resolved", "Resolved"

    tracking_id = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='complaints', null=True, blank=True)
    user_full_name = models.CharField(max_length=255, null=True, blank=True)  # Store user's full name for admin view
    user_barangay = models.CharField(max_length=120, null=True, blank=True)  # Store user's barangay for admin view
    barangay = models.CharField(max_length=120)
    complaint_type = models.CharField(max_length=120)
    description = models.TextField()
    location = models.CharField(max_length=255)
    # Store uploaded image as base64 string for now to avoid MEDIA config changes
    image_base64 = models.TextField(blank=True, null=True)
    # Store resolution image as base64 string for resolved cases
    resolution_image = models.TextField(blank=True, null=True, help_text='Base64 image showing evidence of resolution')
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.tracking_id} — {self.complaint_type} ({self.status})"


class AdminProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="admin_profile")
    barangay = models.CharField(max_length=120)
    access_key_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"AdminProfile({self.user.get_username()} — {self.barangay})"


class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="user_profile")
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)
    barangay = models.CharField(max_length=120)
    password = models.CharField(max_length=128, null=True, blank=True)  # Store hashed password
    email_verified = models.BooleanField(default=False)
    profile_picture = models.TextField(blank=True, null=True)  # Store base64 image data
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"UserProfile({self.full_name} — {self.email} — {self.barangay})"


class EmailOTP(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"OTP for {self.email} ({self.otp_code})"

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at


class ChatConversation(models.Model):
    """Represents a chat conversation between admin and user"""
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='chat_conversations')
    admin = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='admin_conversations')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = ['complaint', 'admin', 'user']

    def __str__(self) -> str:
        return f"Chat: {self.complaint.tracking_id} - {self.admin.email} & {self.user.email}"
    
    def update_timestamp(self):
        """Update the updated_at timestamp to current time"""
        from django.utils import timezone
        self.updated_at = timezone.now()
        self.save(update_fields=['updated_at'])


class ChatMessage(models.Model):
    """Individual messages in a chat conversation"""
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_admin_message = models.BooleanField(default=False)  # True if sent by admin, False if by user
    is_read = models.BooleanField(default=False)  # Track if message has been read by admin
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        sender_type = "Admin" if self.is_admin_message else "User"
        return f"{sender_type} message in {self.conversation.complaint.tracking_id}"

