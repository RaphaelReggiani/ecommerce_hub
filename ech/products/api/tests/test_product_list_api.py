from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
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


class ProductListAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email=f"ops{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            user_name="ops_user",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            is_active=True,
            email_confirmed=True,
        )
        cls.product_list_url = reverse("products-api:product-list")

    def setUp(self):
        cache.clear()

        Product.objects.create(
            name="Keyboard",
            product_type=Product.PRODUCT_CHOICES[0][0],
            brand="Razer",
            sold_by=self.user,
            description="Keyboard",
            technical_information="RGB",
            price=Decimal("300.00"),
            is_active=True,
        )

        Product.objects.create(
            name="Inactive Product",
            product_type=Product.PRODUCT_CHOICES[0][0],
            brand="Test",
            sold_by=self.user,
            description="Test",
            technical_information="Test",
            price=Decimal("100.00"),
            is_active=False,
        )

    def test_list_products_is_public_and_returns_only_active_products(self):
        """Ensure public product listing returns only active products."""
        response = self.client.get(self.product_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        products = response.data["results"]

        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]["name"], "Keyboard")

    def test_product_list_allows_unauthenticated_access(self):
        """API should allow unauthenticated access to the public product list."""
        response = self.client.get(self.product_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_list_pagination_consistency(self):
        """Pagination should not duplicate products across pages."""
        for i in range(30):
            Product.objects.create(
                name=f"Product {i}",
                product_type=Product.PRODUCT_CHOICES[0][0],
                brand="Test",
                sold_by=self.user,
                description="Test",
                technical_information="Test",
                price=Decimal("100.00"),
                is_active=True,
            )

        page1 = self.client.get(f"{self.product_list_url}?page=1")
        page2 = self.client.get(f"{self.product_list_url}?page=2")

        self.assertEqual(page1.status_code, status.HTTP_200_OK)
        self.assertEqual(page2.status_code, status.HTTP_200_OK)

        ids_page1 = {p["id"] for p in page1.data["results"]}
        ids_page2 = {p["id"] for p in page2.data["results"]}

        self.assertTrue(ids_page1.isdisjoint(ids_page2))