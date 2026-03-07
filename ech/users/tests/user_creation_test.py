from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

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
        self.customer_email = "user@test.com"
        self.corporate_email = f"user{CORPORATE_EMAIL_DOMAIN}"

    def test_create_user_without_email_raises_error(self):
        """
        Creating a user without email must raise ValueError.
        """

        with self.assertRaisesMessage(ValueError, MSG_VALUE_ERROR_INFORM_EMAIL):
            User.objects.create_user(
                email=None,
                password=self.valid_password,
                user_name="Test User",
            )

    def test_create_user_without_password_raises_error(self):
        """
        Creating a user without password must raise ValueError.
        """

        with self.assertRaisesMessage(ValueError, MSG_VALUE_ERROR_INFORM_PASSWORD):
            User.objects.create_user(
                email=self.customer_email,
                password=None,
                user_name="Test User",
            )

    def test_create_user_default_role_is_customer_user(self):
        """
        User created without role must default to customer user.
        """

        user = User.objects.create_user(
            email=self.customer_email,
            password=self.valid_password,
            user_name="Test User",
        )

        self.assertEqual(user.user_role, User.ROLE_CUSTOMER_USER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_email_is_saved_in_lowercase(self):
        """
        Email must be normalized and saved in lowercase.
        """

        user = User.objects.create_user(
            email="USER@TEST.COM",
            password=self.valid_password,
            user_name="Test User",
        )

        self.assertEqual(user.user_email, "user@test.com")

    def test_password_is_hashed(self):
        """
        Password must be stored hashed and not in plain text.
        """

        user = User.objects.create_user(
            email=self.customer_email,
            password=self.valid_password,
            user_name="Test User",
        )

        self.assertNotEqual(user.password, self.valid_password)
        self.assertTrue(user.check_password(self.valid_password))

    def test_create_superuser_sets_proper_flags(self):
        """
        Creating a superuser must set admin role and permission flags.
        """

        user = User.objects.create_superuser(
            email=self.corporate_email,
            password=self.valid_password,
            user_name="Super Admin",
        )

        self.assertEqual(user.user_role, User.ROLE_SUPERADMIN)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertTrue(user.email_confirmed)

    def test_adm_sets_staff_true_and_not_superuser(self):
        """
        ADMIN role must set staff permission but not superuser.
        """

        user = User.objects.create_user(
            email=self.corporate_email,
            password=self.valid_password,
            role=User.ROLE_ADMIN,
            user_name="Admin",
        )

        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_customer_user_is_not_staff_nor_superuser(self):
        """
        customer user role must not grant staff or superuser permissions.
        """

        user = User.objects.create_user(
            email=self.customer_email,
            password=self.valid_password,
            role=User.ROLE_CUSTOMER_USER,
            user_name="Customer User",
        )

        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_staff_user_with_non_corporate_email_raises_validation_error(self):
        """
        Staff users must use a corporate email domain.
        """

        with self.assertRaisesMessage(
            ValidationError,
            MSG_VALIDATION_ERROR_STAFF_EMAIL,
        ):
            user = User(
                user_email="staff@gmail.com",
                user_name="Staff User",
                user_role=User.ROLE_ADMIN,
            )
            user.set_password(self.valid_password)
            user.full_clean()

    def test_user_below_minimum_age_raises_validation_error(self):
        """
        Users below the minimum allowed age must raise validation error.
        """
        
        with self.assertRaises(ValidationError):
            user = User(
                user_email=self.customer_email,
                user_name="Young User",
                user_role=User.ROLE_CUSTOMER_USER,
                user_age=MINIMUM_AGE - 1,
            )
            user.set_password(self.valid_password)
            user.full_clean()