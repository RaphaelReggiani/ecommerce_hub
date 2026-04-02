from django.test import TestCase

from ech.users.constants.constants import CORPORATE_EMAIL_DOMAIN
from ech.users.exceptions import (
    InvalidRoleAssignmentError,
    UserDomainError,
)
from ech.users.models import CustomUser
from ech.users.services.user_update_service import UserUpdateService


class UserUpdateServiceTestCase(TestCase):
    def setUp(self):
        corporate_domain = CORPORATE_EMAIL_DOMAIN.lstrip("@")

        self.user = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            user_phone="111111111",
            user_country="Brazil",
            user_state="SP",
            user_address="Old Address",
            user_age=30,
        )

        self.admin_user = CustomUser.objects.create_user(
            email=f"admin@{corporate_domain}",
            password="StrongPassword123",
            user_name="Admin User",
            role=CustomUser.ROLE_ADMIN,
        )

    def test_update_user_updates_allowed_profile_fields(self):
        updated_user = UserUpdateService.update_user(
            user=self.user,
            user_name="Updated Name",
            user_phone="999999999",
            user_country="USA",
            user_state="CA",
            user_address="New Address",
            user_age=35,
        )

        self.user.refresh_from_db()

        self.assertEqual(updated_user.pk, self.user.pk)
        self.assertEqual(self.user.user_name, "Updated Name")
        self.assertEqual(self.user.user_phone, "999999999")
        self.assertEqual(self.user.user_country, "USA")
        self.assertEqual(self.user.user_state, "CA")
        self.assertEqual(self.user.user_address, "New Address")
        self.assertEqual(self.user.user_age, 35)

    def test_update_user_ignores_unknown_fields(self):
        updated_user = UserUpdateService.update_user(
            user=self.user,
            user_name="Known Change",
            unknown_field="ignored value",
        )

        self.user.refresh_from_db()

        self.assertEqual(updated_user.pk, self.user.pk)
        self.assertEqual(self.user.user_name, "Known Change")
        self.assertEqual(self.user.user_email, "customer@test.com")

    def test_update_user_returns_same_instance_when_no_valid_fields_are_provided(self):
        updated_user = UserUpdateService.update_user(
            user=self.user,
            unsupported_field="value",
        )

        self.user.refresh_from_db()

        self.assertEqual(updated_user.pk, self.user.pk)
        self.assertEqual(self.user.user_name, "Customer User")
        self.assertEqual(self.user.user_phone, "111111111")

    def test_update_user_returns_same_instance_when_no_changes_are_needed(self):
        updated_user = UserUpdateService.update_user(
            user=self.user,
            user_name="Customer User",
            user_phone="111111111",
        )

        self.user.refresh_from_db()

        self.assertEqual(updated_user.pk, self.user.pk)
        self.assertEqual(self.user.user_name, "Customer User")
        self.assertEqual(self.user.user_phone, "111111111")

    def test_update_user_raises_error_when_user_is_none(self):
        with self.assertRaises(UserDomainError):
            UserUpdateService.update_user(
                user=None,
                user_name="Invalid",
            )

    def test_update_user_allows_role_change_when_performed_by_authorized_user(self):
        corporate_domain = CORPORATE_EMAIL_DOMAIN.lstrip("@")

        staff_candidate = CustomUser.objects.create_user(
            email=f"staffcandidate@{corporate_domain}",
            password="StrongPassword123",
            user_name="Staff Candidate",
            role=CustomUser.ROLE_CUSTOMER_USER,
        )

        updated_user = UserUpdateService.update_user(
            user=staff_candidate,
            performed_by=self.admin_user,
            user_role=CustomUser.ROLE_SUPPORT_STAFF,
        )

        staff_candidate.refresh_from_db()

        self.assertEqual(updated_user.pk, staff_candidate.pk)
        self.assertEqual(staff_candidate.user_role, CustomUser.ROLE_SUPPORT_STAFF)
        self.assertFalse(staff_candidate.is_staff)
        self.assertFalse(staff_candidate.is_superuser)

    def test_update_user_rejects_role_change_without_performed_by(self):
        with self.assertRaises(InvalidRoleAssignmentError):
            UserUpdateService.update_user(
                user=self.user,
                user_role=CustomUser.ROLE_SUPPORT_STAFF,
            )

    def test_update_user_rejects_role_change_when_performed_by_user_is_not_authorized(self):
        another_customer = CustomUser.objects.create_user(
            email="another@test.com",
            password="StrongPassword123",
            user_name="Another Customer",
            role=CustomUser.ROLE_CUSTOMER_USER,
        )

        with self.assertRaises(InvalidRoleAssignmentError):
            UserUpdateService.update_user(
                user=self.user,
                performed_by=another_customer,
                user_role=CustomUser.ROLE_SUPPORT_STAFF,
            )

    def test_update_user_rejects_staff_role_assignment_for_non_corporate_email(self):
        with self.assertRaises(InvalidRoleAssignmentError):
            UserUpdateService.update_user(
                user=self.user,
                performed_by=self.admin_user,
                user_role=CustomUser.ROLE_SUPPORT_STAFF,
            )

    def test_update_user_allows_customer_role_assignment_for_non_corporate_email(self):
        updated_user = UserUpdateService.update_user(
            user=self.user,
            performed_by=self.admin_user,
            user_role=CustomUser.ROLE_CUSTOMER_USER,
        )

        self.user.refresh_from_db()

        self.assertEqual(updated_user.pk, self.user.pk)
        self.assertEqual(self.user.user_role, CustomUser.ROLE_CUSTOMER_USER)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_update_user_allows_staff_role_assignment_for_corporate_email(self):
        corporate_domain = CORPORATE_EMAIL_DOMAIN.lstrip("@")

        staff_user = CustomUser.objects.create_user(
            email=f"staff@{corporate_domain}",
            password="StrongPassword123",
            user_name="Staff Candidate",
            role=CustomUser.ROLE_CUSTOMER_USER,
        )

        updated_user = UserUpdateService.update_user(
            user=staff_user,
            performed_by=self.admin_user,
            user_role=CustomUser.ROLE_OPERATIONS_STAFF,
        )

        staff_user.refresh_from_db()

        self.assertEqual(updated_user.pk, staff_user.pk)
        self.assertEqual(
            staff_user.user_role,
            CustomUser.ROLE_OPERATIONS_STAFF,
        )
        self.assertFalse(staff_user.is_staff)
        self.assertFalse(staff_user.is_superuser)