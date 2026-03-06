from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from ech.users.models import UserToken

User = get_user_model()


class ConfirmEmailApiTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="StrongPassword123",
            user_name="Test User",
            email_confirmed=False,
            is_active=False,
        )

        self.token_obj = UserToken.create_token(
            user=self.user,
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            hours_valid=24,
        )

        self.token = self.token_obj.token

        self.url = f"/api/v1/users/confirm-email/{self.token}/"

    def test_confirm_email_success(self):
        """
        Valid email confirmation token must activate and confirm the user.
        """

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        self.assertTrue(self.user.email_confirmed)
        self.assertTrue(self.user.is_active)

    def test_confirm_email_invalid_token(self):
        """
        Invalid confirmation token must return 400 response.
        """
        
        url = "/api/v1/users/confirm-email/invalidtoken/"

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)