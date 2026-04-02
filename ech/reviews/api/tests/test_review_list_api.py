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


class ReviewListApiTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("reviews-api:review-list")

        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.other_customer = CustomUser.objects.create_user(
            email="other@test.com",
            password="StrongPassword123",
            user_name="Other Customer",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.admin = CustomUser.objects.create_user(
            email="admin@company.com",
            password="StrongPassword123",
            user_name="Admin User",
            role=CustomUser.ROLE_ADMIN,
            is_active=True,
            email_confirmed=True,
        )

        self.product = self._create_product()

        self.review_customer = self._create_review(
            customer=self.customer,
            rating=5,
            title="Excellent mouse",
        )

        self.review_other = self._create_review(
            customer=self.other_customer,
            rating=3,
            title="Average mouse",
        )

    def authenticate(self, user):
        """Authenticate the test client with the provided user."""
        self.client.force_authenticate(user=user)

    def _create_product(self):
        """Create a minimal product instance for review tests."""
        return Product.objects.create(
            name="Gaming Mouse X",
            product_type=Product.MOUSE,
            brand="TechBrand",
            sold_by=self.admin,
            description="High precision gaming mouse.",
            technical_information="16000 DPI sensor",
            price="199.90",
            discount_price="149.90",
            is_active=True,
        )

    def _create_review(self, *, customer, rating=5, title="Test Review"):
        """Create a minimal review instance with its lifecycle."""
        review = Review.objects.create(
            customer=customer,
            product=self.product,
            rating=rating,
            title=title,
            comment="Test comment",
            idempotency_key=uuid.uuid4(),
            status=Review.REVIEW_STATUS_APPROVED,
            is_verified_purchase=False,
        )
        ReviewLifecycle.objects.create(review=review)
        return review

    def test_list_reviews_requires_authentication(self):
        """Reject review listing for unauthenticated users."""
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_list_reviews_returns_only_user_reviews(self):
        """Return only reviews created by the authenticated customer."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], str(self.review_customer.id))
        self.assertEqual(results[0]["title"], "Excellent mouse")
        self.assertEqual(results[0]["rating"], 5)

    def test_list_reviews_returns_correct_reviews_for_other_customer(self):
        """Return reviews belonging to the other authenticated customer."""
        self.authenticate(self.other_customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], str(self.review_other.id))
        self.assertEqual(results[0]["title"], "Average mouse")
        self.assertEqual(results[0]["rating"], 3)

    def test_list_reviews_returns_empty_list_when_user_has_no_reviews(self):
        """Return an empty list when the authenticated user has no reviews."""
        new_user = CustomUser.objects.create_user(
            email="new@test.com",
            password="StrongPassword123",
            user_name="New User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.authenticate(new_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)

    def test_list_reviews_supports_pagination_structure(self):
        """Return paginated results with the expected pagination fields."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

    def test_list_reviews_response_contains_expected_fields(self):
        """Ensure the list response contains the expected review fields."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        review_data = response.data["results"][0]

        self.assertIn("id", review_data)
        self.assertIn("product", review_data)
        self.assertIn("rating", review_data)
        self.assertIn("title", review_data)
        self.assertIn("comment", review_data)
        self.assertIn("status", review_data)
        self.assertIn("is_verified_purchase", review_data)
        self.assertIn("moderation_reason", review_data)
        self.assertIn("moderated_at", review_data)
        self.assertIn("created_at", review_data)
        self.assertIn("updated_at", review_data)

    def test_list_reviews_does_not_return_reviews_from_other_users(self):
        """Ensure reviews from other users are not exposed in the list endpoint."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        review_ids = [item["id"] for item in response.data["results"]]

        self.assertIn(str(self.review_customer.id), review_ids)
        self.assertNotIn(str(self.review_other.id), review_ids)