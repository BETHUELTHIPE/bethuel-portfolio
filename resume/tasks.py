from celery import shared_task
import time

from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage


@shared_task
def demo_add(x, y):
    """Simple demo task that adds two numbers."""
    time.sleep(5)  # simulate a slow operation
    return x + y


@shared_task
def send_verification_email_task(subject, message, recipient_email):
    """Send a verification email asynchronously."""
    from_email = settings.EMAIL_HOST_USER or 'noreply@bethuelportfolio.com'
    send_mail(
        subject,
        message,
        from_email,
        [recipient_email],
        fail_silently=False,
    )


@shared_task
def send_resume_email_task(recipient_email):
    """Email the resume PDF to the given recipient, if available."""
    resume_path = "myapp/resume.pdf"
    if not staticfiles_storage.exists(resume_path):
        return

    with staticfiles_storage.open(resume_path, "rb") as resume_file:
        content = resume_file.read()

    subject = "Your Requested Resume from Bethuel"
    body = (
        "Hi,\n\n"
        "As requested, here is a copy of my resume attached as a PDF.\n\n"
        "Best regards,\nBethuel"
    )
    from_email = settings.EMAIL_HOST_USER or 'noreply@bethuelportfolio.com'

    email = EmailMessage(subject, body, from_email, [recipient_email])
    email.attach("resume.pdf", content, "application/pdf")
    email.send(fail_silently=False)
