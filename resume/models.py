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


# Resume upload model for admin
class Resume(models.Model):
    title = models.CharField(max_length=200, default="My Resume")
    file = models.FileField(upload_to='myapp/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, help_text="Set as active resume")

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Resume"
        verbose_name_plural = "Resumes"

    def __str__(self):
        return f"{self.title} - {'Active' if self.is_active else 'Inactive'}"

    def save(self, *args, **kwargs):
        # If this resume is set as active, deactivate all others
        if self.is_active:
            Resume.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
