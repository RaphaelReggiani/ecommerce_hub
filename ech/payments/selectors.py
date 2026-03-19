from ech.payments.constants.messages import (
    MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND,
    MSG_EXCEPTIONS_ERROR_PAYMENT_REFUND_NOT_FOUND,
    MSG_ERROR_PAYMENT_NOT_FOUND_FOR_PROVIDED_ORDER,
    MSG_ERROR_PAYMENT_LIFECYCLE_NOT_FOUND,
)

from django.db.models import Prefetch, QuerySet

from ech.payments.models import (
    Payment,
    PaymentEvent,
    PaymentLifecycle,
    PaymentRefund,
    PaymentTransaction,
)
from ech.payments.exceptions import (
    PaymentNotFound,
    PaymentRefundNotFound,
)


def get_payment_by_id(*, payment_id) -> Payment:
    """
    Return a payment by its ID.

    Raises:
        PaymentNotFound: If no payment matches the provided ID.
    """

    try:
        return Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist as exc:
        raise PaymentNotFound(MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND) from exc


def get_payment_by_reference(*, payment_reference: str) -> Payment:
    """
    Return a payment by its public payment reference.

    Raises:
        PaymentNotFound: If no payment matches the provided reference.
    """

    try:
        return Payment.objects.get(payment_reference=payment_reference)
    except Payment.DoesNotExist as exc:
        raise PaymentNotFound(MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND) from exc


def get_payment_with_details(*, payment_id) -> Payment:
    """
    Return a payment with related objects optimized for detail views.

    Includes:
        - order
        - customer
        - lifecycle
        - transactions
        - refunds
        - events

    Raises:
        PaymentNotFound: If no payment matches the provided ID.
    """

    queryset = (
        Payment.objects
        .select_related(
            "order",
            "customer",
            "lifecycle",
        )
        .prefetch_related(
            Prefetch(
                "transactions",
                queryset=PaymentTransaction.objects.select_related("performed_by"),
            ),
            Prefetch(
                "refunds",
                queryset=PaymentRefund.objects.select_related(
                    "requested_by",
                    "processed_by",
                ),
            ),
            Prefetch(
                "events",
                queryset=PaymentEvent.objects.select_related("performed_by"),
            ),
        )
    )

    try:
        return queryset.get(id=payment_id)
    except Payment.DoesNotExist as exc:
        raise PaymentNotFound(MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND) from exc


def get_payment_management_detail(*, payment_id) -> Payment:
    """
    Return a payment with full related data for management/admin detail screens.

    This selector is intended for internal staff/management views.
    """

    return get_payment_with_details(payment_id=payment_id)


def get_payment_for_customer(*, payment_id, customer_id) -> Payment:
    """
    Return a payment detail restricted to the owning customer.

    Raises:
        PaymentNotFound: If the payment does not exist
        or does not belong to the informed customer.
    """

    queryset = (
        Payment.objects
        .select_related(
            "order",
            "customer",
            "lifecycle",
        )
        .prefetch_related(
            Prefetch(
                "transactions",
                queryset=PaymentTransaction.objects.select_related("performed_by"),
            ),
            Prefetch(
                "refunds",
                queryset=PaymentRefund.objects.select_related(
                    "requested_by",
                    "processed_by",
                ),
            ),
        )
    )

    try:
        return queryset.get(id=payment_id, customer_id=customer_id)
    except Payment.DoesNotExist as exc:
        raise PaymentNotFound(MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND) from exc


def get_payment_by_order_id(*, order_id) -> Payment:
    """
    Return the payment associated with the given order.

    Raises:
        PaymentNotFound: If no payment is linked to the informed order.
    """

    try:
        return (
            Payment.objects
            .select_related("order", "customer", "lifecycle")
            .get(order_id=order_id)
        )
    except Payment.DoesNotExist as exc:
        raise PaymentNotFound(MSG_ERROR_PAYMENT_NOT_FOUND_FOR_PROVIDED_ORDER) from exc


def list_payments_for_customer(*, customer_id) -> QuerySet[Payment]:
    """
    Return all payments belonging to the informed customer.

    Optimized for customer payment list endpoints.
    """

    return (
        Payment.objects
        .filter(customer_id=customer_id)
        .select_related("order", "lifecycle")
        .order_by("-created_at")
    )


def list_payments_for_management() -> QuerySet[Payment]:
    """
    Return all payments for management/staff listing.

    Optimized for backoffice list endpoints.
    """

    return (
        Payment.objects
        .select_related("order", "customer", "lifecycle")
        .order_by("-created_at")
    )


def list_payments_by_status(*, status_value: str) -> QuerySet[Payment]:
    """
    Return all payments matching the given payment status.
    """

    return (
        Payment.objects
        .filter(status=status_value)
        .select_related("order", "customer", "lifecycle")
        .order_by("-created_at")
    )


def list_payments_by_method(*, method_value: str) -> QuerySet[Payment]:
    """
    Return all payments matching the given payment method.
    """

    return (
        Payment.objects
        .filter(method=method_value)
        .select_related("order", "customer", "lifecycle")
        .order_by("-created_at")
    )


def list_payment_transactions(*, payment_id) -> QuerySet[PaymentTransaction]:
    """
    Return all transactions for a given payment.
    """

    return (
        PaymentTransaction.objects
        .filter(payment_id=payment_id)
        .select_related("payment", "performed_by")
        .order_by("-created_at")
    )


def list_payment_refunds(*, payment_id) -> QuerySet[PaymentRefund]:
    """
    Return all refunds for a given payment.
    """

    return (
        PaymentRefund.objects
        .filter(payment_id=payment_id)
        .select_related("payment", "requested_by", "processed_by")
        .order_by("-created_at")
    )


def list_payment_events(*, payment_id) -> QuerySet[PaymentEvent]:
    """
    Return all audit events for a given payment.
    """

    return (
        PaymentEvent.objects
        .filter(payment_id=payment_id)
        .select_related("payment", "performed_by")
        .order_by("-created_at")
    )


def get_payment_lifecycle(*, payment_id) -> PaymentLifecycle:
    """
    Return the lifecycle object for a given payment.

    Raises:
        PaymentNotFound: If the payment or lifecycle does not exist.
    """

    try:
        payment = (
            Payment.objects
            .select_related("lifecycle")
            .get(id=payment_id)
        )
    except Payment.DoesNotExist as exc:
        raise PaymentNotFound(MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND) from exc

    if not hasattr(payment, "lifecycle"):
        raise PaymentNotFound(MSG_ERROR_PAYMENT_LIFECYCLE_NOT_FOUND)

    return payment.lifecycle


def get_payment_refund_by_id(*, refund_id) -> PaymentRefund:
    """
    Return a refund by its ID.

    Raises:
        PaymentRefundNotFound: If no refund matches the provided ID.
    """

    try:
        return (
            PaymentRefund.objects
            .select_related("payment", "requested_by", "processed_by")
            .get(id=refund_id)
        )
    except PaymentRefund.DoesNotExist as exc:
        raise PaymentRefundNotFound(MSG_EXCEPTIONS_ERROR_PAYMENT_REFUND_NOT_FOUND) from exc
    

def list_pending_payment_refunds() -> QuerySet[PaymentRefund]:
    """
    Return all pending refunds for staff/management workflows.
    """

    return (
        PaymentRefund.objects
        .filter(status=PaymentRefund.REFUND_STATUS_PENDING)
        .select_related("payment", "requested_by", "processed_by")
        .order_by("-created_at")
    )


def list_payment_refunds_for_management() -> QuerySet[PaymentRefund]:
    """
    Return all refunds for staff/management views.
    """

    return (
        PaymentRefund.objects
        .select_related("payment", "requested_by", "processed_by")
        .order_by("-created_at")
    )