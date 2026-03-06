from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import CustomUser


class PasswordResetConfirmApiTestCase(APITestCase):

    def setUp(self):
        self.url = reverse("users-api:api-password-reset-confirm")

        self.user = CustomUser.objects.create_user(
            user_name="Test User",
            email="test@example.com",
            password="OldPassword123!",
        )

        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)

    def test_password_reset_confirm_success(self):
        """
        Valid uid and token must reset the password successfully.
        """

        data = {
            "uid": self.uid,
            "token": self.token,
            "new_password": "NewSecurePassword123!"
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewSecurePassword123!"))

    def test_password_reset_confirm_invalid_uid(self):
        """
        Invalid uid must return 400 response.
        """

        data = {
            "uid": "invaliduid",
            "token": self.token,
            "new_password": "NewSecurePassword123!"
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_invalid_token(self):
        """
        Invalid token must return 400 response.
        """

        data = {
            "uid": self.uid,
            "token": "invalidtoken",
            "new_password": "NewSecurePassword123!"
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_invalid_password(self):
        """
        Password not meeting validation rules must return 400 response.
        """

        data = {
            "uid": self.uid,
            "token": self.token,
            "new_password": "123"
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_missing_fields(self):
        """
        Missing required fields must return 400 response.
        """
        
        data = {}

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)