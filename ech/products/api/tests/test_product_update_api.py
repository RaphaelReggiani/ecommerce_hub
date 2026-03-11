from decimal import Decimal

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework import status

from ech.products.models import Product

from ech.users.constants.constants import (
    CORPORATE_EMAIL_DOMAIN,
)

from ech.users.models import CustomUser


User = get_user_model()


class ProductUpdateAPITestCase(APITestCase):

    def setUp(self):

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

        self.product = Product.objects.create(
            name="Gaming Monitor",
            product_type=Product.PRODUCT_CHOICES[0][0],
            brand="LG",
            sold_by=self.manager,
            description="Monitor",
            technical_information="144Hz",
            price=Decimal("1500.00"),
        )

    def test_update_product_success(self):
        """
        Operations staff should be able to update a product.
        """

        self.client.force_authenticate(self.manager)

        url = reverse("product-update", args=[str(self.product.id)])

        data = {
            "name": "Gaming Monitor Pro",
            "brand": "LG UltraGear",
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.product.refresh_from_db()

        self.assertEqual(self.product.name, "Gaming Monitor Pro")
        self.assertEqual(self.product.brand, "LG UltraGear")

    def test_update_product_partial(self):
        """
        Partial update should modify only provided fields.
        """

        self.client.force_authenticate(self.manager)

        url = reverse("product-update", args=[str(self.product.id)])

        data = {
            "price": Decimal("1300.00"),
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.product.refresh_from_db()

        self.assertEqual(self.product.price, Decimal("1300.00"))

    def test_update_product_forbidden(self):
        """
        Customer users cannot update products.
        """

        self.client.force_authenticate(self.customer)

        url = reverse("product-update", args=[str(self.product.id)])

        data = {
            "name": "Invalid Update",
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_product_not_found(self):
        """
        Updating a non-existing product should return 404.
        """

        self.client.force_authenticate(self.manager)

        fake_uuid = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

        url = reverse("product-update", args=[fake_uuid])

        data = {
            "name": "Non Existing",
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_product_invalid_discount(self):
        """
        Discount price cannot be greater than product price.
        """

        self.client.force_authenticate(self.manager)

        url = reverse("product-update", args=[str(self.product.id)])

        data = {
            "price": Decimal("1000.00"),
            "discount_price": Decimal("1200.00"),
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_does_not_modify_unrelated_fields(self):
        """
        Updating one field should not change other product fields.
        """

        self.client.force_authenticate(self.manager)

        original_price = self.product.price

        url = reverse("product-update", args=[str(self.product.id)])

        response = self.client.patch(url, {"name": "Updated Name"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.product.refresh_from_db()

        self.assertEqual(self.product.name, "Updated Name")
        self.assertEqual(self.product.price, original_price)