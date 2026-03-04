from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class UserLoginApiTestCase(APITestCase):

    def setUp(self):
        self.password = "StrongPassword123"
        self.user = User.objects.create_user(
            email="user@test.com",
            password=self.password,
            email_confirmed=True,
            is_active=True,
            user_name="Test User",
        )
        self.user.save()

        self.url = "/api/v1/users/login/"

    def test_login_success_returns_tokens(self):
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
        response = self.client.post(
            self.url,
            {
                "email": "user@test.com",
                "password": "wrongpassword",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_unconfirmed_email_returns_400(self):
        self.user.email_confirmed = False
        self.user.save()

        response = self.client.post(
            self.url,
            {
                "email": "user@test.com",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)