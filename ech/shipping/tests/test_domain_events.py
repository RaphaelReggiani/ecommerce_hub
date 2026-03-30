import uuid
from unittest.mock import patch

from importlib import import_module

from django.test import SimpleTestCase

from ech.shipping.apps import ShippingConfig

from ech.shipping.domain_events.dispatcher import DomainEventDispatcher
from ech.shipping.domain_events.events import (
    BaseDomainEvent,
    ShipmentCreatedEvent,
    ShipmentStatusChangedEvent,
)
from ech.shipping.domain_events.handlers import (
    handle_shipment_created,
    handle_shipment_status_changed,
)
from ech.shipping.domain_events.registry import EVENT_HANDLER_REGISTRY


class ShippingAppConfigTestCase(SimpleTestCase):
    def test_ready_imports_domain_event_registry(self):
        """Import domain event registry when app config is ready."""
        config = ShippingConfig("ech.shipping", import_module("ech.shipping"))

        with patch("ech.shipping.domain_events.registry.EVENT_HANDLER_REGISTRY", {}) as _:
            config.ready()


class BaseDomainEventTestCase(SimpleTestCase):
    def test_base_domain_event_to_dict_returns_event_payload_copy(self):
        """Return a copy of the event payload dictionary."""
        event = BaseDomainEvent()
        event.example_field = "example"
        event.numeric_field = 123

        payload = event.to_dict()

        self.assertEqual(
            payload,
            {
                "example_field": "example",
                "numeric_field": 123,
            },
        )
        self.assertIsNot(payload, event.__dict__)

    def test_base_domain_event_exposes_default_event_name(self):
        """Expose the default base event name."""
        self.assertEqual(BaseDomainEvent.event_name, "base_domain_event")


class ShipmentCreatedEventTestCase(SimpleTestCase):
    def test_shipment_created_event_stores_expected_payload(self):
        """Store the expected payload for shipment created event."""
        shipment_id = uuid.uuid4()
        order_id = uuid.uuid4()
        customer_id = 10
        performed_by_id = 20

        event = ShipmentCreatedEvent(
            shipment_id=shipment_id,
            order_id=order_id,
            customer_id=customer_id,
            performed_by_id=performed_by_id,
        )

        self.assertEqual(event.event_name, "shipment_created")
        self.assertEqual(event.shipment_id, shipment_id)
        self.assertEqual(event.order_id, order_id)
        self.assertEqual(event.customer_id, customer_id)
        self.assertEqual(event.performed_by_id, performed_by_id)

    def test_shipment_created_event_to_dict_serializes_payload(self):
        """Serialize shipment created event payload correctly."""
        shipment_id = uuid.uuid4()
        order_id = uuid.uuid4()

        event = ShipmentCreatedEvent(
            shipment_id=shipment_id,
            order_id=order_id,
            customer_id=1,
            performed_by_id=None,
        )

        self.assertEqual(
            event.to_dict(),
            {
                "shipment_id": shipment_id,
                "order_id": order_id,
                "customer_id": 1,
                "performed_by_id": None,
            },
        )


class ShipmentStatusChangedEventTestCase(SimpleTestCase):
    def test_shipment_status_changed_event_stores_expected_payload(self):
        """Store the expected payload for shipment status changed event."""
        shipment_id = uuid.uuid4()

        event = ShipmentStatusChangedEvent(
            shipment_id=shipment_id,
            previous_status="pending",
            new_status="preparing",
            performed_by_id=99,
        )

        self.assertEqual(event.event_name, "shipment_status_changed")
        self.assertEqual(event.shipment_id, shipment_id)
        self.assertEqual(event.previous_status, "pending")
        self.assertEqual(event.new_status, "preparing")
        self.assertEqual(event.performed_by_id, 99)

    def test_shipment_status_changed_event_to_dict_serializes_payload(self):
        """Serialize shipment status changed event payload correctly."""
        shipment_id = uuid.uuid4()

        event = ShipmentStatusChangedEvent(
            shipment_id=shipment_id,
            previous_status="shipped",
            new_status="in_transit",
            performed_by_id=None,
        )

        self.assertEqual(
            event.to_dict(),
            {
                "shipment_id": shipment_id,
                "previous_status": "shipped",
                "new_status": "in_transit",
                "performed_by_id": None,
            },
        )


class DomainEventRegistryTestCase(SimpleTestCase):
    def test_event_handler_registry_contains_shipment_created_event_mapping(self):
        """Register the shipment created handler for shipment created event."""
        self.assertIn(ShipmentCreatedEvent, EVENT_HANDLER_REGISTRY)
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[ShipmentCreatedEvent],
            [handle_shipment_created],
        )

    def test_event_handler_registry_contains_status_changed_event_mapping(self):
        """Register the shipment status changed handler for status changed event."""
        self.assertIn(ShipmentStatusChangedEvent, EVENT_HANDLER_REGISTRY)
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[ShipmentStatusChangedEvent],
            [handle_shipment_status_changed],
        )


class DomainEventDispatcherTestCase(SimpleTestCase):
    def test_dispatch_calls_registered_handler_for_shipment_created_event(self):
        """Dispatch shipment created event to its registered handler."""
        event = ShipmentCreatedEvent(
            shipment_id=uuid.uuid4(),
            order_id=uuid.uuid4(),
            customer_id=1,
            performed_by_id=2,
        )

        captured_events = []

        def handler(event_obj):
            captured_events.append(event_obj)

        with patch(
            "ech.shipping.domain_events.dispatcher.EVENT_HANDLER_REGISTRY",
            {ShipmentCreatedEvent: [handler]},
        ):
            DomainEventDispatcher.dispatch(event)

        self.assertEqual(captured_events, [event])

    def test_dispatch_calls_multiple_registered_handlers(self):
        """Dispatch event to all handlers registered for its class."""
        event = ShipmentStatusChangedEvent(
            shipment_id=uuid.uuid4(),
            previous_status="pending",
            new_status="preparing",
            performed_by_id=2,
        )

        captured_calls = []

        def handler_one(event_obj):
            captured_calls.append(("handler_one", event_obj))

        def handler_two(event_obj):
            captured_calls.append(("handler_two", event_obj))

        with patch(
            "ech.shipping.domain_events.dispatcher.EVENT_HANDLER_REGISTRY",
            {
                ShipmentStatusChangedEvent: [
                    handler_one,
                    handler_two,
                ]
            },
        ):
            DomainEventDispatcher.dispatch(event)

        self.assertEqual(
            captured_calls,
            [
                ("handler_one", event),
                ("handler_two", event),
            ],
        )

    def test_dispatch_does_nothing_when_event_has_no_registered_handlers(self):
        """Do nothing when no handlers are registered for an event class."""

        class UnregisteredEvent(BaseDomainEvent):
            event_name = "unregistered_event"

        event = UnregisteredEvent()

        with patch(
            "ech.shipping.domain_events.dispatcher.EVENT_HANDLER_REGISTRY",
            {},
        ):
            DomainEventDispatcher.dispatch(event)


class DomainEventHandlersTestCase(SimpleTestCase):
    @patch("ech.shipping.domain_events.handlers.logger.info")
    def test_handle_shipment_created_logs_expected_payload(self, logger_info_mock):
        """Log the expected payload for shipment created handler."""
        shipment_id = uuid.uuid4()
        order_id = uuid.uuid4()

        event = ShipmentCreatedEvent(
            shipment_id=shipment_id,
            order_id=order_id,
            customer_id=10,
            performed_by_id=20,
        )

        handle_shipment_created(event)

        logger_info_mock.assert_called_once_with(
            "Handled shipment created domain event.",
            extra={
                "event_name": "shipment_created",
                "shipment_id": str(shipment_id),
                "order_id": str(order_id),
                "customer_id": "10",
                "performed_by_id": 20,
            },
        )

    @patch("ech.shipping.domain_events.handlers.logger.info")
    def test_handle_shipment_status_changed_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log the expected payload for shipment status changed handler."""
        shipment_id = uuid.uuid4()

        event = ShipmentStatusChangedEvent(
            shipment_id=shipment_id,
            previous_status="shipped",
            new_status="in_transit",
            performed_by_id=30,
        )

        handle_shipment_status_changed(event)

        logger_info_mock.assert_called_once_with(
            "Handled shipment status changed domain event.",
            extra={
                "event_name": "shipment_status_changed",
                "shipment_id": str(shipment_id),
                "previous_status": "shipped",
                "new_status": "in_transit",
                "performed_by_id": 30,
            },
        )