import pytest

from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from rest_framework.test import APIClient
from rest_framework import status

from ech.users.models import CustomUser


@pytest.mark.django_db
class TestPasswordResetConfirmInvalidTokenApi:

    def setup_method(self):

        self.client = APIClient()

        self.url = reverse("users-api:api-password-reset-confirm")

        self.user = CustomUser.objects.create_user(
            email="user@test.com",
            password="StrongPass123!",
            user_name="User Test"
        )

        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))

    def test_password_reset_confirm_invalid_token(self):
        """
        Invalid token must return error.
        """

        payload = {
            "uid": self.uid,
            "token": "invalid-token",
            "new_password": "NewStrongPass123!"
        }

        response = self.client.post(self.url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST