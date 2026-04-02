from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from ech.users.exceptions import (
    EmailTokenExpiredError,
    EmailTokenInvalidError,
)
from ech.users.models import CustomUser, UserToken
from ech.users.services.user_email_confirmation_service import (
    UserEmailConfirmationService,
)


class UserEmailConfirmationServiceTestCase(TestCase):
    def test_confirm_email_activates_user_and_marks_email_as_confirmed(self):
        """Ensure confirm_email activates the user and confirms email."""
        user = CustomUser.objects.create_user(
            email="confirm@test.com",
            password="StrongPassword123",
            user_name="Confirm User",
        )

        token = UserToken.objects.create(
            user=user,
            token="valid-confirm-token",
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            expires_at=timezone.now() + timedelta(hours=1),
            used=False,
        )

        confirmed_user = UserEmailConfirmationService.confirm_email(token.token)

        user.refresh_from_db()

        self.assertEqual(confirmed_user, user)
        self.assertTrue(user.is_active)
        self.assertTrue(user.email_confirmed)
        self.assertFalse(UserToken.objects.filter(pk=token.pk).exists())

    def test_confirm_email_raises_invalid_error_when_token_does_not_exist(self):
        """Ensure confirm_email raises EmailTokenInvalidError for missing tokens."""
        with self.assertRaises(EmailTokenInvalidError):
            UserEmailConfirmationService.confirm_email("missing-token")

    def test_confirm_email_raises_expired_error_and_deletes_expired_token(self):
        """Ensure confirm_email deletes expired token and raises EmailTokenExpiredError."""
        user = CustomUser.objects.create_user(
            email="expiredconfirm@test.com",
            password="StrongPassword123",
            user_name="Expired Confirm",
        )

        token = UserToken.objects.create(
            user=user,
            token="expired-confirm-token",
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            expires_at=timezone.now() + timedelta(hours=1),
            used=False,
        )

        with patch(
            "ech.users.services.user_email_confirmation_service.get_email_confirmation_token",
            return_value=token,
        ), patch.object(token, "is_expired", return_value=True):
            with self.assertRaises(EmailTokenExpiredError):
                UserEmailConfirmationService.confirm_email(token.token)

        self.assertFalse(UserToken.objects.filter(pk=token.pk).exists())