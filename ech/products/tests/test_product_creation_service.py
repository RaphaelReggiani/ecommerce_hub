from decimal import Decimal

from django.test import TestCase

from ech.users.models import CustomUser
from ech.products.models import Product, ProductInventory
from ech.products.services.product_creation_service import create_product
from ech.products.exceptions import (
    ProductCreationPermissionDeniedError,
    InvalidProductTypeError,
    InvalidProductPriceError,
    InvalidDiscountPriceError,
    InvalidInventoryValueError,
)


class ProductCreationServiceTestCase(TestCase):
    def setUp(self):
        self.allowed_user = CustomUser.objects.create_user(
            email="staff@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Staff User",
        )

        self.disallowed_user = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_CUSTOMER_USER,
            user_name="Customer User",
        )

        self.valid_payload = {
            "name": "Gaming Mouse",
            "product_type": Product.MOUSE,
            "brand": "Logitech",
            "description": "Gaming mouse",
            "technical_information": "Specs",
            "price": Decimal("200.00"),
            "discount_price": Decimal("150.00"),
            "inventory": 10,
        }

    def test_create_product_successfully_creates_product_and_inventory(self):
        """Ensure create_product creates product and inventory successfully."""
        product = create_product(
            user=self.allowed_user,
            **self.valid_payload,
        )

        self.assertIsInstance(product, Product)
        self.assertEqual(product.name, "Gaming Mouse")
        self.assertEqual(product.sold_by, self.allowed_user)

        inventory = ProductInventory.objects.get(product=product)
        self.assertEqual(inventory.quantity, 10)

    def test_create_product_with_no_discount_creates_product_successfully(self):
        """Ensure create_product works when discount_price is None."""
        payload = self.valid_payload.copy()
        payload["discount_price"] = None

        product = create_product(
            user=self.allowed_user,
            **payload,
        )

        self.assertIsNone(product.discount_price)

    def test_create_product_with_zero_inventory(self):
        """Ensure create_product allows zero inventory."""
        payload = self.valid_payload.copy()
        payload["inventory"] = 0

        product = create_product(
            user=self.allowed_user,
            **payload,
        )

        inventory = ProductInventory.objects.get(product=product)
        self.assertEqual(inventory.quantity, 0)

    def test_create_product_raises_permission_error_for_invalid_user(self):
        """Ensure create_product raises error when user has no permission."""
        with self.assertRaises(ProductCreationPermissionDeniedError):
            create_product(
                user=self.disallowed_user,
                **self.valid_payload,
            )

    def test_create_product_raises_invalid_product_type_error(self):
        """Ensure invalid product type raises InvalidProductTypeError."""
        payload = self.valid_payload.copy()
        payload["product_type"] = "INVALID_TYPE"

        with self.assertRaises(InvalidProductTypeError):
            create_product(
                user=self.allowed_user,
                **payload,
            )

    def test_create_product_raises_invalid_price_when_none(self):
        """Ensure None price raises InvalidProductPriceError."""
        payload = self.valid_payload.copy()
        payload["price"] = None

        with self.assertRaises(InvalidProductPriceError):
            create_product(
                user=self.allowed_user,
                **payload,
            )

    def test_create_product_raises_invalid_price_when_zero_or_negative(self):
        """Ensure zero or negative price raises InvalidProductPriceError."""
        for invalid_price in [0, -10]:
            payload = self.valid_payload.copy()
            payload["price"] = invalid_price

            with self.assertRaises(InvalidProductPriceError):
                create_product(
                    user=self.allowed_user,
                    **payload,
                )

    def test_create_product_raises_invalid_discount_when_negative(self):
        """Ensure negative discount raises InvalidDiscountPriceError."""
        payload = self.valid_payload.copy()
        payload["discount_price"] = Decimal("-10.00")

        with self.assertRaises(InvalidDiscountPriceError):
            create_product(
                user=self.allowed_user,
                **payload,
            )

    def test_create_product_raises_invalid_discount_when_greater_or_equal_price(self):
        """Ensure discount >= price raises InvalidDiscountPriceError."""
        for discount in [Decimal("200.00"), Decimal("250.00")]:
            payload = self.valid_payload.copy()
            payload["discount_price"] = discount

            with self.assertRaises(InvalidDiscountPriceError):
                create_product(
                    user=self.allowed_user,
                    **payload,
                )

    def test_create_product_raises_invalid_inventory_when_negative(self):
        """Ensure negative inventory raises InvalidInventoryValueError."""
        payload = self.valid_payload.copy()
        payload["inventory"] = -1

        with self.assertRaises(InvalidInventoryValueError):
            create_product(
                user=self.allowed_user,
                **payload,
            )

    def test_create_product_does_not_create_anything_on_failure(self):
        """Ensure transaction is rolled back when validation fails."""
        payload = self.valid_payload.copy()
        payload["inventory"] = -5  # vai falhar

        initial_product_count = Product.objects.count()
        initial_inventory_count = ProductInventory.objects.count()

        with self.assertRaises(InvalidInventoryValueError):
            create_product(
                user=self.allowed_user,
                **payload,
            )

        self.assertEqual(Product.objects.count(), initial_product_count)
        self.assertEqual(ProductInventory.objects.count(), initial_inventory_count)