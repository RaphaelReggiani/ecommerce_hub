import uuid
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from ech.products.models import (
    Product,
)
from ech.reviews.exceptions import (
    DuplicateReviewException,
    InvalidReviewRatingException,
)
from ech.reviews.models import (
    Review, 
    ReviewLifecycle, 
    ReviewEvent,
)
from ech.reviews.services.review_creation_service import ReviewsCreationService


User = get_user_model()


class BaseReviewCreateServiceFactoryMixin:
    def create_user(self, **kwargs):
        suffix = uuid.uuid4().hex[:8]
        role = kwargs.get("role", User.ROLE_CUSTOMER_USER)

        corporate_roles = {
            User.ROLE_SUPERADMIN,
            User.ROLE_ADMIN,
            User.ROLE_SUPPORT_STAFF,
            User.ROLE_OPERATIONS_STAFF,
        }

        domain = "company.com" if role in corporate_roles else "test.com"

        data = {
            "email": f"user_{suffix}@{domain}",
            "password": "StrongPassword123",
            "user_name": f"User {suffix}",
            "role": User.ROLE_CUSTOMER_USER,
            "is_active": True,
            "email_confirmed": True,
        }
        data.update(kwargs)
        return User.objects.create_user(**data)

    def create_product(self, **kwargs):
        suffix = uuid.uuid4().hex[:8]

        operator = kwargs.pop(
            "sold_by",
            None,
        ) or self.create_user(
            email=f"operator_{suffix}@company.com",
            user_name=f"Operator {suffix}",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        data = {
            "name": f"Product {suffix}",
            "product_type": Product.PHONE,
            "brand": "Test Brand",
            "sold_by": operator,
            "description": "Product description",
            "technical_information": "Technical information",
            "price": Decimal("19.90"),
            "discount_price": None,
            "is_active": True,
        }
        data.update(kwargs)

        return Product.objects.create(**data)


class ReviewsCreationServiceTestCase(
    BaseReviewCreateServiceFactoryMixin,
    TestCase,
):
    def test_create_review_success(self):
        """Create a review successfully with lifecycle and event."""
        customer = self.create_user()
        product = self.create_product()
        idempotency_key = uuid.uuid4()

        review = ReviewsCreationService.create_review(
            customer=customer,
            product=product,
            rating=5,
            title="Excellent",
            comment="Very good product.",
            idempotency_key=idempotency_key,
            is_verified_purchase=True,
        )

        self.assertIsInstance(review, Review)
        self.assertEqual(review.customer, customer)
        self.assertEqual(review.product, product)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.title, "Excellent")
        self.assertEqual(review.comment, "Very good product.")
        self.assertEqual(review.idempotency_key, idempotency_key)
        self.assertTrue(review.is_verified_purchase)
        self.assertEqual(review.status, Review.REVIEW_STATUS_PENDING)

        self.assertTrue(
            ReviewLifecycle.objects.filter(review=review).exists()
        )

        event = ReviewEvent.objects.get(review=review)
        self.assertEqual(event.event_type, ReviewEvent.TYPE_CREATED)
        self.assertEqual(event.performed_by, customer)
        self.assertEqual(
            event.metadata,
            {
                "rating": 5,
                "verified_purchase": True,
            },
        )

    def test_create_review_applies_default_optional_values(self):
        """Apply default values for optional fields when omitted."""
        customer = self.create_user()
        product = self.create_product()

        review = ReviewsCreationService.create_review(
            customer=customer,
            product=product,
            rating=4,
        )

        self.assertEqual(review.title, "")
        self.assertEqual(review.comment, "")
        self.assertIsNone(review.idempotency_key)
        self.assertFalse(review.is_verified_purchase)
        self.assertEqual(review.status, Review.REVIEW_STATUS_PENDING)

    def test_create_review_invalid_rating_below_min_raises_exception(self):
        """Reject rating below the allowed minimum."""
        customer = self.create_user()
        product = self.create_product()

        with self.assertRaises(InvalidReviewRatingException):
            ReviewsCreationService.create_review(
                customer=customer,
                product=product,
                rating=0,
            )

        self.assertEqual(Review.objects.count(), 0)

    def test_create_review_invalid_rating_above_max_raises_exception(self):
        """Reject rating above the allowed maximum."""
        customer = self.create_user()
        product = self.create_product()

        with self.assertRaises(InvalidReviewRatingException):
            ReviewsCreationService.create_review(
                customer=customer,
                product=product,
                rating=6,
            )

        self.assertEqual(Review.objects.count(), 0)

    def test_create_review_duplicate_customer_product_raises_exception(self):
        """Prevent duplicate review creation for same customer and product."""
        customer = self.create_user()
        product = self.create_product()

        ReviewsCreationService.create_review(
            customer=customer,
            product=product,
            rating=5,
        )

        with self.assertRaises(DuplicateReviewException):
            ReviewsCreationService.create_review(
                customer=customer,
                product=product,
                rating=4,
            )

        self.assertEqual(Review.objects.count(), 1)

    def test_create_review_returns_existing_review_for_same_idempotency_key(self):
        """Return existing review when idempotency key was already used."""
        customer = self.create_user()
        product = self.create_product()
        idempotency_key = uuid.uuid4()

        first_review = ReviewsCreationService.create_review(
            customer=customer,
            product=product,
            rating=5,
            title="First title",
            comment="First comment",
            idempotency_key=idempotency_key,
        )

        second_review = ReviewsCreationService.create_review(
            customer=customer,
            product=product,
            rating=1,
            title="Second title",
            comment="Second comment",
            idempotency_key=idempotency_key,
        )

        self.assertEqual(first_review.id, second_review.id)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(ReviewLifecycle.objects.count(), 1)
        self.assertEqual(ReviewEvent.objects.count(), 1)

    @patch(
        "ech.reviews.services.review_creation_service.ReviewsLogService.log_review_created"
    )
    def test_create_review_calls_logging_service(self, log_review_created_mock):
        """Call structured logging after successful review creation."""
        customer = self.create_user()
        product = self.create_product()

        review = ReviewsCreationService.create_review(
            customer=customer,
            product=product,
            rating=5,
            idempotency_key=uuid.uuid4(),
        )

        log_review_created_mock.assert_called_once_with(
            review=review,
            performed_by=customer,
            metadata={
                "rating": 5,
                "product_id": product.id,
            },
        )

    @patch(
        "ech.reviews.services.review_creation_service.ReviewsLogService.log_review_created"
    )
    def test_create_review_does_not_log_when_idempotent_replay_returns_existing_review(
        self,
        log_review_created_mock,
    ):
        """Do not log a second time when idempotency returns existing review."""
        customer = self.create_user()
        product = self.create_product()
        idempotency_key = uuid.uuid4()

        ReviewsCreationService.create_review(
            customer=customer,
            product=product,
            rating=5,
            idempotency_key=idempotency_key,
        )

        self.assertEqual(log_review_created_mock.call_count, 1)

        ReviewsCreationService.create_review(
            customer=customer,
            product=product,
            rating=3,
            idempotency_key=idempotency_key,
        )

        self.assertEqual(log_review_created_mock.call_count, 1)

    def test_create_review_creates_single_lifecycle_record(self):
        """Create exactly one lifecycle record for a new review."""
        customer = self.create_user()
        product = self.create_product()

        review = ReviewsCreationService.create_review(
            customer=customer,
            product=product,
            rating=5,
        )

        self.assertEqual(
            ReviewLifecycle.objects.filter(review=review).count(),
            1,
        )

    def test_create_review_creates_single_created_event(self):
        """Create exactly one created event for a new review."""
        customer = self.create_user()
        product = self.create_product()

        review = ReviewsCreationService.create_review(
            customer=customer,
            product=product,
            rating=5,
        )

        events = ReviewEvent.objects.filter(review=review)

        self.assertEqual(events.count(), 1)
        self.assertEqual(events.first().event_type, ReviewEvent.TYPE_CREATED)