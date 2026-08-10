"""Automated authentication API and permission tests."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User


class AuthApiTests(APITestCase):
    """Verify authapi behavior."""
    def test_registration_success(self):
        data = {
            "fullname": "Test User",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "repeated_password": "TestPassword123!",
        }
        response = self.client.post(reverse("registration"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertIn("token", response.data)

    def test_registration_password_mismatch(self):
        data = {
            "fullname": "Test User",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "repeated_password": "WrongPassword123!",
        }
        response = self.client.post(reverse("registration"), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        self._create_user()
        data = {
            "email": "test@example.com",
            "password": "TestPassword123!",
        }
        response = self.client.post(reverse("login"), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertIn("token", response.data)

    def test_login_wrong_password(self):
        self._create_user()
        data = {
            "email": "test@example.com",
            "password": "WrongPassword123!",
        }
        response = self.client.post(reverse("login"), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _create_user(self):
        return User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!",
            fullname="Test User",
        )
