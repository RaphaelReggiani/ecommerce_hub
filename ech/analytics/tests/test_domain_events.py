import uuid
from datetime import timedelta
from unittest.mock import patch

from django.test import SimpleTestCase
from django.utils import timezone

from ech.analytics.domain_events.dispatcher import DomainEventDispatcher
from ech.analytics.domain_events.events import (
    AnalyticsSnapshotCreatedEvent,
    AnalyticsSnapshotFailedEvent,
    AnalyticsSnapshotRefreshedEvent,
    BaseDomainEvent,
)
from ech.analytics.domain_events.handlers import (
    handle_analytics_snapshot_created,
    handle_analytics_snapshot_failed,
    handle_analytics_snapshot_refreshed,
)
from ech.analytics.domain_events.registry import EVENT_HANDLER_REGISTRY


class BaseDomainEventTestCase(SimpleTestCase):
    def test_base_domain_event_to_dict_returns_event_payload_copy(self):
        """Return a shallow copy of the event payload dictionary."""
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


class AnalyticsSnapshotCreatedEventTestCase(SimpleTestCase):
    def test_snapshot_created_event_stores_expected_payload(self):
        """Store the expected payload for analytics snapshot created event."""
        snapshot_id = uuid.uuid4()
        period_start = timezone.now() - timedelta(days=1)
        period_end = timezone.now()

        event = AnalyticsSnapshotCreatedEvent(
            snapshot_id=snapshot_id,
            period_type="daily",
            period_start=period_start,
            period_end=period_end,
            generated_by_id=10,
        )

        self.assertEqual(event.event_name, "analytics_snapshot_created")
        self.assertEqual(event.snapshot_id, snapshot_id)
        self.assertEqual(event.period_type, "daily")
        self.assertEqual(event.period_start, period_start)
        self.assertEqual(event.period_end, period_end)
        self.assertEqual(event.generated_by_id, 10)

    def test_snapshot_created_event_to_dict_serializes_payload(self):
        """Serialize analytics snapshot created event payload correctly."""
        snapshot_id = uuid.uuid4()
        period_start = timezone.now() - timedelta(days=7)
        period_end = timezone.now()

        event = AnalyticsSnapshotCreatedEvent(
            snapshot_id=snapshot_id,
            period_type="weekly",
            period_start=period_start,
            period_end=period_end,
            generated_by_id=None,
        )

        self.assertEqual(
            event.to_dict(),
            {
                "snapshot_id": snapshot_id,
                "period_type": "weekly",
                "period_start": period_start,
                "period_end": period_end,
                "generated_by_id": None,
            },
        )


class AnalyticsSnapshotRefreshedEventTestCase(SimpleTestCase):
    def test_snapshot_refreshed_event_stores_expected_payload(self):
        """Store the expected payload for analytics snapshot refreshed event."""
        snapshot_id = uuid.uuid4()
        period_start = timezone.now() - timedelta(days=30)
        period_end = timezone.now()

        event = AnalyticsSnapshotRefreshedEvent(
            snapshot_id=snapshot_id,
            period_type="monthly",
            period_start=period_start,
            period_end=period_end,
            refreshed_by_id=20,
        )

        self.assertEqual(event.event_name, "analytics_snapshot_refreshed")
        self.assertEqual(event.snapshot_id, snapshot_id)
        self.assertEqual(event.period_type, "monthly")
        self.assertEqual(event.period_start, period_start)
        self.assertEqual(event.period_end, period_end)
        self.assertEqual(event.refreshed_by_id, 20)

    def test_snapshot_refreshed_event_to_dict_serializes_payload(self):
        """Serialize analytics snapshot refreshed event payload correctly."""
        snapshot_id = uuid.uuid4()
        period_start = timezone.now() - timedelta(days=1)
        period_end = timezone.now()

        event = AnalyticsSnapshotRefreshedEvent(
            snapshot_id=snapshot_id,
            period_type="daily",
            period_start=period_start,
            period_end=period_end,
            refreshed_by_id=None,
        )

        self.assertEqual(
            event.to_dict(),
            {
                "snapshot_id": snapshot_id,
                "period_type": "daily",
                "period_start": period_start,
                "period_end": period_end,
                "refreshed_by_id": None,
            },
        )


class AnalyticsSnapshotFailedEventTestCase(SimpleTestCase):
    def test_snapshot_failed_event_stores_expected_payload(self):
        """Store the expected payload for analytics snapshot failed event."""
        snapshot_id = uuid.uuid4()
        period_start = timezone.now() - timedelta(days=1)
        period_end = timezone.now()

        event = AnalyticsSnapshotFailedEvent(
            snapshot_id=snapshot_id,
            period_type="daily",
            period_start=period_start,
            period_end=period_end,
            error_message="generation failed",
            performed_by_id=30,
        )

        self.assertEqual(event.event_name, "analytics_snapshot_failed")
        self.assertEqual(event.snapshot_id, snapshot_id)
        self.assertEqual(event.period_type, "daily")
        self.assertEqual(event.period_start, period_start)
        self.assertEqual(event.period_end, period_end)
        self.assertEqual(event.error_message, "generation failed")
        self.assertEqual(event.performed_by_id, 30)

    def test_snapshot_failed_event_allows_null_snapshot_id(self):
        """Allow snapshot_id to be None for failures before snapshot creation."""
        period_start = timezone.now() - timedelta(days=7)
        period_end = timezone.now()

        event = AnalyticsSnapshotFailedEvent(
            snapshot_id=None,
            period_type="weekly",
            period_start=period_start,
            period_end=period_end,
            error_message="unexpected failure",
            performed_by_id=None,
        )

        self.assertIsNone(event.snapshot_id)
        self.assertEqual(event.error_message, "unexpected failure")
        self.assertIsNone(event.performed_by_id)

    def test_snapshot_failed_event_to_dict_serializes_payload(self):
        """Serialize analytics snapshot failed event payload correctly."""
        period_start = timezone.now() - timedelta(days=30)
        period_end = timezone.now()

        event = AnalyticsSnapshotFailedEvent(
            snapshot_id=None,
            period_type="monthly",
            period_start=period_start,
            period_end=period_end,
            error_message="refresh failed",
            performed_by_id=99,
        )

        self.assertEqual(
            event.to_dict(),
            {
                "snapshot_id": None,
                "period_type": "monthly",
                "period_start": period_start,
                "period_end": period_end,
                "error_message": "refresh failed",
                "performed_by_id": 99,
            },
        )


class DomainEventRegistryTestCase(SimpleTestCase):
    def test_event_handler_registry_contains_snapshot_created_event_mapping(self):
        """Register the snapshot created handler for snapshot created event."""
        self.assertIn(AnalyticsSnapshotCreatedEvent, EVENT_HANDLER_REGISTRY)
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[AnalyticsSnapshotCreatedEvent],
            [handle_analytics_snapshot_created],
        )

    def test_event_handler_registry_contains_snapshot_refreshed_event_mapping(self):
        """Register the snapshot refreshed handler for snapshot refreshed event."""
        self.assertIn(AnalyticsSnapshotRefreshedEvent, EVENT_HANDLER_REGISTRY)
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[AnalyticsSnapshotRefreshedEvent],
            [handle_analytics_snapshot_refreshed],
        )

    def test_event_handler_registry_contains_snapshot_failed_event_mapping(self):
        """Register the snapshot failed handler for snapshot failed event."""
        self.assertIn(AnalyticsSnapshotFailedEvent, EVENT_HANDLER_REGISTRY)
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[AnalyticsSnapshotFailedEvent],
            [handle_analytics_snapshot_failed],
        )


class DomainEventDispatcherTestCase(SimpleTestCase):
    def test_dispatch_calls_registered_handler_for_snapshot_created_event(self):
        """Dispatch snapshot created event to its registered handler."""
        event = AnalyticsSnapshotCreatedEvent(
            snapshot_id=uuid.uuid4(),
            period_type="daily",
            period_start=timezone.now() - timedelta(days=1),
            period_end=timezone.now(),
            generated_by_id=1,
        )

        captured_events = []

        def handler(event_obj):
            captured_events.append(event_obj)

        with patch(
            "ech.analytics.domain_events.dispatcher.EVENT_HANDLER_REGISTRY",
            {AnalyticsSnapshotCreatedEvent: [handler]},
        ):
            DomainEventDispatcher.dispatch(event)

        self.assertEqual(captured_events, [event])

    def test_dispatch_calls_multiple_registered_handlers(self):
        """Dispatch event to all handlers registered for its class."""
        event = AnalyticsSnapshotRefreshedEvent(
            snapshot_id=uuid.uuid4(),
            period_type="weekly",
            period_start=timezone.now() - timedelta(days=7),
            period_end=timezone.now(),
            refreshed_by_id=2,
        )

        captured_calls = []

        def handler_one(event_obj):
            captured_calls.append(("handler_one", event_obj))

        def handler_two(event_obj):
            captured_calls.append(("handler_two", event_obj))

        with patch(
            "ech.analytics.domain_events.dispatcher.EVENT_HANDLER_REGISTRY",
            {
                AnalyticsSnapshotRefreshedEvent: [
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
            "ech.analytics.domain_events.dispatcher.EVENT_HANDLER_REGISTRY",
            {},
        ):
            DomainEventDispatcher.dispatch(event)


class DomainEventHandlersTestCase(SimpleTestCase):
    @patch("ech.analytics.domain_events.handlers.logger.info")
    def test_handle_snapshot_created_logs_expected_payload(self, logger_info_mock):
        """Log the expected payload for snapshot created handler."""
        snapshot_id = uuid.uuid4()
        period_start = timezone.now() - timedelta(days=1)
        period_end = timezone.now()

        event = AnalyticsSnapshotCreatedEvent(
            snapshot_id=snapshot_id,
            period_type="daily",
            period_start=period_start,
            period_end=period_end,
            generated_by_id=10,
        )

        handle_analytics_snapshot_created(event)

        logger_info_mock.assert_called_once_with(
            "Handled analytics snapshot created domain event.",
            extra={
                "event_name": "analytics_snapshot_created",
                "snapshot_id": str(snapshot_id),
                "period_type": "daily",
                "period_start": str(period_start),
                "period_end": str(period_end),
                "generated_by_id": 10,
            },
        )

    @patch("ech.analytics.domain_events.handlers.logger.info")
    def test_handle_snapshot_refreshed_logs_expected_payload(self, logger_info_mock):
        """Log the expected payload for snapshot refreshed handler."""
        snapshot_id = uuid.uuid4()
        period_start = timezone.now() - timedelta(days=7)
        period_end = timezone.now()

        event = AnalyticsSnapshotRefreshedEvent(
            snapshot_id=snapshot_id,
            period_type="weekly",
            period_start=period_start,
            period_end=period_end,
            refreshed_by_id=20,
        )

        handle_analytics_snapshot_refreshed(event)

        logger_info_mock.assert_called_once_with(
            "Handled analytics snapshot refreshed domain event.",
            extra={
                "event_name": "analytics_snapshot_refreshed",
                "snapshot_id": str(snapshot_id),
                "period_type": "weekly",
                "period_start": str(period_start),
                "period_end": str(period_end),
                "refreshed_by_id": 20,
            },
        )

    @patch("ech.analytics.domain_events.handlers.logger.warning")
    def test_handle_snapshot_failed_logs_expected_payload(self, logger_warning_mock):
        """Log the expected payload for snapshot failed handler."""
        period_start = timezone.now() - timedelta(days=30)
        period_end = timezone.now()

        event = AnalyticsSnapshotFailedEvent(
            snapshot_id=None,
            period_type="monthly",
            period_start=period_start,
            period_end=period_end,
            error_message="snapshot generation failed",
            performed_by_id=30,
        )

        handle_analytics_snapshot_failed(event)

        logger_warning_mock.assert_called_once_with(
            "Handled analytics snapshot failed domain event.",
            extra={
                "event_name": "analytics_snapshot_failed",
                "snapshot_id": None,
                "period_type": "monthly",
                "period_start": str(period_start),
                "period_end": str(period_end),
                "error_message": "snapshot generation failed",
                "performed_by_id": 30,
            },
        )

    @patch("ech.analytics.domain_events.handlers.logger.warning")
    def test_handle_snapshot_failed_logs_snapshot_id_when_present(
        self,
        logger_warning_mock,
    ):
        """Log snapshot id as string when failure event contains one."""
        snapshot_id = uuid.uuid4()
        period_start = timezone.now() - timedelta(days=1)
        period_end = timezone.now()

        event = AnalyticsSnapshotFailedEvent(
            snapshot_id=snapshot_id,
            period_type="daily",
            period_start=period_start,
            period_end=period_end,
            error_message="refresh failed",
            performed_by_id=None,
        )

        handle_analytics_snapshot_failed(event)

        logger_warning_mock.assert_called_once_with(
            "Handled analytics snapshot failed domain event.",
            extra={
                "event_name": "analytics_snapshot_failed",
                "snapshot_id": str(snapshot_id),
                "period_type": "daily",
                "period_start": str(period_start),
                "period_end": str(period_end),
                "error_message": "refresh failed",
                "performed_by_id": None,
            },
        )