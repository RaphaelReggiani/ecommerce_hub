import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
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
            user_name="User Test",
            is_active=True,
            email_confirmed=True,
        )

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
            "refresh": "invalid-refresh-token",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_requires_authentication(self):
        """
        Logout endpoint must reject unauthenticated requests.
        """

        client = APIClient()

        response = client.post(
            self.url,
            {"refresh": "invalid-refresh-token"},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_rejects_inactive_authenticated_user(self):
            """
            Logout endpoint must reject inactive users.
            """

            inactive_user = CustomUser.objects.create_user(
                email="inactive@test.com",
                password="StrongPass123!",
                user_name="Inactive User",
                is_active=False,
                email_confirmed=True,
            )

            refresh = RefreshToken.for_user(inactive_user)
            access = refresh.access_token

            client = APIClient()
            client.credentials(
                HTTP_AUTHORIZATION=f"Bearer {access}"
            )

            response = client.post(
                self.url,
                {"refresh": str(refresh)},
                format="json",
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED