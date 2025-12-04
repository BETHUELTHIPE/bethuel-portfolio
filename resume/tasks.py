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
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Try to get the active resume from database first
        from .models import Resume
        active_resume = Resume.objects.filter(is_active=True).first()
        
        if active_resume and active_resume.file:
            # Use the uploaded resume from database
            with active_resume.file.open('rb') as resume_file:
                content = resume_file.read()
            filename = active_resume.file.name.split('/')[-1]
        else:
            # Fallback to static resume
            resume_path = "myapp/resume.pdf"
            if not staticfiles_storage.exists(resume_path):
                logger.warning(f"Resume not found for {recipient_email}")
                return
            
            with staticfiles_storage.open(resume_path, "rb") as resume_file:
                content = resume_file.read()
            filename = "resume.pdf"

        subject = "Your Requested Resume - Bethuel Moukangwe"
        body = (
            "Dear Recipient,\n\n"
            "Thank you for your interest in my profile!\n\n"
            "Please find attached my resume as requested. "
            "I am a Data Engineer with expertise in cloud computing, "
            "big data processing, and ETL pipelines.\n\n"
            "Feel free to reach out if you have any questions or would like to discuss opportunities. "
            "You are also welcome to visit me at my physical address:\n\n"
            "27 Tshivhase Street\n"
            "Atteridgeville\n"
            "Pretoria West, 0006\n"
            "South Africa\n\n"
            "Contact Information:\n"
            "Email: bethuelmoukangwe8@gmail.com\n"
            "Cell: 071415 6665\n\n"
            "Best regards,\n"
            "Bethuel Moukangwe\n"
            "Data Engineer"
        )
        from_email = settings.EMAIL_HOST_USER or 'bethuelmoukangwe8@gmail.com'

        email = EmailMessage(subject, body, from_email, [recipient_email])
        email.attach(filename, content, "application/pdf")
        email.send(fail_silently=False)
        
        logger.info(f"Resume successfully sent to {recipient_email}")
        
    except Exception as e:
        logger.error(f"Failed to send resume to {recipient_email}: {str(e)}")
        raise
