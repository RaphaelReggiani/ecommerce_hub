from rest_framework.permissions import BasePermission

from ech.admin_dashboard.constants.roles_management import (
    ALLOWED_ADMIN_DASHBOARD_ACCESS_ROLES,
    ALLOWED_ORDER_BULK_ACTION_ROLES,
    ALLOWED_REVIEW_BULK_MODERATION_ROLES,
    ALLOWED_NOTIFICATION_RETRY_ROLES,
    ALLOWED_PAYMENT_OPERATIONAL_ROLES,
)

from ech.admin_dashboard.constants.messages import (
    ADMIN_DASHBOARD_ACCESS_DENIED,
    ADMIN_ORDER_BULK_ACTION_PERMISSION_DENIED,
    ADMIN_REVIEW_BULK_MODERATION_PERMISSION_DENIED,
    ADMIN_NOTIFICATION_RETRY_PERMISSION_DENIED,
)


class CanAccessAdminDashboard(BasePermission):
    """
    Allows access to the Admin Dashboard for authorized administrative roles.
    """

    message = ADMIN_DASHBOARD_ACCESS_DENIED

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.user_role in ALLOWED_ADMIN_DASHBOARD_ACCESS_ROLES


class CanExecuteOrderBulkActions(BasePermission):
    """
    Allows execution of bulk order operations only for authorized roles.
    """

    message = ADMIN_ORDER_BULK_ACTION_PERMISSION_DENIED

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.user_role in ALLOWED_ORDER_BULK_ACTION_ROLES


class CanModerateReviews(BasePermission):
    """
    Allows bulk review moderation actions only for authorized roles.
    """

    message = ADMIN_REVIEW_BULK_MODERATION_PERMISSION_DENIED

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.user_role in ALLOWED_REVIEW_BULK_MODERATION_ROLES


class CanRetryNotifications(BasePermission):
    """
    Allows retry of failed notifications only for authorized roles.
    """

    message = ADMIN_NOTIFICATION_RETRY_PERMISSION_DENIED

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.user_role in ALLOWED_NOTIFICATION_RETRY_ROLES


class CanAccessPaymentOperationalMetrics(BasePermission):
    """
    Allows access to payment operational monitoring metrics.
    """

    message = ADMIN_DASHBOARD_ACCESS_DENIED

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.user_role in ALLOWED_PAYMENT_OPERATIONAL_ROLES


class CanAccessAdminDashboardObject(BasePermission):
    """
    Object-level permission for admin dashboard resources.
    """

    message = ADMIN_DASHBOARD_ACCESS_DENIED

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.user_role in ALLOWED_ADMIN_DASHBOARD_ACCESS_ROLES