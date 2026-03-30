from ech.reviews.domain_events.dispatcher import ReviewEventDispatcher
from ech.reviews.domain_events.events import (
    ReviewCreatedEvent,
    ReviewUpdatedEvent,
    ReviewApprovedEvent,
    ReviewRejectedEvent,
    ReviewHiddenEvent,
    ReviewRestoredEvent,
    ReviewCancelledEvent,
)
from ech.reviews.domain_events.handlers import (
    handle_review_created,
    handle_review_updated,
    handle_review_approved,
    handle_review_rejected,
    handle_review_hidden,
    handle_review_restored,
    handle_review_cancelled,
)


def register_review_event_handlers():
    """
    Register all reviews domain event handlers.

    Safe to call multiple times because dispatcher registration
    prevents duplicate handlers.
    """

    ReviewEventDispatcher.register(
        ReviewCreatedEvent,
        handle_review_created,
    )
    ReviewEventDispatcher.register(
        ReviewUpdatedEvent,
        handle_review_updated,
    )
    ReviewEventDispatcher.register(
        ReviewApprovedEvent,
        handle_review_approved,
    )
    ReviewEventDispatcher.register(
        ReviewRejectedEvent,
        handle_review_rejected,
    )
    ReviewEventDispatcher.register(
        ReviewHiddenEvent,
        handle_review_hidden,
    )
    ReviewEventDispatcher.register(
        ReviewRestoredEvent,
        handle_review_restored,
    )
    ReviewEventDispatcher.register(
        ReviewCancelledEvent,
        handle_review_cancelled,
    )