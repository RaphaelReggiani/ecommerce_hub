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


class ProductPublicReviewsApiTestCase(APITestCase):
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

        self.product = self._create_product()

        self.approved_review = self._create_review(
            customer=self.customer_one,
            status=Review.REVIEW_STATUS_APPROVED,
            rating=5,
            title="Excellent product",
        )

        self.pending_review = self._create_review(
            customer=self.customer_two,
            status=Review.REVIEW_STATUS_PENDING,
            rating=4,
            title="Pending review",
        )

        self.hidden_review = self._create_review(
            customer=self.customer_three,
            status=Review.REVIEW_STATUS_HIDDEN,
            rating=3,
            title="Hidden review",
        )

        self.url = reverse(
            "reviews-api:product-review-list",
            kwargs={"product_id": self.product.id},
        )

    def _create_customer(self, *, email, name):
        """Create a minimal customer user for public review tests."""
        return CustomUser.objects.create_user(
            email=email,
            password="StrongPassword123",
            user_name=name,
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

    def _create_product(self):
        """Create a minimal product instance for public review tests."""
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

    def _create_review(self, *, customer, status, rating, title):
        """Create a minimal review instance with lifecycle."""
        review = Review.objects.create(
            customer=customer,
            product=self.product,
            rating=rating,
            title=title,
            comment="Public review comment",
            idempotency_key=uuid.uuid4(),
            status=status,
            is_verified_purchase=False,
        )

        ReviewLifecycle.objects.create(review=review)

        return review

    def test_public_reviews_endpoint_does_not_require_authentication(self):
        """Allow unauthenticated users to access product reviews."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_public_reviews_returns_only_approved_reviews(self):
        """Return only approved reviews in the public listing."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Excellent product")
        self.assertEqual(results[0]["rating"], 5)

    def test_public_reviews_excludes_pending_reviews(self):
        """Ensure pending reviews are not exposed publicly."""
        response = self.client.get(self.url)

        review_titles = [item["title"] for item in response.data["results"]]

        self.assertNotIn("Pending review", review_titles)

    def test_public_reviews_excludes_hidden_reviews(self):
        """Ensure hidden reviews are not exposed publicly."""
        response = self.client.get(self.url)

        review_titles = [item["title"] for item in response.data["results"]]

        self.assertNotIn("Hidden review", review_titles)

    def test_public_reviews_returns_empty_when_no_approved_reviews(self):
        """Return an empty list when a product has no approved reviews."""
        self.approved_review.status = Review.REVIEW_STATUS_REJECTED
        self.approved_review.save(update_fields=["status", "updated_at"])

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)

    def test_public_reviews_supports_pagination_structure(self):
        """Return paginated response structure."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

    def test_public_reviews_returns_not_found_for_invalid_product(self):
        """Return 404 when requesting reviews for a non-existent product."""
        invalid_url = reverse(
            "reviews-api:product-review-list",
            kwargs={"product_id": uuid.uuid4()},
        )

        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_public_reviews_response_contains_expected_fields(self):
        """Ensure public review responses contain expected fields."""
        response = self.client.get(self.url)

        review_data = response.data["results"][0]

        self.assertIn("id", review_data)
        self.assertIn("customer", review_data)
        self.assertIn("rating", review_data)
        self.assertIn("title", review_data)
        self.assertIn("comment", review_data)
        self.assertIn("is_verified_purchase", review_data)
        self.assertIn("created_at", review_data)