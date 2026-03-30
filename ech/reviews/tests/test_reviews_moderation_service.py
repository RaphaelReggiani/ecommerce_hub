import uuid
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from ech.products.models import (
    Product,
)
from ech.reviews.constants.constants import (
    REVIEW_ACTION_APPROVE,
    REVIEW_ACTION_REJECT,
    REVIEW_ACTION_HIDE,
    REVIEW_ACTION_RESTORE,
)
from ech.reviews.exceptions import (
    InvalidReviewModerationActionException,
    ReviewModerationNotAllowedException,
)
from ech.reviews.models import (
    Review,
    ReviewLifecycle,
    ReviewEvent
)
from ech.reviews.services.reviews_moderation_service import (
    ReviewsModerationService,
)


User = get_user_model()


class BaseReviewModerationFactoryMixin:
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
            "title": "Review title",
            "comment": "Review comment",
            "status": Review.REVIEW_STATUS_PENDING,
        }
        data.update(kwargs)

        review = Review.objects.create(**data)
        ReviewLifecycle.objects.create(review=review)

        return review


class ReviewsModerationServiceTestCase(
    BaseReviewModerationFactoryMixin,
    TestCase,
):
    def test_moderate_review_approve_success(self):
        """Approve a pending review successfully."""
        review = self.create_review()

        staff = self.create_user(
            role=User.ROLE_SUPPORT_STAFF,
            email="support@company.com",
        )

        updated = ReviewsModerationService.moderate_review(
            review_id=review.id,
            action=REVIEW_ACTION_APPROVE,
            performed_by=staff,
            reason="Content validated",
        )

        self.assertEqual(updated.status, Review.REVIEW_STATUS_APPROVED)
        self.assertEqual(updated.moderated_by, staff)

        lifecycle = ReviewLifecycle.objects.get(review=review)
        self.assertIsNotNone(lifecycle.approved_at)

    def test_moderate_review_reject_success(self):
        """Reject a pending review successfully."""
        review = self.create_review()

        staff = self.create_user(
            role=User.ROLE_SUPPORT_STAFF,
            email="support@company.com",
        )

        updated = ReviewsModerationService.moderate_review(
            review_id=review.id,
            action=REVIEW_ACTION_REJECT,
            performed_by=staff,
            reason="Spam content",
        )

        self.assertEqual(updated.status, Review.REVIEW_STATUS_REJECTED)

        lifecycle = ReviewLifecycle.objects.get(review=review)
        self.assertIsNotNone(lifecycle.rejected_at)

    def test_moderate_review_hide_success(self):
        """Hide an approved review successfully."""
        review = self.create_review(
            status=Review.REVIEW_STATUS_APPROVED,
        )

        staff = self.create_user(
            role=User.ROLE_SUPPORT_STAFF,
            email="support@company.com",
        )

        updated = ReviewsModerationService.moderate_review(
            review_id=review.id,
            action=REVIEW_ACTION_HIDE,
            performed_by=staff,
            reason="Policy violation",
        )

        self.assertEqual(updated.status, Review.REVIEW_STATUS_HIDDEN)

        lifecycle = ReviewLifecycle.objects.get(review=review)
        self.assertIsNotNone(lifecycle.hidden_at)

    def test_moderate_review_restore_success(self):
        """Restore a hidden review successfully."""
        review = self.create_review(
            status=Review.REVIEW_STATUS_HIDDEN,
        )

        staff = self.create_user(
            role=User.ROLE_SUPPORT_STAFF,
            email="support@company.com",
        )

        updated = ReviewsModerationService.moderate_review(
            review_id=review.id,
            action=REVIEW_ACTION_RESTORE,
            performed_by=staff,
            reason="Restored after manual review",
        )

        self.assertEqual(updated.status, Review.REVIEW_STATUS_APPROVED)

    def test_moderate_review_creates_event(self):
        """Create moderation event through status service."""
        review = self.create_review()

        staff = self.create_user(
            role=User.ROLE_SUPPORT_STAFF,
            email="support@company.com",
        )

        ReviewsModerationService.moderate_review(
            review_id=review.id,
            action=REVIEW_ACTION_APPROVE,
            performed_by=staff,
            reason="Approved by moderation team",
        )

        event = ReviewEvent.objects.get(review=review)

        self.assertEqual(event.event_type, ReviewEvent.TYPE_APPROVED)
        self.assertEqual(event.performed_by, staff)
        self.assertEqual(
            event.metadata["moderation_action"],
            REVIEW_ACTION_APPROVE,
        )

    @patch(
        "ech.reviews.services.reviews_status_service.ReviewsLogService.log_review_status_changed"
    )
    def test_moderate_review_calls_logging(self, log_mock):
        """Call logging through status service."""
        review = self.create_review()

        staff = self.create_user(
            role=User.ROLE_SUPPORT_STAFF,
            email="support@company.com",
        )

        ReviewsModerationService.moderate_review(
            review_id=review.id,
            action=REVIEW_ACTION_APPROVE,
            performed_by=staff,
            reason="Approved after review",
        )

        log_mock.assert_called_once()

    def test_moderate_review_invalid_action_raises_exception(self):
        """Reject unsupported moderation actions."""
        review = self.create_review()

        with self.assertRaises(InvalidReviewModerationActionException):
            ReviewsModerationService.moderate_review(
                review_id=review.id,
                action="invalid_action",
            )

    def test_moderate_review_restore_from_non_hidden_raises_exception(self):
        """Reject restore action when review is not hidden."""
        review = self.create_review(
            status=Review.REVIEW_STATUS_PENDING,
        )

        with self.assertRaises(ReviewModerationNotAllowedException):
            ReviewsModerationService.moderate_review(
                review_id=review.id,
                action=REVIEW_ACTION_RESTORE,
            )

    def test_moderate_review_hide_from_non_approved_raises_exception(self):
        """Reject hide action when review is not approved."""
        review = self.create_review(
            status=Review.REVIEW_STATUS_PENDING,
        )

        with self.assertRaises(ReviewModerationNotAllowedException):
            ReviewsModerationService.moderate_review(
                review_id=review.id,
                action=REVIEW_ACTION_HIDE,
            )

    def test_moderate_review_reject_from_non_pending_raises_exception(self):
        """Reject reject action when review is not pending."""
        review = self.create_review(
            status=Review.REVIEW_STATUS_APPROVED,
        )

        with self.assertRaises(ReviewModerationNotAllowedException):
            ReviewsModerationService.moderate_review(
                review_id=review.id,
                action=REVIEW_ACTION_REJECT,
            )