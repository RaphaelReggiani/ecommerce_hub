import logging


logger = logging.getLogger(__name__)


def handle_shipment_created(event):
    """
    Handle shipment created event.

    This handler is intentionally lightweight and currently
    focused on observability. It can later be expanded to:
    - invalidate cache
    - notify analytics
    - trigger integrations
    """

    logger.info(
        "Handled shipment created domain event.",
        extra={
            "event_name": event.event_name,
            "shipment_id": str(event.shipment_id),
            "order_id": str(event.order_id),
            "customer_id": str(event.customer_id),
            "performed_by_id": event.performed_by_id,
        },
    )


def handle_shipment_status_changed(event):
    """
    Handle shipment status changed event.

    This handler is intentionally lightweight and can later
    be expanded with additional side effects.
    """

    logger.info(
        "Handled shipment status changed domain event.",
        extra={
            "event_name": event.event_name,
            "shipment_id": str(event.shipment_id),
            "previous_status": event.previous_status,
            "new_status": event.new_status,
            "performed_by_id": event.performed_by_id,
        },
    )