import uuid
from unittest.mock import patch

from importlib import import_module

from django.test import SimpleTestCase

from ech.notifications.apps import NotificationsConfig

from ech.notifications.domain_events.dispatcher import DomainEventDispatcher
from ech.notifications.domain_events.events import (
    BaseDomainEvent,
    NotificationCreatedEvent,
    NotificationStatusChangedEvent,
)
from ech.notifications.domain_events.handlers import (
    handle_notification_created,
    handle_notification_status_changed,
)
from ech.notifications.domain_events.registry import EVENT_HANDLER_REGISTRY


class NotificationsAppConfigTestCase(SimpleTestCase):
    def test_ready_imports_domain_event_registry(self):
        """Import domain event registry when app config is ready."""
        config = NotificationsConfig(
            "ech.notifications",
            import_module("ech.notifications"),
        )

        with patch(
            "ech.notifications.domain_events.registry.EVENT_HANDLER_REGISTRY",
            {},
        ) as _:
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


class NotificationCreatedEventTestCase(SimpleTestCase):
    def test_notification_created_event_stores_expected_payload(self):
        """Store the expected payload for notification created event."""
        notification_id = uuid.uuid4()
        recipient_id = 10
        performed_by_id = 20

        event = NotificationCreatedEvent(
            notification_id=notification_id,
            recipient_id=recipient_id,
            notification_type="order_shipped",
            channel="email",
            performed_by_id=performed_by_id,
        )

        self.assertEqual(event.event_name, "notification_created")
        self.assertEqual(event.notification_id, notification_id)
        self.assertEqual(event.recipient_id, recipient_id)
        self.assertEqual(event.notification_type, "order_shipped")
        self.assertEqual(event.channel, "email")
        self.assertEqual(event.performed_by_id, performed_by_id)

    def test_notification_created_event_to_dict_serializes_payload(self):
        """Serialize notification created event payload correctly."""
        notification_id = uuid.uuid4()

        event = NotificationCreatedEvent(
            notification_id=notification_id,
            recipient_id=1,
            notification_type="payment_captured",
            channel="in_app",
            performed_by_id=None,
        )

        self.assertEqual(
            event.to_dict(),
            {
                "notification_id": notification_id,
                "recipient_id": 1,
                "notification_type": "payment_captured",
                "channel": "in_app",
                "performed_by_id": None,
            },
        )


class NotificationStatusChangedEventTestCase(SimpleTestCase):
    def test_notification_status_changed_event_stores_expected_payload(self):
        """Store the expected payload for notification status changed event."""
        notification_id = uuid.uuid4()

        event = NotificationStatusChangedEvent(
            notification_id=notification_id,
            previous_status="pending",
            new_status="unread",
            performed_by_id=99,
        )

        self.assertEqual(event.event_name, "notification_status_changed")
        self.assertEqual(event.notification_id, notification_id)
        self.assertEqual(event.previous_status, "pending")
        self.assertEqual(event.new_status, "unread")
        self.assertEqual(event.performed_by_id, 99)

    def test_notification_status_changed_event_to_dict_serializes_payload(self):
        """Serialize notification status changed event payload correctly."""
        notification_id = uuid.uuid4()

        event = NotificationStatusChangedEvent(
            notification_id=notification_id,
            previous_status="unread",
            new_status="read",
            performed_by_id=None,
        )

        self.assertEqual(
            event.to_dict(),
            {
                "notification_id": notification_id,
                "previous_status": "unread",
                "new_status": "read",
                "performed_by_id": None,
            },
        )


class DomainEventRegistryTestCase(SimpleTestCase):
    def test_event_handler_registry_contains_notification_created_event_mapping(
        self,
    ):
        """Register the notification created handler for notification created event."""
        self.assertIn(NotificationCreatedEvent, EVENT_HANDLER_REGISTRY)
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[NotificationCreatedEvent],
            [handle_notification_created],
        )

    def test_event_handler_registry_contains_status_changed_event_mapping(self):
        """Register the notification status changed handler for status changed event."""
        self.assertIn(NotificationStatusChangedEvent, EVENT_HANDLER_REGISTRY)
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[NotificationStatusChangedEvent],
            [handle_notification_status_changed],
        )


class DomainEventDispatcherTestCase(SimpleTestCase):
    def test_dispatch_calls_registered_handler_for_notification_created_event(
        self,
    ):
        """Dispatch notification created event to its registered handler."""
        event = NotificationCreatedEvent(
            notification_id=uuid.uuid4(),
            recipient_id=1,
            notification_type="order_shipped",
            channel="email",
            performed_by_id=2,
        )

        captured_events = []

        def handler(event_obj):
            captured_events.append(event_obj)

        with patch(
            "ech.notifications.domain_events.dispatcher.EVENT_HANDLER_REGISTRY",
            {NotificationCreatedEvent: [handler]},
        ):
            DomainEventDispatcher.dispatch(event)

        self.assertEqual(captured_events, [event])

    def test_dispatch_calls_multiple_registered_handlers(self):
        """Dispatch event to all handlers registered for its class."""
        event = NotificationStatusChangedEvent(
            notification_id=uuid.uuid4(),
            previous_status="pending",
            new_status="unread",
            performed_by_id=2,
        )

        captured_calls = []

        def handler_one(event_obj):
            captured_calls.append(("handler_one", event_obj))

        def handler_two(event_obj):
            captured_calls.append(("handler_two", event_obj))

        with patch(
            "ech.notifications.domain_events.dispatcher.EVENT_HANDLER_REGISTRY",
            {
                NotificationStatusChangedEvent: [
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
            "ech.notifications.domain_events.dispatcher.EVENT_HANDLER_REGISTRY",
            {},
        ):
            DomainEventDispatcher.dispatch(event)


class DomainEventHandlersTestCase(SimpleTestCase):
    @patch("ech.notifications.domain_events.handlers.logger.info")
    def test_handle_notification_created_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log the expected payload for notification created handler."""
        notification_id = uuid.uuid4()

        event = NotificationCreatedEvent(
            notification_id=notification_id,
            recipient_id=10,
            notification_type="order_shipped",
            channel="email",
            performed_by_id=20,
        )

        handle_notification_created(event)

        logger_info_mock.assert_called_once_with(
            "Handled notification created domain event.",
            extra={
                "event_name": "notification_created",
                "notification_id": str(notification_id),
                "recipient_id": "10",
                "notification_type": "order_shipped",
                "channel": "email",
                "performed_by_id": 20,
            },
        )

    @patch("ech.notifications.domain_events.handlers.logger.info")
    def test_handle_notification_status_changed_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log the expected payload for notification status changed handler."""
        notification_id = uuid.uuid4()

        event = NotificationStatusChangedEvent(
            notification_id=notification_id,
            previous_status="unread",
            new_status="read",
            performed_by_id=30,
        )

        handle_notification_status_changed(event)

        logger_info_mock.assert_called_once_with(
            "Handled notification status changed domain event.",
            extra={
                "event_name": "notification_status_changed",
                "notification_id": str(notification_id),
                "previous_status": "unread",
                "new_status": "read",
                "performed_by_id": 30,
            },
        )