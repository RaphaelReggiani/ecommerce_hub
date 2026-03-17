from ech.orders.domain_events.dispatcher import EventDispatcher
from ech.orders.domain_events.events import (
    OrderCreatedEvent,
    OrderConfirmedEvent,
    OrderProcessingStartedEvent,
    OrderShippedEvent,
    OrderDeliveredEvent,
    OrderCancelledEvent,
)
from ech.orders.domain_events.handlers import (
    handle_order_created_event,
    handle_order_confirmed_event,
    handle_order_processing_started_event,
    handle_order_shipped_event,
    handle_order_delivered_event,
    handle_order_cancelled_event,
)


def register_order_event_handlers():
    EventDispatcher._handlers = {}

    EventDispatcher.register(OrderCreatedEvent, handle_order_created_event)
    EventDispatcher.register(OrderConfirmedEvent, handle_order_confirmed_event)
    EventDispatcher.register(OrderProcessingStartedEvent, handle_order_processing_started_event)
    EventDispatcher.register(OrderShippedEvent, handle_order_shipped_event)
    EventDispatcher.register(OrderDeliveredEvent, handle_order_delivered_event)
    EventDispatcher.register(OrderCancelledEvent, handle_order_cancelled_event)