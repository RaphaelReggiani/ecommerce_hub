from django.db import transaction
from django.utils import timezone

from ech.reviews.models import (
    Review, 
    ReviewEvent,
)
from ech.reviews.exceptions import (
    InvalidReviewStatusTransitionException,
)
from ech.reviews.selectors import get_review_by_id
from ech.reviews.services.review_log_service import ReviewsLogService
from ech.reviews.services.cache_service import ReviewsCacheService
from ech.reviews.domain_events.dispatcher import ReviewEventDispatcher
from ech.reviews.domain_events.events import (
    ReviewApprovedEvent,
    ReviewRejectedEvent,
    ReviewHiddenEvent,
    ReviewRestoredEvent,
    ReviewCancelledEvent,
)


class ReviewsStatusService:
    """
    Service responsible for review status transitions.

    Centralizes lifecycle transition validation, lifecycle timestamp updates,
    audit event creation, structured logging, and cache invalidation.
    """

    ALLOWED_TRANSITIONS = {
        Review.REVIEW_STATUS_PENDING: {
            Review.REVIEW_STATUS_APPROVED,
            Review.REVIEW_STATUS_REJECTED,
            Review.REVIEW_STATUS_CANCELLED,
        },
        Review.REVIEW_STATUS_APPROVED: {
            Review.REVIEW_STATUS_HIDDEN,
            Review.REVIEW_STATUS_CANCELLED,
        },
        Review.REVIEW_STATUS_REJECTED: {
            Review.REVIEW_STATUS_APPROVED,
            Review.REVIEW_STATUS_CANCELLED,
        },
        Review.REVIEW_STATUS_HIDDEN: {
            Review.REVIEW_STATUS_APPROVED,
            Review.REVIEW_STATUS_CANCELLED,
        },
        Review.REVIEW_STATUS_CANCELLED: set(),
    }

    EVENT_TYPE_BY_STATUS = {
        Review.REVIEW_STATUS_APPROVED: ReviewEvent.TYPE_APPROVED,
        Review.REVIEW_STATUS_REJECTED: ReviewEvent.TYPE_REJECTED,
        Review.REVIEW_STATUS_HIDDEN: ReviewEvent.TYPE_HIDDEN,
        Review.REVIEW_STATUS_CANCELLED: ReviewEvent.TYPE_CANCELLED,
    }

    DOMAIN_EVENT_BY_STATUS = {
        Review.REVIEW_STATUS_APPROVED: ReviewApprovedEvent,
        Review.REVIEW_STATUS_REJECTED: ReviewRejectedEvent,
        Review.REVIEW_STATUS_HIDDEN: ReviewHiddenEvent,
        Review.REVIEW_STATUS_CANCELLED: ReviewCancelledEvent,
    }

    @classmethod
    def _validate_transition(cls, current_status, new_status):
        allowed_statuses = cls.ALLOWED_TRANSITIONS.get(current_status, set())

        if new_status not in allowed_statuses:
            raise InvalidReviewStatusTransitionException()

    @staticmethod
    def _update_lifecycle_fields(lifecycle, previous_status, new_status):
        now = timezone.now()

        if new_status == Review.REVIEW_STATUS_APPROVED:
            lifecycle.approved_at = now

            if previous_status == Review.REVIEW_STATUS_HIDDEN:
                lifecycle.hidden_at = None

            if previous_status == Review.REVIEW_STATUS_REJECTED:
                lifecycle.rejected_at = None

        elif new_status == Review.REVIEW_STATUS_REJECTED:
            lifecycle.rejected_at = now

        elif new_status == Review.REVIEW_STATUS_HIDDEN:
            lifecycle.hidden_at = now

        elif new_status == Review.REVIEW_STATUS_CANCELLED:
            lifecycle.cancelled_at = now

        lifecycle.save()

    @classmethod
    @transaction.atomic
    def change_status(
        cls,
        *,
        review_id,
        new_status,
        performed_by=None,
        moderation_reason="",
        metadata=None,
    ):
        """
        Change review status with lifecycle tracking,
        event registration, structured logging, and cache invalidation.
        """

        review = get_review_by_id(review_id)

        if review.status == new_status:
            return review

        previous_status = review.status

        cls._validate_transition(previous_status, new_status)

        review.status = new_status

        if new_status in {
            Review.REVIEW_STATUS_APPROVED,
            Review.REVIEW_STATUS_REJECTED,
            Review.REVIEW_STATUS_HIDDEN,
        }:
            review.moderated_by = performed_by
            review.moderated_at = timezone.now()
            review.moderation_reason = moderation_reason or ""

        review.save(
            update_fields=[
                "status",
                "moderated_by",
                "moderated_at",
                "moderation_reason",
                "updated_at",
            ]
        )

        cls._update_lifecycle_fields(
            review.lifecycle,
            previous_status,
            new_status,
        )

        event_type = cls.EVENT_TYPE_BY_STATUS.get(new_status)

        merged_metadata = {
            "previous_status": previous_status,
            "new_status": new_status,
            "moderation_reason": moderation_reason or "",
            **(metadata or {}),
        }

        if event_type:
            ReviewEvent.objects.create(
                review=review,
                event_type=event_type,
                performed_by=performed_by,
                metadata=merged_metadata,
            )

        ReviewsLogService.log_review_status_changed(
            review=review,
            performed_by=performed_by,
            metadata=merged_metadata,
        )

        domain_event_class = cls.DOMAIN_EVENT_BY_STATUS.get(new_status)

        if domain_event_class:
            if (
                previous_status == Review.REVIEW_STATUS_HIDDEN
                and new_status == Review.REVIEW_STATUS_APPROVED
            ):
                domain_event_class = ReviewRestoredEvent

            ReviewEventDispatcher.dispatch(
                domain_event_class(
                    review_id=review.id,
                    metadata={
                        **merged_metadata,
                        "performed_by_id": (
                            performed_by.id if performed_by else None
                        ),
                    },
                )
            )

        ReviewsCacheService.invalidate_review_aggregate(
            review_id=review.id,
            customer_id=review.customer_id,
            product_id=review.product_id,
        )

        return review