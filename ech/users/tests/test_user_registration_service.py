import uuid
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from ech.users.constants.constants import EMAIL_CONFIRMATION_EXPIRATION_HOURS
from ech.users.exceptions import (
    IdempotencyConflictError,
    UserAlreadyExistsError,
)

from ech.users.models import CustomUser, UserToken
from ech.users.services.user_registration_service import UserRegistrationService


class UserRegistrationServiceTestCase(TestCase):
    def test_register_user_creates_inactive_unconfirmed_user_with_default_role(self):
        """Ensure register_user creates an inactive unconfirmed customer user."""
        with patch(
            "ech.users.services.user_registration_service.UserRegistrationService._send_confirmation_email"
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
            "ech.users.services.user_registration_service.UserRegistrationService._send_confirmation_email"
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
            "ech.users.services.user_registration_service.UserRegistrationService._send_confirmation_email"
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

    def test_register_user_persists_idempotency_key_when_provided(self):
        """Ensure register_user persists the provided idempotency key."""
        idempotency_key = uuid.uuid4()

        with patch(
            "ech.users.services.user_registration_service.UserRegistrationService._send_confirmation_email"
        ):
            user = UserRegistrationService.register_user(
                email="idempotent@test.com",
                password="StrongPassword123",
                user_name="Idempotent User",
                idempotency_key=idempotency_key,
            )

        self.assertEqual(user.idempotency_key, idempotency_key)

    def test_register_user_with_same_idempotency_key_returns_same_user(self):
        """Ensure repeated calls with the same idempotency key return the same user."""
        idempotency_key = uuid.uuid4()

        with patch(
            "ech.users.services.user_registration_service.UserRegistrationService._send_confirmation_email"
        ):
            first_user = UserRegistrationService.register_user(
                email="samekey@test.com",
                password="StrongPassword123",
                user_name="Same Key User",
                idempotency_key=idempotency_key,
            )

            second_user = UserRegistrationService.register_user(
                email="samekey@test.com",
                password="StrongPassword123",
                user_name="Same Key User",
                idempotency_key=idempotency_key,
            )

        self.assertEqual(first_user.pk, second_user.pk)
        self.assertEqual(
            CustomUser.objects.filter(user_email="samekey@test.com").count(),
            1,
        )

    @patch("ech.users.services.user_registration_service.transaction.on_commit")
    def test_register_user_with_same_idempotency_key_does_not_schedule_on_commit_twice(
        self,
        mock_on_commit,
    ):
        """Ensure idempotent replay does not register a second on_commit callback."""
        idempotency_key = uuid.uuid4()

        first_user = UserRegistrationService.register_user(
            email="scheduled-idempotent@test.com",
            password="StrongPassword123",
            user_name="Scheduled Idempotent User",
            idempotency_key=idempotency_key,
        )

        second_user = UserRegistrationService.register_user(
            email="scheduled-idempotent@test.com",
            password="StrongPassword123",
            user_name="Scheduled Idempotent User",
            idempotency_key=idempotency_key,
        )

        self.assertEqual(first_user.pk, second_user.pk)
        self.assertEqual(mock_on_commit.call_count, 1)

    def test_register_user_with_same_idempotency_key_does_not_generate_new_token(self):
        """Ensure idempotent replay does not create a second confirmation token."""
        idempotency_key = uuid.uuid4()

        with patch(
            "ech.users.services.user_registration_service.UserRegistrationService._send_confirmation_email"
        ):
            first_user = UserRegistrationService.register_user(
                email="token-idempotent@test.com",
                password="StrongPassword123",
                user_name="Token Idempotent",
                idempotency_key=idempotency_key,
            )

            first_token = UserToken.objects.get(
                user=first_user,
                token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            )

            second_user = UserRegistrationService.register_user(
                email="token-idempotent@test.com",
                password="StrongPassword123",
                user_name="Token Idempotent",
                idempotency_key=idempotency_key,
            )

        tokens = UserToken.objects.filter(
            user=first_user,
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
        )

        self.assertEqual(first_user.pk, second_user.pk)
        self.assertEqual(tokens.count(), 1)
        self.assertEqual(tokens.first().pk, first_token.pk)

    def test_register_user_with_same_idempotency_key_and_different_payload_raises_conflict(self):
        """Ensure reused idempotency key with different payload raises conflict."""
        idempotency_key = uuid.uuid4()

        with patch(
            "ech.users.services.user_registration_service.UserRegistrationService._send_confirmation_email"
        ):
            UserRegistrationService.register_user(
                email="conflict@test.com",
                password="StrongPassword123",
                user_name="Original User",
                idempotency_key=idempotency_key,
            )

            with self.assertRaises(IdempotencyConflictError):
                UserRegistrationService.register_user(
                    email="different@test.com",
                    password="StrongPassword123",
                    user_name="Different User",
                    idempotency_key=idempotency_key,
                )

    def test_register_user_persists_idempotency_request_hash_when_provided(self):
        """Ensure register_user stores the request fingerprint hash."""
        idempotency_key = uuid.uuid4()

        with patch(
            "ech.users.services.user_registration_service.UserRegistrationService._send_confirmation_email"
        ):
            user = UserRegistrationService.register_user(
                email="hash@test.com",
                password="StrongPassword123",
                user_name="Hash User",
                idempotency_key=idempotency_key,
            )

        self.assertTrue(user.idempotency_request_hash)
        self.assertEqual(len(user.idempotency_request_hash), 64)

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

        self.assertFalse(UserToken.objects.filter(pk=old_token.pk).exists())
        self.assertTrue(
            UserToken.objects.filter(
                user=user,
                token=new_token,
                token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            ).exists()
        )

    @patch("ech.users.services.user_registration_service.transaction.on_commit")
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
        "ech.users.services.user_registration_service.UserRegistrationService._send_confirmation_email"
    )
    def test_register_user_on_commit_callback_executes_email_sending(self, mock_send_email):
        """Ensure the registered on_commit callback sends the confirmation email."""
        captured_callback = None

        def store_callback(callback):
            nonlocal captured_callback
            captured_callback = callback

        with patch(
            "ech.users.services.user_registration_service.transaction.on_commit",
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
        _, kwargs = mock_send_email.call_args
        self.assertEqual(kwargs["user"], user)
        self.assertIsInstance(kwargs["token"], str)
        self.assertTrue(kwargs["token"])

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

        expected_min = before_call + timedelta(
            hours=EMAIL_CONFIRMATION_EXPIRATION_HOURS
        )
        expected_max = after_call + timedelta(
            hours=EMAIL_CONFIRMATION_EXPIRATION_HOURS
        )

        self.assertGreaterEqual(token_obj.expires_at, expected_min)
        self.assertLessEqual(token_obj.expires_at, expected_max)

    @override_settings(
        SITE_URL="https://example.com",
        DEFAULT_FROM_EMAIL="noreply@example.com",
    )
    @patch("ech.users.services.user_registration_service.send_mail")
    @patch("ech.users.services.user_registration_service.reverse")
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

        UserRegistrationService._send_confirmation_email(
            user=user,
            token="test-token",
        )

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

    def test_register_user_with_existing_email_raises_user_already_exists_error(self):
        """Ensure duplicate email validation is converted to UserAlreadyExistsError."""
        CustomUser.objects.create_user(
            email="existing@test.com",
            password="StrongPassword123",
            user_name="Existing User",
        )

        with self.assertRaises(UserAlreadyExistsError):
            UserRegistrationService.register_user(
                email="existing@test.com",
                password="StrongPassword123",
                user_name="Another User",
            )