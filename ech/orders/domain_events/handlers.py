from django.utils import timezone

from ech.orders.models import OrderEvent
from ech.orders.domain_events.events import (
    OrderCreatedEvent,
    OrderConfirmedEvent,
    OrderProcessingStartedEvent,
    OrderShippedEvent,
    OrderDeliveredEvent,
    OrderCancelledEvent,
)


def handle_order_created_event(event: OrderCreatedEvent):
    OrderEvent.objects.create(
        order=event.order,
        event_type=OrderEvent.TYPE_CREATED,
        performed_by=event.performed_by,
        metadata={
            "created_at": timezone.now().isoformat()
        },
    )


def handle_order_confirmed_event(event: OrderConfirmedEvent):
    OrderEvent.objects.create(
        order=event.order,
        event_type=OrderEvent.TYPE_CONFIRMED,
        performed_by=event.performed_by,
        metadata={},
    )


def handle_order_processing_started_event(event: OrderProcessingStartedEvent):
    OrderEvent.objects.create(
        order=event.order,
        event_type=OrderEvent.TYPE_PROCESSING_STARTED,
        performed_by=event.performed_by,
        metadata={},
    )


def handle_order_shipped_event(event: OrderShippedEvent):
    OrderEvent.objects.create(
        order=event.order,
        event_type=OrderEvent.TYPE_SHIPPED,
        performed_by=event.performed_by,
        metadata={},
    )


def handle_order_delivered_event(event: OrderDeliveredEvent):
    OrderEvent.objects.create(
        order=event.order,
        event_type=OrderEvent.TYPE_DELIVERED,
        performed_by=event.performed_by,
        metadata={},
    )


def handle_order_cancelled_event(event: OrderCancelledEvent):
    OrderEvent.objects.create(
        order=event.order,
        event_type=OrderEvent.TYPE_CANCELLED,
        performed_by=event.performed_by,
        metadata={
            "reason": event.reason,
        },
    )