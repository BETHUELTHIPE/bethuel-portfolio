from django.contrib import admin

from .models import Contact, EmailVerification, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'cell_number', 'address', 'resume_download_count', 'resume_email_count')
    search_fields = ('user__username', 'user__email', 'cell_number')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'submitted_at')
    search_fields = ('name', 'email')
    list_filter = ('submitted_at',)


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'is_verified', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('is_verified', 'created_at')
