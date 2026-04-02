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
    ReviewEvent,
)


class ReviewCancelApiTestCase(APITestCase):
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
            status=Review.REVIEW_STATUS_PENDING,
        )

        self.url = reverse(
            "reviews-api:review-cancel",
            kwargs={"review_id": self.review.id},
        )

    def authenticate(self, user):
        """Authenticate the API client with the provided user."""
        self.client.force_authenticate(user=user)

    def _create_product(self):
        """Create a minimal product instance used for review tests."""
        return Product.objects.create(
            name="Gaming Mouse Pro",
            product_type=Product.MOUSE,
            brand="TechBrand",
            sold_by=self.admin,
            description="Professional gaming mouse.",
            technical_information="Ultra-lightweight and wireless.",
            price="299.90",
            discount_price="249.90",
            is_active=True,
        )

    def _create_review(
        self,
        *,
        customer,
        status=Review.REVIEW_STATUS_PENDING,
        rating=5,
    ):
        """Create a minimal review instance with lifecycle."""
        review = Review.objects.create(
            customer=customer,
            product=self.product,
            rating=rating,
            title="Great product",
            comment="Initial review comment",
            idempotency_key=uuid.uuid4(),
            status=status,
            is_verified_purchase=False,
        )

        ReviewLifecycle.objects.create(review=review)
        return review

    def test_cancel_review_requires_authentication(self):
        """Reject review cancellation requests from unauthenticated users."""
        response = self.client.post(self.url, {}, format="json")

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_cancel_review_successfully_by_owner(self):
        """Allow the review owner to cancel the review successfully."""
        self.authenticate(self.customer)

        response = self.client.post(
            self.url,
            {"reason": "I want to withdraw this review."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.review.refresh_from_db()
        lifecycle = self.review.lifecycle

        self.assertEqual(self.review.status, Review.REVIEW_STATUS_CANCELLED)
        self.assertEqual(self.review.moderation_reason, "")
        self.assertIsNotNone(lifecycle.cancelled_at)

        self.assertTrue(
            ReviewEvent.objects.filter(
                review=self.review,
                event_type=ReviewEvent.TYPE_CANCELLED,
            ).exists()
        )

        self.assertEqual(response.data["id"], str(self.review.id))
        self.assertEqual(response.data["status"], Review.REVIEW_STATUS_CANCELLED)

    def test_cancel_review_successfully_without_reason(self):
        """Allow review cancellation when no reason is provided."""
        self.authenticate(self.customer)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.review.refresh_from_db()
        self.assertEqual(self.review.status, Review.REVIEW_STATUS_CANCELLED)
        self.assertEqual(self.review.moderation_reason, "")

    def test_cancel_review_rejects_other_customer(self):
        """Reject cancellation attempts from a different customer."""
        self.authenticate(self.other_customer)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cancel_review_rejects_admin_on_customer_endpoint(self):
        """Reject admin cancellation attempts on the customer cancel endpoint."""
        self.authenticate(self.admin)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cancel_review_rejects_already_cancelled_review(self):
        """Reject cancellation when the review is already cancelled."""
        self.review.status = Review.REVIEW_STATUS_CANCELLED
        self.review.save(update_fields=["status", "updated_at"])

        self.authenticate(self.customer)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_review_returns_not_found_for_invalid_review(self):
        """Return 404 when attempting to cancel a non-existent review."""
        self.authenticate(self.customer)

        invalid_url = reverse(
            "reviews-api:review-cancel",
            kwargs={"review_id": uuid.uuid4()},
        )

        response = self.client.post(invalid_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_review_response_contains_expected_fields(self):
        """Ensure the cancellation response contains the expected review detail fields."""
        self.authenticate(self.customer)

        response = self.client.post(
            self.url,
            {"reason": "Cancelling this review."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        review_data = response.data

        self.assertIn("id", review_data)
        self.assertIn("customer", review_data)
        self.assertIn("product", review_data)
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