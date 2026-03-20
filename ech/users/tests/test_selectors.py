from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from ech.users.models import CustomUser, UserToken
from ech.users.selectors import (
    get_user_by_id,
    get_user_by_email,
    list_users_by_role,
    list_active_users,
    list_staff_users,
    get_email_confirmation_token,
    get_valid_token,
)


class UserSelectorsTestCase(TestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer",
        )

        self.admin = CustomUser.objects.create_user(
            email="admin@company.com",
            password="StrongPassword123",
            user_name="Admin",
            role=CustomUser.ROLE_ADMIN,
        )

        self.active_user = CustomUser.objects.create_user(
            email="active@test.com",
            password="StrongPassword123",
            user_name="Active",
        )
        self.active_user.is_active = True
        self.active_user.save()

    def test_get_user_by_id_returns_user(self):
        """Ensure get_user_by_id returns the correct user."""
        user = get_user_by_id(self.customer.id)
        self.assertEqual(user, self.customer)

    def test_get_user_by_id_returns_none_when_not_found(self):
        """Ensure get_user_by_id returns None for invalid ID."""
        user = get_user_by_id(9999)
        self.assertIsNone(user)

    def test_get_user_by_email_returns_user(self):
        """Ensure get_user_by_email returns the correct user."""
        user = get_user_by_email("customer@test.com")
        self.assertEqual(user, self.customer)

    def test_get_user_by_email_is_case_insensitive(self):
        """Ensure get_user_by_email normalizes email to lowercase."""
        user = get_user_by_email("CUSTOMER@TEST.COM")
        self.assertEqual(user, self.customer)

    def test_get_user_by_email_returns_none_when_not_found(self):
        """Ensure get_user_by_email returns None for unknown email."""
        user = get_user_by_email("notfound@test.com")
        self.assertIsNone(user)

    def test_list_users_by_role_returns_correct_users(self):
        """Ensure list_users_by_role filters users by role."""
        users = list_users_by_role(CustomUser.ROLE_ADMIN)
        self.assertIn(self.admin, users)
        self.assertNotIn(self.customer, users)

    def test_list_active_users_returns_only_active_users(self):
        """Ensure list_active_users returns only active users."""
        users = list_active_users()
        self.assertIn(self.active_user, users)
        self.assertNotIn(self.customer, users)

    def test_list_staff_users_returns_only_staff_users(self):
        """Ensure list_staff_users returns only staff users."""
        users = list_staff_users()
        self.assertIn(self.admin, users)
        self.assertNotIn(self.customer, users)


class UserTokenSelectorsTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="token@test.com",
            password="StrongPassword123",
            user_name="Token User",
        )

        self.valid_token = UserToken.objects.create(
            user=self.user,
            token="valid-token",
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            expires_at=timezone.now() + timedelta(hours=1),
            used=False,
        )

        self.used_token = UserToken.objects.create(
            user=self.user,
            token="used-token",
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            expires_at=timezone.now() + timedelta(hours=1),
            used=True,
        )

        self.expired_token = UserToken.objects.create(
            user=self.user,
            token="expired-token",
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            expires_at=timezone.now() - timedelta(minutes=1),
            used=False,
        )

    def test_get_email_confirmation_token_returns_valid_token(self):
        """Ensure get_email_confirmation_token returns a valid unused token."""
        token = get_email_confirmation_token("valid-token")
        self.assertEqual(token, self.valid_token)

    def test_get_email_confirmation_token_returns_none_if_used(self):
        """Ensure get_email_confirmation_token ignores used tokens."""
        token = get_email_confirmation_token("used-token")
        self.assertIsNone(token)

    def test_get_email_confirmation_token_returns_none_if_not_found(self):
        """Ensure get_email_confirmation_token returns None if token does not exist."""
        token = get_email_confirmation_token("invalid-token")
        self.assertIsNone(token)

    def test_get_valid_token_returns_valid_token(self):
        """Ensure get_valid_token returns a valid and non-expired token."""
        token = get_valid_token(
            token="valid-token",
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
        )
        self.assertEqual(token, self.valid_token)

    def test_get_valid_token_returns_none_if_expired(self):
        """Ensure get_valid_token ignores expired tokens."""
        token = get_valid_token(
            token="expired-token",
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
        )
        self.assertIsNone(token)

    def test_get_valid_token_returns_none_if_used(self):
        """Ensure get_valid_token ignores used tokens."""
        token = get_valid_token(
            token="used-token",
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
        )
        self.assertIsNone(token)

    def test_get_valid_token_returns_none_if_wrong_type(self):
        """Ensure get_valid_token filters by token type."""
        token = get_valid_token(
            token="valid-token",
            token_type=UserToken.TYPE_PASSWORD_RESET,
        )
        self.assertIsNone(token)

    def test_get_valid_token_returns_none_if_not_found(self):
        """Ensure get_valid_token returns None for non-existing tokens."""
        token = get_valid_token(
            token="invalid-token",
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
        )
        self.assertIsNone(token)