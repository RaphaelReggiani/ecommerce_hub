from decimal import Decimal
import uuid
from unittest.mock import patch

from django.test import TestCase

from ech.products.domain_events.events import ProductUpdatedEvent
from ech.products.exceptions import ProductNotFoundError
from ech.products.models import Product
from ech.products.services.product_update_service import update_product
from ech.users.models import CustomUser


class ProductUpdateServiceTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="staff@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Staff User",
        )

        self.product = Product.objects.create(
            name="Gaming Mouse",
            product_type=Product.MOUSE,
            brand="Logitech",
            sold_by=self.user,
            description="Gaming mouse",
            technical_information="16000 DPI sensor",
            price=Decimal("299.90"),
            discount_price=Decimal("249.90"),
            is_active=True,
        )

    def test_update_product_updates_single_field_successfully(self):
        """Ensure update_product updates a single field successfully."""
        updated_product = update_product(
            product_id=self.product.id,
            name="Updated Gaming Mouse",
        )

        self.product.refresh_from_db()

        self.assertEqual(updated_product.id, self.product.id)
        self.assertEqual(self.product.name, "Updated Gaming Mouse")

    def test_update_product_updates_multiple_fields_successfully(self):
        """Ensure update_product updates multiple fields successfully."""
        updated_product = update_product(
            product_id=self.product.id,
            name="Updated Mouse",
            brand="Razer",
            price=Decimal("349.90"),
            discount_price=Decimal("299.90"),
            is_active=False,
        )

        self.product.refresh_from_db()

        self.assertEqual(updated_product.id, self.product.id)
        self.assertEqual(self.product.name, "Updated Mouse")
        self.assertEqual(self.product.brand, "Razer")
        self.assertEqual(self.product.price, Decimal("349.90"))
        self.assertEqual(self.product.discount_price, Decimal("299.90"))
        self.assertFalse(self.product.is_active)

    def test_update_product_updates_description_and_technical_information(self):
        """Ensure update_product updates text fields correctly."""
        updated_product = update_product(
            product_id=self.product.id,
            description="Updated description",
            technical_information="Updated technical specs",
        )

        self.product.refresh_from_db()

        self.assertEqual(updated_product.description, "Updated description")
        self.assertEqual(
            updated_product.technical_information,
            "Updated technical specs",
        )
        self.assertEqual(self.product.description, "Updated description")
        self.assertEqual(
            self.product.technical_information,
            "Updated technical specs",
        )

    def test_update_product_returns_updated_product_instance(self):
        """Ensure update_product returns the updated product instance."""
        updated_product = update_product(
            product_id=self.product.id,
            name="Returned Updated Product",
        )

        self.assertEqual(updated_product.id, self.product.id)
        self.assertEqual(updated_product.name, "Returned Updated Product")

    @patch("ech.products.services.product_update_service.EventDispatcher.dispatch")
    def test_update_product_dispatches_product_updated_event(self, dispatch_mock):
        """Ensure update_product dispatches ProductUpdatedEvent after successful update."""
        updated_product = update_product(
            product_id=self.product.id,
            performed_by=self.user,
            name="Event Updated Product",
        )

        dispatch_mock.assert_called_once()
        dispatched_event = dispatch_mock.call_args[0][0]

        self.assertIsInstance(dispatched_event, ProductUpdatedEvent)
        self.assertEqual(dispatched_event.product.id, updated_product.id)
        self.assertEqual(dispatched_event.performed_by, self.user)

    def test_update_product_raises_product_not_found_error_for_missing_product(self):
        """Ensure update_product raises ProductNotFoundError when product does not exist."""
        with self.assertRaises(ProductNotFoundError):
            update_product(
                product_id=uuid.uuid4(),
                name="Missing Product",
            )

    @patch("ech.products.services.product_update_service.EventDispatcher.dispatch")
    def test_update_product_with_no_fields_keeps_existing_values_and_does_not_dispatch_event(
        self,
        dispatch_mock,
    ):
        """Ensure update_product with no fields keeps values unchanged and does not dispatch event."""
        original_name = self.product.name
        original_brand = self.product.brand
        original_price = self.product.price
        original_discount_price = self.product.discount_price
        original_is_active = self.product.is_active

        updated_product = update_product(product_id=self.product.id)

        self.product.refresh_from_db()

        self.assertEqual(updated_product.id, self.product.id)
        self.assertEqual(self.product.name, original_name)
        self.assertEqual(self.product.brand, original_brand)
        self.assertEqual(self.product.price, original_price)
        self.assertEqual(self.product.discount_price, original_discount_price)
        self.assertEqual(self.product.is_active, original_is_active)
        dispatch_mock.assert_not_called()