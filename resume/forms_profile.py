from django import forms

from .models import UserProfile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "cell_number",
            "address",
            "biography",
            "photo",
        ]
        widgets = {
            "biography": forms.Textarea(attrs={"rows": 4}),
        }
