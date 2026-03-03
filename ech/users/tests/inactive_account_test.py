from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

from ech.users.models import UserToken
from ech.users.services.password_reset_service import PasswordResetService

User = get_user_model()


class InactiveAccountTestCase(TestCase):

    def setUp(self):
        self.password = "StrongPassword123"

        self.inactive_user = User.objects.create_user(
            email="inactive@test.com",
            password=self.password,
            user_name="Inactive User",
        )
        self.inactive_user.is_active = False
        self.inactive_user.save()

    @patch("ech.users.services.password_reset_service.send_mail")
    def test_inactive_user_cannot_request_password_reset(self, mock_send_mail):
        PasswordResetService.request_password_reset(
            self.inactive_user.user_email
        )

        self.assertEqual(UserToken.objects.count(), 0)
        mock_send_mail.assert_not_called()

    @patch("ech.users.services.password_reset_service.send_mail")
    def test_non_existent_user_request_does_nothing(self, mock_send_mail):
        PasswordResetService.request_password_reset(
            "nonexistent@test.com"
        )

        self.assertEqual(UserToken.objects.count(), 0)
        mock_send_mail.assert_not_called()