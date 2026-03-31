import uuid

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import (
    CustomUser
)
from ech.products.models import (
    Product
)
from ech.reviews.models import (
    Review,
    ReviewLifecycle,
)


class ReviewManagementListApiTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("reviews-api:review-management-list")

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

        self.product_one = self._create_product(
            name="Gaming Headset",
            product_type=Product.HEADSET,
        )
        self.product_two = self._create_product(
            name="Mechanical Keyboard",
            product_type=Product.KEYBOARD,
        )

        self.review_one = self._create_review(
            customer=self.customer,
            product=self.product_one,
            rating=5,
            status=Review.REVIEW_STATUS_PENDING,
            title="Excellent headset",
            is_verified_purchase=True,
        )

        self.review_two = self._create_review(
            customer=self.other_customer,
            product=self.product_two,
            rating=3,
            status=Review.REVIEW_STATUS_APPROVED,
            title="Average keyboard",
            is_verified_purchase=False,
            moderated_by=self.support_staff,
        )

    def authenticate(self, user):
        """Authenticate the API client with the provided user."""
        self.client.force_authenticate(user=user)

    def _create_product(self, *, name, product_type):
        """Create a minimal product instance for management review tests."""
        return Product.objects.create(
            name=name,
            product_type=product_type,
            brand="TechBrand",
            sold_by=self.seller,
            description=f"{name} description.",
            technical_information=f"{name} technical details.",
            price="299.90",
            discount_price="249.90",
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
        is_verified_purchase,
        moderated_by=None,
    ):
        """Create a minimal review instance with lifecycle."""
        review = Review.objects.create(
            customer=customer,
            product=product,
            rating=rating,
            title=title,
            comment="Management review comment",
            idempotency_key=uuid.uuid4(),
            status=status,
            is_verified_purchase=is_verified_purchase,
            moderated_by=moderated_by,
        )

        ReviewLifecycle.objects.create(review=review)
        return review

    def test_management_list_requires_authentication(self):
        """Reject management review listing for unauthenticated users."""
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_management_list_rejects_customer_user(self):
        """Reject management review listing for customer users."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_management_list_allows_support_staff(self):
        """Allow support staff to access the management review list."""
        self.authenticate(self.support_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_management_list_allows_admin(self):
        """Allow admin users to access the management review list."""
        self.authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_management_list_returns_all_reviews_for_authorized_staff(self):
        """Return all reviews in the management list for authorized staff users."""
        self.authenticate(self.support_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        review_ids = [item["id"] for item in response.data["results"]]

        self.assertIn(str(self.review_one.id), review_ids)
        self.assertIn(str(self.review_two.id), review_ids)

    def test_management_list_supports_status_filter(self):
        """Filter management reviews by status."""
        self.authenticate(self.support_staff)

        response = self.client.get(self.url, {"status": Review.REVIEW_STATUS_PENDING})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.review_one.id),
        )

    def test_management_list_supports_rating_filter(self):
        """Filter management reviews by exact rating."""
        self.authenticate(self.support_staff)

        response = self.client.get(self.url, {"rating": 3})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.review_two.id),
        )

    def test_management_list_supports_product_filter(self):
        """Filter management reviews by product identifier."""
        self.authenticate(self.support_staff)

        response = self.client.get(
            self.url,
            {"product_id": str(self.product_one.id)},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.review_one.id),
        )

    def test_management_list_supports_customer_filter(self):
        """Filter management reviews by customer identifier."""
        self.authenticate(self.support_staff)

        response = self.client.get(
            self.url,
            {"customer_id": self.other_customer.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.review_two.id),
        )

    def test_management_list_supports_verified_purchase_filter(self):
        """Filter management reviews by verified purchase flag."""
        self.authenticate(self.support_staff)

        response = self.client.get(
            self.url,
            {"is_verified_purchase": True},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.review_one.id),
        )

    def test_management_list_supports_moderated_by_filter(self):
        """Filter management reviews by moderator identifier."""
        self.authenticate(self.support_staff)

        response = self.client.get(
            self.url,
            {"moderated_by_id": self.support_staff.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.review_two.id),
        )

    def test_management_list_supports_pagination_structure(self):
        """Return paginated response structure for management list."""
        self.authenticate(self.support_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

    def test_management_list_response_contains_expected_fields(self):
        """Ensure management list responses contain expected fields."""
        self.authenticate(self.support_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        review_data = response.data["results"][0]

        self.assertIn("id", review_data)
        self.assertIn("customer", review_data)
        self.assertIn("product", review_data)
        self.assertIn("rating", review_data)
        self.assertIn("title", review_data)
        self.assertIn("status", review_data)
        self.assertIn("is_verified_purchase", review_data)
        self.assertIn("moderated_by", review_data)
        self.assertIn("moderated_by_name", review_data)
        self.assertIn("moderated_by_email", review_data)
        self.assertIn("moderated_at", review_data)
        self.assertIn("created_at", review_data)
        self.assertIn("updated_at", review_data)