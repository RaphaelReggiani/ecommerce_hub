from decimal import Decimal
from uuid import uuid4
from unittest.mock import patch

from django.test import TestCase

from ech.products.domain_events.events import ProductCreatedEvent
from ech.products.exceptions import (
    IdempotencyConflictError,
    InvalidDiscountPriceError,
    InvalidInventoryValueError,
    InvalidProductPriceError,
    InvalidProductTypeError,
    ProductCreationPermissionDeniedError,
)
from ech.products.models import Product, ProductInventory
from ech.products.services.product_creation_service import create_product
from ech.users.models import CustomUser


class ProductCreationServiceTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.allowed_user = CustomUser.objects.create_user(
            email="staff@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Staff User",
        )

        cls.disallowed_user = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_CUSTOMER_USER,
            user_name="Customer User",
        )

        cls.valid_payload = {
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

    def test_create_product_persists_idempotency_fields(self):
        """Ensure create_product persists idempotency key and request hash."""
        idempotency_key = uuid4()

        product = create_product(
            user=self.allowed_user,
            idempotency_key=idempotency_key,
            **self.valid_payload,
        )

        self.assertEqual(product.idempotency_key, idempotency_key)
        self.assertIsNotNone(product.idempotency_request_hash)
        self.assertEqual(len(product.idempotency_request_hash), 64)

    def test_create_product_with_same_idempotency_key_and_same_payload_returns_same_product(self):
        """Ensure repeated requests with same idempotency key return the same product."""
        idempotency_key = uuid4()

        first_product = create_product(
            user=self.allowed_user,
            idempotency_key=idempotency_key,
            **self.valid_payload,
        )

        second_product = create_product(
            user=self.allowed_user,
            idempotency_key=idempotency_key,
            **self.valid_payload,
        )

        self.assertEqual(first_product.id, second_product.id)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(ProductInventory.objects.count(), 1)

    def test_create_product_with_same_idempotency_key_and_different_payload_raises_conflict(self):
        """Ensure reused idempotency key with different payload raises conflict."""
        idempotency_key = uuid4()

        create_product(
            user=self.allowed_user,
            idempotency_key=idempotency_key,
            **self.valid_payload,
        )

        conflicting_payload = self.valid_payload.copy()
        conflicting_payload["name"] = "Different Mouse"

        with self.assertRaises(IdempotencyConflictError):
            create_product(
                user=self.allowed_user,
                idempotency_key=idempotency_key,
                **conflicting_payload,
            )

    @patch("ech.products.services.product_creation_service.EventDispatcher.dispatch")
    def test_create_product_dispatches_product_created_event(self, dispatch_mock):
        """Ensure create_product dispatches ProductCreatedEvent after success."""
        product = create_product(
            user=self.allowed_user,
            **self.valid_payload,
        )

        dispatch_mock.assert_called_once()
        dispatched_event = dispatch_mock.call_args[0][0]

        self.assertIsInstance(dispatched_event, ProductCreatedEvent)
        self.assertEqual(dispatched_event.product.id, product.id)
        self.assertEqual(dispatched_event.performed_by, self.allowed_user)

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
        payload["inventory"] = -5

        initial_product_count = Product.objects.count()
        initial_inventory_count = ProductInventory.objects.count()

        with self.assertRaises(InvalidInventoryValueError):
            create_product(
                user=self.allowed_user,
                **payload,
            )

        self.assertEqual(Product.objects.count(), initial_product_count)
        self.assertEqual(ProductInventory.objects.count(), initial_inventory_count)