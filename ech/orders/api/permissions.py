from rest_framework.permissions import BasePermission

from ech.orders.constants.roles_management import (
    ALLOWED_ORDERS_ROLES,
)

from ech.orders.constants.messages import (
    MSG_ERROR_PERMISSIONDENIED_TO_ACCESS_ORDER,
    MSG_ERROR_PERMISSIONDENIED_TO_MANAGE_ORDER,
)


class IsOrderOwner(BasePermission):
    """
    Allows access only to the owner of the order.
    """

    message = MSG_ERROR_PERMISSIONDENIED_TO_ACCESS_ORDER

    def has_object_permission(self, request, view, obj):
        return obj.customer_id == request.user.id


class CanManageOrders(BasePermission):
    """
    Allows access only to users with management roles
    for the orders domain.
    """

    message = MSG_ERROR_PERMISSIONDENIED_TO_MANAGE_ORDER

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.user_role in ALLOWED_ORDERS_ROLES


class IsOrderOwnerOrCanManageOrders(BasePermission):
    """
    Allows access to the order owner or users who can manage orders.
    Useful for detail endpoints shared by customers and staff.
    """

    message = MSG_ERROR_PERMISSIONDENIED_TO_ACCESS_ORDER

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if obj.customer_id == user.id:
            return True

        return user.user_role in ALLOWED_ORDERS_ROLES
