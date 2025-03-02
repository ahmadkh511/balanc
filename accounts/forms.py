from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # إضافة حقل البريد الإلكتروني

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')