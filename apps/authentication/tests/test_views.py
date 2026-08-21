from unittest.mock import patch
from django.test import TestCase
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import CustomUser
from apps.authentication.models import SocialAccount


class EmailVerificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="test@example.com", password="StrongPass123", full_name="Test User"
        )
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        cache.clear()

    def test_request_and_confirm_verification(self):
        with patch("apps.authentication.services.send_mail") as mock_send:
            response = self.client.post("/api/v1/auth/email/verify/request/")
        self.assertEqual(response.status_code, 200)
        mock_send.assert_called_once()

        code = cache.get(f"otp:email_verification:{self.user.id}")
        response = self.client.post("/api/v1/auth/email/verify/confirm/", {"code": code})
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_wrong_code_rejected(self):
        with patch("apps.authentication.services.send_mail"):
            self.client.post("/api/v1/auth/email/verify/request/")
        response = self.client.post("/api/v1/auth/email/verify/confirm/", {"code": "000000"})
        self.assertEqual(response.status_code, 400)


class GoogleAuthTests(TestCase):
    def test_invalid_token_rejected(self):
        client = APIClient()
        with patch("apps.authentication.views.verify_google_token", return_value=None):
            response = client.post("/api/v1/auth/google/", {"id_token": "bad"})
        self.assertEqual(response.status_code, 401)

    def test_new_google_user_creates_account_and_social_link(self):
        client = APIClient()
        payload = {"sub": "google-uid-123", "email": "newuser@example.com", "name": "New User"}
        with patch("apps.authentication.views.verify_google_token", return_value=payload):
            response = client.post("/api/v1/auth/google/", {"id_token": "good"})
        self.assertEqual(response.status_code, 200)
        user = CustomUser.objects.get(email="newuser@example.com")
        self.assertTrue(SocialAccount.objects.filter(user=user, provider_uid="google-uid-123").exists())

    def test_existing_password_account_not_silently_merged(self):
        CustomUser.objects.create_user(
            email="existing@example.com", password="StrongPass123", full_name="Existing"
        )
        client = APIClient()
        payload = {"sub": "google-uid-999", "email": "existing@example.com", "name": "Existing"}
        with patch("apps.authentication.views.verify_google_token", return_value=payload):
            response = client.post("/api/v1/auth/google/", {"id_token": "good"})
        self.assertEqual(response.status_code, 409)

    def test_returning_google_user_logs_in_via_social_account(self):
        user = CustomUser.objects.create_user(email="g@example.com", password=None, full_name="G User")
        SocialAccount.objects.create(user=user, provider="google", provider_uid="google-uid-555")
        client = APIClient()
        payload = {"sub": "google-uid-555", "email": "g@example.com", "name": "G User"}
        with patch("apps.authentication.views.verify_google_token", return_value=payload):
            response = client.post("/api/v1/auth/google/", {"id_token": "good"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Login successful.")


class LogoutTests(TestCase):
    def test_logout_blacklists_refresh_token(self):
        user = CustomUser.objects.create_user(
            email="logout@example.com", password="StrongPass123", full_name="Logout User"
        )
        refresh = RefreshToken.for_user(user)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post("/api/v1/auth/logout/", {"refresh": str(refresh)})
        self.assertEqual(response.status_code, 200)

        # Using the same refresh token again should now fail
        response = client.post("/api/v1/users/login/refresh/", {"refresh": str(refresh)})
        self.assertEqual(response.status_code, 401)
        