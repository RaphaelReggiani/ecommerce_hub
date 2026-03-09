from rest_framework.permissions import BasePermission, SAFE_METHODS
from ech.users.models import CustomUser

from ech.products.constants.messages import (
    MSG_NOT_HAVE_PERMISSION_TO_MANAGE_PRODUCTS,
    MSG_NOT_HAVE_PERMISSION_TO_MODIFY_PRODUCTS,
)

from ech.products.constants.roles_management import (
    ALLOWED_OPERATION_ROLES,
)


class BaseRolePermission(BasePermission):
    """
    Base permission class for role-based checks.
    """

    allowed_roles = set()

    def is_allowed(self, user):
        return (
            user
            and user.is_authenticated
            and user.user_role in self.allowed_roles
        )


class IsOperationsAdminOrSuperAdmin(BaseRolePermission):
    """
    Allows access only to Operations Staff, Admin and SuperAdmin users.
    Used for product management endpoints.
    """

    message = MSG_NOT_HAVE_PERMISSION_TO_MANAGE_PRODUCTS
    allowed_roles = ALLOWED_OPERATION_ROLES

    def has_permission(self, request, view):
        return self.is_allowed(request.user)


class IsPublicOrProductManager(BaseRolePermission):
    """
    Allows public read-only access to products,
    while restricting write operations to product managers.
    """

    allowed_roles = ALLOWED_OPERATION_ROLES

    def has_permission(self, request, view):

        if request.method in SAFE_METHODS:
            return True

        return self.is_allowed(request.user)


class IsProductOwnerOrManager(BaseRolePermission):
    """
    Allows modification if the user manages products
    or owns the product.
    """

    message = MSG_NOT_HAVE_PERMISSION_TO_MODIFY_PRODUCTS
    allowed_roles = ALLOWED_OPERATION_ROLES

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True

        user = request.user

        if self.is_allowed(user):
            return True

        return obj.sold_by == user