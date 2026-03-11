from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from ech.products.models import (
    Product, 
    ProductInventory,
)
from ech.products.services.product_inventory_service import decrease_inventory

from ech.users.models import (
    CustomUser,
)

from ech.products.exceptions import ProductOutOfStockError
from ech.users.constants.constants import (
    CORPORATE_EMAIL_DOMAIN,
)


User = get_user_model()


class ProductInventoryServiceTestCase(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            email=f"ops{CORPORATE_EMAIL_DOMAIN}",
            password="StrongPassword123",
            user_name="ops_user",
            role=CustomUser.ROLE_OPERATIONS_STAFF
        )

        self.product = Product.objects.create(
            name="Gaming Mouse",
            product_type=Product.PRODUCT_CHOICES[0][0],
            brand="Logitech",
            sold_by=self.user,
            description="Gaming mouse",
            technical_information="16000 DPI",
            price=Decimal("200.00"),
        )

        self.inventory = ProductInventory.objects.create(
            product=self.product,
            quantity=10
        )

    def test_decrease_inventory_success(self):
        """
        Inventory should decrease correctly.
        """

        decrease_inventory(
            product_id=self.product.id,
            quantity=3
        )

        self.inventory.refresh_from_db()

        self.assertEqual(self.inventory.quantity, 7)

    def test_decrease_inventory_exact_stock(self):
        """
        Should allow decreasing entire stock.
        """

        decrease_inventory(
            product_id=self.product.id,
            quantity=10
        )

        self.inventory.refresh_from_db()

        self.assertEqual(self.inventory.quantity, 0)

    def test_decrease_inventory_insufficient_stock(self):
        """
        Should raise error when stock is insufficient.
        """

        with self.assertRaises(ProductOutOfStockError):

            decrease_inventory(
                product_id=self.product.id,
                quantity=20
            )

        self.inventory.refresh_from_db()

        self.assertEqual(self.inventory.quantity, 10)

    def test_decrease_inventory_does_not_go_negative(self):
        """
        Inventory must never become negative.
        """

        with self.assertRaises(ProductOutOfStockError):

            decrease_inventory(
                product_id=self.product.id,
                quantity=11
            )

        self.inventory.refresh_from_db()

        self.assertGreaterEqual(self.inventory.quantity, 0)

    def test_inventory_unchanged_after_exception(self):
        """
        Transaction should rollback on failure.
        """

        try:
            decrease_inventory(
                product_id=self.product.id,
                quantity=100
            )
        except ProductOutOfStockError:
            pass

        self.inventory.refresh_from_db()

        self.assertEqual(self.inventory.quantity, 10)