from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from allauth.socialaccount.models import SocialAccount

from .models import UserProfile


@receiver(user_signed_up)
def create_profile_for_social_signup(request, user, **kwargs):
    """Ensure a UserProfile exists when a user signs up via social auth (e.g. Google)."""
    profile, created = UserProfile.objects.get_or_create(user=user)

    # Try to populate basic fields from the social account data if available
    try:
        socialaccount = SocialAccount.objects.filter(user=user).first()
    except SocialAccount.DoesNotExist:  # pragma: no cover - safety guard
        socialaccount = None

    extra = getattr(socialaccount, "extra_data", {}) or {}

    first_name = extra.get("given_name") or extra.get("first_name")
    last_name = extra.get("family_name") or extra.get("last_name")

    if first_name and not user.first_name:
        user.first_name = first_name
    if last_name and not user.last_name:
        user.last_name = last_name

    # Save user if we updated names
    user.save(update_fields=["first_name", "last_name"])

    # Leave cell_number and address empty for Google signups; user can fill them later
    if created:
        profile.cell_number = profile.cell_number or ""
        profile.address = profile.address or ""
        profile.save(update_fields=["cell_number", "address"])
