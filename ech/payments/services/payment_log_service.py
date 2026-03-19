from typing import Any

from ech.payments.models import (
    Payment, 
    PaymentEvent,
)


class PaymentLogService:
    """
    Service responsible for registering payment audit events.

    This service centralizes PaymentEvent creation to keep
    business services cleaner and more consistent.
    """

    @staticmethod
    def log_event(
        *,
        payment: Payment,
        event_type: str,
        performed_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentEvent:
        """
        Create and return a payment audit event.

        Args:
            payment: The related payment instance.
            event_type: The payment event type.
            performed_by: Optional user responsible for the event.
            metadata: Optional structured event metadata.

        Returns:
            PaymentEvent: The created payment event.
        """

        return PaymentEvent.objects.create(
            payment=payment,
            event_type=event_type,
            performed_by=performed_by,
            metadata=metadata or {},
        )

    @staticmethod
    def log_created(
        *,
        payment: Payment,
        performed_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentEvent:
        """
        Register a payment created event.
        """

        return PaymentLogService.log_event(
            payment=payment,
            event_type=PaymentEvent.TYPE_CREATED,
            performed_by=performed_by,
            metadata=metadata,
        )

    @staticmethod
    def log_processing_started(
        *,
        payment: Payment,
        performed_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentEvent:
        """
        Register a payment processing started event.
        """

        return PaymentLogService.log_event(
            payment=payment,
            event_type=PaymentEvent.TYPE_PROCESSING_STARTED,
            performed_by=performed_by,
            metadata=metadata,
        )

    @staticmethod
    def log_authorized(
        *,
        payment: Payment,
        performed_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentEvent:
        """
        Register a payment authorized event.
        """

        return PaymentLogService.log_event(
            payment=payment,
            event_type=PaymentEvent.TYPE_AUTHORIZED,
            performed_by=performed_by,
            metadata=metadata,
        )

    @staticmethod
    def log_captured(
        *,
        payment: Payment,
        performed_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentEvent:
        """
        Register a payment captured event.
        """

        return PaymentLogService.log_event(
            payment=payment,
            event_type=PaymentEvent.TYPE_CAPTURED,
            performed_by=performed_by,
            metadata=metadata,
        )

    @staticmethod
    def log_failed(
        *,
        payment: Payment,
        performed_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentEvent:
        """
        Register a payment failed event.
        """

        return PaymentLogService.log_event(
            payment=payment,
            event_type=PaymentEvent.TYPE_FAILED,
            performed_by=performed_by,
            metadata=metadata,
        )

    @staticmethod
    def log_cancelled(
        *,
        payment: Payment,
        performed_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentEvent:
        """
        Register a payment cancelled event.
        """

        return PaymentLogService.log_event(
            payment=payment,
            event_type=PaymentEvent.TYPE_CANCELLED,
            performed_by=performed_by,
            metadata=metadata,
        )

    @staticmethod
    def log_refund_requested(
        *,
        payment: Payment,
        performed_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentEvent:
        """
        Register a payment refund requested event.
        """

        return PaymentLogService.log_event(
            payment=payment,
            event_type=PaymentEvent.TYPE_REFUND_REQUESTED,
            performed_by=performed_by,
            metadata=metadata,
        )

    @staticmethod
    def log_partially_refunded(
        *,
        payment: Payment,
        performed_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentEvent:
        """
        Register a payment partially refunded event.
        """

        return PaymentLogService.log_event(
            payment=payment,
            event_type=PaymentEvent.TYPE_PARTIALLY_REFUNDED,
            performed_by=performed_by,
            metadata=metadata,
        )

    @staticmethod
    def log_refunded(
        *,
        payment: Payment,
        performed_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentEvent:
        """
        Register a payment fully refunded event.
        """

        return PaymentLogService.log_event(
            payment=payment,
            event_type=PaymentEvent.TYPE_REFUNDED,
            performed_by=performed_by,
            metadata=metadata,
        )
    
    @staticmethod
    def log_refund_failed(
        *,
        payment: Payment,
        performed_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentEvent:
        """
        Register a payment refund failed event.
        """

        return PaymentLogService.log_event(
            payment=payment,
            event_type=PaymentEvent.TYPE_REFUND_FAILED,
            performed_by=performed_by,
            metadata=metadata,
        )

    @staticmethod
    def log_refund_cancelled(
        *,
        payment: Payment,
        performed_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentEvent:
        """
        Register a payment refund cancelled event.
        """

        return PaymentLogService.log_event(
            payment=payment,
            event_type=PaymentEvent.TYPE_REFUND_CANCELLED,
            performed_by=performed_by,
            metadata=metadata,
        )