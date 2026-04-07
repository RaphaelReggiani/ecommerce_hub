import logging


logger = logging.getLogger(__name__)


def handle_analytics_snapshot_created(event):
    """
    Handle analytics snapshot created event.

    This handler is intentionally lightweight and currently
    focused on observability. It can later be expanded to:

    - invalidate analytics cache
    - trigger dashboard refresh
    - update external analytics pipelines
    """

    logger.info(
        "Handled analytics snapshot created domain event.",
        extra={
            "event_name": event.event_name,
            "snapshot_id": str(event.snapshot_id),
            "period_type": event.period_type,
            "period_start": str(event.period_start),
            "period_end": str(event.period_end),
            "generated_by_id": event.generated_by_id,
        },
    )


def handle_analytics_snapshot_refreshed(event):
    """
    Handle analytics snapshot refreshed event.

    This handler is intentionally lightweight and can later
    be expanded with additional side effects.
    """

    logger.info(
        "Handled analytics snapshot refreshed domain event.",
        extra={
            "event_name": event.event_name,
            "snapshot_id": str(event.snapshot_id),
            "period_type": event.period_type,
            "period_start": str(event.period_start),
            "period_end": str(event.period_end),
            "refreshed_by_id": event.refreshed_by_id,
        },
    )


def handle_analytics_snapshot_failed(event):
    """
    Handle analytics snapshot failure event.

    This event provides observability for failed analytics
    snapshot generation or refresh operations.
    """

    logger.warning(
        "Handled analytics snapshot failed domain event.",
        extra={
            "event_name": event.event_name,
            "snapshot_id": str(event.snapshot_id) if event.snapshot_id else None,
            "period_type": event.period_type,
            "period_start": str(event.period_start),
            "period_end": str(event.period_end),
            "error_message": event.error_message,
            "performed_by_id": event.performed_by_id,
        },
    )