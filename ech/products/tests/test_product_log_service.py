from decimal import Decimal

from django.test import TestCase

from ech.products.models import Product, ProductEventLog
from ech.products.services.product_log_service import log_product_event
from ech.users.models import CustomUser


class ProductLogServiceTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            email="logs@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Log User",
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

    def test_log_product_event_creates_event_log(self):
        """Ensure log_product_event creates a ProductEventLog entry."""
        log_product_event(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_CREATED,
            user=self.user,
            metadata={"source": "test"},
        )

        event = ProductEventLog.objects.get()

        self.assertEqual(event.product, self.product)
        self.assertEqual(event.event_type, ProductEventLog.EVENT_PRODUCT_CREATED)
        self.assertEqual(event.performed_by, self.user)
        self.assertIn("timestamp", event.metadata)
        self.assertEqual(event.metadata["source"], "test")

    def test_log_product_event_sets_timestamp_when_metadata_is_none(self):
        """Ensure log_product_event creates metadata with timestamp when metadata is None."""
        log_product_event(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_UPDATED,
            user=self.user,
        )

        event = ProductEventLog.objects.get()

        self.assertIn("timestamp", event.metadata)
        self.assertEqual(len(event.metadata), 1)

    def test_log_product_event_allows_null_user(self):
        """Ensure log_product_event allows events without performer."""
        log_product_event(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_DELETED,
            user=None,
        )

        event = ProductEventLog.objects.get()

        self.assertIsNone(event.performed_by)
        self.assertIn("timestamp", event.metadata)

    def test_log_product_event_persists_multiple_events(self):
        """Ensure multiple log events can be created for the same product."""
        log_product_event(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_CREATED,
            user=self.user,
        )

        log_product_event(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_UPDATED,
            user=self.user,
        )

        self.assertEqual(ProductEventLog.objects.count(), 2)