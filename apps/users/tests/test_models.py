from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_create_user(self):
        """Test creating a regular user"""
        self.assertEqual(self.user.email, self.user_data['email'])
        self.assertTrue(self.user.check_password(self.user_data['password']))
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertTrue(self.user.is_active)

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='admin123'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)

    def test_user_string_representation(self):
        """Test the string representation of user"""
        self.assertEqual(str(self.user), self.user.email)

    def test_user_full_name(self):
        """Test get_full_name method"""
        self.assertEqual(
            self.user.get_full_name(),
            f"{self.user.first_name} {self.user.last_name}"
        )
        
        # Test with only email
        user2 = User.objects.create_user(
            email='test2@example.com',
            password='testpass123'
        )
        self.assertEqual(user2.get_full_name(), user2.email)

    def test_create_user_without_email(self):
        """Test creating user without email raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='testpass123')

    def test_profile_completion_status(self):
        """Test is_profile_complete property"""
        self.assertTrue(self.user.is_profile_complete)
        
        incomplete_user = User.objects.create_user(
            email='incomplete@example.com',
            password='testpass123'
        )
        self.assertFalse(incomplete_user.is_profile_complete)

    def test_user_last_activity(self):
        """Test last_activity field is set correctly"""
        self.assertIsNotNone(self.user.last_activity)
        self.assertIsInstance(self.user.last_activity, timezone.datetime)

    def test_seller_status(self):
        """Test is_seller property"""
        self.assertFalse(self.user.is_seller)
        # Note: Additional shop creation tests would be in the shops app tests