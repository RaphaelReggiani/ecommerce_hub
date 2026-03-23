from rest_framework.permissions import BasePermission

from ech.payments.constants.messages import (
    MSG_EXCEPTIONS_ERROR_PERMISSION_DENIED_TO_PERFORM_PAYMENT,
)
from ech.payments.constants.roles_management import ALLOWED_PAYMENT_ROLES


def _user_is_authenticated(user) -> bool:
    """
    Return whether the given user is authenticated.
    """
    return bool(user and user.is_authenticated)


def _user_is_payment_staff(user) -> bool:
    """
    Return whether the given user has one of the allowed
    payment management roles.
    """
    if not _user_is_authenticated(user):
        return False

    return user.user_role in ALLOWED_PAYMENT_ROLES


def _user_owns_payment(user, payment) -> bool:
    """
    Return whether the given user owns the payment.
    """
    if not _user_is_authenticated(user):
        return False

    if payment is None:
        return False

    return payment.customer_id == user.id


class IsAuthenticatedForPayments(BasePermission):
    """
    Allows access only to authenticated users.
    """

    message = MSG_EXCEPTIONS_ERROR_PERMISSION_DENIED_TO_PERFORM_PAYMENT

    def has_permission(self, request, view):
        return _user_is_authenticated(request.user)


class IsPaymentManagementRole(BasePermission):
    """
    Allows access only to users with payment management roles.
    Intended for operational/staff endpoints.
    """

    message = MSG_EXCEPTIONS_ERROR_PERMISSION_DENIED_TO_PERFORM_PAYMENT

    def has_permission(self, request, view):
        return _user_is_payment_staff(request.user)


class IsPaymentOwner(BasePermission):
    """
    Object-level permission that allows access only to the owner
    of the payment resource.
    """

    message = MSG_EXCEPTIONS_ERROR_PERMISSION_DENIED_TO_PERFORM_PAYMENT

    def has_object_permission(self, request, view, obj):
        return _user_owns_payment(request.user, obj)


class IsPaymentOwnerOrManagementRole(BasePermission):
    """
    Object-level permission that allows access to:
        - the payment owner
        - users with payment management roles
    Intended for detail endpoints where customers can see their own
    payment and staff can see any payment.
    """

    message = MSG_EXCEPTIONS_ERROR_PERMISSION_DENIED_TO_PERFORM_PAYMENT

    def has_permission(self, request, view):
        return _user_is_authenticated(request.user)

    def has_object_permission(self, request, view, obj):
        return (
            _user_owns_payment(request.user, obj)
            or _user_is_payment_staff(request.user)
        )


class IsPaymentTransactionOwnerOrManagementRole(BasePermission):
    """
    Object-level permission for payment transaction resources.

    Access is allowed to:
        - the owner of the related payment
        - users with payment management roles
    """

    message = MSG_EXCEPTIONS_ERROR_PERMISSION_DENIED_TO_PERFORM_PAYMENT

    def has_permission(self, request, view):
        return _user_is_authenticated(request.user)

    def has_object_permission(self, request, view, obj):
        payment = getattr(obj, "payment", None)

        return (
            _user_owns_payment(request.user, payment)
            or _user_is_payment_staff(request.user)
        )


class IsPaymentRefundOwnerOrManagementRole(BasePermission):
    """
    Object-level permission for payment refund resources.

    Access is allowed to:
        - the owner of the related payment
        - users with payment management roles
    """

    message = MSG_EXCEPTIONS_ERROR_PERMISSION_DENIED_TO_PERFORM_PAYMENT

    def has_permission(self, request, view):
        return _user_is_authenticated(request.user)

    def has_object_permission(self, request, view, obj):
        payment = getattr(obj, "payment", None)

        return (
            _user_owns_payment(request.user, payment)
            or _user_is_payment_staff(request.user)
        )