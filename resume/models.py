from django.db import models




from django.contrib.auth.models import User
import uuid

# UserProfile for extra registration fields
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cell_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    resume_download_count = models.PositiveIntegerField(default=0)
    resume_email_count = models.PositiveIntegerField(default=0)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    biography = models.TextField(blank=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Email verification model
class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Verification for {self.user.username}"
