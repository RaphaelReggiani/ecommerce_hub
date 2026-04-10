from rest_framework.permissions import BasePermission

from ech.analytics.constants.roles_management import (
    ALLOWED_ANALYTICS_ROLES,
)

from ech.analytics.constants.messages import (
    ANALYTICS_SNAPSHOT_ACCESS_DENIED,
)


class CanAccessAnalytics(BasePermission):
    """
    Allows access only to users with analytics management roles.
    """

    message = ANALYTICS_SNAPSHOT_ACCESS_DENIED

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.user_role in ALLOWED_ANALYTICS_ROLES


class CanAccessAnalyticsObject(BasePermission):
    """
    Allows access to analytics objects only for authorized analytics roles.
    Useful for detail endpoints involving specific analytics resources.
    """

    message = ANALYTICS_SNAPSHOT_ACCESS_DENIED

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.user_role in ALLOWED_ANALYTICS_ROLES