from django.contrib.auth.forms import UserCreationForm
from .models import User, AdminSignupRequest
from django import forms


class UsersignupForm(forms.Form):
    """
    Normal user signup form.
    If request_admin is checked, an AdminSignupRequest is created instead.
    """
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    GENDER_CHOICE = (
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    gender = forms.ChoiceField(choices=GENDER_CHOICE, required=False)
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        initial='user',
        label='Role'
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        if AdminSignupRequest.objects.filter(email=email, status='pending').exists():
            raise forms.ValidationError("An admin request with this email is already pending.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(),
        }


class OTPVerifyForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        label='Enter OTP',
        widget=forms.TextInput(attrs={
            'placeholder': '6-digit code',
            'autocomplete': 'one-time-code',
            'inputmode': 'numeric',
            'maxlength': '6',
        })
    )

    def clean_otp(self):
        otp = self.cleaned_data.get('otp', '').strip()
        if not otp.isdigit():
            raise forms.ValidationError("OTP must contain only digits.")
        return otp
