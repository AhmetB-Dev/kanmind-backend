from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User


class EmailCheckTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!",
            fullname="Test User",
        )

    def test_existing_email(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/email-check/?email=test@example.com")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")

    def test_unknown_email(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/email-check/?email=unknown@example.com")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_email_check_requires_authentication(self):
        response = self.client.get("/api/email-check/?email=test@example.com")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
