from django.urls import path


from .views import (
    home,
    about,
    projects,
    experience,
    certificate,
    contact,
    success_view,
    resume,
    email_resume,
    analytics_dashboard,
    profile,
    register,
    verify_email,
    resend_verification,
    CustomLoginView,
)


urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('projects/', projects, name='projects'),
    path('experience/', experience, name='experience'),
    path('contact/', contact, name='contact'),
    path('resume/', resume, name='resume'),
    path('email-resume/', email_resume, name='email_resume'),
    path('analytics/', analytics_dashboard, name='analytics_dashboard'),
    path('profile/', profile, name='profile'),
    path('register/', register, name='register'),
    path('verify-email/<uuid:token>/', verify_email, name='verify_email'),
    path('registration-success/', lambda request: __import__('django.shortcuts').shortcuts.render(request, 'registration_success.html'), name='registration_success'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('resend-verification/', resend_verification, name='resend_verification'),
    path('logout/',
        __import__('django.contrib.auth.views').contrib.auth.views.LogoutView.as_view(next_page='home'),
        name='logout'),
    path('success/', success_view, name='success'),
    path('certificate/', certificate, name='certificate'),
]





