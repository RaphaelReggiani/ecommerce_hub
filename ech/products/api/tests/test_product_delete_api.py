from decimal import Decimal

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework import status

from ech.products.models import Product
from ech.products.constants.constants import ProductType

from ech.users.constants.constants import (
    CORPORATE_EMAIL_DOMAIN,
)

from ech.users.models import CustomUser


User = get_user_model()


class ProductDeleteAPITestCase(APITestCase):

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
            product_type=ProductType.CHOICES[0][0],
            brand="LG",
            sold_by=self.manager,
            description="Monitor",
            technical_information="144Hz",
            price=Decimal("1500.00"),
        )

    def test_delete_product_success(self):
        """
        Operations staff should be able to delete a product.
        """

        self.client.force_authenticate(self.manager)

        url = reverse("product-delete", args=[str(self.product.id)])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.product.refresh_from_db()

        self.assertFalse(self.product.is_active)

    def test_delete_product_forbidden(self):
        """
        Customer users cannot delete products.
        """

        self.client.force_authenticate(self.customer)

        url = reverse("product-delete", args=[str(self.product.id)])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_product_not_found(self):
        """
        Deleting a non-existing product should return 404.
        """

        self.client.force_authenticate(self.manager)

        fake_uuid = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

        url = reverse("product-delete", args=[fake_uuid])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_deleted_product_not_visible_in_list(self):
        """
        Soft deleted products should not appear in the product list.
        """

        self.client.force_authenticate(self.manager)

        self.product.is_active = False
        self.product.save()

        url = reverse("product-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        products = response.data["results"]

        product_ids = [p["id"] for p in products]

        self.assertNotIn(str(self.product.id), product_ids)

    def test_delete_product_idempotent(self):
        """
        Deleting the same product twice should not break the API.
        """

        self.client.force_authenticate(self.manager)

        url = reverse("product-delete", args=[str(self.product.id)])

        response1 = self.client.delete(url)
        response2 = self.client.delete(url)

        self.assertEqual(response1.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn(response2.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND])

    def test_deleted_product_not_accessible(self):
        """
        Soft deleted products should not be accessible via detail endpoint.
        """

        self.client.force_authenticate(self.manager)

        self.product.is_active = False
        self.product.save()

        url = reverse("product-detail", args=[str(self.product.id)])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)