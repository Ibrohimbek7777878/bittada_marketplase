from django import forms
from .models import User, Profile

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'display_name', 'company_name', 'bio', 'contact_email', 
            'telegram', 'website', 'address_text'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
