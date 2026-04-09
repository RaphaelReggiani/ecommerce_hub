import uuid
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from ech.products.domain_events.events import ProductDeletedEvent
from ech.products.exceptions import ProductNotFoundError
from ech.products.models import Product
from ech.products.services.product_delete_service import delete_product
from ech.users.models import CustomUser


class ProductDeleteServiceTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            email="staff@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Staff User",
        )

        cls.product = Product.objects.create(
            name="Gaming Keyboard",
            product_type=Product.KEYBOARD,
            brand="Keychron",
            sold_by=cls.user,
            description="Mechanical gaming keyboard",
            technical_information="RGB hot-swappable switches",
            price=Decimal("499.90"),
            discount_price=Decimal("449.90"),
            is_active=True,
        )

    def test_delete_product_sets_is_active_to_false(self):
        """Ensure delete_product deactivates the product."""
        deleted_product = delete_product(product_id=self.product.id)

        self.product.refresh_from_db()

        self.assertEqual(deleted_product.id, self.product.id)
        self.assertFalse(deleted_product.is_active)
        self.assertFalse(self.product.is_active)

    def test_delete_product_returns_updated_product_instance(self):
        """Ensure delete_product returns the deactivated product instance."""
        deleted_product = delete_product(product_id=self.product.id)

        self.assertEqual(deleted_product.id, self.product.id)
        self.assertFalse(deleted_product.is_active)

    @patch("ech.products.services.product_delete_service.EventDispatcher.dispatch")
    def test_delete_product_dispatches_product_deleted_event(self, dispatch_mock):
        """Ensure delete_product dispatches ProductDeletedEvent after successful soft delete."""
        deleted_product = delete_product(
            product_id=self.product.id,
            performed_by=self.user,
        )

        dispatch_mock.assert_called_once()
        dispatched_event = dispatch_mock.call_args[0][0]

        self.assertIsInstance(dispatched_event, ProductDeletedEvent)
        self.assertEqual(dispatched_event.product.id, deleted_product.id)
        self.assertEqual(dispatched_event.performed_by, self.user)

    def test_delete_product_raises_product_not_found_error_when_missing(self):
        """Ensure delete_product raises ProductNotFoundError for missing product."""
        with self.assertRaises(ProductNotFoundError):
            delete_product(product_id=uuid.uuid4())

    def test_delete_product_does_not_remove_record_from_database(self):
        """Ensure delete_product performs soft delete and keeps the record in database."""
        delete_product(product_id=self.product.id)

        self.assertTrue(
            Product.objects.filter(id=self.product.id).exists()
        )
        self.assertFalse(
            Product.objects.get(id=self.product.id).is_active
        )

    def test_delete_product_keeps_other_fields_unchanged(self):
        """Ensure delete_product only changes active status."""
        original_name = self.product.name
        original_brand = self.product.brand
        original_price = self.product.price
        original_discount_price = self.product.discount_price
        original_description = self.product.description
        original_technical_information = self.product.technical_information

        delete_product(product_id=self.product.id)
        self.product.refresh_from_db()

        self.assertEqual(self.product.name, original_name)
        self.assertEqual(self.product.brand, original_brand)
        self.assertEqual(self.product.price, original_price)
        self.assertEqual(self.product.discount_price, original_discount_price)
        self.assertEqual(self.product.description, original_description)
        self.assertEqual(
            self.product.technical_information,
            original_technical_information,
        )
        self.assertFalse(self.product.is_active)