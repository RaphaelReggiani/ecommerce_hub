import pytest
from django.urls import reverse
from django.core import mail
from rest_framework.test import APIClient
from ech.users.models import CustomUser


@pytest.mark.django_db
class TestPasswordResetRequestApi:

    def setup_method(self):
        self.client = APIClient()

        self.url = reverse("users-api:api-password-reset")

        self.user = CustomUser.objects.create_user(
            email="user@test.com",
            password="StrongPass123!",
            user_name="User Teste",
        )

    def test_password_reset_email_sent_for_existing_user(self):
        """
        Send email if user exists.
        """

        payload = {
            "email": "user@test.com"
        }

        response = self.client.post(self.url, payload)

        assert response.status_code == 200

        assert len(mail.outbox) == 1

        email = mail.outbox[0]

        assert "password" in email.subject.lower()
        assert "user@test.com" in email.to

    def test_password_reset_does_not_reveal_if_user_exists(self):
        """
        API doesn't reveals if the email exists.
        """

        payload = {
            "email": "unknown@test.com"
        }

        response = self.client.post(self.url, payload)

        assert response.status_code == 200

        assert len(mail.outbox) == 0

    def test_password_reset_invalid_email(self):
        """
        Invalid email format must return error.
        """

        payload = {
            "email": "invalid-email"
        }

        response = self.client.post(self.url, payload)

        assert response.status_code == 400

    def test_password_reset_requires_email_field(self):
        """
        Email field is obrigatory.
        """

        payload = {}

        response = self.client.post(self.url, payload)

        assert response.status_code == 400