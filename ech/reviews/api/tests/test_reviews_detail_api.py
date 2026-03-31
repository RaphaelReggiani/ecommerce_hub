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


class ReviewDetailApiTestCase(APITestCase):
    def setUp(self):
        cache.clear()

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

        self.review = self._create_review(
            customer=self.customer,
            rating=5,
            title="Excellent product",
        )

        self.url = reverse(
            "reviews-api:review-detail",
            kwargs={"review_id": self.review.id},
        )

    def authenticate(self, user):
        """Authenticate the API client with the provided user."""
        self.client.force_authenticate(user=user)

    def _create_product(self):
        """Create a minimal product instance used by reviews."""
        return Product.objects.create(
            name="Gaming Keyboard",
            product_type=Product.KEYBOARD,
            brand="TechBrand",
            sold_by=self.admin,
            description="Mechanical gaming keyboard.",
            technical_information="RGB, hot-swappable switches.",
            price="399.90",
            discount_price="349.90",
            is_active=True,
        )

    def _create_review(self, *, customer, rating=5, title="Test Review"):
        """Create a minimal review instance with lifecycle."""
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

    def test_review_detail_requires_authentication(self):
        """Reject review detail access for unauthenticated users."""
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_review_detail_returns_review_for_owner(self):
        """Allow the review owner to access their review details."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.review.id))
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["title"], "Excellent product")
        self.assertEqual(response.data["comment"], "Test comment")

    def test_review_detail_rejects_admin_on_customer_endpoint(self):
        """Reject admin access on the customer review detail endpoint."""
        self.authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_review_detail_rejects_other_customer(self):
        """Reject access when a different customer attempts to view the review."""
        self.authenticate(self.other_customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_review_detail_returns_not_found_for_invalid_id(self):
        """Return 404 when requesting a non-existent review."""
        self.authenticate(self.customer)

        invalid_url = reverse(
            "reviews-api:review-detail",
            kwargs={"review_id": uuid.uuid4()},
        )

        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_review_detail_response_contains_expected_fields(self):
        """Ensure the response contains the expected review detail fields."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        review_data = response.data

        self.assertIn("id", review_data)
        self.assertIn("product", review_data)
        self.assertIn("customer", review_data)
        self.assertIn("rating", review_data)
        self.assertIn("title", review_data)
        self.assertIn("comment", review_data)
        self.assertIn("status", review_data)
        self.assertIn("is_verified_purchase", review_data)
        self.assertIn("moderated_by", review_data)
        self.assertIn("moderation_reason", review_data)
        self.assertIn("moderated_at", review_data)
        self.assertIn("lifecycle", review_data)
        self.assertIn("created_at", review_data)
        self.assertIn("updated_at", review_data)