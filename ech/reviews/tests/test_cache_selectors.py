import uuid

from django.core.cache import cache
from django.test import TestCase

from ech.users.models import (
    CustomUser,
)
from ech.products.models import (
    Product,
)
from ech.reviews.models import (
    Review,
)
from ech.reviews.services.cache_service import ReviewsCacheService


class ReviewsCacheSelectorsTestCase(TestCase):
    def setUp(self):
        cache.clear()

        self.admin = CustomUser.objects.create_user(
            email="admin@company.com",
            password="StrongPassword123",
            user_name="Admin User",
            role=CustomUser.ROLE_ADMIN,
            is_active=True,
            email_confirmed=True,
        )

        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.product = Product.objects.create(
            name="Gaming Headset",
            product_type=Product.HEADSET,
            brand="TechBrand",
            sold_by=self.admin,
            description="High quality headset.",
            technical_information="Wireless and low latency.",
            price="499.90",
            discount_price="449.90",
            is_active=True,
        )

        self.review = Review.objects.create(
            customer=self.customer,
            product=self.product,
            rating=5,
            title="Excellent product",
            comment="Very good experience.",
            idempotency_key=uuid.uuid4(),
            status=Review.REVIEW_STATUS_APPROVED,
            is_verified_purchase=True,
        )

    def test_review_detail_cache_key_is_stable_for_same_version(self):
        """Return the same cache key for review detail within the same namespace version."""
        first_key = ReviewsCacheService.get_review_detail_cache_key(
            review_id=self.review.id,
        )
        second_key = ReviewsCacheService.get_review_detail_cache_key(
            review_id=self.review.id,
        )

        self.assertEqual(first_key, second_key)

    def test_review_detail_cache_key_changes_after_invalidation(self):
        """Change the review detail cache key after invalidation bumps the namespace version."""
        first_key = ReviewsCacheService.get_review_detail_cache_key(
            review_id=self.review.id,
        )

        ReviewsCacheService.invalidate_review_detail(review_id=self.review.id)

        second_key = ReviewsCacheService.get_review_detail_cache_key(
            review_id=self.review.id,
        )

        self.assertNotEqual(first_key, second_key)

    def test_set_and_get_review_detail_cache(self):
        """Store and retrieve cached review detail successfully."""
        cached_value = {
            "id": str(self.review.id),
            "rating": 5,
            "status": self.review.status,
        }

        ReviewsCacheService.set_review_detail(
            review_id=self.review.id,
            value=cached_value,
        )

        result = ReviewsCacheService.get_review_detail(
            review_id=self.review.id,
        )

        self.assertEqual(result, cached_value)

    def test_get_or_set_review_detail_returns_cached_value_on_second_call(self):
        """Return the cached review detail value on repeated access."""
        callback_calls = {"count": 0}

        def callback():
            callback_calls["count"] += 1
            return {"id": str(self.review.id), "title": self.review.title}

        first_result = ReviewsCacheService.get_or_set_review_detail(
            review_id=self.review.id,
            callback=callback,
        )
        second_result = ReviewsCacheService.get_or_set_review_detail(
            review_id=self.review.id,
            callback=callback,
        )

        self.assertEqual(first_result, second_result)
        self.assertEqual(callback_calls["count"], 1)

    def test_customer_review_list_cache_is_isolated_by_filters(self):
        """Generate different customer review list cache keys for different filter payloads."""
        first_key = ReviewsCacheService.get_customer_review_list_cache_key(
            customer_id=self.customer.id,
            filters={"status": "approved"},
        )
        second_key = ReviewsCacheService.get_customer_review_list_cache_key(
            customer_id=self.customer.id,
            filters={"status": "pending"},
        )

        self.assertNotEqual(first_key, second_key)

    def test_set_and_get_customer_review_list_cache(self):
        """Store and retrieve cached customer review lists successfully."""
        cached_value = [
            {"id": str(self.review.id), "rating": self.review.rating},
        ]

        ReviewsCacheService.set_customer_review_list(
            customer_id=self.customer.id,
            filters={"status": "approved"},
            value=cached_value,
        )

        result = ReviewsCacheService.get_customer_review_list(
            customer_id=self.customer.id,
            filters={"status": "approved"},
        )

        self.assertEqual(result, cached_value)

    def test_customer_review_list_cache_key_changes_after_invalidation(self):
        """Change the customer review list cache key after invalidation."""
        first_key = ReviewsCacheService.get_customer_review_list_cache_key(
            customer_id=self.customer.id,
            filters={"status": "approved"},
        )

        ReviewsCacheService.invalidate_customer_review_lists(
            customer_id=self.customer.id,
        )

        second_key = ReviewsCacheService.get_customer_review_list_cache_key(
            customer_id=self.customer.id,
            filters={"status": "approved"},
        )

        self.assertNotEqual(first_key, second_key)

    def test_management_review_list_cache_is_isolated_by_filters(self):
        """Generate different management list cache keys for different filter payloads."""
        first_key = ReviewsCacheService.get_management_review_list_cache_key(
            filters={"status": "approved"},
        )
        second_key = ReviewsCacheService.get_management_review_list_cache_key(
            filters={"rating": 5},
        )

        self.assertNotEqual(first_key, second_key)

    def test_set_and_get_management_review_list_cache(self):
        """Store and retrieve cached management review lists successfully."""
        cached_value = [
            {"id": str(self.review.id), "status": self.review.status},
        ]

        ReviewsCacheService.set_management_review_list(
            filters={"status": "approved"},
            value=cached_value,
        )

        result = ReviewsCacheService.get_management_review_list(
            filters={"status": "approved"},
        )

        self.assertEqual(result, cached_value)

    def test_management_review_list_cache_key_changes_after_invalidation(self):
        """Change the management review list cache key after invalidation."""
        first_key = ReviewsCacheService.get_management_review_list_cache_key(
            filters={"status": "approved"},
        )

        ReviewsCacheService.invalidate_management_review_lists()

        second_key = ReviewsCacheService.get_management_review_list_cache_key(
            filters={"status": "approved"},
        )

        self.assertNotEqual(first_key, second_key)

    def test_public_product_review_list_cache_is_isolated_by_filters(self):
        """Generate different public product review list cache keys for different filter payloads."""
        first_key = ReviewsCacheService.get_public_product_review_list_cache_key(
            product_id=self.product.id,
            filters={"ordering": "newest"},
        )
        second_key = ReviewsCacheService.get_public_product_review_list_cache_key(
            product_id=self.product.id,
            filters={"ordering": "rating_high"},
        )

        self.assertNotEqual(first_key, second_key)

    def test_set_and_get_public_product_review_list_cache(self):
        """Store and retrieve cached public product review lists successfully."""
        cached_value = [
            {"id": str(self.review.id), "rating": self.review.rating},
        ]

        ReviewsCacheService.set_public_product_review_list(
            product_id=self.product.id,
            filters={"ordering": "newest"},
            value=cached_value,
        )

        result = ReviewsCacheService.get_public_product_review_list(
            product_id=self.product.id,
            filters={"ordering": "newest"},
        )

        self.assertEqual(result, cached_value)

    def test_public_product_review_list_cache_key_changes_after_invalidation(self):
        """Change the public product review list cache key after invalidation."""
        first_key = ReviewsCacheService.get_public_product_review_list_cache_key(
            product_id=self.product.id,
            filters={"ordering": "newest"},
        )

        ReviewsCacheService.invalidate_public_product_review_lists(
            product_id=self.product.id,
        )

        second_key = ReviewsCacheService.get_public_product_review_list_cache_key(
            product_id=self.product.id,
            filters={"ordering": "newest"},
        )

        self.assertNotEqual(first_key, second_key)

    def test_set_and_get_product_review_summary_cache(self):
        """Store and retrieve cached product review summary successfully."""
        cached_value = {
            "product_id": str(self.product.id),
            "average_rating": 5.0,
            "total_reviews": 1,
            "rating_distribution": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 1},
            "verified_reviews": 1,
        }

        ReviewsCacheService.set_product_review_summary(
            product_id=self.product.id,
            value=cached_value,
        )

        result = ReviewsCacheService.get_product_review_summary(
            product_id=self.product.id,
        )

        self.assertEqual(result, cached_value)

    def test_product_review_summary_cache_key_changes_after_invalidation(self):
        """Change the product review summary cache key after invalidation."""
        first_key = ReviewsCacheService.get_product_review_summary_cache_key(
            product_id=self.product.id,
        )

        ReviewsCacheService.invalidate_product_review_summary(
            product_id=self.product.id,
        )

        second_key = ReviewsCacheService.get_product_review_summary_cache_key(
            product_id=self.product.id,
        )

        self.assertNotEqual(first_key, second_key)

    def test_invalidate_review_aggregate_bumps_all_related_namespaces(self):
        """Invalidate all related cache namespaces through aggregated invalidation."""
        detail_key_before = ReviewsCacheService.get_review_detail_cache_key(
            review_id=self.review.id,
        )
        customer_key_before = ReviewsCacheService.get_customer_review_list_cache_key(
            customer_id=self.customer.id,
            filters={"status": "approved"},
        )
        management_key_before = ReviewsCacheService.get_management_review_list_cache_key(
            filters={"status": "approved"},
        )
        public_key_before = ReviewsCacheService.get_public_product_review_list_cache_key(
            product_id=self.product.id,
            filters={"ordering": "newest"},
        )
        summary_key_before = ReviewsCacheService.get_product_review_summary_cache_key(
            product_id=self.product.id,
        )

        ReviewsCacheService.invalidate_review_aggregate(
            review_id=self.review.id,
            customer_id=self.customer.id,
            product_id=self.product.id,
        )

        detail_key_after = ReviewsCacheService.get_review_detail_cache_key(
            review_id=self.review.id,
        )
        customer_key_after = ReviewsCacheService.get_customer_review_list_cache_key(
            customer_id=self.customer.id,
            filters={"status": "approved"},
        )
        management_key_after = ReviewsCacheService.get_management_review_list_cache_key(
            filters={"status": "approved"},
        )
        public_key_after = ReviewsCacheService.get_public_product_review_list_cache_key(
            product_id=self.product.id,
            filters={"ordering": "newest"},
        )
        summary_key_after = ReviewsCacheService.get_product_review_summary_cache_key(
            product_id=self.product.id,
        )

        self.assertNotEqual(detail_key_before, detail_key_after)
        self.assertNotEqual(customer_key_before, customer_key_after)
        self.assertNotEqual(management_key_before, management_key_after)
        self.assertNotEqual(public_key_before, public_key_after)
        self.assertNotEqual(summary_key_before, summary_key_after)