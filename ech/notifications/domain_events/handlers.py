import logging


logger = logging.getLogger(__name__)


def handle_notification_created(event):
    """
    Handle notification created event.

    This handler is intentionally lightweight and focused on
    observability. It can later be expanded to support:
    - analytics pipelines
    - integration triggers
    - external event streaming
    """

    logger.info(
        "Handled notification created domain event.",
        extra={
            "event_name": event.event_name,
            "notification_id": str(event.notification_id),
            "recipient_id": str(event.recipient_id),
            "notification_type": event.notification_type,
            "channel": event.channel,
            "performed_by_id": event.performed_by_id,
        },
    )


def handle_notification_status_changed(event):
    """
    Handle notification status changed event.
    """

    logger.info(
        "Handled notification status changed domain event.",
        extra={
            "event_name": event.event_name,
            "notification_id": str(event.notification_id),
            "previous_status": event.previous_status,
            "new_status": event.new_status,
            "performed_by_id": event.performed_by_id,
        },
    )


def handle_notification_cancelled(event):
    """
    Handle notification cancelled event.
    """

    logger.info(
        "Handled notification cancelled domain event.",
        extra={
            "event_name": event.event_name,
            "notification_id": str(event.notification_id),
            "recipient_id": str(event.recipient_id),
            "performed_by_id": event.performed_by_id,
        },
    )


def handle_notification_dispatched(event):
    """
    Handle notification dispatch event.
    """

    logger.info(
        "Handled notification dispatched domain event.",
        extra={
            "event_name": event.event_name,
            "notification_id": str(event.notification_id),
            "recipient_id": str(event.recipient_id),
            "channel": event.channel,
            "performed_by_id": event.performed_by_id,
        },
    )


def handle_notification_delivery_succeeded(event):
    """
    Handle successful notification delivery event.
    """

    logger.info(
        "Handled notification delivery succeeded domain event.",
        extra={
            "event_name": event.event_name,
            "notification_id": str(event.notification_id),
            "delivery_id": str(event.delivery_id),
            "recipient_id": str(event.recipient_id),
            "channel": event.channel,
            "performed_by_id": event.performed_by_id,
        },
    )


def handle_notification_delivery_failed(event):
    """
    Handle failed notification delivery event.
    """

    logger.warning(
        "Handled notification delivery failed domain event.",
        extra={
            "event_name": event.event_name,
            "notification_id": str(event.notification_id),
            "delivery_id": str(event.delivery_id),
            "recipient_id": str(event.recipient_id),
            "channel": event.channel,
            "performed_by_id": event.performed_by_id,
        },
    )