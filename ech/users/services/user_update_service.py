from django.contrib.auth import get_user_model
from django.db import transaction

from ech.users.constants.constants import CORPORATE_EMAIL_DOMAIN
from ech.users.exceptions import (
    InvalidRoleAssignmentError,
    UserDomainError,
)

User = get_user_model()


class UserUpdateService:
    """
    Handles controlled user profile updates.
    """

    EDITABLE_FIELDS = {
        "user_name",
        "user_phone",
        "user_country",
        "user_state",
        "user_address",
        "user_age",
    }

    @staticmethod
    @transaction.atomic
    def update_user(
        *,
        user,
        performed_by=None,
        **validated_data,
    ):
        """
        Update allowed user fields safely.

        Rules:
        - regular profile fields can be updated by the user themself
        - role changes should only be performed by authorized staff
        - unknown fields are ignored
        - no-op updates return the same instance unchanged
        """

        if user is None:
            raise UserDomainError("User instance is required.")

        update_fields = []

        profile_fields = {
            field: value
            for field, value in validated_data.items()
            if field in UserUpdateService.EDITABLE_FIELDS
        }

        for field, value in profile_fields.items():
            if getattr(user, field) != value:
                setattr(user, field, value)
                update_fields.append(field)

        if "user_role" in validated_data:
            UserUpdateService._validate_role_update_permissions(
                performed_by=performed_by,
            )

            new_role = validated_data["user_role"]

            if new_role != user.user_role:
                UserUpdateService._validate_role_assignment(
                    email=user.user_email,
                    role=new_role,
                )
                user.user_role = new_role
                update_fields.append("user_role")

                role_flags = UserUpdateService._resolve_role_flags(new_role)

                if user.is_staff != role_flags["is_staff"]:
                    user.is_staff = role_flags["is_staff"]
                    update_fields.append("is_staff")

                if user.is_superuser != role_flags["is_superuser"]:
                    user.is_superuser = role_flags["is_superuser"]
                    update_fields.append("is_superuser")

        if update_fields:
            user.full_clean()
            user.save(update_fields=list(dict.fromkeys(update_fields)))

        return user

    @staticmethod
    def _validate_role_update_permissions(*, performed_by):
        """
        Only privileged users can update roles.
        """

        if performed_by is None or not getattr(performed_by, "can_create_staff", False):
            raise InvalidRoleAssignmentError()

    @staticmethod
    def _validate_role_assignment(*, email: str, role: str):
        """
        Enforce the same staff email rule already used by the model.
        """

        if role == User.ROLE_CUSTOMER_USER:
            return

        corporate_domain = CORPORATE_EMAIL_DOMAIN.lstrip("@")
        email_domain = (email or "").split("@")[-1].lower()

        if email_domain != corporate_domain:
            raise InvalidRoleAssignmentError()

    @staticmethod
    def _resolve_role_flags(role: str):
        """
        Resolve staff/superuser flags based on the target role.
        """

        if role == User.ROLE_SUPERADMIN:
            return {
                "is_staff": True,
                "is_superuser": True,
            }

        if role == User.ROLE_ADMIN:
            return {
                "is_staff": True,
                "is_superuser": False,
            }

        if role in {
            User.ROLE_PAYMENT_STAFF,
            User.ROLE_OPERATIONS_STAFF,
            User.ROLE_SUPPORT_STAFF,
        }:
            return {
                "is_staff": False,
                "is_superuser": False,
            }

        return {
            "is_staff": False,
            "is_superuser": False,
        }