"""Automated authentication API and permission tests."""

from django.test import TestCase

from auth_app.models import User


class UserModelTests(TestCase):
    """Verify usermodel behavior."""
    def test_user_string_representation(self):
        user = User.objects.create_user(
            email="user@example.com",
            password="TestPassword123!",
            fullname="Test User",
        )
        self.assertEqual(str(user), "user@example.com")

    def test_create_user_without_email_fails(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="",
                password="TestPassword123!",
                fullname="Test User",
            )

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="TestPassword123!",
            fullname="Admin User",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
