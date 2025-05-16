from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.users.forms import CustomAuthenticationForm, UserRegistrationForm, UserUpdateForm
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class UserFormsTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)

        # Create a valid small PNG file for testing
        self.avatar_content = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00'
            b'\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDAT'
            b'\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xccY\xe7\x00\x00'
            b'\x00\x00IEND\xaeB`\x82'
        )

    def test_authentication_form_valid(self):
        """Test authentication form with valid data"""
        form = CustomAuthenticationForm(data={
            'username': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())

    def test_authentication_form_invalid(self):
        """Test authentication form with invalid data"""
        form = CustomAuthenticationForm(data={
            'username': 'test@example.com',
            'password': 'wrongpass'
        })
        self.assertFalse(form.is_valid())

    def test_registration_form_valid(self):
        """Test registration form with valid data"""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_passwords_not_matching(self):
        """Test registration form with non-matching passwords"""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'testpass456'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_registration_form_existing_email(self):
        """Test registration form with existing email"""
        form_data = {
            'email': 'test@example.com',  # Email already exists
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_user_update_form_valid(self):
        """Test user update form with valid data"""
        form_data = {
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User'
        }
        form = UserUpdateForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_user_update_form_with_avatar(self):
        """Test user update form with avatar upload"""
        avatar = SimpleUploadedFile(
            "avatar.png",
            self.avatar_content,
            content_type="image/png"
        )
        form_data = {
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User'
        }
        form = UserUpdateForm(
            data=form_data,
            files={'avatar': avatar},
            instance=self.user
        )
        self.assertTrue(form.is_valid())