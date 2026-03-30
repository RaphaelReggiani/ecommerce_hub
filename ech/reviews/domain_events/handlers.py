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
    logger.info(
        "review_domain_event_created",
        extra={
            "payload": {
                "event_type": "review_created",
                "review_id": str(event.review_id),
                "occurred_at": event.occurred_at.isoformat(),
                "metadata": event.metadata,
            }
        },
    )


def handle_review_updated(event: ReviewUpdatedEvent):
    logger.info(
        "review_domain_event_updated",
        extra={
            "payload": {
                "event_type": "review_updated",
                "review_id": str(event.review_id),
                "occurred_at": event.occurred_at.isoformat(),
                "metadata": event.metadata,
            }
        },
    )


def handle_review_approved(event: ReviewApprovedEvent):
    logger.info(
        "review_domain_event_approved",
        extra={
            "payload": {
                "event_type": "review_approved",
                "review_id": str(event.review_id),
                "occurred_at": event.occurred_at.isoformat(),
                "metadata": event.metadata,
            }
        },
    )


def handle_review_rejected(event: ReviewRejectedEvent):
    logger.info(
        "review_domain_event_rejected",
        extra={
            "payload": {
                "event_type": "review_rejected",
                "review_id": str(event.review_id),
                "occurred_at": event.occurred_at.isoformat(),
                "metadata": event.metadata,
            }
        },
    )


def handle_review_hidden(event: ReviewHiddenEvent):
    logger.info(
        "review_domain_event_hidden",
        extra={
            "payload": {
                "event_type": "review_hidden",
                "review_id": str(event.review_id),
                "occurred_at": event.occurred_at.isoformat(),
                "metadata": event.metadata,
            }
        },
    )


def handle_review_restored(event: ReviewRestoredEvent):
    logger.info(
        "review_domain_event_restored",
        extra={
            "payload": {
                "event_type": "review_restored",
                "review_id": str(event.review_id),
                "occurred_at": event.occurred_at.isoformat(),
                "metadata": event.metadata,
            }
        },
    )


def handle_review_cancelled(event: ReviewCancelledEvent):
    logger.info(
        "review_domain_event_cancelled",
        extra={
            "payload": {
                "event_type": "review_cancelled",
                "review_id": str(event.review_id),
                "occurred_at": event.occurred_at.isoformat(),
                "metadata": event.metadata,
            }
        },
    )