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


class ProductDetailAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email=f"ops{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            user_name="ops_user",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
        )

        cls.product = Product.objects.create(
            name="Gaming Headset",
            product_type=Product.PRODUCT_CHOICES[0][0],
            brand="HyperX",
            sold_by=cls.user,
            description="Headset",
            technical_information="7.1 Surround",
            price=Decimal("400.00"),
        )

        cls.product_detail_url = reverse(
            "products-api:product-detail",
            args=[str(cls.product.id)],
        )

    def test_product_detail_success(self):
        """Return product detail successfully when product exists."""

        response = self.client.get(self.product_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_detail_not_found(self):
        """Return 404 when requested product does not exist."""

        url = reverse(
            "products-api:product-detail",
            args=["00000000-0000-0000-0000-000000000000"],
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)