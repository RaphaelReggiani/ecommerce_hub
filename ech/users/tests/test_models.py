from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from ech.users.constants.constants import (
    CORPORATE_EMAIL_DOMAIN,
    MAXIMUM_AGE,
    MINIMUM_AGE,
)
from ech.users.constants.messages import (
    MSG_VALIDATION_ERROR_EXPIRATION_DATETIME,
    MSG_VALIDATION_ERROR_STAFF_EMAIL,
    MSG_VALUE_ERROR_INFORM_EMAIL,
    MSG_VALUE_ERROR_INFORM_PASSWORD,
)
from ech.users.models import CustomUser, UserToken


class CustomUserManagerTestCase(TestCase):
    def test_create_user_success_with_default_customer_role(self):
        """Ensure create_user creates a default customer user successfully."""
        user = CustomUser.objects.create_user(
            email="USER@TEST.COM",
            password="StrongPassword123",
            user_name="Test User",
        )

        self.assertEqual(user.user_email, "user@test.com")
        self.assertEqual(user.user_role, CustomUser.ROLE_CUSTOMER_USER)
        self.assertEqual(user.user_name, "Test User")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_active)
        self.assertFalse(user.email_confirmed)
        self.assertTrue(user.check_password("StrongPassword123"))

    def test_create_user_success_with_explicit_customer_role(self):
        """Ensure create_user respects an explicit customer role."""
        user = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_CUSTOMER_USER,
            user_name="Customer User",
        )

        self.assertEqual(user.user_role, CustomUser.ROLE_CUSTOMER_USER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_raises_value_error_when_email_is_missing(self):
        """Ensure create_user raises ValueError when email is missing."""
        with self.assertRaisesMessage(ValueError, MSG_VALUE_ERROR_INFORM_EMAIL):
            CustomUser.objects.create_user(
                email="",
                password="StrongPassword123",
                user_name="Test User",
            )

    def test_create_user_raises_value_error_when_password_is_missing(self):
        """Ensure create_user raises ValueError when password is missing."""
        with self.assertRaisesMessage(ValueError, MSG_VALUE_ERROR_INFORM_PASSWORD):
            CustomUser.objects.create_user(
                email="user@test.com",
                password=None,
                user_name="Test User",
            )

    def test_create_user_with_staff_role_and_corporate_email(self):
        """Ensure staff user creation succeeds with a corporate email."""
        user = CustomUser.objects.create_user(
            email=f"staff{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            role=CustomUser.ROLE_SUPPORT_STAFF,
            user_name="Support User",
        )

        self.assertEqual(user.user_role, CustomUser.ROLE_SUPPORT_STAFF)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_with_staff_role_and_non_corporate_email_raises_validation_error(self):
        """Ensure staff user creation fails with a non-corporate email."""
        with self.assertRaises(ValidationError) as context:
            CustomUser.objects.create_user(
                email="staff@gmail.com",
                password="StrongPassword123",
                role=CustomUser.ROLE_SUPPORT_STAFF,
                user_name="Invalid Staff",
            )

        self.assertIn(MSG_VALIDATION_ERROR_STAFF_EMAIL, context.exception.messages)

    def test_create_superuser_success(self):
        """Ensure create_superuser creates an active privileged user."""
        user = CustomUser.objects.create_superuser(
            email=f"superadmin{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            user_name="Super Admin",
        )

        self.assertEqual(user.user_role, CustomUser.ROLE_SUPERADMIN)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertTrue(user.email_confirmed)
        self.assertTrue(user.check_password("StrongPassword123"))

    def test_create_superuser_normalizes_email_to_lowercase(self):
        """Ensure create_superuser normalizes email to lowercase."""
        user = CustomUser.objects.create_superuser(
            email=f"SUPERADMIN{CORPORATE_EMAIL_DOMAIN.upper()}",
            password="StrongPassword123",
            user_name="Super Admin",
        )

        self.assertEqual(
            user.user_email,
            f"superadmin{CORPORATE_EMAIL_DOMAIN}",
        )


class CustomUserModelTestCase(TestCase):
    def test_str_returns_name_and_email(self):
        """Ensure string representation returns name and email."""
        user = CustomUser.objects.create_user(
            email="user@test.com",
            password="StrongPassword123",
            user_name="Test User",
        )

        self.assertEqual(str(user), "Test User (user@test.com)")

    def test_is_superadmin_property_returns_true_only_for_superadmin(self):
        """Ensure is_superadmin is true only for superadmin users."""
        superadmin = CustomUser.objects.create_user(
            email=f"superadmin{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            role=CustomUser.ROLE_SUPERADMIN,
            user_name="Super Admin",
        )
        customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer",
        )

        self.assertTrue(superadmin.is_superadmin)
        self.assertFalse(customer.is_superadmin)

    def test_can_create_staff_property_returns_true_for_superadmin_and_admin(self):
        """Ensure can_create_staff is true only for admin-level roles."""
        superadmin = CustomUser.objects.create_user(
            email=f"superadmin{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            role=CustomUser.ROLE_SUPERADMIN,
            user_name="Super Admin",
        )
        admin = CustomUser.objects.create_user(
            email=f"admin{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            role=CustomUser.ROLE_ADMIN,
            user_name="Admin User",
        )
        support = CustomUser.objects.create_user(
            email=f"support{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            role=CustomUser.ROLE_SUPPORT_STAFF,
            user_name="Support User",
        )
        customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
        )

        self.assertTrue(superadmin.can_create_staff)
        self.assertTrue(admin.can_create_staff)
        self.assertFalse(support.can_create_staff)
        self.assertFalse(customer.can_create_staff)

    def test_save_sets_flags_for_superadmin(self):
        """Ensure save sets staff and superuser flags for superadmin."""
        user = CustomUser.objects.create_user(
            email=f"superadmin2{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            role=CustomUser.ROLE_SUPERADMIN,
            user_name="Super Admin",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_save_sets_flags_for_admin(self):
        """Ensure save sets only the staff flag for admin users."""
        user = CustomUser.objects.create_user(
            email=f"admin2{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            role=CustomUser.ROLE_ADMIN,
            user_name="Admin User",
        )

        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_save_sets_flags_for_non_admin_roles(self):
        """Ensure save clears staff privileges for non-admin roles."""
        support_user = CustomUser.objects.create_user(
            email=f"support2{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            role=CustomUser.ROLE_SUPPORT_STAFF,
            user_name="Support User",
        )
        customer_user = CustomUser.objects.create_user(
            email="customer2@test.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_CUSTOMER_USER,
            user_name="Customer User",
        )

        self.assertFalse(support_user.is_staff)
        self.assertFalse(support_user.is_superuser)
        self.assertFalse(customer_user.is_staff)
        self.assertFalse(customer_user.is_superuser)

    def test_save_always_lowercases_email(self):
        """Ensure save always lowercases the user email."""
        user = CustomUser(
            user_email="MIXEDCASE@TEST.COM",
            user_name="Mixed User",
            user_role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=False,
        )
        user.set_password("StrongPassword123")
        user.full_clean()
        user.save()

        self.assertEqual(user.user_email, "mixedcase@test.com")

    def test_clean_allows_customer_user_with_non_corporate_email(self):
        """Ensure customer users may use non-corporate email addresses."""
        user = CustomUser(
            user_email="customer@gmail.com",
            user_name="Customer User",
            user_role=CustomUser.ROLE_CUSTOMER_USER,
        )
        user.set_password("StrongPassword123")

        user.full_clean()

    def test_clean_rejects_staff_user_with_non_corporate_email(self):
        """Ensure staff users must use a corporate email address."""
        user = CustomUser(
            user_email="staff@gmail.com",
            user_name="Staff User",
            user_role=CustomUser.ROLE_PAYMENT_STAFF,
        )
        user.set_password("StrongPassword123")

        with self.assertRaises(ValidationError) as context:
            user.full_clean()

        self.assertIn(MSG_VALIDATION_ERROR_STAFF_EMAIL, context.exception.messages)

    def test_clean_allows_staff_user_with_corporate_email(self):
        """Ensure staff users pass validation with a corporate email."""
        user = CustomUser(
            user_email=f"staff{CORPORATE_EMAIL_DOMAIN}",
            user_name="Staff User",
            user_role=CustomUser.ROLE_OPERATIONS_STAFF,
        )
        user.set_password("StrongPassword123")

        user.full_clean()

    def test_user_email_must_be_unique(self):
        """Ensure duplicate user emails are rejected by model validation."""
        CustomUser.objects.create_user(
            email="duplicate@test.com",
            password="StrongPassword123",
            user_name="First User",
        )

        with self.assertRaises(ValidationError) as context:
            CustomUser.objects.create_user(
                email="duplicate@test.com",
                password="StrongPassword123",
                user_name="Second User",
            )

        self.assertIn("user_email", context.exception.message_dict)

    def test_user_age_accepts_minimum_age(self):
        """Ensure minimum valid age is accepted."""
        user = CustomUser.objects.create_user(
            email="minage@test.com",
            password="StrongPassword123",
            user_name="Min Age User",
            user_age=MINIMUM_AGE,
        )

        self.assertEqual(user.user_age, MINIMUM_AGE)

    def test_user_age_accepts_maximum_age(self):
        """Ensure maximum valid age is accepted."""
        user = CustomUser.objects.create_user(
            email="maxage@test.com",
            password="StrongPassword123",
            user_name="Max Age User",
            user_age=MAXIMUM_AGE,
        )

        self.assertEqual(user.user_age, MAXIMUM_AGE)

    def test_user_age_below_minimum_raises_validation_error(self):
        """Ensure age below minimum raises a validation error."""
        with self.assertRaises(ValidationError):
            CustomUser.objects.create_user(
                email="young@test.com",
                password="StrongPassword123",
                user_name="Young User",
                user_age=MINIMUM_AGE - 1,
            )

    def test_user_age_above_maximum_raises_validation_error(self):
        """Ensure age above maximum raises a validation error."""
        with self.assertRaises(ValidationError):
            CustomUser.objects.create_user(
                email="old@test.com",
                password="StrongPassword123",
                user_name="Old User",
                user_age=MAXIMUM_AGE + 1,
            )

    def test_username_field_and_required_fields_are_configured(self):
        """Ensure authentication fields are configured correctly."""
        self.assertEqual(CustomUser.USERNAME_FIELD, "user_email")
        self.assertEqual(CustomUser.REQUIRED_FIELDS, ["user_name"])


class UserTokenModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            email="tokenuser@test.com",
            password="StrongPassword123",
            user_name="Token User",
        )

    def test_create_token_creates_valid_token_instance(self):
        """Ensure create_token creates a valid unused token."""
        token = UserToken.create_token(
            user=self.user,
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            hours_valid=24,
        )

        self.assertEqual(token.user, self.user)
        self.assertEqual(token.token_type, UserToken.TYPE_EMAIL_CONFIRMATION)
        self.assertEqual(len(token.token), 48)
        self.assertFalse(token.used)
        self.assertGreater(token.expires_at, timezone.now())

    def test_create_token_generates_unique_token_values(self):
        """Ensure create_token generates different token values."""
        token_1 = UserToken.create_token(
            user=self.user,
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            hours_valid=24,
        )
        token_2 = UserToken.create_token(
            user=self.user,
            token_type=UserToken.TYPE_PASSWORD_RESET,
            hours_valid=2,
        )

        self.assertNotEqual(token_1.token, token_2.token)

    def test_clean_rejects_expired_token(self):
        """Ensure token validation rejects past expiration dates."""
        token = UserToken(
            user=self.user,
            token="expired-token-value",
            token_type=UserToken.TYPE_PASSWORD_RESET,
            expires_at=timezone.now() - timedelta(minutes=1),
        )

        with self.assertRaises(ValidationError) as context:
            token.full_clean()

        self.assertIn(
            MSG_VALIDATION_ERROR_EXPIRATION_DATETIME,
            context.exception.messages,
        )

    def test_clean_allows_future_expiration(self):
        """Ensure token validation accepts future expiration dates."""
        token = UserToken(
            user=self.user,
            token="future-token-value",
            token_type=UserToken.TYPE_PASSWORD_RESET,
            expires_at=timezone.now() + timedelta(hours=1),
        )

        token.full_clean()

    def test_is_expired_returns_false_for_future_token(self):
        """Ensure is_expired returns false for valid tokens."""
        token = UserToken.create_token(
            user=self.user,
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            hours_valid=1,
        )

        self.assertFalse(token.is_expired())

    def test_is_expired_returns_true_for_past_token(self):
        """Ensure is_expired returns true for expired tokens."""
        token = UserToken.objects.create(
            user=self.user,
            token="past-token-value",
            token_type=UserToken.TYPE_PASSWORD_RESET,
            expires_at=timezone.now() + timedelta(hours=1),
        )

        UserToken.objects.filter(pk=token.pk).update(
            expires_at=timezone.now() - timedelta(seconds=1)
        )
        token.refresh_from_db()

        self.assertTrue(token.is_expired())

    def test_mark_as_used_sets_used_to_true(self):
        """Ensure mark_as_used updates the token as used."""
        token = UserToken.create_token(
            user=self.user,
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            hours_valid=1,
        )

        self.assertFalse(token.used)

        token.mark_as_used()
        token.refresh_from_db()

        self.assertTrue(token.used)

    def test_token_string_must_be_unique(self):
        """Ensure duplicate token strings are rejected."""
        UserToken.objects.create(
            user=self.user,
            token="unique-token-value",
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            expires_at=timezone.now() + timedelta(hours=1),
        )

        with self.assertRaises(ValidationError):
            duplicated = UserToken(
                user=self.user,
                token="unique-token-value",
                token_type=UserToken.TYPE_PASSWORD_RESET,
                expires_at=timezone.now() + timedelta(hours=2),
            )
            duplicated.full_clean()

    def test_token_has_expected_related_name(self):
        """Ensure the related_name tokens works for user access."""
        token = UserToken.create_token(
            user=self.user,
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            hours_valid=1,
        )

        self.assertIn(token, self.user.tokens.all())

    def test_token_metadata_accepts_null_and_dict(self):
        """Ensure token metadata accepts null and dictionary values."""
        token_null_metadata = UserToken.objects.create(
            user=self.user,
            token="token-null-metadata",
            token_type=UserToken.TYPE_EMAIL_CONFIRMATION,
            expires_at=timezone.now() + timedelta(hours=1),
            metadata=None,
        )
        token_dict_metadata = UserToken.objects.create(
            user=self.user,
            token="token-dict-metadata",
            token_type=UserToken.TYPE_PASSWORD_RESET,
            expires_at=timezone.now() + timedelta(hours=1),
            metadata={"ip": "127.0.0.1", "source": "test"},
        )

        self.assertIsNone(token_null_metadata.metadata)
        self.assertEqual(
            token_dict_metadata.metadata,
            {"ip": "127.0.0.1", "source": "test"},
        )