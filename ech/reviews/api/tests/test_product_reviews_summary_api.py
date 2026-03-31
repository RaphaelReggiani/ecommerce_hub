import uuid

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import (
    CustomUser,
)
from ech.products.models import (
    Product,
)
from ech.reviews.models import (
    Review,
    ReviewLifecycle,
)


class ProductReviewSummaryApiTestCase(APITestCase):
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

        self.customer_one = self._create_customer(
            email="customer1@test.com",
            name="Customer One",
        )
        self.customer_two = self._create_customer(
            email="customer2@test.com",
            name="Customer Two",
        )
        self.customer_three = self._create_customer(
            email="customer3@test.com",
            name="Customer Three",
        )
        self.customer_four = self._create_customer(
            email="customer4@test.com",
            name="Customer Four",
        )

        self.product = self._create_product()

        self._create_review(
            customer=self.customer_one,
            rating=5,
            status=Review.REVIEW_STATUS_APPROVED,
            is_verified_purchase=True,
        )
        self._create_review(
            customer=self.customer_two,
            rating=4,
            status=Review.REVIEW_STATUS_APPROVED,
            is_verified_purchase=False,
        )
        self._create_review(
            customer=self.customer_three,
            rating=2,
            status=Review.REVIEW_STATUS_APPROVED,
            is_verified_purchase=True,
        )
        self._create_review(
            customer=self.customer_four,
            rating=1,
            status=Review.REVIEW_STATUS_PENDING,
            is_verified_purchase=True,
        )

        self.url = reverse(
            "reviews-api:product-review-summary",
            kwargs={"product_id": self.product.id},
        )

    def _create_customer(self, *, email, name):
        """Create a minimal customer user for product review summary tests."""
        return CustomUser.objects.create_user(
            email=email,
            password="StrongPassword123",
            user_name=name,
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

    def _create_product(self):
        """Create a minimal product instance for review summary tests."""
        return Product.objects.create(
            name="Gaming Headset",
            product_type=Product.HEADSET,
            brand="TechBrand",
            sold_by=self.admin,
            description="High quality gaming headset.",
            technical_information="Wireless surround audio.",
            price="499.90",
            discount_price="449.90",
            is_active=True,
        )

    def _create_review(
        self,
        *,
        customer,
        rating,
        status,
        is_verified_purchase,
    ):
        """Create a minimal review instance with lifecycle."""
        review = Review.objects.create(
            customer=customer,
            product=self.product,
            rating=rating,
            title=f"Review {rating}",
            comment="Summary review comment",
            idempotency_key=uuid.uuid4(),
            status=status,
            is_verified_purchase=is_verified_purchase,
        )

        ReviewLifecycle.objects.create(review=review)
        return review

    def test_product_review_summary_does_not_require_authentication(self):
        """Allow unauthenticated users to access product review summary."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_review_summary_returns_aggregated_data_for_approved_reviews(self):
        """Return aggregated summary considering only approved reviews."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["product_id"], str(self.product.id))
        self.assertEqual(response.data["total_reviews"], 3)
        self.assertEqual(response.data["verified_reviews"], 2)
        self.assertAlmostEqual(response.data["average_rating"], (5 + 4 + 2) / 3)

    def test_product_review_summary_ignores_non_approved_reviews(self):
        """Ignore non-approved reviews in public product summary calculations."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_reviews"], 3)

        distribution = response.data["rating_distribution"]

        self.assertEqual(distribution["1"], 0)
        self.assertEqual(distribution["2"], 1)
        self.assertEqual(distribution["4"], 1)
        self.assertEqual(distribution["5"], 1)

    def test_product_review_summary_returns_expected_rating_distribution(self):
        """Return the expected rating distribution for approved reviews."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        distribution = response.data["rating_distribution"]

        self.assertEqual(distribution["1"], 0)
        self.assertEqual(distribution["2"], 1)
        self.assertEqual(distribution["3"], 0)
        self.assertEqual(distribution["4"], 1)
        self.assertEqual(distribution["5"], 1)

    def test_product_review_summary_returns_zero_counts_when_no_approved_reviews(self):
        """Return zeroed summary data when the product has no approved reviews."""
        Review.objects.filter(product=self.product).update(
            status=Review.REVIEW_STATUS_REJECTED
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_reviews"], 0)
        self.assertEqual(response.data["verified_reviews"], 0)
        self.assertIsNone(response.data["average_rating"])

        distribution = response.data["rating_distribution"]

        self.assertEqual(distribution["1"], 0)
        self.assertEqual(distribution["2"], 0)
        self.assertEqual(distribution["3"], 0)
        self.assertEqual(distribution["4"], 0)
        self.assertEqual(distribution["5"], 0)

    def test_product_review_summary_returns_not_found_for_invalid_product(self):
        """Return 404 when requesting summary for a non-existent product."""
        invalid_url = reverse(
            "reviews-api:product-review-summary",
            kwargs={"product_id": uuid.uuid4()},
        )

        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_product_review_summary_response_contains_expected_fields(self):
        """Ensure the product review summary response contains expected fields."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("product_id", response.data)
        self.assertIn("average_rating", response.data)
        self.assertIn("total_reviews", response.data)
        self.assertIn("rating_distribution", response.data)
        self.assertIn("verified_reviews", response.data)