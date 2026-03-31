import uuid

from django.core.cache import cache
from django.test import TestCase

from ech.users.models import CustomUser
from ech.products.models import Product
from ech.reviews.models import (
    Review,
    ReviewLifecycle,
)
from ech.reviews.services.cache_service import ReviewsCacheService


class ReviewsCacheInvalidationTestCase(TestCase):
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
            comment="Initial comment",
            idempotency_key=uuid.uuid4(),
            status=Review.REVIEW_STATUS_APPROVED,
            is_verified_purchase=True,
        )

        ReviewLifecycle.objects.create(review=self.review)

    def test_invalidate_review_detail_changes_detail_cache_key(self):
        """Change the review detail cache key after detail invalidation."""
        first_key = ReviewsCacheService.get_review_detail_cache_key(
            review_id=self.review.id,
        )

        ReviewsCacheService.invalidate_review_detail(
            review_id=self.review.id,
        )

        second_key = ReviewsCacheService.get_review_detail_cache_key(
            review_id=self.review.id,
        )

        self.assertNotEqual(first_key, second_key)

    def test_invalidate_customer_review_lists_changes_customer_list_cache_key(self):
        """Change the customer review list cache key after customer list invalidation."""
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

    def test_invalidate_management_review_lists_changes_management_list_cache_key(self):
        """Change the management review list cache key after management invalidation."""
        first_key = ReviewsCacheService.get_management_review_list_cache_key(
            filters={"status": "approved"},
        )

        ReviewsCacheService.invalidate_management_review_lists()

        second_key = ReviewsCacheService.get_management_review_list_cache_key(
            filters={"status": "approved"},
        )

        self.assertNotEqual(first_key, second_key)

    def test_invalidate_public_product_review_lists_changes_public_list_cache_key(self):
        """Change the public product review list cache key after public list invalidation."""
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

    def test_invalidate_product_review_summary_changes_summary_cache_key(self):
        """Change the product review summary cache key after summary invalidation."""
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

    def test_invalidate_review_aggregate_changes_all_related_cache_keys(self):
        """Change all related cache keys after aggregated review invalidation."""
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

    def test_cached_review_detail_is_not_available_through_new_key_after_invalidation(self):
        """Make previously cached review detail unavailable after namespace invalidation."""
        ReviewsCacheService.set_review_detail(
            review_id=self.review.id,
            value={"id": str(self.review.id), "cached": "detail"},
        )

        self.assertIsNotNone(
            ReviewsCacheService.get_review_detail(review_id=self.review.id)
        )

        ReviewsCacheService.invalidate_review_detail(
            review_id=self.review.id,
        )

        self.assertIsNone(
            ReviewsCacheService.get_review_detail(review_id=self.review.id)
        )

    def test_cached_customer_review_list_is_not_available_through_new_key_after_invalidation(self):
        """Make previously cached customer review list unavailable after namespace invalidation."""
        ReviewsCacheService.set_customer_review_list(
            customer_id=self.customer.id,
            filters={"status": "approved"},
            value=[{"cached": "customer_list"}],
        )

        self.assertIsNotNone(
            ReviewsCacheService.get_customer_review_list(
                customer_id=self.customer.id,
                filters={"status": "approved"},
            )
        )

        ReviewsCacheService.invalidate_customer_review_lists(
            customer_id=self.customer.id,
        )

        self.assertIsNone(
            ReviewsCacheService.get_customer_review_list(
                customer_id=self.customer.id,
                filters={"status": "approved"},
            )
        )

    def test_cached_management_review_list_is_not_available_through_new_key_after_invalidation(self):
        """Make previously cached management review list unavailable after namespace invalidation."""
        ReviewsCacheService.set_management_review_list(
            filters={"status": "approved"},
            value=[{"cached": "management_list"}],
        )

        self.assertIsNotNone(
            ReviewsCacheService.get_management_review_list(
                filters={"status": "approved"},
            )
        )

        ReviewsCacheService.invalidate_management_review_lists()

        self.assertIsNone(
            ReviewsCacheService.get_management_review_list(
                filters={"status": "approved"},
            )
        )

    def test_cached_public_product_review_list_is_not_available_through_new_key_after_invalidation(self):
        """Make previously cached public product review list unavailable after namespace invalidation."""
        ReviewsCacheService.set_public_product_review_list(
            product_id=self.product.id,
            filters={"ordering": "newest"},
            value=[{"cached": "public_list"}],
        )

        self.assertIsNotNone(
            ReviewsCacheService.get_public_product_review_list(
                product_id=self.product.id,
                filters={"ordering": "newest"},
            )
        )

        ReviewsCacheService.invalidate_public_product_review_lists(
            product_id=self.product.id,
        )

        self.assertIsNone(
            ReviewsCacheService.get_public_product_review_list(
                product_id=self.product.id,
                filters={"ordering": "newest"},
            )
        )

    def test_cached_product_review_summary_is_not_available_through_new_key_after_invalidation(self):
        """Make previously cached product review summary unavailable after namespace invalidation."""
        ReviewsCacheService.set_product_review_summary(
            product_id=self.product.id,
            value={
                "product_id": str(self.product.id),
                "average_rating": 5.0,
                "total_reviews": 1,
                "rating_distribution": {
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "4": 0,
                    "5": 1,
                },
                "verified_reviews": 1,
            },
        )

        self.assertIsNotNone(
            ReviewsCacheService.get_product_review_summary(
                product_id=self.product.id,
            )
        )

        ReviewsCacheService.invalidate_product_review_summary(
            product_id=self.product.id,
        )

        self.assertIsNone(
            ReviewsCacheService.get_product_review_summary(
                product_id=self.product.id,
            )
        )