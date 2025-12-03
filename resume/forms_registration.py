from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    cell_number = forms.CharField(max_length=20, required=True, label="Cell Number")
    address = forms.CharField(max_length=255, required=True, label="Address")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "cell_number", "address", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_cell_number(self):
        cell = self.cleaned_data.get("cell_number", "").strip()
        digits = "".join(ch for ch in cell if ch.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError("Please enter a valid cell number with at least 10 digits.")
        return cell

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.is_active = False  # Deactivate account until email confirmed
        if commit:
            user.save()
            # Save UserProfile
            UserProfile.objects.create(
                user=user,
                cell_number=self.cleaned_data["cell_number"],
                address=self.cleaned_data["address"]
            )
        return user
