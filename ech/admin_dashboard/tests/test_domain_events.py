import uuid
from unittest.mock import patch

from django.test import SimpleTestCase

from ech.admin_dashboard.domain_events.dispatcher import DomainEventDispatcher
from ech.admin_dashboard.domain_events.events import (
    AdminDashboardAccessedEvent,
    AdminBulkOrderActionExecutedEvent,
    AdminBulkOrderActionFailedEvent,
    AdminBulkReviewModerationExecutedEvent,
    AdminBulkReviewModerationFailedEvent,
    AdminNotificationRetryExecutedEvent,
    AdminNotificationRetryFailedEvent,
    AdminDashboardAlertGeneratedEvent,
    BaseDomainEvent,
)
from ech.admin_dashboard.domain_events.handlers import (
    handle_admin_dashboard_accessed,
    handle_admin_bulk_order_action_executed,
    handle_admin_bulk_order_action_failed,
    handle_admin_bulk_review_moderation_executed,
    handle_admin_bulk_review_moderation_failed,
    handle_admin_notification_retry_executed,
    handle_admin_notification_retry_failed,
    handle_admin_dashboard_alert_generated,
)
from ech.admin_dashboard.domain_events.registry import EVENT_HANDLER_REGISTRY


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


class AdminDashboardAccessedEventTestCase(SimpleTestCase):
    def test_admin_dashboard_accessed_event_stores_expected_payload(self):
        """Store the expected payload for dashboard accessed event."""
        event = AdminDashboardAccessedEvent(user_id=10)

        self.assertEqual(event.event_name, "admin_dashboard_accessed")
        self.assertEqual(event.user_id, 10)

    def test_admin_dashboard_accessed_event_to_dict_serializes_payload(self):
        """Serialize dashboard accessed event payload correctly."""
        event = AdminDashboardAccessedEvent(user_id=None)

        self.assertEqual(
            event.to_dict(),
            {
                "user_id": None,
            },
        )


class AdminBulkOrderActionExecutedEventTestCase(SimpleTestCase):
    def test_bulk_order_action_executed_event_stores_expected_payload(self):
        """Store the expected payload for bulk order action executed event."""
        order_ids = [uuid.uuid4(), uuid.uuid4()]

        event = AdminBulkOrderActionExecutedEvent(
            action_type="mark_processing",
            order_ids=order_ids,
            performed_by_id=20,
        )

        self.assertEqual(
            event.event_name,
            "admin_bulk_order_action_executed",
        )
        self.assertEqual(event.action_type, "mark_processing")
        self.assertEqual(event.order_ids, order_ids)
        self.assertEqual(event.performed_by_id, 20)

    def test_bulk_order_action_executed_event_to_dict_serializes_payload(self):
        """Serialize bulk order action executed event payload correctly."""
        order_ids = [uuid.uuid4()]

        event = AdminBulkOrderActionExecutedEvent(
            action_type="mark_shipped",
            order_ids=order_ids,
            performed_by_id=None,
        )

        self.assertEqual(
            event.to_dict(),
            {
                "action_type": "mark_shipped",
                "order_ids": order_ids,
                "performed_by_id": None,
            },
        )


class AdminBulkOrderActionFailedEventTestCase(SimpleTestCase):
    def test_bulk_order_action_failed_event_stores_expected_payload(self):
        """Store the expected payload for bulk order action failed event."""
        order_ids = [uuid.uuid4()]

        event = AdminBulkOrderActionFailedEvent(
            action_type="cancel_orders",
            order_ids=order_ids,
            error_message="bulk failure",
            performed_by_id=30,
        )

        self.assertEqual(
            event.event_name,
            "admin_bulk_order_action_failed",
        )
        self.assertEqual(event.action_type, "cancel_orders")
        self.assertEqual(event.order_ids, order_ids)
        self.assertEqual(event.error_message, "bulk failure")
        self.assertEqual(event.performed_by_id, 30)

    def test_bulk_order_action_failed_event_allows_null_performed_by_id(self):
        """Allow performed_by_id to be None for failed bulk order event."""
        event = AdminBulkOrderActionFailedEvent(
            action_type="cancel_orders",
            order_ids=[],
            error_message="unexpected error",
            performed_by_id=None,
        )

        self.assertEqual(event.order_ids, [])
        self.assertEqual(event.error_message, "unexpected error")
        self.assertIsNone(event.performed_by_id)

    def test_bulk_order_action_failed_event_to_dict_serializes_payload(self):
        """Serialize bulk order action failed event payload correctly."""
        order_ids = [uuid.uuid4(), uuid.uuid4()]

        event = AdminBulkOrderActionFailedEvent(
            action_type="mark_processing",
            order_ids=order_ids,
            error_message="processing failed",
            performed_by_id=99,
        )

        self.assertEqual(
            event.to_dict(),
            {
                "action_type": "mark_processing",
                "order_ids": order_ids,
                "error_message": "processing failed",
                "performed_by_id": 99,
            },
        )


class AdminBulkReviewModerationExecutedEventTestCase(SimpleTestCase):
    def test_bulk_review_moderation_executed_event_stores_expected_payload(self):
        """Store the expected payload for bulk review moderation executed event."""
        review_ids = [uuid.uuid4(), uuid.uuid4()]

        event = AdminBulkReviewModerationExecutedEvent(
            moderation_action="approve",
            review_ids=review_ids,
            performed_by_id=40,
        )

        self.assertEqual(
            event.event_name,
            "admin_bulk_review_moderation_executed",
        )
        self.assertEqual(event.moderation_action, "approve")
        self.assertEqual(event.review_ids, review_ids)
        self.assertEqual(event.performed_by_id, 40)

    def test_bulk_review_moderation_executed_event_to_dict_serializes_payload(
        self,
    ):
        """Serialize bulk review moderation executed event payload correctly."""
        review_ids = [uuid.uuid4()]

        event = AdminBulkReviewModerationExecutedEvent(
            moderation_action="hide",
            review_ids=review_ids,
            performed_by_id=None,
        )

        self.assertEqual(
            event.to_dict(),
            {
                "moderation_action": "hide",
                "review_ids": review_ids,
                "performed_by_id": None,
            },
        )


class AdminBulkReviewModerationFailedEventTestCase(SimpleTestCase):
    def test_bulk_review_moderation_failed_event_stores_expected_payload(self):
        """Store the expected payload for bulk review moderation failed event."""
        review_ids = [uuid.uuid4()]

        event = AdminBulkReviewModerationFailedEvent(
            moderation_action="reject",
            review_ids=review_ids,
            error_message="moderation failed",
            performed_by_id=50,
        )

        self.assertEqual(
            event.event_name,
            "admin_bulk_review_moderation_failed",
        )
        self.assertEqual(event.moderation_action, "reject")
        self.assertEqual(event.review_ids, review_ids)
        self.assertEqual(event.error_message, "moderation failed")
        self.assertEqual(event.performed_by_id, 50)

    def test_bulk_review_moderation_failed_event_allows_null_performed_by_id(self):
        """Allow performed_by_id to be None for failed bulk review event."""
        event = AdminBulkReviewModerationFailedEvent(
            moderation_action="restore",
            review_ids=[],
            error_message="unexpected moderation error",
            performed_by_id=None,
        )

        self.assertEqual(event.review_ids, [])
        self.assertEqual(event.error_message, "unexpected moderation error")
        self.assertIsNone(event.performed_by_id)

    def test_bulk_review_moderation_failed_event_to_dict_serializes_payload(
        self,
    ):
        """Serialize bulk review moderation failed event payload correctly."""
        review_ids = [uuid.uuid4(), uuid.uuid4()]

        event = AdminBulkReviewModerationFailedEvent(
            moderation_action="approve",
            review_ids=review_ids,
            error_message="approval failed",
            performed_by_id=88,
        )

        self.assertEqual(
            event.to_dict(),
            {
                "moderation_action": "approve",
                "review_ids": review_ids,
                "error_message": "approval failed",
                "performed_by_id": 88,
            },
        )


class AdminNotificationRetryExecutedEventTestCase(SimpleTestCase):
    def test_notification_retry_executed_event_stores_expected_payload(self):
        """Store the expected payload for notification retry executed event."""
        notification_ids = [uuid.uuid4(), uuid.uuid4()]

        event = AdminNotificationRetryExecutedEvent(
            notification_ids=notification_ids,
            performed_by_id=60,
        )

        self.assertEqual(
            event.event_name,
            "admin_notification_retry_executed",
        )
        self.assertEqual(event.notification_ids, notification_ids)
        self.assertEqual(event.performed_by_id, 60)

    def test_notification_retry_executed_event_to_dict_serializes_payload(
        self,
    ):
        """Serialize notification retry executed event payload correctly."""
        notification_ids = [uuid.uuid4()]

        event = AdminNotificationRetryExecutedEvent(
            notification_ids=notification_ids,
            performed_by_id=None,
        )

        self.assertEqual(
            event.to_dict(),
            {
                "notification_ids": notification_ids,
                "performed_by_id": None,
            },
        )


class AdminNotificationRetryFailedEventTestCase(SimpleTestCase):
    def test_notification_retry_failed_event_stores_expected_payload(self):
        """Store the expected payload for notification retry failed event."""
        notification_ids = [uuid.uuid4()]

        event = AdminNotificationRetryFailedEvent(
            notification_ids=notification_ids,
            error_message="retry failed",
            performed_by_id=70,
        )

        self.assertEqual(
            event.event_name,
            "admin_notification_retry_failed",
        )
        self.assertEqual(event.notification_ids, notification_ids)
        self.assertEqual(event.error_message, "retry failed")
        self.assertEqual(event.performed_by_id, 70)

    def test_notification_retry_failed_event_allows_null_performed_by_id(self):
        """Allow performed_by_id to be None for failed notification retry event."""
        event = AdminNotificationRetryFailedEvent(
            notification_ids=[],
            error_message="unexpected retry error",
            performed_by_id=None,
        )

        self.assertEqual(event.notification_ids, [])
        self.assertEqual(event.error_message, "unexpected retry error")
        self.assertIsNone(event.performed_by_id)

    def test_notification_retry_failed_event_to_dict_serializes_payload(
        self,
    ):
        """Serialize notification retry failed event payload correctly."""
        notification_ids = [uuid.uuid4(), uuid.uuid4()]

        event = AdminNotificationRetryFailedEvent(
            notification_ids=notification_ids,
            error_message="provider failure",
            performed_by_id=77,
        )

        self.assertEqual(
            event.to_dict(),
            {
                "notification_ids": notification_ids,
                "error_message": "provider failure",
                "performed_by_id": 77,
            },
        )


class AdminDashboardAlertGeneratedEventTestCase(SimpleTestCase):
    def test_dashboard_alert_generated_event_stores_expected_payload(self):
        """Store the expected payload for dashboard alert generated event."""
        metadata = {"alerts_count": 3, "severity": "critical"}

        event = AdminDashboardAlertGeneratedEvent(
            alert_type="failed_payments",
            alert_message="Failed payments detected.",
            metadata=metadata,
        )

        self.assertEqual(
            event.event_name,
            "admin_dashboard_alert_generated",
        )
        self.assertEqual(event.alert_type, "failed_payments")
        self.assertEqual(
            event.alert_message,
            "Failed payments detected.",
        )
        self.assertEqual(event.metadata, metadata)

    def test_dashboard_alert_generated_event_defaults_metadata_to_empty_dict(
        self,
    ):
        """Default metadata to an empty dictionary when omitted."""
        event = AdminDashboardAlertGeneratedEvent(
            alert_type="low_stock_products",
            alert_message="Low stock products detected.",
        )

        self.assertEqual(event.metadata, {})

    def test_dashboard_alert_generated_event_to_dict_serializes_payload(self):
        """Serialize dashboard alert generated event payload correctly."""
        event = AdminDashboardAlertGeneratedEvent(
            alert_type="pending_orders",
            alert_message="Pending orders require attention.",
            metadata={"value": 5},
        )

        self.assertEqual(
            event.to_dict(),
            {
                "alert_type": "pending_orders",
                "alert_message": "Pending orders require attention.",
                "metadata": {"value": 5},
            },
        )


class DomainEventRegistryTestCase(SimpleTestCase):
    def test_event_handler_registry_contains_dashboard_accessed_event_mapping(
        self,
    ):
        """Register the dashboard accessed handler for dashboard accessed event."""
        self.assertIn(AdminDashboardAccessedEvent, EVENT_HANDLER_REGISTRY)
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[AdminDashboardAccessedEvent],
            [handle_admin_dashboard_accessed],
        )

    def test_event_handler_registry_contains_bulk_order_executed_event_mapping(
        self,
    ):
        """Register the bulk order executed handler for its event."""
        self.assertIn(
            AdminBulkOrderActionExecutedEvent,
            EVENT_HANDLER_REGISTRY,
        )
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[AdminBulkOrderActionExecutedEvent],
            [handle_admin_bulk_order_action_executed],
        )

    def test_event_handler_registry_contains_bulk_order_failed_event_mapping(
        self,
    ):
        """Register the bulk order failed handler for its event."""
        self.assertIn(
            AdminBulkOrderActionFailedEvent,
            EVENT_HANDLER_REGISTRY,
        )
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[AdminBulkOrderActionFailedEvent],
            [handle_admin_bulk_order_action_failed],
        )

    def test_event_handler_registry_contains_bulk_review_executed_event_mapping(
        self,
    ):
        """Register the bulk review moderation executed handler for its event."""
        self.assertIn(
            AdminBulkReviewModerationExecutedEvent,
            EVENT_HANDLER_REGISTRY,
        )
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[AdminBulkReviewModerationExecutedEvent],
            [handle_admin_bulk_review_moderation_executed],
        )

    def test_event_handler_registry_contains_bulk_review_failed_event_mapping(
        self,
    ):
        """Register the bulk review moderation failed handler for its event."""
        self.assertIn(
            AdminBulkReviewModerationFailedEvent,
            EVENT_HANDLER_REGISTRY,
        )
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[AdminBulkReviewModerationFailedEvent],
            [handle_admin_bulk_review_moderation_failed],
        )

    def test_event_handler_registry_contains_notification_retry_executed_event_mapping(
        self,
    ):
        """Register the notification retry executed handler for its event."""
        self.assertIn(
            AdminNotificationRetryExecutedEvent,
            EVENT_HANDLER_REGISTRY,
        )
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[AdminNotificationRetryExecutedEvent],
            [handle_admin_notification_retry_executed],
        )

    def test_event_handler_registry_contains_notification_retry_failed_event_mapping(
        self,
    ):
        """Register the notification retry failed handler for its event."""
        self.assertIn(
            AdminNotificationRetryFailedEvent,
            EVENT_HANDLER_REGISTRY,
        )
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[AdminNotificationRetryFailedEvent],
            [handle_admin_notification_retry_failed],
        )

    def test_event_handler_registry_contains_alert_generated_event_mapping(
        self,
    ):
        """Register the dashboard alert generated handler for its event."""
        self.assertIn(
            AdminDashboardAlertGeneratedEvent,
            EVENT_HANDLER_REGISTRY,
        )
        self.assertEqual(
            EVENT_HANDLER_REGISTRY[AdminDashboardAlertGeneratedEvent],
            [handle_admin_dashboard_alert_generated],
        )


class DomainEventDispatcherTestCase(SimpleTestCase):
    def test_dispatch_calls_registered_handler_for_dashboard_accessed_event(
        self,
    ):
        """Dispatch dashboard accessed event to its registered handler."""
        event = AdminDashboardAccessedEvent(user_id=1)

        captured_events = []

        def handler(event_obj):
            captured_events.append(event_obj)

        with patch(
            "ech.admin_dashboard.domain_events.dispatcher.EVENT_HANDLER_REGISTRY",
            {AdminDashboardAccessedEvent: [handler]},
        ):
            DomainEventDispatcher.dispatch(event)

        self.assertEqual(captured_events, [event])

    def test_dispatch_calls_multiple_registered_handlers(self):
        """Dispatch event to all handlers registered for its class."""
        event = AdminNotificationRetryExecutedEvent(
            notification_ids=[uuid.uuid4()],
            performed_by_id=2,
        )

        captured_calls = []

        def handler_one(event_obj):
            captured_calls.append(("handler_one", event_obj))

        def handler_two(event_obj):
            captured_calls.append(("handler_two", event_obj))

        with patch(
            "ech.admin_dashboard.domain_events.dispatcher.EVENT_HANDLER_REGISTRY",
            {
                AdminNotificationRetryExecutedEvent: [
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
            "ech.admin_dashboard.domain_events.dispatcher.EVENT_HANDLER_REGISTRY",
            {},
        ):
            DomainEventDispatcher.dispatch(event)


class DomainEventHandlersTestCase(SimpleTestCase):
    @patch("ech.admin_dashboard.domain_events.handlers.logger.info")
    def test_handle_admin_dashboard_accessed_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log the expected payload for dashboard accessed handler."""
        event = AdminDashboardAccessedEvent(user_id=10)

        handle_admin_dashboard_accessed(event)

        logger_info_mock.assert_called_once_with(
            "Handled admin dashboard accessed domain event.",
            extra={
                "event_name": "admin_dashboard_accessed",
                "user_id": 10,
            },
        )

    @patch("ech.admin_dashboard.domain_events.handlers.logger.info")
    def test_handle_admin_bulk_order_action_executed_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log the expected payload for bulk order action executed handler."""
        order_ids = [uuid.uuid4(), uuid.uuid4()]

        event = AdminBulkOrderActionExecutedEvent(
            action_type="mark_processing",
            order_ids=order_ids,
            performed_by_id=20,
        )

        handle_admin_bulk_order_action_executed(event)

        logger_info_mock.assert_called_once_with(
            "Handled admin bulk order action executed event.",
            extra={
                "event_name": "admin_bulk_order_action_executed",
                "action_type": "mark_processing",
                "order_ids": order_ids,
                "performed_by_id": 20,
            },
        )

    @patch("ech.admin_dashboard.domain_events.handlers.logger.warning")
    def test_handle_admin_bulk_order_action_failed_logs_expected_payload(
        self,
        logger_warning_mock,
    ):
        """Log the expected payload for bulk order action failed handler."""
        order_ids = [uuid.uuid4()]

        event = AdminBulkOrderActionFailedEvent(
            action_type="cancel_orders",
            order_ids=order_ids,
            error_message="order failure",
            performed_by_id=30,
        )

        handle_admin_bulk_order_action_failed(event)

        logger_warning_mock.assert_called_once_with(
            "Handled admin bulk order action failed event.",
            extra={
                "event_name": "admin_bulk_order_action_failed",
                "action_type": "cancel_orders",
                "order_ids": order_ids,
                "error_message": "order failure",
                "performed_by_id": 30,
            },
        )

    @patch("ech.admin_dashboard.domain_events.handlers.logger.info")
    def test_handle_admin_bulk_review_moderation_executed_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log the expected payload for bulk review moderation executed handler."""
        review_ids = [uuid.uuid4(), uuid.uuid4()]

        event = AdminBulkReviewModerationExecutedEvent(
            moderation_action="approve",
            review_ids=review_ids,
            performed_by_id=40,
        )

        handle_admin_bulk_review_moderation_executed(event)

        logger_info_mock.assert_called_once_with(
            "Handled admin bulk review moderation executed event.",
            extra={
                "event_name": "admin_bulk_review_moderation_executed",
                "moderation_action": "approve",
                "review_ids": review_ids,
                "performed_by_id": 40,
            },
        )

    @patch("ech.admin_dashboard.domain_events.handlers.logger.warning")
    def test_handle_admin_bulk_review_moderation_failed_logs_expected_payload(
        self,
        logger_warning_mock,
    ):
        """Log the expected payload for bulk review moderation failed handler."""
        review_ids = [uuid.uuid4()]

        event = AdminBulkReviewModerationFailedEvent(
            moderation_action="reject",
            review_ids=review_ids,
            error_message="review failure",
            performed_by_id=50,
        )

        handle_admin_bulk_review_moderation_failed(event)

        logger_warning_mock.assert_called_once_with(
            "Handled admin bulk review moderation failed event.",
            extra={
                "event_name": "admin_bulk_review_moderation_failed",
                "moderation_action": "reject",
                "review_ids": review_ids,
                "error_message": "review failure",
                "performed_by_id": 50,
            },
        )

    @patch("ech.admin_dashboard.domain_events.handlers.logger.info")
    def test_handle_admin_notification_retry_executed_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log the expected payload for notification retry executed handler."""
        notification_ids = [uuid.uuid4(), uuid.uuid4()]

        event = AdminNotificationRetryExecutedEvent(
            notification_ids=notification_ids,
            performed_by_id=60,
        )

        handle_admin_notification_retry_executed(event)

        logger_info_mock.assert_called_once_with(
            "Handled admin notification retry executed event.",
            extra={
                "event_name": "admin_notification_retry_executed",
                "notification_ids": notification_ids,
                "performed_by_id": 60,
            },
        )

    @patch("ech.admin_dashboard.domain_events.handlers.logger.warning")
    def test_handle_admin_notification_retry_failed_logs_expected_payload(
        self,
        logger_warning_mock,
    ):
        """Log the expected payload for notification retry failed handler."""
        notification_ids = [uuid.uuid4()]

        event = AdminNotificationRetryFailedEvent(
            notification_ids=notification_ids,
            error_message="retry failure",
            performed_by_id=70,
        )

        handle_admin_notification_retry_failed(event)

        logger_warning_mock.assert_called_once_with(
            "Handled admin notification retry failed event.",
            extra={
                "event_name": "admin_notification_retry_failed",
                "notification_ids": notification_ids,
                "error_message": "retry failure",
                "performed_by_id": 70,
            },
        )

    @patch("ech.admin_dashboard.domain_events.handlers.logger.warning")
    def test_handle_admin_dashboard_alert_generated_logs_expected_payload(
        self,
        logger_warning_mock,
    ):
        """Log the expected payload for dashboard alert generated handler."""
        event = AdminDashboardAlertGeneratedEvent(
            alert_type="failed_payments",
            alert_message="Failed payments detected.",
            metadata={"alerts_count": 3},
        )

        handle_admin_dashboard_alert_generated(event)

        logger_warning_mock.assert_called_once_with(
            "Handled admin dashboard alert generated event.",
            extra={
                "event_name": "admin_dashboard_alert_generated",
                "alert_type": "failed_payments",
                "alert_message": "Failed payments detected.",
                "metadata": {"alerts_count": 3},
            },
        )