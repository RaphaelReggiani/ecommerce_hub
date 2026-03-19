from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from django.utils import timezone


@dataclass(slots=True)
class BasePaymentDomainEvent:
    """
    Base class for all payment domain events.
    """

    payment_id: UUID
    occurred_at: datetime = field(default_factory=timezone.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PaymentCreatedEvent(BasePaymentDomainEvent):
    """
    Dispatched when a payment is successfully created.
    """

    order_id: UUID | None = None
    customer_id: UUID | None = None
    payment_reference: str = ""
    method: str = ""
    status: str = ""
    amount: str = ""
    currency: str = ""


@dataclass(slots=True)
class PaymentProcessingStartedEvent(BasePaymentDomainEvent):
    """
    Dispatched when a payment enters processing state.
    """

    previous_status: str = ""
    new_status: str = ""


@dataclass(slots=True)
class PaymentAuthorizedEvent(BasePaymentDomainEvent):
    """
    Dispatched when a payment is authorized.
    """

    previous_status: str = ""
    new_status: str = ""
    transaction_id: UUID | None = None


@dataclass(slots=True)
class PaymentCapturedEvent(BasePaymentDomainEvent):
    """
    Dispatched when a payment is captured.
    """

    previous_status: str = ""
    new_status: str = ""
    transaction_id: UUID | None = None


@dataclass(slots=True)
class PaymentFailedEvent(BasePaymentDomainEvent):
    """
    Dispatched when a payment fails.
    """

    previous_status: str = ""
    new_status: str = ""
    transaction_id: UUID | None = None
    failure_code: str = ""
    failure_message: str = ""


@dataclass(slots=True)
class PaymentCancelledEvent(BasePaymentDomainEvent):
    """
    Dispatched when a payment is cancelled.
    """

    previous_status: str = ""
    new_status: str = ""
    transaction_id: UUID | None = None


@dataclass(slots=True)
class PaymentRefundRequestedEvent(BasePaymentDomainEvent):
    """
    Dispatched when a refund request is created.
    """

    refund_id: UUID | None = None
    amount: str = ""
    reason: str = ""


@dataclass(slots=True)
class PaymentRefundProcessedEvent(BasePaymentDomainEvent):
    """
    Dispatched when a refund is processed successfully.
    """

    refund_id: UUID | None = None
    transaction_id: UUID | None = None
    amount: str = ""
    refunded_amount: str = ""
    full_refund: bool = False
    partial_refund: bool = False


@dataclass(slots=True)
class PaymentRefundFailedEvent(BasePaymentDomainEvent):
    """
    Dispatched when a refund processing fails.
    """

    refund_id: UUID | None = None
    amount: str = ""
    reason: str = ""


@dataclass(slots=True)
class PaymentRefundCancelledEvent(BasePaymentDomainEvent):
    """
    Dispatched when a refund request is cancelled.
    """

    refund_id: UUID | None = None
    amount: str = ""
    reason: str = ""