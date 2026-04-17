from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class CurrentUserApiTestCase(APITestCase):
    def setUp(self):
        cache.clear()

        self.password = "StrongPassword123"

        self.user = User.objects.create_user(
            email="user@test.com",
            password=self.password,
            email_confirmed=True,
            is_active=True,
            user_name="Test User",
        )

        self.login_url = "/api/v1/users/login/"
        self.me_url = "/api/v1/users/me/"

    def authenticate_with_jwt(self):
        """
        Helper method to authenticate user with JWT token.
        """

        response = self.client.post(
            self.login_url,
            {
                "email": "user@test.com",
                "password": self.password,
            },
            format="json",
        )

        token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

    def test_me_requires_authentication(self):
        """
        Endpoint must reject unauthenticated requests.
        """

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_authenticated_user_data(self):
        """
        Authenticated user must receive correct user information.
        """

        self.authenticate_with_jwt()

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["email"], self.user.user_email)
        self.assertEqual(response.data["user_name"], self.user.user_name)
        self.assertEqual(response.data["role"], self.user.user_role)
        self.assertEqual(response.data["is_active"], self.user.is_active)
        self.assertEqual(
            response.data["email_confirmed"],
            self.user.email_confirmed,
        )

    def test_me_rejects_user_with_unconfirmed_email(self):
        """
        Users with unconfirmed email must not access the endpoint.
        """

        self.user.email_confirmed = False
        self.user.save(update_fields=["email_confirmed"])

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_me_rejects_inactive_user(self):
        """
        Inactive users must not access the endpoint.
        """

        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)