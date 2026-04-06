from rest_framework.permissions import BasePermission

from ech.notifications.constants.roles_management import (
    ALLOWED_NOTIFICATIONS_ROLES,
)

from ech.notifications.constants.messages import (
    MSG_NOTIFICATION_MANAGEMENT_ACCESS_DENIED,
)


class IsNotificationRecipient(BasePermission):
    """
    Allows access only to the recipient of the notification.
    """

    message = MSG_NOTIFICATION_MANAGEMENT_ACCESS_DENIED

    def has_object_permission(self, request, view, obj):
        return obj.recipient_id == request.user.id


class CanManageNotifications(BasePermission):
    """
    Allows access only to users with management roles
    for the notifications domain.
    """

    message = MSG_NOTIFICATION_MANAGEMENT_ACCESS_DENIED

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.user_role in ALLOWED_NOTIFICATIONS_ROLES


class IsNotificationRecipientOrCanManageNotifications(BasePermission):
    """
    Allows access to the notification recipient or users
    who can manage notifications.
    Useful for endpoints shared by customers and staff.
    """

    message = MSG_NOTIFICATION_MANAGEMENT_ACCESS_DENIED

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if obj.recipient_id == user.id:
            return True

        return user.user_role in ALLOWED_NOTIFICATIONS_ROLES