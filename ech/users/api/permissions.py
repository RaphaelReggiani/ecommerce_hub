from rest_framework.permissions import BasePermission

from ech.users.constants.messages import (
    MSG_ERROR_RESTRICTED_ACCESS,
)


class IsAuthenticatedAndActive(BasePermission):
    """
    Allows access only to authenticated and active users.
    """

    message = MSG_ERROR_RESTRICTED_ACCESS

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.is_active


class IsAuthenticatedActiveAndEmailConfirmed(BasePermission):
    """
    Allows access only to authenticated users with confirmed email.
    """

    message = MSG_ERROR_RESTRICTED_ACCESS

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if not user.is_active:
            return False

        return getattr(user, "email_confirmed", False)