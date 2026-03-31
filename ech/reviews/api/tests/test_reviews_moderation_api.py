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


class ReviewModerationApiTestCase(APITestCase):

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

        self.staff = CustomUser.objects.create_user(
            email="support@company.com",
            password="StrongPassword123",
            user_name="Support Staff",
            role=CustomUser.ROLE_SUPPORT_STAFF,
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
            "reviews-api:review-moderate",
            kwargs={"review_id": self.review.id},
        )

    def authenticate(self, user):
        """Authenticate the API client with the provided user."""
        self.client.force_authenticate(user=user)

    def _create_product(self):
        """Create a minimal product instance for moderation tests."""
        return Product.objects.create(
            name="Wireless Headset",
            product_type=Product.HEADSET,
            brand="TechBrand",
            sold_by=self.admin,
            description="Wireless gaming headset.",
            technical_information="Low latency wireless audio.",
            price="499.90",
            discount_price="449.90",
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
            title="Great headset",
            comment="Initial review comment",
            idempotency_key=uuid.uuid4(),
            status=status,
            is_verified_purchase=False,
        )

        ReviewLifecycle.objects.create(review=review)
        return review

    def test_moderation_requires_authentication(self):
        """Reject moderation requests from unauthenticated users."""
        response = self.client.post(
            self.url,
            {"action": "approve"},
            format="json",
        )

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_moderation_rejects_customer_user(self):
        """Reject moderation attempts from customer users."""
        self.authenticate(self.customer)

        response = self.client.post(
            self.url,
            {"action": "approve"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderation_allows_support_staff_to_approve_review(self):
        """Allow support staff to approve pending reviews."""
        self.authenticate(self.staff)

        response = self.client.post(
            self.url,
            {
                "action": "approve",
                "reason": "Review meets moderation guidelines.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.review.refresh_from_db()
        lifecycle = self.review.lifecycle

        self.assertEqual(self.review.status, Review.REVIEW_STATUS_APPROVED)
        self.assertEqual(
            self.review.moderation_reason,
            "Review meets moderation guidelines.",
        )
        self.assertIsNotNone(lifecycle.approved_at)

        self.assertTrue(
            ReviewEvent.objects.filter(
                review=self.review,
                event_type=ReviewEvent.TYPE_APPROVED,
            ).exists()
        )

    def test_moderation_allows_admin_to_reject_review(self):
        """Allow admin users to reject pending reviews."""
        self.authenticate(self.admin)

        response = self.client.post(
            self.url,
            {
                "action": "reject",
                "reason": "Inappropriate language detected.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.review.refresh_from_db()

        self.assertEqual(self.review.status, Review.REVIEW_STATUS_REJECTED)
        self.assertEqual(
            self.review.moderation_reason,
            "Inappropriate language detected.",
        )

        self.assertTrue(
            ReviewEvent.objects.filter(
                review=self.review,
                event_type=ReviewEvent.TYPE_REJECTED,
            ).exists()
        )

    def test_moderation_can_hide_approved_review(self):
        """Allow staff to hide an already approved review."""
        self.review.status = Review.REVIEW_STATUS_APPROVED
        self.review.save(update_fields=["status", "updated_at"])

        self.authenticate(self.staff)

        response = self.client.post(
            self.url,
            {"action": "hide", "reason": "Temporarily hidden."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.review.refresh_from_db()

        self.assertEqual(self.review.status, Review.REVIEW_STATUS_HIDDEN)

    def test_moderation_can_restore_hidden_review(self):
        """Allow staff to restore hidden reviews."""
        self.review.status = Review.REVIEW_STATUS_HIDDEN
        self.review.save(update_fields=["status", "updated_at"])

        self.authenticate(self.staff)

        response = self.client.post(
            self.url,
            {"action": "restore"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.review.refresh_from_db()

        self.assertEqual(self.review.status, Review.REVIEW_STATUS_APPROVED)

    def test_moderation_rejects_invalid_action(self):
        """Reject moderation requests with invalid actions."""
        self.authenticate(self.staff)

        response = self.client.post(
            self.url,
            {"action": "invalid_action"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_moderation_rejects_invalid_transition(self):
        """Reject moderation when the requested transition is invalid."""
        self.review.status = Review.REVIEW_STATUS_APPROVED
        self.review.save(update_fields=["status", "updated_at"])

        self.authenticate(self.staff)

        response = self.client.post(
            self.url,
            {"action": "reject"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_moderation_returns_not_found_for_invalid_review(self):
        """Return 404 when moderating a non-existent review."""
        self.authenticate(self.staff)

        invalid_url = reverse(
            "reviews-api:review-moderate",
            kwargs={"review_id": uuid.uuid4()},
        )

        response = self.client.post(
            invalid_url,
            {"action": "approve"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_moderation_response_contains_expected_fields(self):
        """Ensure the moderation response contains expected review detail fields."""
        self.authenticate(self.staff)

        response = self.client.post(
            self.url,
            {"action": "approve"},
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
        self.assertIn("moderation_reason", review_data)
        self.assertIn("moderated_by", review_data)
        self.assertIn("moderated_at", review_data)
        self.assertIn("lifecycle", review_data)
        self.assertIn("created_at", review_data)
        self.assertIn("updated_at", review_data)