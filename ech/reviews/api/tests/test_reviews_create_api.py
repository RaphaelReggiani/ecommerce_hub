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


class ReviewCreateApiTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("reviews-api:review-create")

        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.other_customer = CustomUser.objects.create_user(
            email="othercustomer@test.com",
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

        self.product = self._create_product(sold_by=self.admin)

    def authenticate(self, user):
        """Authenticate the current API client with the given user."""
        self.client.force_authenticate(user=user)

    def _create_product(self, *, sold_by):
        """Create a minimal valid product instance for review API tests."""
        return Product.objects.create(
            name="Gaming Headset X",
            product_type=Product.HEADSET,
            brand="AudioTech",
            sold_by=sold_by,
            description="High-quality gaming headset.",
            technical_information="Wireless, surround, low latency.",
            price="499.90",
            discount_price="449.90",
            is_active=True,
        )

    def _build_payload(self, **overrides):
        """Build a valid payload for review creation requests."""
        payload = {
            "product_id": str(self.product.id),
            "rating": 5,
            "title": "Excellent headset",
            "comment": "Sound quality is great and battery life is solid.",
            "idempotency_key": str(uuid.uuid4()),
            "is_verified_purchase": False,
        }
        payload.update(overrides)
        return payload

    def test_create_review_returns_unauthorized_for_unauthenticated_user(self):
        """Reject review creation for unauthenticated users."""
        payload = self._build_payload()

        response = self.client.post(self.url, payload, format="json")

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )
        self.assertEqual(Review.objects.count(), 0)

    def test_create_review_successfully_as_authenticated_customer(self):
        """Allow an authenticated customer to create a review successfully."""
        self.authenticate(self.customer)
        payload = self._build_payload()

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)

        review = Review.objects.select_related(
            "customer",
            "product",
            "lifecycle",
        ).get()

        self.assertEqual(review.customer, self.customer)
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.title, "Excellent headset")
        self.assertEqual(
            review.comment,
            "Sound quality is great and battery life is solid.",
        )
        self.assertEqual(review.status, Review.REVIEW_STATUS_PENDING)
        self.assertFalse(review.is_verified_purchase)
        self.assertEqual(
            str(review.idempotency_key),
            payload["idempotency_key"],
        )

        self.assertTrue(
            ReviewLifecycle.objects.filter(review=review).exists()
        )
        self.assertTrue(
            ReviewEvent.objects.filter(
                review=review,
                event_type=ReviewEvent.TYPE_CREATED,
            ).exists()
        )

        self.assertEqual(response.data["id"], str(review.id))
        self.assertEqual(response.data["status"], Review.REVIEW_STATUS_PENDING)
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["title"], "Excellent headset")

    def test_create_review_allows_staff_user_if_authenticated(self):
        """Allow any authenticated user to create a review under the current API rules."""
        self.authenticate(self.admin)
        payload = self._build_payload()

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)

        review = Review.objects.get()
        self.assertEqual(review.customer, self.admin)

    def test_create_review_rejects_invalid_product(self):
        """Reject review creation when the referenced product does not exist."""
        self.authenticate(self.customer)
        payload = self._build_payload(product_id=str(uuid.uuid4()))

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 0)

    def test_create_review_rejects_rating_below_minimum(self):
        """Reject review creation when rating is below the allowed minimum."""
        self.authenticate(self.customer)
        payload = self._build_payload(rating=0)

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 0)

    def test_create_review_rejects_rating_above_maximum(self):
        """Reject review creation when rating is above the allowed maximum."""
        self.authenticate(self.customer)
        payload = self._build_payload(rating=6)

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 0)

    def test_create_review_rejects_duplicate_review_for_same_customer_and_product(self):
        """Reject a second review for the same customer and product."""
        self.authenticate(self.customer)

        first_payload = self._build_payload()
        first_response = self.client.post(self.url, first_payload, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)

        second_payload = self._build_payload(idempotency_key=str(uuid.uuid4()))
        response = self.client.post(self.url, second_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 1)

    def test_create_review_is_idempotent_for_repeated_requests(self):
        """Return the existing review for repeated requests with the same idempotency key."""
        self.authenticate(self.customer)

        idem_key = str(uuid.uuid4())
        payload = self._build_payload(idempotency_key=idem_key)

        first_response = self.client.post(self.url, payload, format="json")
        second_response = self.client.post(self.url, payload, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)

        review = Review.objects.get()
        self.assertEqual(str(review.idempotency_key), idem_key)
        self.assertEqual(first_response.data["id"], second_response.data["id"])

    def test_create_review_allows_same_product_for_different_customers(self):
        """Allow different customers to create one review each for the same product."""
        first_payload = self._build_payload()

        self.authenticate(self.customer)
        first_response = self.client.post(self.url, first_payload, format="json")

        self.client.force_authenticate(user=None)

        self.authenticate(self.other_customer)
        second_payload = self._build_payload(idempotency_key=str(uuid.uuid4()))
        second_response = self.client.post(self.url, second_payload, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 2)

    def test_create_review_rejects_missing_required_fields(self):
        """Reject review creation when required fields are missing."""
        self.authenticate(self.customer)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 0)

    def test_create_review_persists_verified_purchase_flag_when_provided(self):
        """Persist the verified purchase flag when it is explicitly provided in the payload."""
        self.authenticate(self.customer)
        payload = self._build_payload(is_verified_purchase=True)

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)

        review = Review.objects.get()
        self.assertTrue(review.is_verified_purchase)
        self.assertTrue(response.data["is_verified_purchase"])