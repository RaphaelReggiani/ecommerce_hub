from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from ech.users.constants.constants import (
    CORPORATE_EMAIL_DOMAIN,
)
from ech.users.constants.messages import (
    MSG_VALIDATION_ERROR_STAFF_EMAIL,
)

User = get_user_model()


class InvalidRoleTestCase(TestCase):

    def setUp(self):
        self.valid_password = "StrongPassword123"
        self.customer_email = "user@test.com"
        self.corporate_email = f"user{CORPORATE_EMAIL_DOMAIN}"

    def test_invalid_role_choice_raises_validation_error(self):
        """
        Invalid user role choice must raise ValidationError.
        """
        
        user = User(
            user_email=self.customer_email,
            user_name="Invalid Role User",
            user_role="invalid_role_value",
        )
        user.set_password(self.valid_password)

        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_adm_with_non_corporate_email_raises_error(self):
        """
        ADMIN role must require a corporate email domain.
        """

        user = User(
            user_email="staff@gmail.com",
            user_name="Admin",
            user_role=User.ROLE_ADMIN,
        )
        user.set_password(self.valid_password)

        with self.assertRaisesMessage(
            ValidationError,
            MSG_VALIDATION_ERROR_STAFF_EMAIL,
        ):
            user.full_clean()

    def test_superadm_with_non_corporate_email_raises_error(self):
        """
        Super admin role must require a corporate email domain.
        """

        user = User(
            user_email="admin@gmail.com",
            user_name="Super Admin",
            user_role=User.ROLE_SUPERADMIN,
        )
        user.set_password(self.valid_password)

        with self.assertRaisesMessage(
            ValidationError,
            MSG_VALIDATION_ERROR_STAFF_EMAIL,
        ):
            user.full_clean()

    def test_adm_with_corporate_email_is_valid(self):
        """
        ADMIN with corporate email must pass validation.
        """
        
        user = User(
            user_email=self.corporate_email,
            user_name="Admin",
            user_role=User.ROLE_ADMIN,
        )
        user.set_password(self.valid_password)

        try:
            user.full_clean()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly for valid corporate email.")