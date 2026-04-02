import uuid
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.products.models import (
    Product,
)
from ech.reviews.models import (
    Review, 
    ReviewLifecycle,
)
from ech.reviews.services.review_log_service import ReviewsLogService


User = get_user_model()


class BaseReviewLoggingFactoryMixin:
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


class ReviewsLogServiceTestCase(
    BaseReviewLoggingFactoryMixin,
    TestCase,
):
    def test_serialize_value_uuid(self):
        """Serialize UUID values as strings."""
        value = uuid.uuid4()

        result = ReviewsLogService._serialize_value(value)

        self.assertEqual(result, str(value))

    def test_serialize_value_datetime(self):
        """Serialize datetime values as ISO strings."""
        value = timezone.now()

        result = ReviewsLogService._serialize_value(value)

        self.assertEqual(result, value.isoformat())

    def test_serialize_value_returns_plain_value(self):
        """Return non-special values unchanged."""
        self.assertEqual(ReviewsLogService._serialize_value("abc"), "abc")
        self.assertEqual(ReviewsLogService._serialize_value(123), 123)
        self.assertEqual(ReviewsLogService._serialize_value(True), True)

    def test_serialize_metadata_returns_empty_dict_for_none(self):
        """Return empty dict when metadata is None."""
        result = ReviewsLogService._serialize_metadata(None)

        self.assertEqual(result, {})

    def test_serialize_metadata_serializes_uuid_and_datetime(self):
        """Serialize metadata values safely."""
        review_id = uuid.uuid4()
        timestamp = timezone.now()

        result = ReviewsLogService._serialize_metadata(
            {
                "review_id": review_id,
                "timestamp": timestamp,
                "message": "ok",
            }
        )

        self.assertEqual(result["review_id"], str(review_id))
        self.assertEqual(result["timestamp"], timestamp.isoformat())
        self.assertEqual(result["message"], "ok")

    def test_build_payload_with_review_and_performed_by(self):
        """Build structured payload with review and user context."""
        review = self.create_review()
        staff = self.create_user(
            role=User.ROLE_SUPPORT_STAFF,
            email="support@company.com",
        )

        payload = ReviewsLogService._build_payload(
            action="review_created",
            review=review,
            performed_by=staff,
            metadata={"source": "unit-test"},
        )

        self.assertEqual(payload["action"], "review_created")
        self.assertEqual(payload["review_id"], str(review.id))
        self.assertEqual(payload["product_id"], str(review.product_id))
        self.assertEqual(payload["customer_id"], review.customer_id)
        self.assertEqual(payload["performed_by_id"], staff.id)
        self.assertEqual(payload["status"], review.status)
        self.assertEqual(payload["metadata"], {"source": "unit-test"})

    def test_build_payload_without_review(self):
        """Build structured payload safely without review instance."""
        staff = self.create_user(
            role=User.ROLE_SUPPORT_STAFF,
            email="support@company.com",
        )

        payload = ReviewsLogService._build_payload(
            action="review_created",
            review=None,
            performed_by=staff,
            metadata={"source": "unit-test"},
        )

        self.assertEqual(payload["action"], "review_created")
        self.assertIsNone(payload["review_id"])
        self.assertIsNone(payload["product_id"])
        self.assertIsNone(payload["customer_id"])
        self.assertEqual(payload["performed_by_id"], staff.id)
        self.assertIsNone(payload["status"])
        self.assertEqual(payload["metadata"], {"source": "unit-test"})

    @patch("ech.reviews.services.review_log_service.logger.info")
    def test_log_review_created_calls_logger(self, logger_mock):
        """Log review creation with structured payload."""
        review = self.create_review()

        ReviewsLogService.log_review_created(
            review=review,
            performed_by=review.customer,
            metadata={"rating": 5},
        )

        logger_mock.assert_called_once()
        call_args = logger_mock.call_args

        self.assertEqual(call_args[0][0], "review_created")
        self.assertEqual(
            call_args[1]["extra"]["payload"]["action"],
            "review_created",
        )

    @patch("ech.reviews.services.review_log_service.logger.info")
    def test_log_review_updated_calls_logger(self, logger_mock):
        """Log review update with structured payload."""
        review = self.create_review()

        ReviewsLogService.log_review_updated(
            review=review,
            performed_by=review.customer,
            metadata={"updated_fields": ["title"]},
        )

        logger_mock.assert_called_once()
        call_args = logger_mock.call_args

        self.assertEqual(call_args[0][0], "review_updated")
        self.assertEqual(
            call_args[1]["extra"]["payload"]["action"],
            "review_updated",
        )

    @patch("ech.reviews.services.review_log_service.logger.info")
    def test_log_review_status_changed_calls_logger(self, logger_mock):
        """Log review status changes with structured payload."""
        review = self.create_review(
            status=Review.REVIEW_STATUS_APPROVED,
        )

        ReviewsLogService.log_review_status_changed(
            review=review,
            performed_by=review.customer,
            metadata={"new_status": Review.REVIEW_STATUS_APPROVED},
        )

        logger_mock.assert_called_once()
        call_args = logger_mock.call_args

        self.assertEqual(call_args[0][0], "review_status_changed")
        self.assertEqual(
            call_args[1]["extra"]["payload"]["action"],
            "review_status_changed",
        )

    @patch("ech.reviews.services.review_log_service.logger.info")
    def test_log_review_cancelled_calls_logger(self, logger_mock):
        """Log review cancellation with structured payload."""
        review = self.create_review(
            status=Review.REVIEW_STATUS_CANCELLED,
        )

        ReviewsLogService.log_review_cancelled(
            review=review,
            performed_by=review.customer,
            metadata={"reason": "Customer request"},
        )

        logger_mock.assert_called_once()
        call_args = logger_mock.call_args

        self.assertEqual(call_args[0][0], "review_cancelled")
        self.assertEqual(
            call_args[1]["extra"]["payload"]["action"],
            "review_cancelled",
        )

    @patch("ech.reviews.services.review_log_service.logger.info")
    def test_log_review_moderated_calls_logger(self, logger_mock):
        """Log review moderation with structured payload."""
        review = self.create_review(
            status=Review.REVIEW_STATUS_APPROVED,
        )
        staff = self.create_user(
            role=User.ROLE_SUPPORT_STAFF,
            email="support@company.com",
        )

        ReviewsLogService.log_review_moderated(
            review=review,
            performed_by=staff,
            metadata={"moderation_action": "approve"},
        )

        logger_mock.assert_called_once()
        call_args = logger_mock.call_args

        self.assertEqual(call_args[0][0], "review_moderated")
        self.assertEqual(
            call_args[1]["extra"]["payload"]["action"],
            "review_moderated",
        )