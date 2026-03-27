from rest_framework.permissions import BasePermission

from ech.shipping.constants.roles_management import (
    ALLOWED_SHIPPING_ROLES,
)

from ech.shipping.constants.messages import (
    SHIPMENT_ACCESS_DENIED,
)


class IsShipmentOwner(BasePermission):
    """
    Allows access only to the owner of the shipment.
    """

    message = SHIPMENT_ACCESS_DENIED

    def has_object_permission(self, request, view, obj):
        return obj.customer_id == request.user.id


class CanManageShipments(BasePermission):
    """
    Allows access only to users with management roles
    for the shipping domain.
    """

    message = SHIPMENT_ACCESS_DENIED

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.user_role in ALLOWED_SHIPPING_ROLES


class IsShipmentOwnerOrCanManageShipments(BasePermission):
    """
    Allows access to the shipment owner or users who can manage shipments.
    Useful for detail endpoints shared by customers and staff.
    """

    message = SHIPMENT_ACCESS_DENIED

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if obj.customer_id == user.id:
            return True

        return user.user_role in ALLOWED_SHIPPING_ROLES