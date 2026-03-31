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


class ReviewUpdateApiTestCase(APITestCase):
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
            rating=4,
            title="Good keyboard",
        )

        self.url = reverse(
            "reviews-api:review-update",
            kwargs={"review_id": self.review.id},
        )

    def authenticate(self, user):
        """Authenticate the API client with the provided user."""
        self.client.force_authenticate(user=user)

    def _create_product(self):
        """Create a minimal product instance used for review tests."""
        return Product.objects.create(
            name="Mechanical Keyboard",
            product_type=Product.KEYBOARD,
            brand="TechBrand",
            sold_by=self.admin,
            description="Mechanical keyboard for gaming.",
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
            comment="Initial comment",
            idempotency_key=uuid.uuid4(),
            status=Review.REVIEW_STATUS_PENDING,
            is_verified_purchase=False,
        )

        ReviewLifecycle.objects.create(review=review)

        return review

    def test_update_review_requires_authentication(self):
        """Reject review update requests from unauthenticated users."""
        response = self.client.patch(self.url, {"rating": 5}, format="json")

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_update_review_successfully_by_owner(self):
        """Allow the review owner to update editable fields."""
        self.authenticate(self.customer)

        payload = {
            "rating": 5,
            "title": "Excellent keyboard",
            "comment": "After using it for a while, it feels amazing.",
        }

        response = self.client.patch(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.review.refresh_from_db()

        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.title, "Excellent keyboard")
        self.assertEqual(
            self.review.comment,
            "After using it for a while, it feels amazing.",
        )

    def test_update_review_accepts_same_existing_values(self):
        """Return success when the submitted values match the current persisted values."""
        self.authenticate(self.customer)

        payload = {
            "rating": self.review.rating,
            "title": self.review.title,
            "comment": self.review.comment,
        }

        response = self.client.patch(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.review.refresh_from_db()

        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.title, "Good keyboard")
        self.assertEqual(self.review.comment, "Initial comment")

    def test_update_review_rejects_other_customer(self):
        """Reject review updates attempted by another customer."""
        self.authenticate(self.other_customer)

        response = self.client.patch(
            self.url,
            {"rating": 1},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_review_rejects_admin_on_customer_endpoint(self):
        """Reject admin attempts to update a review through the customer endpoint."""
        self.authenticate(self.admin)

        response = self.client.patch(
            self.url,
            {"rating": 5},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_review_rejects_invalid_rating(self):
        """Reject updates when rating is outside the allowed range."""
        self.authenticate(self.customer)

        response = self.client.patch(
            self.url,
            {"rating": 6},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_review_returns_bad_request_for_empty_payload(self):
        """Reject review updates when no fields are provided."""
        self.authenticate(self.customer)

        response = self.client.patch(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_review_returns_not_found_for_invalid_review(self):
        """Return 404 when attempting to update a non-existent review."""
        self.authenticate(self.customer)

        invalid_url = reverse(
            "reviews-api:review-update",
            kwargs={"review_id": uuid.uuid4()},
        )

        response = self.client.patch(
            invalid_url,
            {"rating": 5},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)