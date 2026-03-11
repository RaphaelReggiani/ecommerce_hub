from decimal import Decimal

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework import status

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

        self.url = reverse("product-create")

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

        self.client.force_authenticate(self.manager)

        response = self.client.post(self.url, self.payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)

    def test_create_product_forbidden_for_customer(self):

        self.client.force_authenticate(self.customer)

        response = self.client.post(self.url, self.payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_invalid_discount(self):

        self.client.force_authenticate(self.manager)

        self.payload["discount_price"] = "300.00"

        response = self.client.post(self.url, self.payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_extreme_price_validation(self):
        """
        API should reject unrealistic product prices.
        """

        self.client.force_authenticate(self.manager)

        url = reverse("product-create")

        data = {
            "name": "Extreme Product",
            "product_type": Product.PRODUCT_CHOICES[0][0],
            "brand": "Test",
            "description": "Test",
            "technical_information": "Test",
            "price": "999999999999.99",
            "inventory": 10,
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)