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

    def setUp(self):

        self.user = User.objects.create_user(
            email=f"ops{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            user_name="ops_user",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
        )

        self.product = Product.objects.create(
            name="Gaming Headset",
            product_type=Product.PRODUCT_CHOICES[0][0],
            brand="HyperX",
            sold_by=self.user,
            description="Headset",
            technical_information="7.1 Surround",
            price=Decimal("400.00"),
        )

    def test_product_detail_success(self):

        url = reverse("product-detail", args=[str(self.product.id)])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_detail_not_found(self):

        url = reverse("product-detail", args=["00000000-0000-0000-0000-000000000000"])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)