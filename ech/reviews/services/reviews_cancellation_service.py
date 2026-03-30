from django.db import transaction

from ech.reviews.models import (
    Review,
)
from ech.reviews.exceptions import (
    ReviewCancellationNotAllowedException,
)
from ech.reviews.selectors import get_review_by_id
from ech.reviews.services.reviews_status_service import ReviewsStatusService


class ReviewsCancellationService:
    """
    Service responsible for review cancellation rules.

    Cancellation is treated as a dedicated domain operation,
    while the actual status transition is delegated to
    ReviewsStatusService.
    """

    NOT_CANCELLABLE_STATUSES = {
        Review.REVIEW_STATUS_CANCELLED,
    }

    @classmethod
    def _validate_cancellation(cls, review):
        if review.status in cls.NOT_CANCELLABLE_STATUSES:
            raise ReviewCancellationNotAllowedException()

    @classmethod
    @transaction.atomic
    def cancel_review(
        cls,
        *,
        review_id,
        performed_by=None,
        reason="",
        metadata=None,
    ):
        """
        Cancel a review if allowed by domain rules.
        """

        review = get_review_by_id(review_id)

        cls._validate_cancellation(review)

        return ReviewsStatusService.change_status(
            review_id=review.id,
            new_status=Review.REVIEW_STATUS_CANCELLED,
            performed_by=performed_by,
            moderation_reason=reason,
            metadata=metadata,
        )