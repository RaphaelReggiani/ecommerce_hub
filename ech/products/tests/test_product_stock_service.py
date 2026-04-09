from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from ech.products.constants.messages import (
    MSG_ERROR_STOCK_NOT_ENOUGH_STOCK_AVAILABLE,
)
from ech.products.models import Product, ProductInventory
from ech.products.services.product_stock_service import (
    OutOfStockError,
    get_available_stock,
    release_stock,
    reserve_stock,
)
from ech.users.models import CustomUser


class ProductStockServiceTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            email="stock@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Stock User",
        )

        cls.product = Product.objects.create(
            name="Gaming Mouse",
            product_type=Product.MOUSE,
            brand="Logitech",
            sold_by=cls.user,
            description="Gaming mouse",
            technical_information="Specs",
            price=Decimal("200.00"),
            is_active=True,
        )

        cls.inventory = ProductInventory.objects.create(
            product=cls.product,
            quantity=10,
        )

    def test_get_available_stock_returns_inventory_quantity(self):
        """Ensure get_available_stock returns the current available quantity."""
        available_stock = get_available_stock(self.product.id)

        self.assertEqual(available_stock, 10)

    def test_reserve_stock_reduces_quantity_successfully(self):
        """Ensure reserve_stock reduces inventory quantity correctly."""
        updated_inventory = reserve_stock(self.product.id, 3)

        self.inventory.refresh_from_db()

        self.assertEqual(updated_inventory.quantity, 7)
        self.assertEqual(self.inventory.quantity, 7)

    def test_reserve_stock_allows_exact_quantity_reduction(self):
        """Ensure reserve_stock allows reducing stock exactly to zero."""
        updated_inventory = reserve_stock(self.product.id, 10)

        self.inventory.refresh_from_db()

        self.assertEqual(updated_inventory.quantity, 0)
        self.assertEqual(self.inventory.quantity, 0)

    def test_reserve_stock_raises_out_of_stock_error_when_quantity_is_insufficient(self):
        """Ensure reserve_stock raises OutOfStockError when stock is insufficient."""
        with self.assertRaises(OutOfStockError) as context:
            reserve_stock(self.product.id, 11)

        self.inventory.refresh_from_db()

        self.assertEqual(str(context.exception), MSG_ERROR_STOCK_NOT_ENOUGH_STOCK_AVAILABLE)
        self.assertEqual(self.inventory.quantity, 10)

    def test_reserve_stock_returns_inventory_instance(self):
        """Ensure reserve_stock returns the updated inventory instance."""
        updated_inventory = reserve_stock(self.product.id, 2)

        self.assertEqual(updated_inventory.product, self.product)
        self.assertEqual(updated_inventory.quantity, 8)

    @patch("ech.products.services.product_stock_service.invalidate_product_list_cache")
    @patch("ech.products.services.product_stock_service.invalidate_product_cache")
    def test_reserve_stock_invalidates_related_caches(
        self,
        invalidate_product_cache_mock,
        invalidate_product_list_cache_mock,
    ):
        """Ensure reserve_stock invalidates product and product list caches."""
        reserve_stock(self.product.id, 2)

        invalidate_product_cache_mock.assert_called_once_with(self.product.id)
        invalidate_product_list_cache_mock.assert_called_once()

    def test_release_stock_increases_quantity_successfully(self):
        """Ensure release_stock increases inventory quantity correctly."""
        updated_inventory = release_stock(self.product.id, 4)

        self.inventory.refresh_from_db()

        self.assertEqual(updated_inventory.quantity, 14)
        self.assertEqual(self.inventory.quantity, 14)

    def test_release_stock_returns_inventory_instance(self):
        """Ensure release_stock returns the updated inventory instance."""
        updated_inventory = release_stock(self.product.id, 5)

        self.assertEqual(updated_inventory.product, self.product)
        self.assertEqual(updated_inventory.quantity, 15)

    @patch("ech.products.services.product_stock_service.invalidate_product_list_cache")
    @patch("ech.products.services.product_stock_service.invalidate_product_cache")
    def test_release_stock_invalidates_related_caches(
        self,
        invalidate_product_cache_mock,
        invalidate_product_list_cache_mock,
    ):
        """Ensure release_stock invalidates product and product list caches."""
        release_stock(self.product.id, 3)

        invalidate_product_cache_mock.assert_called_once_with(self.product.id)
        invalidate_product_list_cache_mock.assert_called_once()

    def test_get_available_stock_raises_does_not_exist_when_inventory_is_missing(self):
        """Ensure get_available_stock raises DoesNotExist when inventory is missing."""
        ProductInventory.objects.filter(product=self.product).delete()

        with self.assertRaises(ProductInventory.DoesNotExist):
            get_available_stock(self.product.id)

    def test_reserve_stock_raises_does_not_exist_when_inventory_is_missing(self):
        """Ensure reserve_stock raises DoesNotExist when inventory is missing."""
        ProductInventory.objects.filter(product=self.product).delete()

        with self.assertRaises(ProductInventory.DoesNotExist):
            reserve_stock(self.product.id, 1)

    def test_release_stock_raises_does_not_exist_when_inventory_is_missing(self):
        """Ensure release_stock raises DoesNotExist when inventory is missing."""
        ProductInventory.objects.filter(product=self.product).delete()

        with self.assertRaises(ProductInventory.DoesNotExist):
            release_stock(self.product.id, 1)