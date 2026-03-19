import logging

from ech.payments.domain_events.events import (
    PaymentAuthorizedEvent,
    PaymentCancelledEvent,
    PaymentCapturedEvent,
    PaymentCreatedEvent,
    PaymentFailedEvent,
    PaymentProcessingStartedEvent,
    PaymentRefundCancelledEvent,
    PaymentRefundFailedEvent,
    PaymentRefundProcessedEvent,
    PaymentRefundRequestedEvent,
)

logger = logging.getLogger(__name__)


def handle_payment_created(event: PaymentCreatedEvent) -> None:
    """
    Handle payment created domain event.
    """

    logger.info(
        "Payment created event dispatched.",
        extra={
            "payment_id": str(event.payment_id),
            "order_id": str(event.order_id) if event.order_id else "",
            "customer_id": str(event.customer_id) if event.customer_id else "",
            "payment_reference": event.payment_reference,
            "method": event.method,
            "status": event.status,
            "amount": event.amount,
            "currency": event.currency,
            "metadata": event.metadata,
        },
    )


def handle_payment_processing_started(event: PaymentProcessingStartedEvent) -> None:
    """
    Handle payment processing started domain event.
    """

    logger.info(
        "Payment processing started event dispatched.",
        extra={
            "payment_id": str(event.payment_id),
            "previous_status": event.previous_status,
            "new_status": event.new_status,
            "metadata": event.metadata,
        },
    )


def handle_payment_authorized(event: PaymentAuthorizedEvent) -> None:
    """
    Handle payment authorized domain event.
    """

    logger.info(
        "Payment authorized event dispatched.",
        extra={
            "payment_id": str(event.payment_id),
            "previous_status": event.previous_status,
            "new_status": event.new_status,
            "transaction_id": str(event.transaction_id) if event.transaction_id else "",
            "metadata": event.metadata,
        },
    )


def handle_payment_captured(event: PaymentCapturedEvent) -> None:
    """
    Handle payment captured domain event.
    """

    logger.info(
        "Payment captured event dispatched.",
        extra={
            "payment_id": str(event.payment_id),
            "previous_status": event.previous_status,
            "new_status": event.new_status,
            "transaction_id": str(event.transaction_id) if event.transaction_id else "",
            "metadata": event.metadata,
        },
    )


def handle_payment_failed(event: PaymentFailedEvent) -> None:
    """
    Handle payment failed domain event.
    """

    logger.warning(
        "Payment failed event dispatched.",
        extra={
            "payment_id": str(event.payment_id),
            "previous_status": event.previous_status,
            "new_status": event.new_status,
            "transaction_id": str(event.transaction_id) if event.transaction_id else "",
            "failure_code": event.failure_code,
            "failure_message": event.failure_message,
            "metadata": event.metadata,
        },
    )


def handle_payment_cancelled(event: PaymentCancelledEvent) -> None:
    """
    Handle payment cancelled domain event.
    """

    logger.info(
        "Payment cancelled event dispatched.",
        extra={
            "payment_id": str(event.payment_id),
            "previous_status": event.previous_status,
            "new_status": event.new_status,
            "transaction_id": str(event.transaction_id) if event.transaction_id else "",
            "metadata": event.metadata,
        },
    )


def handle_payment_refund_requested(event: PaymentRefundRequestedEvent) -> None:
    """
    Handle payment refund requested domain event.
    """

    logger.info(
        "Payment refund requested event dispatched.",
        extra={
            "payment_id": str(event.payment_id),
            "refund_id": str(event.refund_id) if event.refund_id else "",
            "amount": event.amount,
            "reason": event.reason,
            "metadata": event.metadata,
        },
    )


def handle_payment_refund_processed(event: PaymentRefundProcessedEvent) -> None:
    """
    Handle payment refund processed domain event.
    """

    logger.info(
        "Payment refund processed event dispatched.",
        extra={
            "payment_id": str(event.payment_id),
            "refund_id": str(event.refund_id) if event.refund_id else "",
            "transaction_id": str(event.transaction_id) if event.transaction_id else "",
            "amount": event.amount,
            "refunded_amount": event.refunded_amount,
            "full_refund": event.full_refund,
            "partial_refund": event.partial_refund,
            "metadata": event.metadata,
        },
    )


def handle_payment_refund_failed(event: PaymentRefundFailedEvent) -> None:
    """
    Handle payment refund failed domain event.
    """

    logger.warning(
        "Payment refund failed event dispatched.",
        extra={
            "payment_id": str(event.payment_id),
            "refund_id": str(event.refund_id) if event.refund_id else "",
            "amount": event.amount,
            "reason": event.reason,
            "metadata": event.metadata,
        },
    )


def handle_payment_refund_cancelled(event: PaymentRefundCancelledEvent) -> None:
    """
    Handle payment refund cancelled domain event.
    """

    logger.info(
        "Payment refund cancelled event dispatched.",
        extra={
            "payment_id": str(event.payment_id),
            "refund_id": str(event.refund_id) if event.refund_id else "",
            "amount": event.amount,
            "reason": event.reason,
            "metadata": event.metadata,
        },
    )