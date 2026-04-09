from importlib import import_module
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase

from ech.orders.apps import OrdersConfig
from ech.orders.domain_events.dispatcher import EventDispatcher
from ech.orders.domain_events.events import (
    OrderCancelledEvent,
    OrderConfirmedEvent,
    OrderCreatedEvent,
    OrderDeliveredEvent,
    OrderProcessingStartedEvent,
    OrderShippedEvent,
)
from ech.orders.domain_events.handlers import (
    handle_order_cancelled_event,
    handle_order_confirmed_event,
    handle_order_created_event,
    handle_order_delivered_event,
    handle_order_processing_started_event,
    handle_order_shipped_event,
)
from ech.orders.domain_events.registry import register_order_event_handlers
from ech.orders.models import Order, OrderEvent, OrderLifecycle


class OrdersAppConfigTestCase(SimpleTestCase):
    def test_ready_calls_register_order_event_handlers(self):
        """Call register_order_event_handlers when app config is ready."""
        config = OrdersConfig("ech.orders", import_module("ech.orders"))

        with patch(
            "ech.orders.domain_events.registry.register_order_event_handlers"
        ) as register_mock:
            config.ready()

        register_mock.assert_called_once_with()


class OrderCreatedEventTestCase(SimpleTestCase):
    def test_order_created_event_stores_expected_payload(self):
        """Store the expected payload for order created event."""
        order = object()
        performed_by = object()

        event = OrderCreatedEvent(order=order, performed_by=performed_by)

        self.assertEqual(event.order, order)
        self.assertEqual(event.performed_by, performed_by)


class OrderConfirmedEventTestCase(SimpleTestCase):
    def test_order_confirmed_event_stores_expected_payload(self):
        """Store the expected payload for order confirmed event."""
        order = object()
        performed_by = object()

        event = OrderConfirmedEvent(order=order, performed_by=performed_by)

        self.assertEqual(event.order, order)
        self.assertEqual(event.performed_by, performed_by)


class OrderProcessingStartedEventTestCase(SimpleTestCase):
    def test_order_processing_started_event_stores_expected_payload(self):
        """Store the expected payload for order processing started event."""
        order = object()
        performed_by = object()

        event = OrderProcessingStartedEvent(
            order=order,
            performed_by=performed_by,
        )

        self.assertEqual(event.order, order)
        self.assertEqual(event.performed_by, performed_by)


class OrderShippedEventTestCase(SimpleTestCase):
    def test_order_shipped_event_stores_expected_payload(self):
        """Store the expected payload for order shipped event."""
        order = object()
        performed_by = object()

        event = OrderShippedEvent(order=order, performed_by=performed_by)

        self.assertEqual(event.order, order)
        self.assertEqual(event.performed_by, performed_by)


class OrderDeliveredEventTestCase(SimpleTestCase):
    def test_order_delivered_event_stores_expected_payload(self):
        """Store the expected payload for order delivered event."""
        order = object()
        performed_by = object()

        event = OrderDeliveredEvent(order=order, performed_by=performed_by)

        self.assertEqual(event.order, order)
        self.assertEqual(event.performed_by, performed_by)


class OrderCancelledEventTestCase(SimpleTestCase):
    def test_order_cancelled_event_stores_expected_payload(self):
        """Store the expected payload for order cancelled event."""
        order = object()
        performed_by = object()

        event = OrderCancelledEvent(
            order=order,
            performed_by=performed_by,
            reason="manual_cancellation",
        )

        self.assertEqual(event.order, order)
        self.assertEqual(event.performed_by, performed_by)
        self.assertEqual(event.reason, "manual_cancellation")

    def test_order_cancelled_event_uses_default_reason(self):
        """Use the default cancellation reason when none is provided."""
        event = OrderCancelledEvent(
            order=object(),
            performed_by=object(),
        )

        self.assertEqual(event.reason, "manual_cancellation")


class EventDispatcherTestCase(SimpleTestCase):
    def tearDown(self):
        EventDispatcher.clear()

    def test_register_adds_handler_for_event_type(self):
        """Register a handler for an event type."""
        def handler(event):
            return event

        EventDispatcher.clear()
        EventDispatcher.register(OrderConfirmedEvent, handler)

        self.assertIn(OrderConfirmedEvent, EventDispatcher._handlers)
        self.assertEqual(EventDispatcher._handlers[OrderConfirmedEvent], [handler])

    def test_dispatch_calls_registered_handler(self):
        """Dispatch an event to its registered handler."""
        captured_events = []

        def handler(event):
            captured_events.append(event)

        event = OrderConfirmedEvent(order=object(), performed_by=object())

        EventDispatcher.clear()
        EventDispatcher.register(OrderConfirmedEvent, handler)
        EventDispatcher.dispatch(event)

        self.assertEqual(captured_events, [event])

    def test_dispatch_calls_multiple_registered_handlers(self):
        """Dispatch an event to all registered handlers."""
        captured_calls = []

        def handler_one(event):
            captured_calls.append(("handler_one", event))

        def handler_two(event):
            captured_calls.append(("handler_two", event))

        event = OrderCancelledEvent(
            order=object(),
            performed_by=object(),
            reason="manual_cancellation",
        )

        EventDispatcher.clear()
        EventDispatcher.register(OrderCancelledEvent, handler_one)
        EventDispatcher.register(OrderCancelledEvent, handler_two)
        EventDispatcher.dispatch(event)

        self.assertEqual(
            captured_calls,
            [
                ("handler_one", event),
                ("handler_two", event),
            ],
        )

    def test_dispatch_does_nothing_when_no_handlers_are_registered(self):
        """Do nothing when no handlers are registered for an event."""
        event = OrderCreatedEvent(order=object(), performed_by=object())

        EventDispatcher.clear()
        EventDispatcher.dispatch(event)

        self.assertEqual(EventDispatcher._handlers, {})

    def test_clear_removes_all_registered_handlers(self):
        """Clear all registered handlers."""
        def handler(event):
            return event

        EventDispatcher.register(OrderCreatedEvent, handler)
        EventDispatcher.clear()

        self.assertEqual(EventDispatcher._handlers, {})


class DomainEventRegistryTestCase(SimpleTestCase):
    def tearDown(self):
        EventDispatcher.clear()

    def test_register_order_event_handlers_registers_all_expected_mappings(self):
        """Register all expected order event handlers."""
        EventDispatcher.clear()

        register_order_event_handlers()

        self.assertEqual(
            EventDispatcher._handlers.get(OrderCreatedEvent),
            [handle_order_created_event],
        )
        self.assertEqual(
            EventDispatcher._handlers.get(OrderConfirmedEvent),
            [handle_order_confirmed_event],
        )
        self.assertEqual(
            EventDispatcher._handlers.get(OrderProcessingStartedEvent),
            [handle_order_processing_started_event],
        )
        self.assertEqual(
            EventDispatcher._handlers.get(OrderShippedEvent),
            [handle_order_shipped_event],
        )
        self.assertEqual(
            EventDispatcher._handlers.get(OrderDeliveredEvent),
            [handle_order_delivered_event],
        )
        self.assertEqual(
            EventDispatcher._handlers.get(OrderCancelledEvent),
            [handle_order_cancelled_event],
        )

    def test_register_order_event_handlers_resets_existing_registry(self):
        """Reset existing handlers before registering the expected ones."""
        def dummy_handler(event):
            return event

        EventDispatcher.clear()
        EventDispatcher.register(OrderCreatedEvent, dummy_handler)

        register_order_event_handlers()

        self.assertEqual(
            EventDispatcher._handlers.get(OrderCreatedEvent),
            [handle_order_created_event],
        )


class OrderDomainEventHandlersTestCase(TestCase):
    user_counter = 0

    @classmethod
    def _create_user(cls, **overrides):
        User = get_user_model()
        cls.user_counter += 1
        idx = cls.user_counter

        data = {
            "email": f"user_{idx}@test.com",
            "user_name": f"Test User {idx}",
            "password": "StrongPass123!",
        }
        data.update(overrides)
        return User.objects.create_user(**data)

    def create_order(self):
        order = Order.objects.create(
            customer=self._create_user(),
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )
        OrderLifecycle.objects.create(order=order)
        return order

    def test_handle_order_created_event_creates_created_order_event(self):
        """Create created order event record from created domain event."""
        order = self.create_order()
        performed_by = self._create_user()

        handle_order_created_event(
            OrderCreatedEvent(order=order, performed_by=performed_by)
        )

        event = OrderEvent.objects.get()

        self.assertEqual(event.order, order)
        self.assertEqual(event.event_type, OrderEvent.TYPE_CREATED)
        self.assertEqual(event.performed_by, performed_by)
        self.assertIn("created_at", event.metadata)

    def test_handle_order_confirmed_event_creates_confirmed_order_event(self):
        """Create confirmed order event record from confirmed domain event."""
        order = self.create_order()
        performed_by = self._create_user()

        handle_order_confirmed_event(
            OrderConfirmedEvent(order=order, performed_by=performed_by)
        )

        event = OrderEvent.objects.get()

        self.assertEqual(event.event_type, OrderEvent.TYPE_CONFIRMED)
        self.assertEqual(event.metadata, {})

    def test_handle_order_processing_started_event_creates_processing_event(self):
        """Create processing started event record from processing domain event."""
        order = self.create_order()
        performed_by = self._create_user()

        handle_order_processing_started_event(
            OrderProcessingStartedEvent(order=order, performed_by=performed_by)
        )

        event = OrderEvent.objects.get()

        self.assertEqual(event.event_type, OrderEvent.TYPE_PROCESSING_STARTED)
        self.assertEqual(event.metadata, {})

    def test_handle_order_shipped_event_creates_shipped_order_event(self):
        """Create shipped order event record from shipped domain event."""
        order = self.create_order()
        performed_by = self._create_user()

        handle_order_shipped_event(
            OrderShippedEvent(order=order, performed_by=performed_by)
        )

        event = OrderEvent.objects.get()

        self.assertEqual(event.event_type, OrderEvent.TYPE_SHIPPED)
        self.assertEqual(event.metadata, {})

    def test_handle_order_delivered_event_creates_delivered_order_event(self):
        """Create delivered order event record from delivered domain event."""
        order = self.create_order()
        performed_by = self._create_user()

        handle_order_delivered_event(
            OrderDeliveredEvent(order=order, performed_by=performed_by)
        )

        event = OrderEvent.objects.get()

        self.assertEqual(event.event_type, OrderEvent.TYPE_DELIVERED)
        self.assertEqual(event.metadata, {})

    def test_handle_order_cancelled_event_creates_cancelled_order_event(self):
        """Create cancelled order event record from cancelled domain event."""
        order = self.create_order()
        performed_by = self._create_user()

        handle_order_cancelled_event(
            OrderCancelledEvent(
                order=order,
                performed_by=performed_by,
                reason="manual_cancellation",
            )
        )

        event = OrderEvent.objects.get()

        self.assertEqual(event.event_type, OrderEvent.TYPE_CANCELLED)
        self.assertEqual(event.metadata, {"reason": "manual_cancellation"})


class OrderDomainEventDispatchIntegrationTestCase(TestCase):
    user_counter = 0

    @classmethod
    def _create_user(cls, **overrides):
        User = get_user_model()
        cls.user_counter += 1
        idx = cls.user_counter

        data = {
            "email": f"dispatch_user_{idx}@test.com",
            "user_name": f"Dispatch User {idx}",
            "password": "StrongPass123!",
        }
        data.update(overrides)
        return User.objects.create_user(**data)

    def create_order(self):
        order = Order.objects.create(
            customer=self._create_user(),
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )
        OrderLifecycle.objects.create(order=order)
        return order

    def setUp(self):
        EventDispatcher.clear()
        register_order_event_handlers()

    def tearDown(self):
        EventDispatcher.clear()
        register_order_event_handlers()

    def test_dispatch_created_event_creates_order_event_record(self):
        """Dispatch created event and persist created order event record."""
        order = self.create_order()
        performed_by = self._create_user()

        EventDispatcher.dispatch(
            OrderCreatedEvent(order=order, performed_by=performed_by)
        )

        event = OrderEvent.objects.get()

        self.assertEqual(event.event_type, OrderEvent.TYPE_CREATED)
        self.assertEqual(event.order, order)
        self.assertEqual(event.performed_by, performed_by)
        self.assertIn("created_at", event.metadata)

    def test_dispatch_cancelled_event_creates_cancelled_order_event_record(self):
        """Dispatch cancelled event and persist cancelled order event record."""
        order = self.create_order()
        performed_by = self._create_user()

        EventDispatcher.dispatch(
            OrderCancelledEvent(
                order=order,
                performed_by=performed_by,
                reason="manual_cancellation",
            )
        )

        event = OrderEvent.objects.get()

        self.assertEqual(event.event_type, OrderEvent.TYPE_CANCELLED)
        self.assertEqual(event.metadata, {"reason": "manual_cancellation"})