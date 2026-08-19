from django.test import TestCase
from apps.users.models import CustomUser

class CustomUserModelTests(TestCase):
    def test_create_user(self):
        user = CustomUser.objects.create_user(
            email = "test@example.com",
            password = "StrongPass123",
            full_name = "Test User"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("StrongPass123"))
        self.assertTrue(hasattr(user, "profile"))  #signal fired

    def test_create_superuser(self):
        admin = CustomUser.objects.create_superuser(
            email="admin@example.com", password="AdminPass123", full_name="Admin"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)