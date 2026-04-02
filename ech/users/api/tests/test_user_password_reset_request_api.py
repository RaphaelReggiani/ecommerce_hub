import pytest
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from ech.users.models import CustomUser


@pytest.mark.django_db(transaction=True)
class TestPasswordResetRequestApi:
    def setup_method(self):
        mail.outbox = []
        self.client = APIClient()
        self.url = reverse("users-api:api-password-reset")

        self.user = CustomUser.objects.create_user(
            email="user@test.com",
            password="StrongPass123!",
            user_name="User Teste",
            is_active=True,
            email_confirmed=True,
        )

    def test_password_reset_email_sent_for_existing_active_user(self):
        """
        Send reset email if user exists and is active.
        """

        payload = {
            "email": "user@test.com",
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1

        email = mail.outbox[0]

        assert "password" in email.subject.lower()
        assert "user@test.com" in email.to

    def test_password_reset_does_not_reveal_if_user_exists(self):
        """
        API must not reveal whether the email exists.
        """

        payload = {
            "email": "unknown@test.com",
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 0

    def test_password_reset_does_not_send_email_for_inactive_user(self):
        """
        Inactive users must not receive password reset email.
        """

        inactive_user = CustomUser.objects.create_user(
            email="inactive@test.com",
            password="StrongPass123!",
            user_name="Inactive User",
            is_active=False,
            email_confirmed=True,
        )

        response = self.client.post(
            self.url,
            {"email": inactive_user.user_email},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 0

    def test_password_reset_invalid_email(self):
        """
        Invalid email format must return error.
        """

        payload = {
            "email": "invalid-email",
        }

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_requires_email_field(self):
        """
        Email field is required.
        """

        payload = {}

        response = self.client.post(self.url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST