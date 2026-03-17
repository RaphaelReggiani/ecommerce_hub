from dataclasses import dataclass


@dataclass(frozen=True)
class OrderCreatedEvent:
    order: object
    performed_by: object


@dataclass(frozen=True)
class OrderConfirmedEvent:
    order: object
    performed_by: object


@dataclass(frozen=True)
class OrderProcessingStartedEvent:
    order: object
    performed_by: object


@dataclass(frozen=True)
class OrderShippedEvent:
    order: object
    performed_by: object


@dataclass(frozen=True)
class OrderDeliveredEvent:
    order: object
    performed_by: object


@dataclass(frozen=True)
class OrderCancelledEvent:
    order: object
    performed_by: object
    reason: str = "manual_cancellation"