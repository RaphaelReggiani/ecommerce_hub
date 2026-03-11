from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from ech.products.models import (
    Product, 
    ProductInventory,
)
from ech.products.selectors import (
    get_product_by_id,
    get_active_product_by_id,
    get_all_active_products,
    get_products_by_type,
    get_products_with_discount,
    search_products,
    get_products_created_by_user,
    get_available_products,
)


User = get_user_model()


class ProductSelectorsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="seller@test.com",
            password="StrongPassword123",
            user_name="seller"
        )

        self.product_active = Product.objects.create(
            name="Gaming Mouse",
            product_type=Product.PRODUCT_CHOICES[0][0],
            brand="Logitech",
            sold_by=self.user,
            description="Gaming mouse",
            technical_information="16000 DPI",
            price=Decimal("200.00"),
            is_active=True
        )

        self.product_inactive = Product.objects.create(
            name="Old Mouse",
            product_type=Product.PRODUCT_CHOICES[0][0],
            brand="Generic",
            sold_by=self.user,
            description="Old model",
            technical_information="Basic",
            price=Decimal("50.00"),
            is_active=False
        )

        self.product_discount = Product.objects.create(
            name="Gaming Keyboard",
            product_type=Product.PRODUCT_CHOICES[0][0],
            brand="Corsair",
            sold_by=self.user,
            description="Mechanical keyboard",
            technical_information="RGB",
            price=Decimal("500.00"),
            discount_price=Decimal("400.00"),
            is_active=True
        )

    def test_get_product_by_id(self):
        """Should return product regardless of active status."""
        product = get_product_by_id(self.product_active.id)

        self.assertIsNotNone(product)
        self.assertEqual(product.id, self.product_active.id)

    def test_get_product_by_id_not_found(self):
        """Should return None if product does not exist."""
        product = get_product_by_id(999)

        self.assertIsNone(product)

    def test_get_active_product_by_id(self):
        """Should return only active products."""
        product = get_active_product_by_id(self.product_active.id)

        self.assertIsNotNone(product)
        self.assertEqual(product.id, self.product_active.id)

    def test_get_active_product_by_id_inactive(self):
        """Inactive product should return None."""
        product = get_active_product_by_id(self.product_inactive.id)

        self.assertIsNone(product)

    def test_get_all_active_products(self):
        """Should return only active products."""
        products = get_all_active_products()

        self.assertEqual(products.count(), 2)

    def test_get_products_by_type(self):
        """Should filter active products by type."""
        products = get_products_by_type(self.product_active.product_type)

        self.assertEqual(products.count(), 2)

    def test_get_products_with_discount(self):
        """Should return products that have discount_price."""
        products = get_products_with_discount()

        self.assertEqual(products.count(), 1)
        self.assertEqual(products.first().id, self.product_discount.id)

    def test_search_products_by_name(self):
        """Search should match product name."""
        results = search_products("mouse")

        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().id, self.product_active.id)

    def test_search_products_by_brand(self):
        """Search should match product brand."""
        results = search_products("corsair")

        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().id, self.product_discount.id)

    def test_search_products_excludes_inactive(self):
        """Search should exclude inactive products."""
        results = search_products("old")

        self.assertEqual(results.count(), 0)

    def test_get_products_created_by_user(self):
        """Should return products created by specific user."""
        products = get_products_created_by_user(self.user)

        self.assertEqual(products.count(), 3)

    def test_get_available_products(self):
        """Should return only products with inventory > 0."""

        ProductInventory.objects.create(
            product=self.product_active,
            quantity=10
        )

        ProductInventory.objects.create(
            product=self.product_discount,
            quantity=0
        )

        products = get_available_products()

        self.assertEqual(products.count(), 1)
        self.assertEqual(products.first().id, self.product_active.id)