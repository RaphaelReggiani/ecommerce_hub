from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegisterApiTestCase(APITestCase):

    def setUp(self):
        self.url = "/api/v1/users/register/"

    def test_register_user_success(self):
        data = {
            "email": "newuser@test.com",
            "password": "StrongPassword123",
            "user_name": "New User",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data["email"], data["email"])
        self.assertEqual(response.data["user_name"], data["user_name"])

        self.assertTrue(
            User.objects.filter(user_email=data["email"]).exists()
        )

    def test_register_user_with_invalid_email_returns_400(self):
        data = {
            "email": "invalid-email",
            "password": "StrongPassword123",
            "user_name": "New User",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_with_short_password_returns_400(self):
        data = {
            "email": "newuser@test.com",
            "password": "123",
            "user_name": "New User",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)