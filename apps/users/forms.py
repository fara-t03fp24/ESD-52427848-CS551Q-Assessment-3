from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    is_seller = forms.BooleanField(
        required=False,
        label='Register as a Seller',
        help_text='Check this if you want to sell 3D models in your own shop.',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'seller-checkbox'
        })
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2', 'is_seller']
        help_texts = {
            'email': 'We\'ll use this to notify you about your 3D printing orders',
            'first_name': 'Your first name will be shown on your 3D model listings',
            'last_name': 'Your last name will be shown on your 3D model listings'
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
                'autocomplete': 'email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a secure password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
        # Custom help texts
        self.fields['password1'].help_text = 'Create a strong password with at least 8 characters'
        self.fields['password2'].help_text = 'Enter the same password as above, for verification'


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'avatar']
        help_texts = {
            'email': 'We\'ll use this to notify you about your 3D printing orders and model sales',
            'first_name': 'Your first name appears on your 3D model listings and orders',
            'last_name': 'Your last name appears on your 3D model listings and orders',
            'avatar': 'Upload a profile picture to personalize your account'
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Update your email address',
                'autocomplete': 'email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Update your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Update your last name'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        # Check if email exists but exclude current user
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email