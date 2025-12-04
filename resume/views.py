from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login as auth_login
from .forms import ContactForm
from .models import Contact, EmailVerification, UserProfile
from .forms_registration import CustomUserCreationForm
from .forms_profile import ProfileForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta

from .tasks import send_verification_email_task, send_resume_email_task


# Home view
def home(request):
    return render(request, "home.html")


# About view
def about(request):
    return render(request, "about.html")


# Projects view
def projects(request):
    projects_show = [
        {
            'title': 'cloud-computing-project',
            'path': 'images/serverless_DESIGN_project.png',
            'link': (
                'https://github.com/BETHUELTHIPE/cloud-computing-predict'
            ),
        },
        {
            'title': 'moving-big-data-project-airflow',
            'path': 'images/Streaming data.png',
            'link': (
                'https://github.com/BETHUELTHIPE/moving-big-data-predict-airflow'
            ),
        },
        {
            'title': 'data-migration-on-premise-to-aws',
            'path': 'images/Storingbigdata.png',
            'link': (
                'https://github.com/BETHUELTHIPE/data-migration-on-premise-to-aws'
            ),
        },
        {
            'title': 'Integrated-project',
            'path': 'images/etl_insurance_pipeline.jpg',
            'link': (
                'https://github.com/BETHUELTHIPE/Integrated-project'
            ),
        },
        {
            'title': 'processing-big-data-predict',
            'path': 'images/end-to-end-pipeline.jpg',
            'link': (
                'https://github.com/BETHUELTHIPE/processing-big-data-predict'
            ),
        },
        {
            'title': 'Store-BIG-DATA-PROJECT01',
            'path': 'images/end-to-end-pipeline.jpg',
            'link': (
                'https://github.com/BETHUELTHIPE/Store-BIG-DATA-PROJECT01'
            ),
        },
    ]
    context = {"projects_show": projects_show}
    return render(
        request,
        "projects.html",
        context
    )


# Experience view
def experience(request):
    experience = [
        {
            "company": "EXPLOREAI Cape Town South Africa",
            "position": "Data Engineer Intern",
        },
        {
            "company": "Department of Higher Education and Training",
            "position": "Mathematics and Physics Lecturer",
        },
        {
            "company": "Umalusi Quality Council",
            "position": (
                "Evaluator/Subject Specialist/Team Leader"
            ),
        },
        {
            "company": "Audrin Developers",
            "position": "Web Applications Developer",
        },
    ]
    context = {"experience": experience}
    return render(
        request,
        "experience.html",
        context
    )


# Certificate view
def certificate(request):
    return render(request, "certificate.html")


# Contact view
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect('success')  # Redirect to a success page
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})



# Resume download view (login required)
@login_required(login_url='/login/')
def resume(request):
    resume_path = "myapp/resume.pdf"
    if staticfiles_storage.exists(resume_path):
        with staticfiles_storage.open(resume_path, 'rb') as resume_file:
            body = resume_file.read()
            response = HttpResponse(
                body,
                content_type="application/pdf"
            )
            response['Content-Disposition'] = (
                'attachment; filename="resume.pdf"'
            )
            # Increment per-user download counter
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            profile.resume_download_count += 1
            profile.save(update_fields=['resume_download_count'])

            # Also email the resume PDF to the logged-in user's email if available
            if request.user.email:
                send_resume_email_task.delay(request.user.email)
            return response
    else:
        return HttpResponse(
            "Resume not found",
            status=404
        )



# Logged-in users can request resume via email only
@login_required(login_url='/login/')
def email_resume(request):
    if not request.user.email:
        messages.error(request, 'No email address is associated with this account. Please update your profile.')
        return redirect('home')

    try:
        # Queue Celery task to send the resume PDF as an email attachment
        send_resume_email_task.delay(request.user.email)

        # Increment per-user email counter
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.resume_email_count += 1
        profile.save(update_fields=['resume_email_count'])
        
        messages.success(
            request, 
            f'Resume is being sent to {request.user.email}. Please check your inbox in a few moments.'
        )
    except Exception as e:
        messages.error(
            request, 
            'There was an error processing your request. Please try again later or contact support.'
        )
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Email resume error for user {request.user.username}: {str(e)}")
    
    return redirect('home')



@login_required(login_url='/login/')
def profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profile.html', {"form": form})



@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def analytics_dashboard(request):
    from django.contrib.auth.models import User
    from django.db.models import Sum, Count
    from django.db.models.functions import TruncDate

    total_users = User.objects.count()
    verified_users = EmailVerification.objects.filter(is_verified=True).count()
    unverified_users = total_users - verified_users
    total_contacts = Contact.objects.count()

    totals = UserProfile.objects.aggregate(
        total_downloads=Sum('resume_download_count'),
        total_emails=Sum('resume_email_count'),
    )

    # Build per-user analytics list
    users = User.objects.all().select_related('userprofile').order_by('date_joined')
    user_rows = []
    verifications = {ev.user_id: ev.is_verified for ev in EmailVerification.objects.all()}

    for user in users:
        profile = getattr(user, 'userprofile', None)
        user_rows.append({
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_verified': verifications.get(user.id, False),
            'downloads': getattr(profile, 'resume_download_count', 0),
            'emails': getattr(profile, 'resume_email_count', 0),
            'date_joined': user.date_joined,
            'last_login': user.last_login,
        })

    # Signups per day (for line chart)
    signups_qs = (
        User.objects
        .annotate(day=TruncDate('date_joined'))
        .values('day')
        .order_by('day')
        .annotate(count=Count('id'))
    )
    chart_signups_labels = [row['day'].isoformat() for row in signups_qs]
    chart_signups_values = [row['count'] for row in signups_qs]

    context = {
        'total_users': total_users,
        'verified_users': verified_users,
        'unverified_users': unverified_users,
        'total_contacts': total_contacts,
        'total_resume_downloads': totals['total_downloads'] or 0,
        'total_resume_emails': totals['total_emails'] or 0,
        'user_rows': user_rows,
        # Simple series for charts
        'chart_verified': [verified_users, unverified_users],
        'chart_resume': [totals['total_downloads'] or 0, totals['total_emails'] or 0],
        'chart_signups_labels': chart_signups_labels,
        'chart_signups_values': chart_signups_values,
    }
    return render(request, 'analytics_dashboard.html', context)



# Custom registration with email verification
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            verification = EmailVerification.objects.create(user=user)
            verification_url = request.build_absolute_uri(
                f"/verify-email/{verification.token}/"
            )
            subject = 'Welcome to Bethuel Portfolio - Verify Your Email'
            message = (
                f"Hi {user.first_name},\n\n"
                f"Thank you for registering at Bethuel Portfolio!\n\n"
                f"Please verify your email address by clicking the link below:\n"
                f"{verification_url}\n\n"
                f"If you did not register, please ignore this email.\n\n"
                f"Best regards,\nBethuel Portfolio Team"
            )
            send_verification_email_task.delay(subject, message, user.email)
            return redirect('registration_success')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


# Email verification view
# Email verification view
def verify_email(request, token):
    verification = get_object_or_404(EmailVerification, token=token)

    # Check expiry: tokens older than 48 hours are invalid
    if verification.created_at < timezone.now() - timedelta(hours=48):
        messages.error(request, 'This verification link has expired. Please request a new one.')
        return redirect('resend_verification')

    if not verification.is_verified:
        verification.is_verified = True
        verification.save()
        user = verification.user
        user.is_active = True
        user.save()
        return render(request, 'email_verified.html', {'user': user})
    else:
        return render(request, 'email_already_verified.html')


# Resend verification email view
def resend_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                verification, created = EmailVerification.objects.get_or_create(user=user)

                # Rate limit: allow resend only every 10 minutes
                if not created and verification.created_at > timezone.now() - timedelta(minutes=10):
                    messages.warning(
                        request,
                        'A verification email was sent recently. Please check your inbox or try again later.'
                    )
                    return render(request, 'check_email.html', {'email': user.email, 'resent': False})

                # Update timestamp to now when resending
                verification.created_at = timezone.now()
                verification.save(update_fields=['created_at'])

                verification_url = request.build_absolute_uri(f"/verify-email/{verification.token}/")
                subject = 'Resend: Verify Your Email for Bethuel Portfolio'
                message = (
                    f"Hi {user.first_name},\n\n"
                    f"Please verify your email address by clicking the link below:\n"
                    f"{verification_url}\n\n"
                    f"If you did not register, please ignore this email.\n\n"
                    f"Best regards,\nBethuel Portfolio Team"
                )

                send_verification_email_task.delay(subject, message, user.email)
                return render(request, 'check_email.html', {'email': user.email, 'resent': True})
            else:
                messages.info(request, 'This account is already active. Please login.')
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email.')
    return render(request, 'resend_verification.html')


# Custom login view to check for verification
class CustomLoginView(LoginView):
    template_name = 'login.html'

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active:
            messages.error(self.request, 'Please verify your email before logging in. <a href="/resend-verification/">Resend verification email</a>.')
            return self.form_invalid(form)
        return super().form_valid(form)


# Success view
def success_view(request):
    return render(request, 'success.html')
