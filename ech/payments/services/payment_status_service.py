from django.utils import timezone

from ech.orders.models import Order
from ech.payments.exceptions import (
    InvalidPaymentStatusTransition,
)
from ech.payments.models import Payment
from ech.payments.services.payment_log_service import PaymentLogService

from ech.payments.domain_events.dispatcher import payment_event_dispatcher
from ech.payments.domain_events.events import (
    PaymentAuthorizedEvent,
    PaymentCancelledEvent,
    PaymentCapturedEvent,
    PaymentFailedEvent,
    PaymentProcessingStartedEvent,
    PaymentRefundProcessedEvent,
)


class PaymentStatusService:
    """
    Service responsible for managing payment status transitions.

    This is the single source of truth for:
        - Valid payment state transitions
        - PaymentLifecycle updates
        - Order payment status synchronization
        - Refund lifecycle integration
    """

    VALID_TRANSITIONS = {
        Payment.PAYMENT_STATUS_PENDING: {
            Payment.PAYMENT_STATUS_PROCESSING,
            Payment.PAYMENT_STATUS_FAILED,
            Payment.PAYMENT_STATUS_CANCELLED,
        },
        Payment.PAYMENT_STATUS_PROCESSING: {
            Payment.PAYMENT_STATUS_AUTHORIZED,
            Payment.PAYMENT_STATUS_CAPTURED,
            Payment.PAYMENT_STATUS_FAILED,
            Payment.PAYMENT_STATUS_CANCELLED,
        },
        Payment.PAYMENT_STATUS_AUTHORIZED: {
            Payment.PAYMENT_STATUS_CAPTURED,
            Payment.PAYMENT_STATUS_CANCELLED,
        },
        Payment.PAYMENT_STATUS_CAPTURED: {
            Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED,
            Payment.PAYMENT_STATUS_REFUNDED,
        },
        Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED: {
            Payment.PAYMENT_STATUS_REFUNDED,
        },
        Payment.PAYMENT_STATUS_FAILED: set(),
        Payment.PAYMENT_STATUS_CANCELLED: set(),
        Payment.PAYMENT_STATUS_REFUNDED: set(),
    }

    @classmethod
    def change_status(
        cls,
        *,
        payment: Payment,
        new_status: str,
        performed_by=None,
        metadata: dict | None = None,
    ) -> Payment:
        """
        Change payment status with full domain consistency.

        Handles:
            - status validation
            - lifecycle updates
            - order sync
            - audit logging
        """

        cls._validate_transition(
            current_status=payment.status,
            new_status=new_status,
        )

        previous_status = payment.status

        payment.status = new_status
        payment.save(update_fields=["status", "updated_at"])

        cls._update_lifecycle(payment=payment, new_status=new_status)
        cls._sync_order(payment=payment)

        event_metadata = {
            "previous_status": previous_status,
            "new_status": new_status,
            **(metadata or {}),
        }

        cls._log_event(
            payment=payment,
            previous_status=previous_status,
            new_status=new_status,
            performed_by=performed_by,
            metadata=event_metadata,
        )

        return payment

    @classmethod
    def _validate_transition(
        cls,
        *,
        current_status: str,
        new_status: str,
    ) -> None:
        """
        Validate if a status transition is allowed.
        """

        if current_status == new_status:
            return

        allowed = cls.VALID_TRANSITIONS.get(current_status, set())

        if new_status not in allowed:
            raise InvalidPaymentStatusTransition(
                f"Cannot transition payment from '{current_status}' to '{new_status}'."
            )

    @staticmethod
    def _update_lifecycle(*, payment: Payment, new_status: str) -> None:
        """
        Update PaymentLifecycle timestamps based on status.
        """

        lifecycle = payment.lifecycle
        now = timezone.now()

        update_fields = []

        if new_status == Payment.PAYMENT_STATUS_PROCESSING:
            lifecycle.processing_started_at = lifecycle.processing_started_at or now
            update_fields.append("processing_started_at")

        elif new_status == Payment.PAYMENT_STATUS_AUTHORIZED:
            lifecycle.authorized_at = lifecycle.authorized_at or now
            update_fields.append("authorized_at")

        elif new_status == Payment.PAYMENT_STATUS_CAPTURED:
            lifecycle.captured_at = lifecycle.captured_at or now
            update_fields.append("captured_at")

        elif new_status == Payment.PAYMENT_STATUS_FAILED:
            lifecycle.failed_at = lifecycle.failed_at or now
            update_fields.append("failed_at")

        elif new_status == Payment.PAYMENT_STATUS_CANCELLED:
            lifecycle.cancelled_at = lifecycle.cancelled_at or now
            update_fields.append("cancelled_at")

        elif new_status == Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED:
            lifecycle.partially_refunded_at = lifecycle.partially_refunded_at or now
            update_fields.append("partially_refunded_at")

        elif new_status == Payment.PAYMENT_STATUS_REFUNDED:
            lifecycle.refunded_at = lifecycle.refunded_at or now
            update_fields.append("refunded_at")

        if update_fields:
            lifecycle.save(update_fields=update_fields + ["updated_at"])

    @staticmethod
    def _sync_order(*, payment: Payment) -> None:
        """
        Synchronize Order.payment_status and lifecycle when needed.
        """

        order: Order = payment.order

        order.payment_status = payment.status
        order.save(update_fields=["payment_status", "updated_at"])

        if payment.status == Payment.PAYMENT_STATUS_REFUNDED:
            if hasattr(order, "lifecycle"):
                if not order.lifecycle.refunded_at:
                    order.lifecycle.refunded_at = timezone.now()
                    order.lifecycle.save(update_fields=["refunded_at", "updated_at"])

    @staticmethod
    def _log_event(
        *,
        payment: Payment,
        previous_status: str,
        new_status: str,
        performed_by=None,
        metadata: dict | None = None,
    ) -> None:
        """
        Dispatch appropriate event log based on new status.
        """

        if new_status == Payment.PAYMENT_STATUS_PROCESSING:
            PaymentLogService.log_processing_started(
                payment=payment,
                performed_by=performed_by,
                metadata=metadata,
            )

            payment_event_dispatcher.dispatch(
                PaymentProcessingStartedEvent(
                    payment_id=payment.id,
                    previous_status=previous_status,
                    new_status=new_status,
                    metadata=metadata or {},
                )
            )

        elif new_status == Payment.PAYMENT_STATUS_AUTHORIZED:
            PaymentLogService.log_authorized(
                payment=payment,
                performed_by=performed_by,
                metadata=metadata,
            )

            payment_event_dispatcher.dispatch(
                PaymentAuthorizedEvent(
                    payment_id=payment.id,
                    previous_status=previous_status,
                    new_status=new_status,
                    transaction_id=metadata.get("transaction_id") if metadata else None,
                    metadata=metadata or {},
                )
            )

        elif new_status == Payment.PAYMENT_STATUS_CAPTURED:
            PaymentLogService.log_captured(
                payment=payment,
                performed_by=performed_by,
                metadata=metadata,
            )

            payment_event_dispatcher.dispatch(
                PaymentCapturedEvent(
                    payment_id=payment.id,
                    previous_status=previous_status,
                    new_status=new_status,
                    transaction_id=metadata.get("transaction_id") if metadata else None,
                    metadata=metadata or {},
                )
            )

        elif new_status == Payment.PAYMENT_STATUS_FAILED:
            PaymentLogService.log_failed(
                payment=payment,
                performed_by=performed_by,
                metadata=metadata,
            )

            payment_event_dispatcher.dispatch(
                PaymentFailedEvent(
                    payment_id=payment.id,
                    previous_status=previous_status,
                    new_status=new_status,
                    transaction_id=metadata.get("transaction_id") if metadata else None,
                    failure_code=metadata.get("failure_code", "") if metadata else "",
                    failure_message=metadata.get("failure_message", "") if metadata else "",
                    metadata=metadata or {},
                )
            )

        elif new_status == Payment.PAYMENT_STATUS_CANCELLED:
            PaymentLogService.log_cancelled(
                payment=payment,
                performed_by=performed_by,
                metadata=metadata,
            )

            payment_event_dispatcher.dispatch(
                PaymentCancelledEvent(
                    payment_id=payment.id,
                    previous_status=previous_status,
                    new_status=new_status,
                    transaction_id=metadata.get("transaction_id") if metadata else None,
                    metadata=metadata or {},
                )
            )

        elif new_status == Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED:
            PaymentLogService.log_partially_refunded(
                payment=payment,
                performed_by=performed_by,
                metadata=metadata,
            )

            payment_event_dispatcher.dispatch(
                PaymentRefundProcessedEvent(
                    payment_id=payment.id,
                    refund_id=metadata.get("refund_id") if metadata else None,
                    transaction_id=metadata.get("transaction_id") if metadata else None,
                    amount=metadata.get("amount", "") if metadata else "",
                    refunded_amount=metadata.get("refunded_amount", "") if metadata else "",
                    full_refund=False,
                    partial_refund=True,
                    metadata=metadata or {},
                )
            )

        elif new_status == Payment.PAYMENT_STATUS_REFUNDED:
            PaymentLogService.log_refunded(
                payment=payment,
                performed_by=performed_by,
                metadata=metadata,
            )

            payment_event_dispatcher.dispatch(
                PaymentRefundProcessedEvent(
                    payment_id=payment.id,
                    refund_id=metadata.get("refund_id") if metadata else None,
                    transaction_id=metadata.get("transaction_id") if metadata else None,
                    amount=metadata.get("amount", "") if metadata else "",
                    refunded_amount=metadata.get("refunded_amount", "") if metadata else "",
                    full_refund=True,
                    partial_refund=False,
                    metadata=metadata or {},
                )
            )