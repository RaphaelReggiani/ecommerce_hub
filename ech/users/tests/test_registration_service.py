from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from ech.users.constants.constants import EMAIL_CONFIRMATION_EXPIRATION_HOURS
from ech.users.exceptions import (
    EmailTokenExpiredError,
    EmailTokenInvalidError,
)
from ech.users.models import CustomUser, UserToken
from ech.users.services.registration_service import UserRegistrationService


class UserRegistrationServiceTestCase(TestCase):
    def test_register_user_creates_inactive_unconfirmed_user_with_default_role(self):
        """Ensure register_user creates an inactive unconfirmed customer user."""
        with patch(
            "ech.users.services.registration_service.UserRegistrationService._send_confirmation_email"
        ):
            user = UserRegistrationService.register_user(
                email="newuser@test.com",
                password="StrongPassword123",
                user_name="New User",
            )

        self.assertEqual(user.user_email, "newuser@test.com")
        self.assertEqual(user.user_role, CustomUser.ROLE_CUSTOMER_USER)
        self.assertFalse(user.is_active)
        self.assertFalse(user.email_confirmed)
        self.assertTrue(user.check_password("StrongPassword123"))

    def test_register_user_respects_explicit_role(self):
        """Ensure register_user respects an explicitly provided role."""
        with patch(
            "ech.users.services.registration_service.UserRegistrationService._send_confirmation_email"
        ):
            user = UserRegistrationService.register_user(
                email="customer2@test.com",
                password="StrongPassword123",
                user_name="Customer Two",
                role=CustomUser.ROLE_CUSTOMER_USER,
            )

        self.assertEqual(user.user_role, CustomUser.ROLE_CUSTOMER_USER)

    def test_register_user_creates_email_confirmation_token(self):
        """Ensure register_user creates a confirmation token for the new user."""
        with patch(
            "ech.users.services.registration_service.UserRegistrationService._send_confirmation_email"
        ):
            user = UserRegistrationService.register_user(
                email="tokencreated@test.com",
                password="StrongPassword123",
                user_name="Token Created",
            )

        token = UserToken.objects.filter(
            user=user,
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
        ).first()

        self.assertIsNotNone(token)
        self.assertFalse(token.used)
        self.assertGreater(token.expires_at, timezone.now())

    def test_register_user_removes_previous_email_confirmation_tokens_when_generating_new_one(self):
        """Ensure email token generation removes previous confirmation tokens."""
        user = CustomUser.objects.create_user(
            email="replace-token@test.com",
            password="StrongPassword123",
            user_name="Replace Token",
        )

        old_token = UserToken.objects.create(
            user=user,
            token="old-confirmation-token",
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            expires_at=timezone.now() + timedelta(hours=1),
        )

        new_token = UserRegistrationService._generate_email_token(user)

        self.assertFalse(
            UserToken.objects.filter(pk=old_token.pk).exists()
        )
        self.assertTrue(
            UserToken.objects.filter(
                user=user,
                token=new_token,
                token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            ).exists()
        )

    @patch("ech.users.services.registration_service.transaction.on_commit")
    def test_register_user_schedules_confirmation_email_on_commit(self, mock_on_commit):
        """Ensure register_user schedules confirmation email sending on commit."""
        user = UserRegistrationService.register_user(
            email="scheduled@test.com",
            password="StrongPassword123",
            user_name="Scheduled User",
        )

        self.assertTrue(mock_on_commit.called)
        self.assertEqual(user.user_email, "scheduled@test.com")

    @patch(
        "ech.users.services.registration_service.UserRegistrationService._send_confirmation_email"
    )
    def test_register_user_on_commit_callback_executes_email_sending(self, mock_send_email):
        """Ensure the registered on_commit callback sends the confirmation email."""
        captured_callback = None

        def store_callback(callback):
            nonlocal captured_callback
            captured_callback = callback

        with patch(
            "ech.users.services.registration_service.transaction.on_commit",
            side_effect=store_callback,
        ):
            user = UserRegistrationService.register_user(
                email="callback@test.com",
                password="StrongPassword123",
                user_name="Callback User",
            )

        self.assertIsNotNone(captured_callback)

        captured_callback()

        self.assertTrue(mock_send_email.called)
        sent_user, sent_token = mock_send_email.call_args[0]
        self.assertEqual(sent_user, user)
        self.assertIsInstance(sent_token, str)
        self.assertTrue(sent_token)

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

        confirmed_user = UserRegistrationService.confirm_email(token.token)

        user.refresh_from_db()

        self.assertEqual(confirmed_user, user)
        self.assertTrue(user.is_active)
        self.assertTrue(user.email_confirmed)
        self.assertFalse(UserToken.objects.filter(pk=token.pk).exists())

    def test_confirm_email_raises_invalid_error_when_token_does_not_exist(self):
        """Ensure confirm_email raises EmailTokenInvalidError for missing tokens."""
        with self.assertRaises(EmailTokenInvalidError):
            UserRegistrationService.confirm_email("missing-token")

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
            "ech.users.services.registration_service.get_email_confirmation_token",
            return_value=token,
        ), patch.object(token, "is_expired", return_value=True):
            with self.assertRaises(EmailTokenExpiredError):
                UserRegistrationService.confirm_email(token.token)

        self.assertFalse(UserToken.objects.filter(pk=token.pk).exists())

    def test_generate_email_token_creates_email_confirmation_token_with_expected_type(self):
        """Ensure _generate_email_token creates an email confirmation token."""
        user = CustomUser.objects.create_user(
            email="gentoken@test.com",
            password="StrongPassword123",
            user_name="Generate Token",
        )

        generated_token = UserRegistrationService._generate_email_token(user)

        token_obj = UserToken.objects.get(token=generated_token)

        self.assertEqual(token_obj.user, user)
        self.assertEqual(
            token_obj.token_type,
            UserToken.TYPE_EMAIL_CONFIRMATION,
        )

    def test_generate_email_token_uses_configured_expiration_hours(self):
        """Ensure _generate_email_token uses configured expiration hours."""
        user = CustomUser.objects.create_user(
            email="expiration@test.com",
            password="StrongPassword123",
            user_name="Expiration User",
        )

        before_call = timezone.now()
        generated_token = UserRegistrationService._generate_email_token(user)
        after_call = timezone.now()

        token_obj = UserToken.objects.get(token=generated_token)

        expected_min = before_call + timedelta(hours=EMAIL_CONFIRMATION_EXPIRATION_HOURS)
        expected_max = after_call + timedelta(hours=EMAIL_CONFIRMATION_EXPIRATION_HOURS)

        self.assertGreaterEqual(token_obj.expires_at, expected_min)
        self.assertLessEqual(token_obj.expires_at, expected_max)

    @override_settings(
        SITE_URL="https://example.com",
        DEFAULT_FROM_EMAIL="noreply@example.com",
    )
    @patch("ech.users.services.registration_service.send_mail")
    @patch("ech.users.services.registration_service.reverse")
    def test_send_confirmation_email_sends_expected_email(
        self,
        mock_reverse,
        mock_send_mail,
    ):
        """Ensure _send_confirmation_email sends email with correct payload."""
        user = CustomUser.objects.create_user(
            email="mailtarget@test.com",
            password="StrongPassword123",
            user_name="Mail Target",
        )
        mock_reverse.return_value = "/users/confirm-email/test-token/"

        UserRegistrationService._send_confirmation_email(user, "test-token")

        mock_reverse.assert_called_once_with(
            "users:confirm_email",
            kwargs={"token": "test-token"},
        )
        mock_send_mail.assert_called_once()

        _, kwargs = mock_send_mail.call_args
        self.assertEqual(kwargs["subject"], "Confirm your E-commerce Hub account")
        self.assertIn("Hello Mail Target", kwargs["message"])
        self.assertIn(
            "https://example.com/users/confirm-email/test-token/",
            kwargs["message"],
        )
        self.assertIn(
            str(EMAIL_CONFIRMATION_EXPIRATION_HOURS),
            kwargs["message"],
        )
        self.assertEqual(kwargs["from_email"], "noreply@example.com")
        self.assertEqual(kwargs["recipient_list"], ["mailtarget@test.com"])
        self.assertFalse(kwargs["fail_silently"])
