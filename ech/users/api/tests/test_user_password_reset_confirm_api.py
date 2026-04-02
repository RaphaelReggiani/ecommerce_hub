from datetime import timedelta

from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import CustomUser, UserToken


class PasswordResetConfirmApiTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("users-api:api-password-reset-confirm")

        self.user = CustomUser.objects.create_user(
            user_name="Test User",
            email="test@example.com",
            password="OldPassword123!",
            is_active=True,
            email_confirmed=True,
        )

        self.token_obj = UserToken.objects.create(
            user=self.user,
            token="valid-reset-token",
            token_type=UserToken.TYPE_PASSWORD_RESET,
            expires_at=timezone.now() + timedelta(hours=1),
            used=False,
        )

    def test_password_reset_confirm_success(self):
        """
        Valid reset token must reset the password successfully.
        """

        data = {
            "token": self.token_obj.token,
            "new_password": "NewSecurePassword123!",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.token_obj.refresh_from_db()

        self.assertTrue(self.user.check_password("NewSecurePassword123!"))
        self.assertTrue(self.token_obj.used)

    def test_password_reset_confirm_invalid_token(self):
        """
        Invalid token must return 400 response.
        """

        data = {
            "token": "invalidtoken",
            "new_password": "NewSecurePassword123!",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_expired_token(self):
        """
        Expired token must return 400 response.
        """

        self.token_obj.expires_at = timezone.now() - timedelta(minutes=1)
        self.token_obj.save(update_fields=["expires_at"])

        data = {
            "token": self.token_obj.token,
            "new_password": "NewSecurePassword123!",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_invalid_password(self):
        """
        Password not meeting validation rules must return 400 response.
        """

        data = {
            "token": self.token_obj.token,
            "new_password": "123",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_missing_fields(self):
        """
        Missing required fields must return 400 response.
        """

        data = {}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_token_cannot_be_reused(self):
        """
        Used password reset token must not be accepted again.
        """

        data = {
            "token": self.token_obj.token,
            "new_password": "NewSecurePassword123!",
        }

        first_response = self.client.post(self.url, data, format="json")
        second_response = self.client.post(
            self.url,
            {
                "token": self.token_obj.token,
                "new_password": "AnotherSecurePassword123!",
            },
            format="json",
        )

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)