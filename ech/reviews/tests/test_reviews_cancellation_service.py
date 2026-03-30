import uuid
from decimal import Decimal

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
from ech.reviews.services.reviews_cancellation_service import (
    ReviewsCancellationService,
)
from ech.reviews.exceptions import ReviewCancellationNotAllowedException


User = get_user_model()


class BaseReviewCancellationFactoryMixin:
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


class ReviewsCancellationServiceTestCase(
    BaseReviewCancellationFactoryMixin,
    TestCase,
):
    def test_cancel_review_success(self):
        """Cancel review successfully when allowed."""
        review = self.create_review()
        staff = self.create_user(
            role=User.ROLE_SUPPORT_STAFF,
            email="support@company.com",
        )

        updated = ReviewsCancellationService.cancel_review(
            review_id=review.id,
            performed_by=staff,
            reason="Customer requested removal.",
        )

        self.assertEqual(updated.status, Review.REVIEW_STATUS_CANCELLED)

    def test_cancel_review_updates_lifecycle(self):
        """Update lifecycle cancelled_at timestamp on cancellation."""
        review = self.create_review()

        ReviewsCancellationService.cancel_review(
            review_id=review.id,
        )

        lifecycle = ReviewLifecycle.objects.get(review=review)

        self.assertIsNotNone(lifecycle.cancelled_at)

    def test_cancel_review_creates_cancelled_event(self):
        """Create cancelled review event after cancellation."""
        review = self.create_review()
        staff = self.create_user(
            role=User.ROLE_SUPPORT_STAFF,
            email="support@company.com",
        )

        ReviewsCancellationService.cancel_review(
            review_id=review.id,
            performed_by=staff,
            reason="Invalid review content.",
        )

        event = ReviewEvent.objects.get(review=review)

        self.assertEqual(event.event_type, ReviewEvent.TYPE_CANCELLED)
        self.assertEqual(event.performed_by, staff)
        self.assertEqual(
            event.metadata["new_status"],
            Review.REVIEW_STATUS_CANCELLED,
        )

    def test_cancel_review_already_cancelled_raises_exception(self):
        """Reject cancellation for already cancelled review."""
        review = self.create_review(
            status=Review.REVIEW_STATUS_CANCELLED,
        )

        with self.assertRaises(ReviewCancellationNotAllowedException):
            ReviewsCancellationService.cancel_review(
                review_id=review.id,
            )

    def test_cancel_review_from_approved_status(self):
        """Allow cancellation from approved status."""
        review = self.create_review(
            status=Review.REVIEW_STATUS_APPROVED,
        )

        updated = ReviewsCancellationService.cancel_review(
            review_id=review.id,
        )

        self.assertEqual(updated.status, Review.REVIEW_STATUS_CANCELLED)

    def test_cancel_review_from_hidden_status(self):
        """Allow cancellation from hidden status."""
        review = self.create_review(
            status=Review.REVIEW_STATUS_HIDDEN,
        )

        updated = ReviewsCancellationService.cancel_review(
            review_id=review.id,
        )

        self.assertEqual(updated.status, Review.REVIEW_STATUS_CANCELLED)