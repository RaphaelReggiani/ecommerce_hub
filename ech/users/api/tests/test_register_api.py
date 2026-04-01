import uuid

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserRegisterApiTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/v1/users/register/"

    def test_register_user_success(self):
        """
        Valid user registration must create user and return 201 response.
        """

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

    def test_register_user_with_idempotency_key_success(self):
        """
        Valid registration with Idempotency-Key must create user and return 201.
        """

        data = {
            "email": "idempotent@test.com",
            "password": "StrongPassword123",
            "user_name": "Idempotent User",
        }
        headers = {
            "HTTP_IDEMPOTENCY_KEY": str(uuid.uuid4()),
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
            **headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], data["email"])
        self.assertEqual(response.data["user_name"], data["user_name"])

        user = User.objects.get(user_email=data["email"])
        self.assertIsNotNone(user.idempotency_key)

    def test_register_user_with_same_idempotency_key_returns_same_user(self):
        """
        Repeated registration with the same Idempotency-Key must return the same user.
        """

        idempotency_key = str(uuid.uuid4())

        data = {
            "email": "samekey@test.com",
            "password": "StrongPassword123",
            "user_name": "Same Key User",
        }

        headers = {
            "HTTP_IDEMPOTENCY_KEY": idempotency_key,
        }

        first_response = self.client.post(
            self.url,
            data,
            format="json",
            **headers,
        )

        second_response = self.client.post(
            self.url,
            data,
            format="json",
            **headers,
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(first_response.data["email"], second_response.data["email"])
        self.assertEqual(first_response.data["user_name"], second_response.data["user_name"])
        self.assertEqual(first_response.data["id"], second_response.data["id"])

        self.assertEqual(
            User.objects.filter(user_email=data["email"]).count(),
            1,
        )

    def test_register_user_with_same_idempotency_key_does_not_create_duplicate_user(self):
        """
        Repeated registration with the same Idempotency-Key must not create duplicate users.
        """

        idempotency_key = str(uuid.uuid4())

        data = {
            "email": "duplicate-prevented@test.com",
            "password": "StrongPassword123",
            "user_name": "Duplicate Prevented",
        }

        headers = {
            "HTTP_IDEMPOTENCY_KEY": idempotency_key,
        }

        self.client.post(
            self.url,
            data,
            format="json",
            **headers,
        )

        self.client.post(
            self.url,
            data,
            format="json",
            **headers,
        )

        self.assertEqual(
            User.objects.filter(user_email=data["email"]).count(),
            1,
        )

    def test_register_user_with_same_idempotency_key_and_different_payload_returns_conflict(self):
        idempotency_key = str(uuid.uuid4())

        first_data = {
            "email": "first@test.com",
            "password": "StrongPassword123",
            "user_name": "First User",
        }

        second_data = {
            "email": "second@test.com",
            "password": "StrongPassword123",
            "user_name": "Second User",
        }

        headers = {
            "HTTP_IDEMPOTENCY_KEY": idempotency_key,
        }

        first_response = self.client.post(
            self.url,
            first_data,
            format="json",
            **headers,
        )

        second_response = self.client.post(
            self.url,
            second_data,
            format="json",
            **headers,
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(User.objects.filter(idempotency_key=idempotency_key).count(), 1)

    def test_register_user_with_invalid_email_returns_400(self):
        """
        Invalid email format must return 400 response.
        """

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
        """
        Password not meeting validation rules must return 400 response.
        """

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