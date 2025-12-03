from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    # Honeypot field: should stay empty; bots often fill every field
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'message', 'honeypot']

    def clean_honeypot(self):
        value = self.cleaned_data.get('honeypot', '').strip()
        if value:
            # Treat any filled honeypot as spam
            raise forms.ValidationError('Spam detected.')
        return value
