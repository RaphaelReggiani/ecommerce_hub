from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserLoginApiTestCase(APITestCase):
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

        self.url = "/api/v1/users/login/"

    def test_login_success_returns_tokens(self):
        """
        Valid credentials must return access and refresh tokens.
        """

        response = self.client.post(
            self.url,
            {
                "email": "user@test.com",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_with_wrong_password_returns_400(self):
        """
        Wrong password must return 400 response.
        """

        response = self.client.post(
            self.url,
            {
                "email": "user@test.com",
                "password": "wrongpassword",
            },
            format="json",
            REMOTE_ADDR="10.0.0.1",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_unconfirmed_email_returns_400(self):
        """
        Users with unconfirmed email must not be able to login.
        """

        self.user.email_confirmed = False
        self.user.save(update_fields=["email_confirmed"])

        response = self.client.post(
            self.url,
            {
                "email": "user@test.com",
                "password": self.password,
            },
            format="json",
            REMOTE_ADDR="10.0.0.2",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_inactive_user_returns_400(self):
        """
        Inactive users must not be able to login.
        """

        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.client.post(
            self.url,
            {
                "email": "user@test.com",
                "password": self.password,
            },
            format="json",
            REMOTE_ADDR="10.0.0.3",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_email_case_variation_still_succeeds(self):
        """
        Login should normalize email casing before authentication.
        """

        response = self.client.post(
            self.url,
            {
                "email": "USER@Test.com",
                "password": self.password,
            },
            format="json",
            REMOTE_ADDR="10.0.0.4",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_with_missing_required_fields_returns_400(self):
        """
        Missing required fields must return 400 response.
        """

        response = self.client.post(
            self.url,
            {
                "email": "user@test.com",
            },
            format="json",
            REMOTE_ADDR="10.0.0.5",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)