import uuid
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from ech.products.models import (
    Product,
)
from ech.reviews.models import (
    Review, 
    ReviewLifecycle, 
    ReviewEvent,
)
from ech.reviews.services.review_update_service import ReviewsUpdateService
from ech.reviews.exceptions import InvalidReviewRatingException


User = get_user_model()


class BaseReviewUpdateServiceFactoryMixin:
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

    def create_product(self):
        suffix = uuid.uuid4().hex[:8]

        operator = self.create_user(
            email=f"operator_{suffix}@company.com",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        return Product.objects.create(
            name=f"Product {suffix}",
            product_type=Product.PHONE,
            brand="Test Brand",
            sold_by=operator,
            description="Product description",
            technical_information="Technical info",
            price=Decimal("10.00"),
        )

    def create_review(self, **kwargs):
        customer = kwargs.pop("customer", None) or self.create_user()
        product = kwargs.pop("product", None) or self.create_product()

        data = {
            "customer": customer,
            "product": product,
            "rating": 5,
            "title": "Original title",
            "comment": "Original comment",
            "status": Review.REVIEW_STATUS_PENDING,
        }

        data.update(kwargs)

        review = Review.objects.create(**data)
        ReviewLifecycle.objects.create(review=review)

        return review


class ReviewsUpdateServiceTestCase(
    BaseReviewUpdateServiceFactoryMixin,
    TestCase,
):

    def test_update_review_success(self):
        """Update review fields successfully."""
        review = self.create_review()

        updated = ReviewsUpdateService.update_review(
            review_id=review.id,
            rating=4,
            title="Updated title",
            comment="Updated comment",
        )

        self.assertEqual(updated.rating, 4)
        self.assertEqual(updated.title, "Updated title")
        self.assertEqual(updated.comment, "Updated comment")

    @patch(
        "ech.reviews.services.review_update_service.ReviewsLogService.log_review_updated"
    )
    def test_update_review_creates_event_and_logs(self, log_mock):
        """Create ReviewEvent and call logging service."""
        review = self.create_review()

        ReviewsUpdateService.update_review(
            review_id=review.id,
            rating=4,
        )

        event = ReviewEvent.objects.get(review=review)

        self.assertEqual(event.event_type, ReviewEvent.TYPE_UPDATED)
        self.assertIn("updated_fields", event.metadata)

        log_mock.assert_called_once()

    def test_update_review_partial_update(self):
        """Allow partial updates."""
        review = self.create_review()

        updated = ReviewsUpdateService.update_review(
            review_id=review.id,
            title="New title",
        )

        self.assertEqual(updated.title, "New title")
        self.assertEqual(updated.rating, 5)
        self.assertEqual(updated.comment, "Original comment")

    def test_update_review_ignores_non_allowed_fields(self):
        """Ignore fields not allowed for update."""
        review = self.create_review()

        updated = ReviewsUpdateService.update_review(
            review_id=review.id,
            status=Review.REVIEW_STATUS_APPROVED,
        )

        self.assertEqual(updated.status, Review.REVIEW_STATUS_PENDING)

    def test_update_review_invalid_rating_raises_exception(self):
        """Reject rating outside allowed range."""
        review = self.create_review()

        with self.assertRaises(InvalidReviewRatingException):
            ReviewsUpdateService.update_review(
                review_id=review.id,
                rating=6,
            )

    def test_update_review_no_changes_returns_same_review(self):
        """Return review when no fields actually change."""
        review = self.create_review()

        result = ReviewsUpdateService.update_review(
            review_id=review.id,
            rating=5,
        )

        self.assertEqual(result.id, review.id)
        self.assertEqual(ReviewEvent.objects.count(), 0)

    def test_update_review_empty_payload_returns_review(self):
        """Return review when no valid fields are provided."""
        review = self.create_review()

        result = ReviewsUpdateService.update_review(
            review_id=review.id,
        )

        self.assertEqual(result.id, review.id)
        self.assertEqual(ReviewEvent.objects.count(), 0)

    def test_update_review_multiple_fields(self):
        """Update multiple fields simultaneously."""
        review = self.create_review()

        updated = ReviewsUpdateService.update_review(
            review_id=review.id,
            rating=3,
            title="Changed",
            comment="Changed comment",
        )

        self.assertEqual(updated.rating, 3)
        self.assertEqual(updated.title, "Changed")
        self.assertEqual(updated.comment, "Changed comment")