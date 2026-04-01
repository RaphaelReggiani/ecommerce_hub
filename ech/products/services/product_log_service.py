from django.utils import timezone

from ech.products.models import ProductEventLog


def log_product_event(*, product, event_type, user=None, metadata=None):
    """
    Creates an audit log entry for product lifecycle events.

    This function is primarily used by domain event handlers to
    record product actions such as:

    - product created
    - product updated
    - product deleted
    - product image uploaded
    """

    ProductEventLog.objects.create(
        product=product,
        event_type=event_type,
        performed_by=user,
        metadata={
            "timestamp": timezone.now().isoformat(),
            **(metadata or {}),
        },
    )