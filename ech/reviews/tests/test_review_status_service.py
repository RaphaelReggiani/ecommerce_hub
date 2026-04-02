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
from ech.reviews.services.review_status_service import ReviewsStatusService
from ech.reviews.exceptions import InvalidReviewStatusTransitionException


User = get_user_model()


class BaseReviewStatusFactoryMixin:
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
            "title": "Title",
            "comment": "Comment",
            "status": Review.REVIEW_STATUS_PENDING,
        }

        data.update(kwargs)

        review = Review.objects.create(**data)
        ReviewLifecycle.objects.create(review=review)

        return review


class ReviewsStatusServiceTestCase(BaseReviewStatusFactoryMixin, TestCase):

    def test_change_status_pending_to_approved(self):
        """Allow valid status transition."""
        review = self.create_review()

        staff = self.create_user(
            role=User.ROLE_SUPPORT_STAFF,
            email="support@company.com",
        )

        updated = ReviewsStatusService.change_status(
            review_id=review.id,
            new_status=Review.REVIEW_STATUS_APPROVED,
            performed_by=staff,
        )

        self.assertEqual(updated.status, Review.REVIEW_STATUS_APPROVED)

        lifecycle = ReviewLifecycle.objects.get(review=review)
        self.assertIsNotNone(lifecycle.approved_at)

    def test_change_status_creates_event(self):
        """Create ReviewEvent for status transition."""
        review = self.create_review()

        staff = self.create_user(
            role=User.ROLE_SUPPORT_STAFF,
            email="support@company.com",
        )

        ReviewsStatusService.change_status(
            review_id=review.id,
            new_status=Review.REVIEW_STATUS_APPROVED,
            performed_by=staff,
        )

        event = ReviewEvent.objects.get(review=review)

        self.assertEqual(event.event_type, ReviewEvent.TYPE_APPROVED)
        self.assertEqual(event.performed_by, staff)

    @patch(
        "ech.reviews.services.review_status_service.ReviewsLogService.log_review_status_changed"
    )
    def test_change_status_calls_logging(self, log_mock):
        """Call structured logging after status change."""
        review = self.create_review()

        staff = self.create_user(
            role=User.ROLE_SUPPORT_STAFF,
            email="support@company.com",
        )

        ReviewsStatusService.change_status(
            review_id=review.id,
            new_status=Review.REVIEW_STATUS_APPROVED,
            performed_by=staff,
        )

        log_mock.assert_called_once()

    def test_invalid_status_transition_raises_exception(self):
        """Reject invalid status transitions."""
        review = self.create_review(
            status=Review.REVIEW_STATUS_CANCELLED
        )

        with self.assertRaises(InvalidReviewStatusTransitionException):
            ReviewsStatusService.change_status(
                review_id=review.id,
                new_status=Review.REVIEW_STATUS_APPROVED,
            )

    def test_change_status_to_hidden_updates_lifecycle(self):
        """Update lifecycle hidden_at timestamp."""
        review = self.create_review(
            status=Review.REVIEW_STATUS_APPROVED
        )

        staff = self.create_user(
            role=User.ROLE_SUPPORT_STAFF,
            email="support@company.com",
        )

        ReviewsStatusService.change_status(
            review_id=review.id,
            new_status=Review.REVIEW_STATUS_HIDDEN,
            performed_by=staff,
        )

        lifecycle = ReviewLifecycle.objects.get(review=review)

        self.assertIsNotNone(lifecycle.hidden_at)

    def test_change_status_sets_moderation_fields(self):
        """Populate moderation fields when moderation occurs."""
        review = self.create_review()

        staff = self.create_user(
            role=User.ROLE_SUPPORT_STAFF,
            email="support@company.com",
        )

        updated = ReviewsStatusService.change_status(
            review_id=review.id,
            new_status=Review.REVIEW_STATUS_APPROVED,
            performed_by=staff,
            moderation_reason="Approved after review",
        )

        self.assertEqual(updated.moderated_by, staff)
        self.assertIsNotNone(updated.moderated_at)
        self.assertEqual(updated.moderation_reason, "Approved after review")

    def test_change_status_same_status_returns_review(self):
        """Return review if status does not change."""
        review = self.create_review()

        result = ReviewsStatusService.change_status(
            review_id=review.id,
            new_status=Review.REVIEW_STATUS_PENDING,
        )

        self.assertEqual(result.id, review.id)
        self.assertEqual(ReviewEvent.objects.count(), 0)