from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:login')
        self.profile_url = reverse('users:profile')
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

    def test_register_view_GET(self):
        """Test GET request to registration page"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_register_view_POST_valid(self):
        """Test valid POST request to registration"""
        data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_register_view_POST_invalid(self):
        """Test invalid POST request to registration"""
        data = {
            'email': 'invalid-email',
            'password1': 'testpass123',
            'password2': 'testpass456'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)  # Stay on same page
        self.assertFalse(User.objects.filter(email='invalid-email').exists())

    def test_login_view_GET(self):
        """Test GET request to login page"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_view_POST_valid(self):
        """Test valid POST request to login"""
        data = {
            'username': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success

    def test_login_view_POST_invalid(self):
        """Test invalid POST request to login"""
        data = {
            'username': 'test@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)  # Stay on same page

    def test_profile_view_unauthenticated(self):
        """Test profile view when user is not authenticated"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_profile_view_authenticated(self):
        """Test profile view when user is authenticated"""
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_profile_update_POST(self):
        """Test updating user profile"""
        self.client.force_login(self.user)
        data = {
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.post(self.profile_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.first_name, 'Updated')

    def test_profile_update_with_avatar(self):
        """Test updating user profile with avatar"""
        self.client.force_login(self.user)
        avatar = SimpleUploadedFile(
            "avatar.png",
            self.avatar_content,
            content_type="image/png"
        )
        data = {
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'Name',
            'avatar': avatar
        }
        response = self.client.post(self.profile_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.user.refresh_from_db()
        self.assertTrue(self.user.avatar)  # Check if avatar was uploaded