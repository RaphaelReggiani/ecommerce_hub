import logging

from ech.reviews.domain_events.events import (
    ReviewCreatedEvent,
    ReviewUpdatedEvent,
    ReviewApprovedEvent,
    ReviewRejectedEvent,
    ReviewHiddenEvent,
    ReviewRestoredEvent,
    ReviewCancelledEvent,
)


logger = logging.getLogger("ech.reviews.domain_events")


def handle_review_created(event: ReviewCreatedEvent):
    metadata = event.metadata or {}
    logger.info(
        "review_domain_event_created",
        extra={
            "payload": {
                "event_type": "review_created",
                "review_id": str(event.review_id),
                "occurred_at": event.occurred_at.isoformat(),
                "metadata": metadata,
            }
        },
    )


def handle_review_updated(event: ReviewUpdatedEvent):
    metadata = event.metadata or {}
    logger.info(
        "review_domain_event_updated",
        extra={
            "payload": {
                "event_type": "review_updated",
                "review_id": str(event.review_id),
                "occurred_at": event.occurred_at.isoformat(),
                "metadata": metadata,
            }
        },
    )


def handle_review_approved(event: ReviewApprovedEvent):
    metadata = event.metadata or {}
    logger.info(
        "review_domain_event_approved",
        extra={
            "payload": {
                "event_type": "review_approved",
                "review_id": str(event.review_id),
                "occurred_at": event.occurred_at.isoformat(),
                "metadata": metadata,
            }
        },
    )


def handle_review_rejected(event: ReviewRejectedEvent):
    metadata = event.metadata or {}
    logger.info(
        "review_domain_event_rejected",
        extra={
            "payload": {
                "event_type": "review_rejected",
                "review_id": str(event.review_id),
                "occurred_at": event.occurred_at.isoformat(),
                "metadata": metadata,
            }
        },
    )


def handle_review_hidden(event: ReviewHiddenEvent):
    metadata = event.metadata or {}
    logger.info(
        "review_domain_event_hidden",
        extra={
            "payload": {
                "event_type": "review_hidden",
                "review_id": str(event.review_id),
                "occurred_at": event.occurred_at.isoformat(),
                "metadata": metadata,
            }
        },
    )


def handle_review_restored(event: ReviewRestoredEvent):
    metadata = event.metadata or {}
    logger.info(
        "review_domain_event_restored",
        extra={
            "payload": {
                "event_type": "review_restored",
                "review_id": str(event.review_id),
                "occurred_at": event.occurred_at.isoformat(),
                "metadata": metadata,
            }
        },
    )


def handle_review_cancelled(event: ReviewCancelledEvent):
    metadata = event.metadata or {}
    logger.info(
        "review_domain_event_cancelled",
        extra={
            "payload": {
                "event_type": "review_cancelled",
                "review_id": str(event.review_id),
                "occurred_at": event.occurred_at.isoformat(),
                "metadata": metadata,
            }
        },
    )