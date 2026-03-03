from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone

from ech.users.constants.constants import (
    MINIMUM_AGE,
    CORPORATE_EMAIL_DOMAIN,
)
from ech.users.constants.messages import (
    MSG_VALUE_ERROR_INFORM_EMAIL,
    MSG_VALUE_ERROR_INFORM_PASSWORD,
    MSG_VALIDATION_ERROR_STAFF_EMAIL,
)

User = get_user_model()


class UserCreationTestCase(TestCase):

    def setUp(self):
        self.valid_password = "StrongPassword123"
        self.common_email = "user@test.com"
        self.corporate_email = f"user{CORPORATE_EMAIL_DOMAIN}"

    def test_create_user_without_email_raises_error(self):
        with self.assertRaisesMessage(ValueError, MSG_VALUE_ERROR_INFORM_EMAIL):
            User.objects.create_user(
                email=None,
                password=self.valid_password,
                user_name="Test User",
            )

    def test_create_user_without_password_raises_error(self):
        with self.assertRaisesMessage(ValueError, MSG_VALUE_ERROR_INFORM_PASSWORD):
            User.objects.create_user(
                email=self.common_email,
                password=None,
                user_name="Test User",
            )

    def test_create_user_default_role_is_common_user(self):
        user = User.objects.create_user(
            email=self.common_email,
            password=self.valid_password,
            user_name="Test User",
        )

        self.assertEqual(user.user_role, User.ROLE_COMMON_USER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_email_is_saved_in_lowercase(self):
        user = User.objects.create_user(
            email="USER@TEST.COM",
            password=self.valid_password,
            user_name="Test User",
        )

        self.assertEqual(user.user_email, "user@test.com")

    def test_password_is_hashed(self):
        user = User.objects.create_user(
            email=self.common_email,
            password=self.valid_password,
            user_name="Test User",
        )

        self.assertNotEqual(user.password, self.valid_password)
        self.assertTrue(user.check_password(self.valid_password))

    def test_create_superuser_sets_proper_flags(self):
        user = User.objects.create_superuser(
            email=self.corporate_email,
            password=self.valid_password,
            user_name="Super Admin",
        )

        self.assertEqual(user.user_role, User.ROLE_SUPERADM)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertTrue(user.email_confirmed)

    def test_super_staff_sets_staff_true_and_not_superuser(self):
        user = User.objects.create_user(
            email=self.corporate_email,
            password=self.valid_password,
            role=User.ROLE_SUPER_STAFF,
            user_name="Super Staff",
        )

        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_common_user_is_not_staff_nor_superuser(self):
        user = User.objects.create_user(
            email=self.common_email,
            password=self.valid_password,
            role=User.ROLE_COMMON_USER,
            user_name="Common User",
        )

        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_staff_user_with_non_corporate_email_raises_validation_error(self):
        with self.assertRaisesMessage(
            ValidationError,
            MSG_VALIDATION_ERROR_STAFF_EMAIL,
        ):
            user = User(
                user_email="staff@gmail.com",
                user_name="Staff User",
                user_role=User.ROLE_SUPER_STAFF,
            )
            user.set_password(self.valid_password)
            user.full_clean()

    def test_user_below_minimum_age_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            user = User(
                user_email=self.common_email,
                user_name="Young User",
                user_role=User.ROLE_COMMON_USER,
                user_age=MINIMUM_AGE - 1,
            )
            user.set_password(self.valid_password)
            user.full_clean()