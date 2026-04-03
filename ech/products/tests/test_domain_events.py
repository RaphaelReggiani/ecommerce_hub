from dataclasses import FrozenInstanceError
from decimal import Decimal
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from ech.products.domain_events.dispatcher import EventDispatcher
from ech.products.domain_events.events import (
    ProductCreatedEvent,
    ProductDeletedEvent,
    ProductImageUploadedEvent,
    ProductUpdatedEvent,
)
from ech.products.domain_events.handlers import (
    handle_product_created_event,
    handle_product_deleted_event,
    handle_product_image_uploaded_event,
    handle_product_updated_event,
)
from ech.products.domain_events.registry import (
    register_product_event_handlers,
)
from ech.products.models import Product, ProductEventLog
from ech.users.models import CustomUser


class ProductCreatedEventTestCase(SimpleTestCase):
    def test_product_created_event_stores_expected_payload(self):
        """Store the expected payload for product created event."""
        product = object()
        performed_by = object()

        event = ProductCreatedEvent(
            product=product,
            performed_by=performed_by,
        )

        self.assertEqual(event.product, product)
        self.assertEqual(event.performed_by, performed_by)

    def test_product_created_event_is_immutable(self):
        """Prevent mutation of frozen product created event."""
        event = ProductCreatedEvent(
            product=object(),
            performed_by=object(),
        )

        with self.assertRaises(FrozenInstanceError):
            event.product = None


class ProductUpdatedEventTestCase(SimpleTestCase):
    def test_product_updated_event_stores_expected_payload(self):
        """Store the expected payload for product updated event."""
        product = object()
        performed_by = object()

        event = ProductUpdatedEvent(
            product=product,
            performed_by=performed_by,
        )

        self.assertEqual(event.product, product)
        self.assertEqual(event.performed_by, performed_by)

    def test_product_updated_event_is_immutable(self):
        """Prevent mutation of frozen product updated event."""
        event = ProductUpdatedEvent(
            product=object(),
            performed_by=object(),
        )

        with self.assertRaises(FrozenInstanceError):
            event.performed_by = None


class ProductDeletedEventTestCase(SimpleTestCase):
    def test_product_deleted_event_stores_expected_payload(self):
        """Store the expected payload for product deleted event."""
        product = object()
        performed_by = object()

        event = ProductDeletedEvent(
            product=product,
            performed_by=performed_by,
            reason="staff_soft_delete",
        )

        self.assertEqual(event.product, product)
        self.assertEqual(event.performed_by, performed_by)
        self.assertEqual(event.reason, "staff_soft_delete")

    def test_product_deleted_event_uses_default_reason(self):
        """Use the default reason for product deleted event."""
        event = ProductDeletedEvent(
            product=object(),
            performed_by=object(),
        )

        self.assertEqual(event.reason, "manual_deletion")

    def test_product_deleted_event_is_immutable(self):
        """Prevent mutation of frozen product deleted event."""
        event = ProductDeletedEvent(
            product=object(),
            performed_by=object(),
        )

        with self.assertRaises(FrozenInstanceError):
            event.reason = "changed"


class ProductImageUploadedEventTestCase(SimpleTestCase):
    def test_product_image_uploaded_event_stores_expected_payload(self):
        """Store the expected payload for product image uploaded event."""
        product = object()
        performed_by = object()

        event = ProductImageUploadedEvent(
            product=product,
            performed_by=performed_by,
        )

        self.assertEqual(event.product, product)
        self.assertEqual(event.performed_by, performed_by)

    def test_product_image_uploaded_event_is_immutable(self):
        """Prevent mutation of frozen product image uploaded event."""
        event = ProductImageUploadedEvent(
            product=object(),
            performed_by=object(),
        )

        with self.assertRaises(FrozenInstanceError):
            event.product = None


class EventDispatcherTestCase(SimpleTestCase):
    def setUp(self):
        EventDispatcher.clear()

    def tearDown(self):
        EventDispatcher.clear()

    def test_register_adds_handler_for_event_type(self):
        """Register handler for a given event type."""

        def handler(event):
            return event

        EventDispatcher.register(ProductCreatedEvent, handler)

        self.assertIn(ProductCreatedEvent, EventDispatcher._handlers)
        self.assertEqual(
            EventDispatcher._handlers[ProductCreatedEvent],
            [handler],
        )

    def test_dispatch_calls_registered_handler_for_event(self):
        """Dispatch event to its registered handler."""
        captured_events = []

        def handler(event_obj):
            captured_events.append(event_obj)

        EventDispatcher.register(ProductCreatedEvent, handler)

        event = ProductCreatedEvent(
            product=object(),
            performed_by=object(),
        )

        EventDispatcher.dispatch(event)

        self.assertEqual(captured_events, [event])

    def test_dispatch_calls_multiple_registered_handlers(self):
        """Dispatch event to all registered handlers."""
        captured_calls = []

        def handler_one(event_obj):
            captured_calls.append(("handler_one", event_obj))

        def handler_two(event_obj):
            captured_calls.append(("handler_two", event_obj))

        EventDispatcher.register(ProductUpdatedEvent, handler_one)
        EventDispatcher.register(ProductUpdatedEvent, handler_two)

        event = ProductUpdatedEvent(
            product=object(),
            performed_by=object(),
        )

        EventDispatcher.dispatch(event)

        self.assertEqual(
            captured_calls,
            [
                ("handler_one", event),
                ("handler_two", event),
            ],
        )

    def test_dispatch_does_nothing_when_no_handlers_are_registered(self):
        """Do nothing when no handlers are registered for event."""
        event = ProductCreatedEvent(
            product=object(),
            performed_by=object(),
        )

        EventDispatcher.dispatch(event)

    def test_dispatch_continues_when_handler_raises_exception(self):
        """Continue dispatching when one handler raises exception."""
        captured_calls = []

        def failing_handler(event_obj):
            raise RuntimeError("simulated failure")

        def success_handler(event_obj):
            captured_calls.append(event_obj)

        EventDispatcher.register(ProductCreatedEvent, failing_handler)
        EventDispatcher.register(ProductCreatedEvent, success_handler)

        event = ProductCreatedEvent(
            product=object(),
            performed_by=object(),
        )

        EventDispatcher.dispatch(event)

        self.assertEqual(captured_calls, [event])

    def test_clear_removes_all_registered_handlers(self):
        """Clear all registered handlers."""

        def handler(event):
            return event

        EventDispatcher.register(ProductCreatedEvent, handler)
        EventDispatcher.register(ProductUpdatedEvent, handler)

        EventDispatcher.clear()

        self.assertEqual(EventDispatcher._handlers, {})


class ProductEventRegistryTestCase(SimpleTestCase):
    def setUp(self):
        EventDispatcher.clear()

    def tearDown(self):
        EventDispatcher.clear()

    def test_register_product_event_handlers_registers_all_expected_handlers(self):
        """Register all expected product domain event handlers."""
        register_product_event_handlers()

        self.assertIn(ProductCreatedEvent, EventDispatcher._handlers)
        self.assertIn(ProductUpdatedEvent, EventDispatcher._handlers)
        self.assertIn(ProductDeletedEvent, EventDispatcher._handlers)
        self.assertIn(ProductImageUploadedEvent, EventDispatcher._handlers)

        self.assertEqual(len(EventDispatcher._handlers[ProductCreatedEvent]), 1)
        self.assertEqual(len(EventDispatcher._handlers[ProductUpdatedEvent]), 1)
        self.assertEqual(len(EventDispatcher._handlers[ProductDeletedEvent]), 1)
        self.assertEqual(
            len(EventDispatcher._handlers[ProductImageUploadedEvent]),
            1,
        )

    def test_register_product_event_handlers_registers_expected_functions(self):
        """Register the expected handler functions for each event."""
        register_product_event_handlers()

        self.assertEqual(
            EventDispatcher._handlers[ProductCreatedEvent],
            [handle_product_created_event],
        )
        self.assertEqual(
            EventDispatcher._handlers[ProductUpdatedEvent],
            [handle_product_updated_event],
        )
        self.assertEqual(
            EventDispatcher._handlers[ProductDeletedEvent],
            [handle_product_deleted_event],
        )
        self.assertEqual(
            EventDispatcher._handlers[ProductImageUploadedEvent],
            [handle_product_image_uploaded_event],
        )

    def test_register_product_event_handlers_resets_existing_handlers(self):
        """Reset existing handlers before re-registering defaults."""

        def custom_handler(event):
            return event

        EventDispatcher.register(ProductCreatedEvent, custom_handler)

        register_product_event_handlers()

        self.assertEqual(len(EventDispatcher._handlers[ProductCreatedEvent]), 1)
        self.assertNotIn(
            custom_handler,
            EventDispatcher._handlers[ProductCreatedEvent],
        )

    def test_register_product_event_handlers_is_safe_to_call_multiple_times(self):
        """Allow multiple registry calls without duplicating handlers."""
        register_product_event_handlers()
        register_product_event_handlers()

        self.assertEqual(len(EventDispatcher._handlers[ProductCreatedEvent]), 1)
        self.assertEqual(len(EventDispatcher._handlers[ProductUpdatedEvent]), 1)
        self.assertEqual(len(EventDispatcher._handlers[ProductDeletedEvent]), 1)
        self.assertEqual(
            len(EventDispatcher._handlers[ProductImageUploadedEvent]),
            1,
        )


class ProductDomainEventHandlersTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="logs@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Log User",
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

    @patch("ech.products.domain_events.handlers.invalidate_product_list_cache")
    @patch("ech.products.domain_events.handlers.set_product_cache")
    def test_handle_product_created_event_creates_expected_event_log(
        self,
        set_product_cache_mock,
        invalidate_product_list_cache_mock,
    ):
        """Create audit log and refresh caches for product created event."""
        event = ProductCreatedEvent(
            product=self.product,
            performed_by=self.user,
        )

        handle_product_created_event(event)

        log = ProductEventLog.objects.get(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_CREATED,
        )

        self.assertEqual(log.performed_by, self.user)
        self.assertIn("created_at", log.metadata)

        set_product_cache_mock.assert_called_once_with(self.product)
        invalidate_product_list_cache_mock.assert_called_once_with()

    @patch("ech.products.domain_events.handlers.invalidate_product_list_cache")
    @patch("ech.products.domain_events.handlers.set_product_cache")
    @patch("ech.products.domain_events.handlers.invalidate_product_cache")
    def test_handle_product_updated_event_creates_expected_event_log(
        self,
        invalidate_product_cache_mock,
        set_product_cache_mock,
        invalidate_product_list_cache_mock,
    ):
        """Create audit log and invalidate caches for product updated event."""
        event = ProductUpdatedEvent(
            product=self.product,
            performed_by=self.user,
        )

        handle_product_updated_event(event)

        log = ProductEventLog.objects.get(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_UPDATED,
        )

        self.assertEqual(log.performed_by, self.user)
        self.assertIn("updated_at", log.metadata)

        invalidate_product_cache_mock.assert_called_once_with(self.product.id)
        set_product_cache_mock.assert_called_once_with(self.product)
        invalidate_product_list_cache_mock.assert_called_once_with()

    @patch("ech.products.domain_events.handlers.invalidate_product_list_cache")
    @patch("ech.products.domain_events.handlers.invalidate_product_cache")
    def test_handle_product_deleted_event_creates_expected_event_log(
        self,
        invalidate_product_cache_mock,
        invalidate_product_list_cache_mock,
    ):
        """Create audit log and invalidate caches for product deleted event."""
        event = ProductDeletedEvent(
            product=self.product,
            performed_by=self.user,
            reason="cleanup_operation",
        )

        handle_product_deleted_event(event)

        log = ProductEventLog.objects.get(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_DELETED,
        )

        self.assertEqual(log.performed_by, self.user)
        self.assertEqual(log.metadata["reason"], "cleanup_operation")
        self.assertIn("deleted_at", log.metadata)

        invalidate_product_cache_mock.assert_called_once_with(self.product.id)
        invalidate_product_list_cache_mock.assert_called_once_with()

    @patch("ech.products.domain_events.handlers.invalidate_product_list_cache")
    @patch("ech.products.domain_events.handlers.set_product_cache")
    @patch("ech.products.domain_events.handlers.invalidate_product_cache")
    def test_handle_product_image_uploaded_event_creates_expected_event_log(
        self,
        invalidate_product_cache_mock,
        set_product_cache_mock,
        invalidate_product_list_cache_mock,
    ):
        """Create audit log and refresh caches for product image uploaded event."""
        event = ProductImageUploadedEvent(
            product=self.product,
            performed_by=self.user,
        )

        handle_product_image_uploaded_event(event)

        log = ProductEventLog.objects.get(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_IMAGE_UPLOADED,
        )

        self.assertEqual(log.performed_by, self.user)
        self.assertIn("uploaded_at", log.metadata)

        invalidate_product_cache_mock.assert_called_once_with(self.product.id)
        set_product_cache_mock.assert_called_once_with(self.product)
        invalidate_product_list_cache_mock.assert_called_once_with()


class ProductDomainEventDispatcherIntegrationTestCase(TestCase):
    def setUp(self):
        EventDispatcher.clear()

        self.user = CustomUser.objects.create_user(
            email="logs2@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Log User Two",
        )

        self.product = Product.objects.create(
            name="Gaming Keyboard",
            product_type=Product.KEYBOARD,
            brand="Logitech",
            sold_by=self.user,
            description="Gaming keyboard",
            technical_information="Switches",
            price=Decimal("300.00"),
            is_active=True,
        )

    def tearDown(self):
        EventDispatcher.clear()

    @patch("ech.products.domain_events.handlers.invalidate_product_list_cache")
    @patch("ech.products.domain_events.handlers.set_product_cache")
    def test_dispatch_executes_registered_created_handler(
        self,
        set_product_cache_mock,
        invalidate_product_list_cache_mock,
    ):
        """Dispatch product created event through registered handler."""
        register_product_event_handlers()

        event = ProductCreatedEvent(
            product=self.product,
            performed_by=self.user,
        )

        EventDispatcher.dispatch(event)

        self.assertTrue(
            ProductEventLog.objects.filter(
                product=self.product,
                event_type=ProductEventLog.EVENT_PRODUCT_CREATED,
            ).exists()
        )

        set_product_cache_mock.assert_called_once_with(self.product)
        invalidate_product_list_cache_mock.assert_called_once_with()

    @patch("ech.products.domain_events.handlers.invalidate_product_list_cache")
    @patch("ech.products.domain_events.handlers.set_product_cache")
    @patch("ech.products.domain_events.handlers.invalidate_product_cache")
    def test_dispatch_executes_registered_updated_handler(
        self,
        invalidate_product_cache_mock,
        set_product_cache_mock,
        invalidate_product_list_cache_mock,
    ):
        """Dispatch product updated event through registered handler."""
        register_product_event_handlers()

        event = ProductUpdatedEvent(
            product=self.product,
            performed_by=self.user,
        )

        EventDispatcher.dispatch(event)

        self.assertTrue(
            ProductEventLog.objects.filter(
                product=self.product,
                event_type=ProductEventLog.EVENT_PRODUCT_UPDATED,
            ).exists()
        )

        invalidate_product_cache_mock.assert_called_once_with(self.product.id)
        set_product_cache_mock.assert_called_once_with(self.product)
        invalidate_product_list_cache_mock.assert_called_once_with()

    @patch("ech.products.domain_events.handlers.invalidate_product_list_cache")
    @patch("ech.products.domain_events.handlers.invalidate_product_cache")
    def test_dispatch_executes_registered_deleted_handler(
        self,
        invalidate_product_cache_mock,
        invalidate_product_list_cache_mock,
    ):
        """Dispatch product deleted event through registered handler."""
        register_product_event_handlers()

        event = ProductDeletedEvent(
            product=self.product,
            performed_by=self.user,
            reason="manual_cleanup",
        )

        EventDispatcher.dispatch(event)

        self.assertTrue(
            ProductEventLog.objects.filter(
                product=self.product,
                event_type=ProductEventLog.EVENT_PRODUCT_DELETED,
            ).exists()
        )

        log = ProductEventLog.objects.get(
            product=self.product,
            event_type=ProductEventLog.EVENT_PRODUCT_DELETED,
        )
        self.assertEqual(log.metadata["reason"], "manual_cleanup")

        invalidate_product_cache_mock.assert_called_once_with(self.product.id)
        invalidate_product_list_cache_mock.assert_called_once_with()

    @patch("ech.products.domain_events.handlers.invalidate_product_list_cache")
    @patch("ech.products.domain_events.handlers.set_product_cache")
    @patch("ech.products.domain_events.handlers.invalidate_product_cache")
    def test_dispatch_executes_registered_image_uploaded_handler(
        self,
        invalidate_product_cache_mock,
        set_product_cache_mock,
        invalidate_product_list_cache_mock,
    ):
        """Dispatch product image uploaded event through registered handler."""
        register_product_event_handlers()

        event = ProductImageUploadedEvent(
            product=self.product,
            performed_by=self.user,
        )

        EventDispatcher.dispatch(event)

        self.assertTrue(
            ProductEventLog.objects.filter(
                product=self.product,
                event_type=ProductEventLog.EVENT_PRODUCT_IMAGE_UPLOADED,
            ).exists()
        )

        invalidate_product_cache_mock.assert_called_once_with(self.product.id)
        set_product_cache_mock.assert_called_once_with(self.product)
        invalidate_product_list_cache_mock.assert_called_once_with()