from datetime import timedelta
from unittest.mock import patch

from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from ech.users.constants.constants import PASSWORD_RESET_EXPIRATION_HOURS
from ech.users.exceptions import TokenExpiredError, TokenInvalidError
from ech.users.models import CustomUser, UserToken
from ech.users.services.user_password_reset_service import PasswordResetService


class PasswordResetRequestTestCase(TestCase):
    def test_request_password_reset_does_nothing_if_user_does_not_exist(self):
        """Ensure no action is taken if user does not exist."""
        PasswordResetService.request_password_reset("notfound@test.com")

        self.assertEqual(UserToken.objects.count(), 0)

    def test_request_password_reset_does_nothing_if_user_is_inactive(self):
        """Ensure no action is taken if user is inactive."""
        user = CustomUser.objects.create_user(
            email="inactive@test.com",
            password="StrongPassword123",
            user_name="Inactive User",
        )

        PasswordResetService.request_password_reset(user.user_email)

        self.assertEqual(UserToken.objects.count(), 0)

    def test_request_password_reset_creates_token_for_active_user(self):
        """Ensure token is created for active user."""
        user = CustomUser.objects.create_user(
            email="active@test.com",
            password="StrongPassword123",
            user_name="Active User",
        )
        user.is_active = True
        user.save()

        with patch(
            "ech.users.services.user_password_reset_service.PasswordResetService._send_reset_email"
        ):
            PasswordResetService.request_password_reset(user.user_email)

        token = UserToken.objects.filter(
            user=user,
            token_type=UserToken.TYPE_PASSWORD_RESET,
        ).first()

        self.assertIsNotNone(token)
        self.assertFalse(token.used)
        self.assertGreater(token.expires_at, timezone.now())

    def test_request_password_reset_replaces_existing_tokens(self):
        """Ensure existing password reset tokens are removed before creating new one."""
        user = CustomUser.objects.create_user(
            email="replace@test.com",
            password="StrongPassword123",
            user_name="Replace User",
        )
        user.is_active = True
        user.save()

        old_token = UserToken.objects.create(
            user=user,
            token="old-token",
            token_type=UserToken.TYPE_PASSWORD_RESET,
            expires_at=timezone.now() + timedelta(hours=1),
        )

        with patch(
            "ech.users.services.user_password_reset_service.PasswordResetService._send_reset_email"
        ):
            PasswordResetService.request_password_reset(user.user_email)

        self.assertFalse(UserToken.objects.filter(pk=old_token.pk).exists())
        self.assertEqual(
            UserToken.objects.filter(user=user).count(),
            1,
        )

    @patch("ech.users.services.user_password_reset_service.transaction.on_commit")
    def test_request_password_reset_schedules_email_on_commit(self, mock_on_commit):
        """Ensure reset email is scheduled via transaction.on_commit."""
        user = CustomUser.objects.create_user(
            email="schedule@test.com",
            password="StrongPassword123",
            user_name="Schedule User",
        )
        user.is_active = True
        user.save()

        PasswordResetService.request_password_reset(user.user_email)

        self.assertTrue(mock_on_commit.called)

    @patch(
        "ech.users.services.user_password_reset_service.PasswordResetService._send_reset_email"
    )
    def test_request_password_reset_executes_email_callback(self, mock_send_email):
        """Ensure on_commit callback sends reset email."""
        captured_callback = None

        def store_callback(callback):
            nonlocal captured_callback
            captured_callback = callback

        user = CustomUser.objects.create_user(
            email="callback@test.com",
            password="StrongPassword123",
            user_name="Callback User",
        )
        user.is_active = True
        user.save()

        with patch(
            "ech.users.services.user_password_reset_service.transaction.on_commit",
            side_effect=store_callback,
        ):
            PasswordResetService.request_password_reset(user.user_email)

        self.assertIsNotNone(captured_callback)

        captured_callback()

        self.assertTrue(mock_send_email.called)
        _, kwargs = mock_send_email.call_args
        self.assertEqual(kwargs["user"], user)
        self.assertIsInstance(kwargs["token"], str)

    def test_request_password_reset_is_functionally_idempotent_for_active_user(self):
        """Ensure repeated password reset requests leave only one valid reset token."""
        user = CustomUser.objects.create_user(
            email="idempotent-reset@test.com",
            password="StrongPassword123",
            user_name="Idempotent Reset User",
        )
        user.is_active = True
        user.save()

        with patch(
            "ech.users.services.user_password_reset_service.PasswordResetService._send_reset_email"
        ):
            PasswordResetService.request_password_reset(user.user_email)
            first_token = UserToken.objects.get(
                user=user,
                token_type=UserToken.TYPE_PASSWORD_RESET,
            )

            PasswordResetService.request_password_reset(user.user_email)

        tokens = UserToken.objects.filter(
            user=user,
            token_type=UserToken.TYPE_PASSWORD_RESET,
        )

        self.assertEqual(tokens.count(), 1)
        self.assertNotEqual(tokens.first().pk, first_token.pk)


class PasswordResetExecutionTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="reset@test.com",
            password="OldPassword123",
            user_name="Reset User",
        )
        self.user.is_active = True
        self.user.save()

    def test_reset_password_successfully_updates_password_and_marks_token_used(self):
        """Ensure valid token resets password and marks token as used."""
        token = UserToken.objects.create(
            user=self.user,
            token="valid-reset-token",
            token_type=UserToken.TYPE_PASSWORD_RESET,
            expires_at=timezone.now() + timedelta(hours=1),
            used=False,
        )

        updated_user = PasswordResetService.reset_password(
            token=token.token,
            new_password="NewPassword123",
        )

        self.user.refresh_from_db()
        token.refresh_from_db()

        self.assertEqual(updated_user, self.user)
        self.assertTrue(self.user.check_password("NewPassword123"))
        self.assertTrue(token.used)

    def test_reset_password_raises_invalid_error_when_token_not_found(self):
        """Ensure invalid token raises TokenInvalidError."""
        with self.assertRaises(TokenInvalidError):
            PasswordResetService.reset_password(
                token="invalid-token",
                new_password="NewPassword123",
            )

    def test_reset_password_raises_expired_error_and_deletes_token(self):
        """Ensure expired token raises TokenExpiredError and is deleted."""
        token = UserToken.objects.create(
            user=self.user,
            token="expired-reset-token",
            token_type=UserToken.TYPE_PASSWORD_RESET,
            expires_at=timezone.now() + timedelta(hours=1),
            used=False,
        )

        with patch(
            "ech.users.services.user_password_reset_service.get_valid_token",
            return_value=token,
        ), patch.object(token, "is_expired", return_value=True):
            with self.assertRaises(TokenExpiredError):
                PasswordResetService.reset_password(
                    token=token.token,
                    new_password="NewPassword123",
                )

        self.assertFalse(UserToken.objects.filter(pk=token.pk).exists())

    def test_reset_password_raises_validation_error_for_weak_password(self):
        """Ensure weak passwords are rejected by Django password validators."""
        token = UserToken.objects.create(
            user=self.user,
            token="weak-password-token",
            token_type=UserToken.TYPE_PASSWORD_RESET,
            expires_at=timezone.now() + timedelta(hours=1),
            used=False,
        )

        with self.assertRaises(DjangoValidationError):
            PasswordResetService.reset_password(
                token=token.token,
                new_password="123",
            )

        self.user.refresh_from_db()
        token.refresh_from_db()

        self.assertTrue(self.user.check_password("OldPassword123"))
        self.assertFalse(token.used)


class PasswordResetEmailTestCase(TestCase):
    @override_settings(
        SITE_URL="https://example.com",
        DEFAULT_FROM_EMAIL="noreply@example.com",
    )
    @patch("ech.users.services.user_password_reset_service.send_mail")
    @patch("ech.users.services.user_password_reset_service.reverse")
    def test_send_reset_email_sends_expected_email(
        self,
        mock_reverse,
        mock_send_mail,
    ):
        """Ensure reset email is sent with correct content and parameters."""
        user = CustomUser.objects.create_user(
            email="email@test.com",
            password="StrongPassword123",
            user_name="Email User",
        )

        mock_reverse.return_value = "/users/reset/test-token/"

        PasswordResetService._send_reset_email(
            user=user,
            token="test-token",
        )

        mock_reverse.assert_called_once_with(
            "users:password_reset_confirm",
            kwargs={"token": "test-token"},
        )

        mock_send_mail.assert_called_once()

        _, kwargs = mock_send_mail.call_args

        self.assertEqual(kwargs["subject"], "Reset your E-commerce Hub password")
        self.assertIn("Hello Email User", kwargs["message"])
        self.assertIn(
            "https://example.com/users/reset/test-token/",
            kwargs["message"],
        )
        self.assertIn(
            str(PASSWORD_RESET_EXPIRATION_HOURS),
            kwargs["message"],
        )
        self.assertEqual(kwargs["from_email"], "noreply@example.com")
        self.assertEqual(kwargs["recipient_list"], ["email@test.com"])
        self.assertFalse(kwargs["fail_silently"])