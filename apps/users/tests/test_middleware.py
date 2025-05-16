from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from apps.users.middleware import UserActivityMiddleware
from apps.users.utils import check_user_completion

User = get_user_model()

class UserMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = UserActivityMiddleware(get_response=lambda r: None)
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def _get_request_with_middleware(self, path='/'):
        """Helper to create request with session and message middleware"""
        request = self.factory.get(path)
        session_middleware = SessionMiddleware(lambda r: None)
        message_middleware = MessageMiddleware(lambda r: None)
        
        session_middleware.process_request(request)
        message_middleware.process_request(request)
        request.session.save()
        
        return request

    def test_activity_tracking(self):
        """Test that user's last_activity is updated"""
        old_last_activity = self.user.last_activity
        request = self._get_request_with_middleware('/')
        request.user = self.user
        
        # Wait a moment to ensure time difference
        self.user.last_activity = timezone.now() - timedelta(minutes=5)
        self.user.save()
        
        self.middleware(request)
        self.user.refresh_from_db()
        
        self.assertGreater(self.user.last_activity, old_last_activity)

    def test_anonymous_user_handling(self):
        """Test middleware behavior with anonymous user"""
        request = self._get_request_with_middleware('/')
        request.user = AnonymousUser()
        response = self.middleware(request)
        self.assertIsNone(response)  # Middleware should pass through

class UserUtilsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_profile_completion_check_incomplete(self):
        """Test profile completion check with incomplete profile"""
        completion_result = check_user_completion(self.user)
        self.assertIsInstance(completion_result, tuple)
        is_complete, missing_fields = completion_result
        self.assertFalse(is_complete)
        self.assertIn('First Name', missing_fields)
        self.assertIn('Last Name', missing_fields)

    def test_profile_completion_check_complete(self):
        """Test profile completion check with complete profile"""
        self.user.first_name = 'Test'
        self.user.last_name = 'User'
        self.user.save()
        completion_result = check_user_completion(self.user)
        self.assertIsInstance(completion_result, tuple)
        is_complete, missing_fields = completion_result
        self.assertTrue(is_complete)
        self.assertEqual(len(missing_fields), 0)