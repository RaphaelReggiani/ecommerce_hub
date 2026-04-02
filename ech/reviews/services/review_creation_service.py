from django.db import transaction

from ech.reviews.models import (
    Review,
    ReviewLifecycle,
    ReviewEvent,
)
from ech.reviews.exceptions import (
    DuplicateReviewException,
    InvalidReviewRatingException,
)
from ech.reviews.selectors import (
    get_review_by_customer_and_product,
    get_review_by_idempotency_key,
)
from ech.reviews.services.review_log_service import ReviewsLogService
from ech.reviews.services.cache_service import ReviewsCacheService
from ech.reviews.domain_events.dispatcher import ReviewEventDispatcher
from ech.reviews.domain_events.events import ReviewCreatedEvent


class ReviewsCreationService:
    """
    Service responsible for creating reviews.

    Guarantees:
    - idempotency protection
    - domain validation
    - lifecycle initialization
    - event recording
    - structured logging
    - cache invalidation for affected read models
    """

    @staticmethod
    def _validate_rating(rating):
        if rating < 1 or rating > 5:
            raise InvalidReviewRatingException()

    @staticmethod
    def _validate_review_uniqueness(customer, product):
        existing_review = get_review_by_customer_and_product(customer, product)

        if existing_review:
            raise DuplicateReviewException()

    @staticmethod
    def _check_idempotency(idempotency_key):
        """
        Return an existing review if the idempotency key
        was already used.
        """
        return get_review_by_idempotency_key(idempotency_key)

    @staticmethod
    @transaction.atomic
    def create_review(
        *,
        customer,
        product,
        rating,
        title="",
        comment="",
        idempotency_key=None,
        is_verified_purchase=False,
    ):
        """
        Create a new review.

        Idempotency-safe.
        """

        existing_review = ReviewsCreationService._check_idempotency(
            idempotency_key
        )

        if existing_review:
            return existing_review

        ReviewsCreationService._validate_rating(rating)

        ReviewsCreationService._validate_review_uniqueness(
            customer,
            product,
        )

        review = Review.objects.create(
            customer=customer,
            product=product,
            rating=rating,
            title=title,
            comment=comment,
            idempotency_key=idempotency_key,
            is_verified_purchase=is_verified_purchase,
            status=Review.REVIEW_STATUS_PENDING,
        )

        ReviewLifecycle.objects.create(
            review=review,
        )

        ReviewEvent.objects.create(
            review=review,
            event_type=ReviewEvent.TYPE_CREATED,
            performed_by=customer,
            metadata={
                "rating": rating,
                "verified_purchase": is_verified_purchase,
            },
        )

        ReviewsLogService.log_review_created(
            review=review,
            performed_by=customer,
            metadata={
                "rating": rating,
                "product_id": product.id,
            },
        )

        ReviewEventDispatcher.dispatch(
            ReviewCreatedEvent(
                review_id=review.id,
                metadata={
                    "customer_id": customer.id,
                    "product_id": product.id,
                    "rating": rating,
                    "verified_purchase": is_verified_purchase,
                },
            )
        )

        ReviewsCacheService.invalidate_customer_review_lists(
            customer_id=customer.id,
        )
        ReviewsCacheService.invalidate_management_review_lists()
        ReviewsCacheService.invalidate_public_product_review_lists(
            product_id=product.id,
        )
        ReviewsCacheService.invalidate_product_review_summary(
            product_id=product.id,
        )

        return review