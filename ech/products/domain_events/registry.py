from ech.products.domain_events.dispatcher import EventDispatcher
from ech.products.domain_events.events import (
    ProductCreatedEvent,
    ProductDeletedEvent,
    ProductImageUploadedEvent,
    ProductUpdatedEvent,
)
from ech.products.domain_events.handlers import (
    handle_product_created_event,
    handle_product_deleted_event,
    handle_product_image_uploaded_event,
    handle_product_updated_event,
)


def register_product_event_handlers():
    """
    Registers all product domain event handlers.

    This function is safe to call multiple times because it resets
    the in-memory handler registry before re-registering handlers.
    """

    EventDispatcher.clear()

    EventDispatcher.register(ProductCreatedEvent, handle_product_created_event)
    EventDispatcher.register(ProductUpdatedEvent, handle_product_updated_event)
    EventDispatcher.register(ProductDeletedEvent, handle_product_deleted_event)
    EventDispatcher.register(ProductImageUploadedEvent, handle_product_image_uploaded_event)