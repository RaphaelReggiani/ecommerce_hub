import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.products.models import (
    Product,
)
from ech.reviews.filters import (
    ReviewFilter,
)
from ech.reviews.models import (
    Review, 
    ReviewLifecycle,
)


User = get_user_model()


class BaseReviewFilterFactoryMixin:
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

    def create_review(self, **kwargs):
        customer = kwargs.pop("customer", None) or self.create_user()
        product = kwargs.pop("product", None) or self.create_product()
        moderated_by = kwargs.pop("moderated_by", None)

        data = {
            "customer": customer,
            "product": product,
            "rating": 5,
            "title": "Excellent",
            "comment": "Very good product.",
            "status": Review.REVIEW_STATUS_PENDING,
            "is_verified_purchase": False,
            "moderated_by": moderated_by,
        }
        data.update(kwargs)

        review = Review.objects.create(**data)
        ReviewLifecycle.objects.create(review=review)
        return review


class ReviewFilterTestCase(BaseReviewFilterFactoryMixin, TestCase):
    def test_filter_by_status(self):
        """Filter reviews by status."""
        approved_review = self.create_review(
            status=Review.REVIEW_STATUS_APPROVED,
            product=self.create_product(),
        )
        self.create_review(
            status=Review.REVIEW_STATUS_PENDING,
            product=self.create_product(),
        )

        queryset = Review.objects.all()
        filtered = ReviewFilter(
            data={"status": Review.REVIEW_STATUS_APPROVED},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), approved_review)

    def test_filter_by_rating(self):
        """Filter reviews by exact rating."""
        rating_five_review = self.create_review(
            rating=5,
            product=self.create_product(),
        )
        self.create_review(
            rating=4,
            product=self.create_product(),
        )

        queryset = Review.objects.all()
        filtered = ReviewFilter(
            data={"rating": 5},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), rating_five_review)

    def test_filter_by_rating_min(self):
        """Filter reviews by minimum rating."""
        review_high = self.create_review(
            rating=5,
            product=self.create_product(),
        )
        review_mid = self.create_review(
            rating=4,
            product=self.create_product(),
        )
        self.create_review(
            rating=2,
            product=self.create_product(),
        )

        queryset = Review.objects.all()
        filtered = ReviewFilter(
            data={"rating_min": 4},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 2)
        self.assertIn(review_high, filtered)
        self.assertIn(review_mid, filtered)

    def test_filter_by_rating_max(self):
        """Filter reviews by maximum rating."""
        review_low = self.create_review(
            rating=1,
            product=self.create_product(),
        )
        review_mid = self.create_review(
            rating=3,
            product=self.create_product(),
        )
        self.create_review(
            rating=5,
            product=self.create_product(),
        )

        queryset = Review.objects.all()
        filtered = ReviewFilter(
            data={"rating_max": 3},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 2)
        self.assertIn(review_low, filtered)
        self.assertIn(review_mid, filtered)

    def test_filter_by_product_id(self):
        """Filter reviews by product identifier."""
        product = self.create_product()
        review = self.create_review(product=product)
        self.create_review(product=self.create_product())

        queryset = Review.objects.all()
        filtered = ReviewFilter(
            data={"product_id": str(product.id)},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), review)

    def test_filter_by_customer_id(self):
        """Filter reviews by customer identifier."""
        customer = self.create_user()
        review = self.create_review(
            customer=customer,
            product=self.create_product(),
        )
        self.create_review(product=self.create_product())

        queryset = Review.objects.all()
        filtered = ReviewFilter(
            data={"customer_id": str(customer.id)},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), review)

    def test_filter_by_verified_purchase(self):
        """Filter reviews by verified purchase flag."""
        verified_review = self.create_review(
            is_verified_purchase=True,
            product=self.create_product(),
        )
        self.create_review(
            is_verified_purchase=False,
            product=self.create_product(),
        )

        queryset = Review.objects.all()
        filtered = ReviewFilter(
            data={"is_verified_purchase": True},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), verified_review)

    def test_filter_by_moderated_by_id(self):
        """Filter reviews by moderator identifier."""
        moderator = self.create_user(
            email="support@company.com",
            role=User.ROLE_SUPPORT_STAFF,
        )
        moderated_review = self.create_review(
            product=self.create_product(),
            status=Review.REVIEW_STATUS_APPROVED,
            moderated_by=moderator,
        )
        self.create_review(product=self.create_product())

        queryset = Review.objects.all()
        filtered = ReviewFilter(
            data={"moderated_by_id": str(moderator.id)},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), moderated_review)

    def test_filter_by_created_after(self):
        """Filter reviews created after the given datetime."""
        older_review = self.create_review(product=self.create_product())
        newer_review = self.create_review(product=self.create_product())

        Review.objects.filter(id=older_review.id).update(
            created_at=timezone.now() - timezone.timedelta(days=5)
        )

        threshold = timezone.now() - timezone.timedelta(days=1)

        queryset = Review.objects.all()
        filtered = ReviewFilter(
            data={"created_after": threshold.isoformat()},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().id, newer_review.id)

    def test_filter_by_created_before(self):
        """Filter reviews created before the given datetime."""
        older_review = self.create_review(product=self.create_product())
        newer_review = self.create_review(product=self.create_product())

        Review.objects.filter(id=older_review.id).update(
            created_at=timezone.now() - timezone.timedelta(days=5)
        )

        threshold = timezone.now() - timezone.timedelta(days=1)

        queryset = Review.objects.all()
        filtered = ReviewFilter(
            data={"created_before": threshold.isoformat()},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().id, older_review.id)

    def test_filter_ordering_newest(self):
        """Order reviews by newest first."""
        older_review = self.create_review(product=self.create_product())
        newer_review = self.create_review(product=self.create_product())

        Review.objects.filter(id=older_review.id).update(
            created_at=timezone.now() - timezone.timedelta(days=3)
        )

        queryset = Review.objects.all()
        filtered = ReviewFilter(
            data={"ordering": "newest"},
            queryset=queryset,
        ).qs

        filtered_ids = list(filtered.values_list("id", flat=True))
        self.assertEqual(filtered_ids[0], newer_review.id)
        self.assertEqual(filtered_ids[1], older_review.id)

    def test_filter_ordering_oldest(self):
        """Order reviews by oldest first."""
        older_review = self.create_review(product=self.create_product())
        newer_review = self.create_review(product=self.create_product())

        Review.objects.filter(id=older_review.id).update(
            created_at=timezone.now() - timezone.timedelta(days=3)
        )

        queryset = Review.objects.all()
        filtered = ReviewFilter(
            data={"ordering": "oldest"},
            queryset=queryset,
        ).qs

        filtered_ids = list(filtered.values_list("id", flat=True))
        self.assertEqual(filtered_ids[0], older_review.id)
        self.assertEqual(filtered_ids[1], newer_review.id)

    def test_filter_ordering_rating_high(self):
        """Order reviews by rating descending."""
        review_low = self.create_review(
            rating=2,
            product=self.create_product(),
        )
        review_high = self.create_review(
            rating=5,
            product=self.create_product(),
        )

        queryset = Review.objects.all()
        filtered = ReviewFilter(
            data={"ordering": "rating_high"},
            queryset=queryset,
        ).qs

        filtered_ids = list(filtered.values_list("id", flat=True))
        self.assertEqual(filtered_ids[0], review_high.id)
        self.assertEqual(filtered_ids[1], review_low.id)

    def test_filter_ordering_rating_low(self):
        """Order reviews by rating ascending."""
        review_low = self.create_review(
            rating=2,
            product=self.create_product(),
        )
        review_high = self.create_review(
            rating=5,
            product=self.create_product(),
        )

        queryset = Review.objects.all()
        filtered = ReviewFilter(
            data={"ordering": "rating_low"},
            queryset=queryset,
        ).qs

        filtered_ids = list(filtered.values_list("id", flat=True))
        self.assertEqual(filtered_ids[0], review_low.id)
        self.assertEqual(filtered_ids[1], review_high.id)

    def test_filter_invalid_ordering_returns_unmodified_queryset(self):
        """Ignore unsupported ordering values."""
        review_one = self.create_review(product=self.create_product())
        review_two = self.create_review(product=self.create_product())

        queryset = Review.objects.all()
        expected_ids = list(queryset.values_list("id", flat=True))

        filtered = ReviewFilter(
            data={"ordering": "invalid_ordering"},
            queryset=queryset,
        ).qs

        filtered_ids = list(filtered.values_list("id", flat=True))

        self.assertEqual(filtered_ids, expected_ids)
        self.assertIn(review_one.id, filtered_ids)
        self.assertIn(review_two.id, filtered_ids)

    def test_filter_combined_queries(self):
        """Apply multiple review filters together."""
        customer = self.create_user()
        product = self.create_product()

        matching_review = self.create_review(
            customer=customer,
            product=product,
            status=Review.REVIEW_STATUS_APPROVED,
            rating=5,
            is_verified_purchase=True,
        )

        self.create_review(
            customer=self.create_user(),
            product=self.create_product(),
            status=Review.REVIEW_STATUS_PENDING,
            rating=3,
            is_verified_purchase=False,
        )

        queryset = Review.objects.all()
        filtered = ReviewFilter(
            data={
                "customer_id": str(customer.id),
                "product_id": str(product.id),
                "status": Review.REVIEW_STATUS_APPROVED,
                "rating": 5,
                "is_verified_purchase": True,
            },
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), matching_review)

    def test_filter_empty_result(self):
        """Return empty queryset when no review matches filters."""
        self.create_review(
            status=Review.REVIEW_STATUS_PENDING,
            product=self.create_product(),
        )

        queryset = Review.objects.all()
        filtered = ReviewFilter(
            data={"status": Review.REVIEW_STATUS_APPROVED},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 0)