from django.utils import timezone

from ech.products.domain_events.events import (
    ProductCreatedEvent,
    ProductDeletedEvent,
    ProductImageUploadedEvent,
    ProductUpdatedEvent,
)
from ech.products.models import ProductEventLog
from ech.products.utils.cache_keys import (
    invalidate_product_cache,
    invalidate_product_list_cache,
    set_product_cache,
)


def handle_product_created_event(event: ProductCreatedEvent):
    ProductEventLog.objects.create(
        product=event.product,
        event_type=ProductEventLog.EVENT_PRODUCT_CREATED,
        performed_by=event.performed_by,
        metadata={
            "created_at": timezone.now().isoformat(),
        },
    )

    set_product_cache(event.product)
    invalidate_product_list_cache()


def handle_product_updated_event(event: ProductUpdatedEvent):
    ProductEventLog.objects.create(
        product=event.product,
        event_type=ProductEventLog.EVENT_PRODUCT_UPDATED,
        performed_by=event.performed_by,
        metadata={
            "updated_at": timezone.now().isoformat(),
        },
    )

    invalidate_product_cache(event.product.id)
    set_product_cache(event.product)
    invalidate_product_list_cache()


def handle_product_deleted_event(event: ProductDeletedEvent):
    ProductEventLog.objects.create(
        product=event.product,
        event_type=ProductEventLog.EVENT_PRODUCT_DELETED,
        performed_by=event.performed_by,
        metadata={
            "reason": event.reason,
            "deleted_at": timezone.now().isoformat(),
        },
    )

    invalidate_product_cache(event.product.id)
    invalidate_product_list_cache()


def handle_product_image_uploaded_event(event: ProductImageUploadedEvent):
    ProductEventLog.objects.create(
        product=event.product,
        event_type=ProductEventLog.EVENT_PRODUCT_IMAGE_UPLOADED,
        performed_by=event.performed_by,
        metadata={
            "uploaded_at": timezone.now().isoformat(),
        },
    )

    invalidate_product_cache(event.product.id)
    set_product_cache(event.product)
    invalidate_product_list_cache()