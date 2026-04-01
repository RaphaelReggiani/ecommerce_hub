import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.products.models import Product
from ech.users.constants.constants import (
    CORPORATE_EMAIL_DOMAIN,
)
from ech.users.models import (
    CustomUser,
)

User = get_user_model()


class ProductCreateAPITestCase(APITestCase):
    def setUp(self):
        self.url = reverse("products-api:product-create")

        self.manager = User.objects.create_user(
            email=f"ops{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            user_name="ops_user",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
        )

        self.customer = User.objects.create_user(
            email="customer@gmail.com",
            password="StrongPassword123",
            user_name="customer_user",
            role=CustomUser.ROLE_CUSTOMER_USER,
        )

        self.payload = {
            "name": "Gaming Mouse",
            "product_type": Product.PRODUCT_CHOICES[0][0],
            "brand": "Logitech",
            "description": "Gaming mouse",
            "technical_information": "16000 DPI",
            "price": "200.00",
            "discount_price": "150.00",
            "inventory": 10,
        }

    def test_create_product_success(self):
        """Create product successfully when performed by operations staff."""
        self.client.force_authenticate(self.manager)

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(response.data["name"], self.payload["name"])
        self.assertEqual(response.data["brand"], self.payload["brand"])

    def test_create_product_success_with_idempotency_key(self):
        """Create product successfully with Idempotency-Key header."""
        self.client.force_authenticate(self.manager)

        response = self.client.post(
            self.url,
            self.payload,
            format="json",
            HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)

        product = Product.objects.get()
        self.assertIsNotNone(product.idempotency_key)
        self.assertIsNotNone(product.idempotency_request_hash)

    def test_create_product_with_same_idempotency_key_and_same_payload_returns_same_product(self):
        """Ensure repeated requests with same idempotency key return the same product."""
        self.client.force_authenticate(self.manager)

        idempotency_key = str(uuid.uuid4())

        first_response = self.client.post(
            self.url,
            self.payload,
            format="json",
            HTTP_IDEMPOTENCY_KEY=idempotency_key,
        )

        second_response = self.client.post(
            self.url,
            self.payload,
            format="json",
            HTTP_IDEMPOTENCY_KEY=idempotency_key,
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(first_response.data["id"], second_response.data["id"])

    def test_create_product_with_same_idempotency_key_and_different_payload_returns_conflict(self):
        """Ensure reused idempotency key with different payload returns 409 conflict."""
        self.client.force_authenticate(self.manager)

        idempotency_key = str(uuid.uuid4())

        first_response = self.client.post(
            self.url,
            self.payload,
            format="json",
            HTTP_IDEMPOTENCY_KEY=idempotency_key,
        )

        conflicting_payload = self.payload.copy()
        conflicting_payload["name"] = "Different Gaming Mouse"

        second_response = self.client.post(
            self.url,
            conflicting_payload,
            format="json",
            HTTP_IDEMPOTENCY_KEY=idempotency_key,
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(Product.objects.count(), 1)

    def test_create_product_forbidden_for_customer(self):
        """Deny product creation for customer users."""
        self.client.force_authenticate(self.customer)

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_invalid_discount(self):
        """Reject product creation when discount price exceeds product price."""
        self.client.force_authenticate(self.manager)

        payload = self.payload.copy()
        payload["discount_price"] = "300.00"

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_extreme_price_validation(self):
        """API should reject unrealistic product prices."""
        self.client.force_authenticate(self.manager)

        data = {
            "name": "Extreme Product",
            "product_type": Product.PRODUCT_CHOICES[0][0],
            "brand": "Test",
            "description": "Test",
            "technical_information": "Test",
            "price": "999999999999.99",
            "inventory": 10,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)