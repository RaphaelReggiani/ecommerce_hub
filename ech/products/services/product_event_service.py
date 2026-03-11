from ech.products.models import ProductEventLog


def log_product_event(product, event_type, user=None, metadata=None):
    """
    Creates an audit log entry for product actions.
    """

    ProductEventLog.objects.create(
        product=product,
        event_type=event_type,
        performed_by=user,
        metadata=metadata or {}
    )