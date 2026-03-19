from ech.payments.domain_events.dispatcher import payment_event_dispatcher
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
from ech.payments.domain_events.handlers import (
    handle_payment_authorized,
    handle_payment_cancelled,
    handle_payment_captured,
    handle_payment_created,
    handle_payment_failed,
    handle_payment_processing_started,
    handle_payment_refund_cancelled,
    handle_payment_refund_failed,
    handle_payment_refund_processed,
    handle_payment_refund_requested,
)


def register_payment_event_handlers() -> None:
    """
    Register all payment domain event handlers.

    This function is intended to be called once during app startup.
    """

    payment_event_dispatcher.register(
        PaymentCreatedEvent,
        handle_payment_created,
    )
    payment_event_dispatcher.register(
        PaymentProcessingStartedEvent,
        handle_payment_processing_started,
    )
    payment_event_dispatcher.register(
        PaymentAuthorizedEvent,
        handle_payment_authorized,
    )
    payment_event_dispatcher.register(
        PaymentCapturedEvent,
        handle_payment_captured,
    )
    payment_event_dispatcher.register(
        PaymentFailedEvent,
        handle_payment_failed,
    )
    payment_event_dispatcher.register(
        PaymentCancelledEvent,
        handle_payment_cancelled,
    )
    payment_event_dispatcher.register(
        PaymentRefundRequestedEvent,
        handle_payment_refund_requested,
    )
    payment_event_dispatcher.register(
        PaymentRefundProcessedEvent,
        handle_payment_refund_processed,
    )
    payment_event_dispatcher.register(
        PaymentRefundFailedEvent,
        handle_payment_refund_failed,
    )
    payment_event_dispatcher.register(
        PaymentRefundCancelledEvent,
        handle_payment_refund_cancelled,
    )