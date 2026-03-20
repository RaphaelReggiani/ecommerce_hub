import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ech.users.models import CustomUser


@pytest.mark.django_db
class TestLogoutInvalidRefreshTokenApi:

    def setup_method(self):

        self.client = APIClient()

        self.url = reverse("users-api:api-logout")

        self.user = CustomUser.objects.create_user(
            email="user@test.com",
            password="StrongPass123!",
            user_name="User Test"
        )

        self.user.is_active = True
        self.user.email_confirmed = True
        self.user.save()

        refresh = RefreshToken.for_user(self.user)
        access = refresh.access_token

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access}"
        )

    def test_logout_invalid_refresh_token(self):
        """
        Invalid refresh token must return 400 error.
        """

        payload = {
            "refresh": "invalid-refresh-token"
        }

        response = self.client.post(self.url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        