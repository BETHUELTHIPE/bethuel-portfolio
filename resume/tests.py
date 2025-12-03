from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Contact, EmailVerification, UserProfile


class RegistrationAndVerificationTests(TestCase):
    def test_register_creates_inactive_user_and_profile(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "new@example.com",
                "cell_number": "0712345678",
                "address": "123 Test Street",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newuser")
        self.assertFalse(user.is_active)
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        self.assertTrue(EmailVerification.objects.filter(user=user).exists())

    def test_cannot_login_before_verification(self):
        user = User.objects.create_user(
            username="novalid",
            password="StrongPass123!",
            email="novalid@example.com",
        )
        user.is_active = False
        user.save()

        login_url = reverse("login")
        response = self.client.post(
            login_url,
            {"username": "novalid", "password": "StrongPass123!"},
        )
        # Should not redirect to home; form invalid and shows default auth error
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Please enter a correct username and password. Note that both fields may be case-sensitive.",
        )


class ContactFormTests(TestCase):
    def test_contact_form_saves_message(self):
        response = self.client.post(
            reverse("contact"),
            {
                "name": "Test Sender",
                "email": "sender@example.com",
                "phone": "0712345678",
                "message": "Hello there",
                "honeypot": "",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Contact.objects.filter(email="sender@example.com").exists())

    def test_contact_form_honeypot_blocks_spam(self):
        response = self.client.post(
            reverse("contact"),
            {
                "name": "Spammer",
                "email": "spam@example.com",
                "phone": "0712345678",
                "message": "Spam",
                "honeypot": "filled",
            },
        )
        # Form should be invalid and not save contact
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Contact.objects.filter(email="spam@example.com").exists())


class ResumeAndProfileAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="resumeuser",
            password="StrongPass123!",
            email="resume@example.com",
        )

    def test_resume_requires_login(self):
        response = self.client.get(reverse("resume"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_profile_requires_login(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_profile_update_creates_profile(self):
        self.client.login(username="resumeuser", password="StrongPass123!")
        response = self.client.post(
            reverse("profile"),
            {
                "cell_number": "0712345678",
                "address": "Profile Street",
                "biography": "Bio text",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.cell_number, "0712345678")
        self.assertEqual(profile.address, "Profile Street")
        self.assertEqual(profile.biography, "Bio text")


class AnalyticsAccessTests(TestCase):
    def setUp(self):
        self.normal_user = User.objects.create_user(
            username="normal",
            password="StrongPass123!",
            email="normal@example.com",
        )
        self.staff_user = User.objects.create_user(
            username="staff",
            password="StrongPass123!",
            email="staff@example.com",
            is_staff=True,
        )

    def test_analytics_redirects_non_staff(self):
        self.client.login(username="normal", password="StrongPass123!")
        response = self.client.get(reverse("analytics_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_analytics_accessible_for_staff(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.get(reverse("analytics_dashboard"))
        self.assertEqual(response.status_code, 200)
