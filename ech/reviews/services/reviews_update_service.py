from django.db import transaction

from ech.reviews.models import ReviewEvent
from ech.reviews.exceptions import (
    InvalidReviewRatingException,
)
from ech.reviews.selectors import get_review_by_id
from ech.reviews.services.reviews_log_service import ReviewsLogService
from ech.reviews.services.cache_service import ReviewsCacheService
from ech.reviews.domain_events.dispatcher import ReviewEventDispatcher
from ech.reviews.domain_events.events import ReviewUpdatedEvent


class ReviewsUpdateService:
    """
    Service responsible for updating reviews.

    Supports partial updates for customer-editable fields only.
    Also handles audit event creation, structured logging,
    domain event dispatch, and cache invalidation.
    """

    ALLOWED_UPDATE_FIELDS = {
        "rating",
        "title",
        "comment",
    }

    @staticmethod
    def _validate_rating(rating):
        if rating is not None and (rating < 1 or rating > 5):
            raise InvalidReviewRatingException()

    @classmethod
    def _extract_valid_fields(cls, **kwargs):
        """
        Keep only fields allowed for review updates.
        Ignore omitted fields represented as None.
        """
        return {
            key: value
            for key, value in kwargs.items()
            if key in cls.ALLOWED_UPDATE_FIELDS and value is not None
        }

    @staticmethod
    @transaction.atomic
    def update_review(
        *,
        review_id,
        performed_by=None,
        **kwargs,
    ):
        """
        Update a review with partial field support.

        Only customer-editable fields are allowed.
        Omitted fields are ignored.
        """

        review = get_review_by_id(review_id)

        update_data = ReviewsUpdateService._extract_valid_fields(**kwargs)

        if not update_data:
            return review

        if "rating" in update_data:
            ReviewsUpdateService._validate_rating(update_data["rating"])

        changed_fields = []

        for field, value in update_data.items():
            if getattr(review, field) != value:
                setattr(review, field, value)
                changed_fields.append(field)

        if not changed_fields:
            return review

        review.save(update_fields=changed_fields + ["updated_at"])

        ReviewEvent.objects.create(
            review=review,
            event_type=ReviewEvent.TYPE_UPDATED,
            performed_by=performed_by,
            metadata={
                "updated_fields": changed_fields,
            },
        )

        ReviewsLogService.log_review_updated(
            review=review,
            performed_by=performed_by,
            metadata={
                "updated_fields": changed_fields,
            },
        )

        ReviewEventDispatcher.dispatch(
            ReviewUpdatedEvent(
                review_id=review.id,
                metadata={
                    "updated_fields": changed_fields,
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