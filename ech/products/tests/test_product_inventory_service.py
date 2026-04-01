from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from ech.products.exceptions import ProductOutOfStockError
from ech.products.models import Product, ProductInventory
from ech.products.services.product_inventory_service import decrease_inventory
from ech.users.models import CustomUser


class ProductInventoryServiceTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="inventory@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Inventory User",
        )

        self.product = Product.objects.create(
            name="Gaming Mouse",
            product_type=Product.MOUSE,
            brand="Logitech",
            sold_by=self.user,
            description="Gaming mouse",
            technical_information="Specs",
            price=Decimal("200.00"),
            is_active=True,
        )

        self.inventory = ProductInventory.objects.create(
            product=self.product,
            quantity=10,
        )

    def test_decrease_inventory_reduces_quantity_successfully(self):
        """Ensure decrease_inventory reduces inventory quantity correctly."""
        updated_inventory = decrease_inventory(
            product_id=self.product.id,
            quantity=3,
        )

        self.inventory.refresh_from_db()

        self.assertEqual(updated_inventory.quantity, 7)
        self.assertEqual(self.inventory.quantity, 7)

    def test_decrease_inventory_allows_exact_quantity_reduction(self):
        """Ensure decrease_inventory allows reducing inventory to zero."""
        updated_inventory = decrease_inventory(
            product_id=self.product.id,
            quantity=10,
        )

        self.inventory.refresh_from_db()

        self.assertEqual(updated_inventory.quantity, 0)
        self.assertEqual(self.inventory.quantity, 0)

    def test_decrease_inventory_raises_error_when_insufficient_stock(self):
        """Ensure decrease_inventory raises ProductOutOfStockError when quantity is insufficient."""
        with self.assertRaises(ProductOutOfStockError):
            decrease_inventory(
                product_id=self.product.id,
                quantity=11,
            )

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 10)

    def test_decrease_inventory_returns_inventory_instance(self):
        """Ensure decrease_inventory returns updated inventory instance."""
        updated_inventory = decrease_inventory(
            product_id=self.product.id,
            quantity=2,
        )

        self.assertEqual(updated_inventory.product, self.product)
        self.assertEqual(updated_inventory.quantity, 8)

    def test_decrease_inventory_persists_changes_in_database(self):
        """Ensure decrease_inventory persists changes in database."""
        decrease_inventory(
            product_id=self.product.id,
            quantity=4,
        )

        refreshed_inventory = ProductInventory.objects.get(product=self.product)

        self.assertEqual(refreshed_inventory.quantity, 6)

    @patch("ech.products.services.product_inventory_service.invalidate_product_list_cache")
    @patch("ech.products.services.product_inventory_service.invalidate_product_cache")
    def test_decrease_inventory_invalidates_related_caches(
        self,
        invalidate_product_cache_mock,
        invalidate_product_list_cache_mock,
    ):
        """Ensure decrease_inventory invalidates product and list caches after stock mutation."""
        decrease_inventory(
            product_id=self.product.id,
            quantity=2,
        )

        invalidate_product_cache_mock.assert_called_once_with(self.product.id)
        invalidate_product_list_cache_mock.assert_called_once()

    def test_decrease_inventory_raises_error_when_inventory_does_not_exist(self):
        """Ensure decrease_inventory raises DoesNotExist when inventory is missing."""
        ProductInventory.objects.filter(product=self.product).delete()

        with self.assertRaises(ProductInventory.DoesNotExist):
            decrease_inventory(
                product_id=self.product.id,
                quantity=1,
            )