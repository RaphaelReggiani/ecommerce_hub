import pytest

from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from ech.users.models import CustomUser


@pytest.mark.django_db
class TestTokenRefreshApi:

    def setup_method(self):
        self.client = APIClient()

        self.url = reverse("users-api:api-token-refresh")

        self.user = CustomUser.objects.create_user(
            email="user@test.com",
            password="StrongPass123!",
            user_name="User Test",
            is_active=True,
        )

        self.refresh = RefreshToken.for_user(self.user)

    def test_token_refresh_success(self):
        """
        Valid refresh token must return new access token.
        """

        payload = {
            "refresh": str(self.refresh)
        }

        response = self.client.post(self.url, payload)

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_token_refresh_invalid_token(self):
        """
        Invalid refresh token must return error.
        """

        payload = {
            "refresh": "invalid-token"
        }

        response = self.client.post(self.url, payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh_requires_refresh_field(self):
        """
        Refresh field is required.
        """

        payload = {}

        response = self.client.post(self.url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_token_refresh_blacklisted_token(self):
        """
        Blacklisted refresh token must not generate new access token.
        """

        token = RefreshToken.for_user(self.user)
        token.blacklist()

        payload = {
            "refresh": str(token)
        }

        response = self.client.post(self.url, payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED