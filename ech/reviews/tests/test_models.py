import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import (
    IntegrityError, 
    transaction,
)
from django.test import TestCase

from ech.products.models import (
    Product,
)
from ech.reviews.models import (
    Review,
    ReviewLifecycle,
    ReviewEvent,
)


User = get_user_model()


class BaseReviewModelFactoryMixin:
    def create_user(self, **kwargs):
        unique_suffix = uuid.uuid4().hex[:8]
        role = kwargs.get("role", User.ROLE_CUSTOMER_USER)

        corporate_roles = {
            User.ROLE_SUPERADMIN,
            User.ROLE_ADMIN,
            User.ROLE_SUPPORT_STAFF,
            User.ROLE_OPERATIONS_STAFF,
        }

        domain = "company.com" if role in corporate_roles else "test.com"

        data = {
            "email": f"user_{unique_suffix}@{domain}",
            "password": "StrongPassword123",
            "user_name": f"Test User {unique_suffix}",
            "role": User.ROLE_CUSTOMER_USER,
            "is_active": True,
            "email_confirmed": True,
        }
        data.update(kwargs)
        return User.objects.create_user(**data)

    def create_product(self, **kwargs):
        unique_suffix = uuid.uuid4().hex[:8]

        seller = kwargs.pop(
            "sold_by",
            None,
        ) or self.create_user(
            email=f"seller_{unique_suffix}@company.com",
            user_name=f"Seller User {unique_suffix}",
            role=User.ROLE_ADMIN,
        )

        data = {
            "name": f"Product {unique_suffix}",
            "product_type": Product.PHONE,
            "brand": "Test Brand",
            "sold_by": seller,
            "description": "Test product description",
            "technical_information": "Test technical information",
            "price": Decimal("19.90"),
            "discount_price": None,
            "is_active": True,
        }
        data.update(kwargs)

        return Product.objects.create(**data)

    def create_review(self, **kwargs):
        customer = kwargs.pop("customer", None) or self.create_user()
        product = kwargs.pop("product", None) or self.create_product()

        data = {
            "customer": customer,
            "product": product,
            "rating": 5,
            "title": "Excellent product",
            "comment": "Very good quality.",
            "status": Review.REVIEW_STATUS_PENDING,
            "is_verified_purchase": False,
        }
        data.update(kwargs)

        return Review.objects.create(**data)


class ReviewModelTestCase(BaseReviewModelFactoryMixin, TestCase):
    def test_review_creation_success(self):
        """Create a review successfully."""
        review = self.create_review()

        self.assertIsInstance(review.id, uuid.UUID)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.status, Review.REVIEW_STATUS_PENDING)
        self.assertFalse(review.is_verified_purchase)
        self.assertIsNotNone(review.created_at)
        self.assertIsNotNone(review.updated_at)

    def test_review_string_representation(self):
        """Return the review identifier in string representation."""
        review = self.create_review()

        self.assertEqual(
            str(review),
            f"Review {review.id} - {review.product_id}",
        )

    def test_review_related_names_work_correctly(self):
        """Expose reviews through product and customer related names."""
        review = self.create_review()

        self.assertIn(review, review.customer.reviews.all())
        self.assertIn(review, review.product.reviews.all())

    def test_review_unique_customer_product_constraint(self):
        """Prevent duplicate reviews for the same customer and product."""
        customer = self.create_user()
        product = self.create_product()

        self.create_review(customer=customer, product=product)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_review(customer=customer, product=product)

    def test_review_idempotency_key_must_be_unique(self):
        """Prevent duplicate idempotency keys."""
        idempotency_key = uuid.uuid4()

        self.create_review(idempotency_key=idempotency_key)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_review(
                    product=self.create_product(),
                    idempotency_key=idempotency_key,
                )

    def test_review_meta_ordering_is_configured(self):
        """Configure review default ordering."""
        self.assertEqual(Review._meta.ordering, ["-created_at"])

    def test_review_meta_indexes_are_configured(self):
        """Configure review indexes correctly."""
        index_names = {index.name for index in Review._meta.indexes}

        self.assertIn("rev_prod_stat_created_idx", index_names)
        self.assertIn("review_customer_created_idx", index_names)
        self.assertIn("review_product_rating_idx", index_names)

    def test_review_status_choices_include_expected_values(self):
        """Expose all supported review statuses."""
        choices = dict(Review.REVIEW_STATUS_CHOICES)

        self.assertIn(Review.REVIEW_STATUS_PENDING, choices)
        self.assertIn(Review.REVIEW_STATUS_APPROVED, choices)
        self.assertIn(Review.REVIEW_STATUS_REJECTED, choices)
        self.assertIn(Review.REVIEW_STATUS_HIDDEN, choices)
        self.assertIn(Review.REVIEW_STATUS_CANCELLED, choices)


class ReviewLifecycleModelTestCase(BaseReviewModelFactoryMixin, TestCase):
    def test_review_lifecycle_creation_success(self):
        """Create lifecycle record successfully."""
        review = self.create_review()

        lifecycle = ReviewLifecycle.objects.create(review=review)

        self.assertEqual(lifecycle.review, review)
        self.assertIsNone(lifecycle.approved_at)
        self.assertIsNone(lifecycle.rejected_at)
        self.assertIsNone(lifecycle.hidden_at)
        self.assertIsNone(lifecycle.cancelled_at)
        self.assertIsNotNone(lifecycle.created_at)
        self.assertIsNotNone(lifecycle.updated_at)

    def test_review_lifecycle_string_representation(self):
        """Return review identifier in lifecycle string representation."""
        review = self.create_review()
        lifecycle = ReviewLifecycle.objects.create(review=review)

        self.assertEqual(
            str(lifecycle),
            f"Lifecycle for Review {review.id}",
        )

    def test_review_lifecycle_related_name_works_correctly(self):
        """Expose lifecycle through review related name."""
        review = self.create_review()
        lifecycle = ReviewLifecycle.objects.create(review=review)

        self.assertEqual(review.lifecycle, lifecycle)


class ReviewEventModelTestCase(BaseReviewModelFactoryMixin, TestCase):
    def test_review_event_creation_success(self):
        """Create review audit event successfully."""
        review = self.create_review()

        operator = self.create_user(
            email="support@company.com",
            role=User.ROLE_SUPPORT_STAFF,
        )

        event = ReviewEvent.objects.create(
            review=review,
            event_type=ReviewEvent.TYPE_CREATED,
            performed_by=operator,
            metadata={"source": "unit-test"},
        )

        self.assertEqual(event.review, review)
        self.assertEqual(event.event_type, ReviewEvent.TYPE_CREATED)
        self.assertEqual(event.performed_by, operator)
        self.assertEqual(event.metadata, {"source": "unit-test"})
        self.assertIsNotNone(event.created_at)

    def test_review_event_string_representation(self):
        """Return event type and review identifier."""
        review = self.create_review()

        event = ReviewEvent.objects.create(
            review=review,
            event_type=ReviewEvent.TYPE_CREATED,
        )

        self.assertEqual(
            str(event),
            f"{ReviewEvent.TYPE_CREATED} - {review.id}",
        )

    def test_review_event_ordering_by_created_at_desc(self):
        """Order review events by newest created_at first."""
        review = self.create_review()

        first = ReviewEvent.objects.create(
            review=review,
            event_type=ReviewEvent.TYPE_CREATED,
        )
        second = ReviewEvent.objects.create(
            review=review,
            event_type=ReviewEvent.TYPE_UPDATED,
        )

        events = list(ReviewEvent.objects.all())

        self.assertEqual(events[0], second)
        self.assertEqual(events[1], first)

    def test_review_event_meta_configuration(self):
        """Configure review event ordering and indexes."""
        self.assertEqual(ReviewEvent._meta.ordering, ["-created_at"])

        index_names = {index.name for index in ReviewEvent._meta.indexes}
        self.assertIn("reviewevent_review_created_idx", index_names)