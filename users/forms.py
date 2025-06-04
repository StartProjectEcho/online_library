from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    username = forms.CharField(max_length=150)

    class Meta:
        model = CustomUser
        fields = ["email", "username", "password1", "password2"]


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')

    class Meta:
        model = CustomUser
        fields = ['email', 'password']

class ProfileUpdateForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['username']