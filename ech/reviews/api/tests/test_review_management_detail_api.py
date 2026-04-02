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


class ReviewManagementDetailApiTestCase(APITestCase):
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

        self.support_staff = CustomUser.objects.create_user(
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

        self.seller = CustomUser.objects.create_user(
            email="seller@company.com",
            password="StrongPassword123",
            user_name="Seller User",
            role=CustomUser.ROLE_ADMIN,
            is_active=True,
            email_confirmed=True,
        )

        self.product = self._create_product()

        self.review = self._create_review(
            customer=self.customer,
            product=self.product,
            rating=5,
            status=Review.REVIEW_STATUS_APPROVED,
            title="Excellent headset",
            moderated_by=self.support_staff,
        )

        ReviewEvent.objects.create(
            review=self.review,
            event_type=ReviewEvent.TYPE_CREATED,
            performed_by=self.customer,
            metadata={"rating": 5},
        )
        ReviewEvent.objects.create(
            review=self.review,
            event_type=ReviewEvent.TYPE_APPROVED,
            performed_by=self.support_staff,
            metadata={"moderation_action": "approve"},
        )

        self.url = reverse(
            "reviews-api:review-management-detail",
            kwargs={"review_id": self.review.id},
        )

    def authenticate(self, user):
        """Authenticate the API client with the provided user."""
        self.client.force_authenticate(user=user)

    def _create_product(self):
        """Create a minimal product instance for management detail tests."""
        return Product.objects.create(
            name="Gaming Headset Pro",
            product_type=Product.HEADSET,
            brand="TechBrand",
            sold_by=self.seller,
            description="Premium gaming headset.",
            technical_information="Wireless audio and noise cancellation.",
            price="599.90",
            discount_price="549.90",
            is_active=True,
        )

    def _create_review(
        self,
        *,
        customer,
        product,
        rating,
        status,
        title,
        moderated_by=None,
    ):
        """Create a minimal review instance with lifecycle."""
        review = Review.objects.create(
            customer=customer,
            product=product,
            rating=rating,
            title=title,
            comment="Management detail review comment",
            idempotency_key=uuid.uuid4(),
            status=status,
            is_verified_purchase=True,
            moderated_by=moderated_by,
            moderation_reason="Approved after staff review." if moderated_by else "",
        )

        ReviewLifecycle.objects.create(review=review)
        return review

    def test_management_detail_requires_authentication(self):
        """Reject management review detail access for unauthenticated users."""
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_management_detail_rejects_customer_user(self):
        """Reject management review detail access for customer users."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_management_detail_allows_support_staff(self):
        """Allow support staff to access review management detail."""
        self.authenticate(self.support_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.review.id))

    def test_management_detail_allows_admin(self):
        """Allow admin users to access review management detail."""
        self.authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.review.id))

    def test_management_detail_returns_not_found_for_invalid_review(self):
        """Return 404 when requesting management detail for a non-existent review."""
        self.authenticate(self.support_staff)

        invalid_url = reverse(
            "reviews-api:review-management-detail",
            kwargs={"review_id": uuid.uuid4()},
        )

        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_management_detail_response_contains_expected_fields(self):
        """Ensure management detail response contains expected review fields."""
        self.authenticate(self.support_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        review_data = response.data

        self.assertIn("id", review_data)
        self.assertIn("customer", review_data)
        self.assertIn("product", review_data)
        self.assertIn("rating", review_data)
        self.assertIn("title", review_data)
        self.assertIn("comment", review_data)
        self.assertIn("status", review_data)
        self.assertIn("idempotency_key", review_data)
        self.assertIn("is_verified_purchase", review_data)
        self.assertIn("moderated_by", review_data)
        self.assertIn("moderated_by_name", review_data)
        self.assertIn("moderated_by_email", review_data)
        self.assertIn("moderation_reason", review_data)
        self.assertIn("moderated_at", review_data)
        self.assertIn("lifecycle", review_data)
        self.assertIn("events", review_data)
        self.assertIn("created_at", review_data)
        self.assertIn("updated_at", review_data)

    def test_management_detail_returns_lifecycle_data(self):
        """Return lifecycle information in management detail responses."""
        self.authenticate(self.support_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("lifecycle", response.data)
        self.assertIsInstance(response.data["lifecycle"], dict)

    def test_management_detail_returns_event_history(self):
        """Return event history in management detail responses."""
        self.authenticate(self.support_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("events", response.data)
        self.assertEqual(len(response.data["events"]), 2)

        event_types = [item["event_type"] for item in response.data["events"]]
        self.assertIn(ReviewEvent.TYPE_CREATED, event_types)
        self.assertIn(ReviewEvent.TYPE_APPROVED, event_types)

    def test_management_detail_returns_nested_customer_data(self):
        """Return nested customer data in management detail responses."""
        self.authenticate(self.support_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["customer"]["id"],
            self.customer.id,
        )
        self.assertEqual(
            response.data["customer"]["user_name"],
            "Customer User",
        )

    def test_management_detail_returns_nested_product_data(self):
        """Return nested product data in management detail responses."""
        self.authenticate(self.support_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["product"]["id"],
            str(self.product.id),
        )
        self.assertEqual(
            response.data["product"]["name"],
            "Gaming Headset Pro",
        )