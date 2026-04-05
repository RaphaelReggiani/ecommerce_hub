from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from ech.notifications.exceptions import (
    InvalidNotificationOperationException,
    NotificationDeliveryFailedException,
)
from ech.notifications.models import (
    Notification,
    NotificationDelivery,
    NotificationEvent,
    NotificationLifecycle,
)
from ech.notifications.services.notification_delivery_service import (
    NotificationDeliveryService,
)


User = get_user_model()


class BaseNotificationDeliveryFactoryMixin:
    def create_user(self, **kwargs):
        suffix = uuid.uuid4().hex[:8]

        data = {
            "email": f"user_{suffix}@test.com",
            "password": "StrongPassword123",
            "user_name": f"User {suffix}",
            "role": User.ROLE_CUSTOMER_USER,
            "is_active": True,
            "email_confirmed": True,
        }

        data.update(kwargs)
        return User.objects.create_user(**data)

    def create_notification(self, **kwargs):
        recipient = kwargs.pop("recipient", None) or self.create_user()
        created_by = kwargs.pop("created_by", None)

        data = {
            "recipient": recipient,
            "created_by": created_by,
            "notification_type": "order_shipped",
            "title": "Order shipped",
            "message": "Your order has been shipped.",
            "status": Notification.STATUS_PENDING,
            "channel": Notification.CHANNEL_IN_APP,
            "priority": Notification.PRIORITY_NORMAL,
            "source_module": "orders",
            "source_event": "order_shipped",
            "source_object_id": "ORDER-001",
            "metadata": {"source": "unit-test"},
        }

        data.update(kwargs)

        notification = Notification.objects.create(**data)
        NotificationLifecycle.objects.create(notification=notification)
        return notification


class NotificationDeliveryServiceTestCase(
    BaseNotificationDeliveryFactoryMixin,
    TestCase,
):
    @patch(
        "ech.notifications.services.notification_delivery_service."
        "NotificationStatusService.mark_as_unread_after_dispatch"
    )
    @patch(
        "ech.notifications.services.notification_delivery_service."
        "NotificationLogService.log_notification_dispatched"
    )
    @patch(
        "ech.notifications.services.notification_delivery_service."
        "NotificationLogService.log_notification_delivery_succeeded"
    )
    @patch(
        "ech.notifications.services.notification_delivery_service."
        "DomainEventDispatcher.dispatch"
    )
    @patch(
        "ech.notifications.services.notification_delivery_service."
        "InAppProvider.deliver"
    )
    def test_dispatch_notification_success_in_app(
        self,
        in_app_deliver_mock,
        dispatch_mock,
        log_delivery_succeeded_mock,
        log_dispatched_mock,
        mark_as_unread_after_dispatch_mock,
    ):
        """Dispatch notification successfully through in-app provider."""
        notification = self.create_notification(
            status=Notification.STATUS_PENDING,
            channel=Notification.CHANNEL_IN_APP,
        )

        in_app_deliver_mock.return_value = {
            "status": NotificationDelivery.STATUS_DELIVERED,
            "provider_name": "in_app_provider",
            "recipient_address": "",
            "external_message_id": "",
            "metadata": {"provider": "in-app"},
        }

        mark_as_unread_after_dispatch_mock.return_value = notification

        result = NotificationDeliveryService.dispatch_notification(
            notification=notification,
        )

        self.assertEqual(result, notification)

        in_app_deliver_mock.assert_called_once_with(
            notification=notification,
        )

        self.assertEqual(NotificationDelivery.objects.count(), 1)
        self.assertEqual(NotificationEvent.objects.count(), 2)

        delivery = NotificationDelivery.objects.get()
        self.assertEqual(delivery.channel, NotificationDelivery.CHANNEL_IN_APP)
        self.assertEqual(delivery.status, NotificationDelivery.STATUS_DELIVERED)
        self.assertEqual(delivery.provider_name, "in_app_provider")
        self.assertEqual(delivery.metadata, {"provider": "in-app"})

        events = list(notification.events.order_by("created_at"))
        self.assertEqual(events[0].event_type, NotificationEvent.TYPE_DELIVERY_SENT)
        self.assertEqual(events[1].event_type, NotificationEvent.TYPE_DISPATCHED)

        mark_as_unread_after_dispatch_mock.assert_called_once_with(
            notification=notification,
            performed_by=None,
            metadata={
                "successful_channels": [
                    NotificationDelivery.CHANNEL_IN_APP,
                ],
            },
        )

        log_delivery_succeeded_mock.assert_called_once_with(
            notification=notification,
            delivery=delivery,
            performed_by=None,
        )
        log_dispatched_mock.assert_called_once_with(
            notification=notification,
            performed_by=None,
        )

        self.assertEqual(dispatch_mock.call_count, 2)

    @patch(
        "ech.notifications.services.notification_delivery_service."
        "NotificationStatusService.mark_as_failed"
    )
    @patch(
        "ech.notifications.services.notification_delivery_service."
        "NotificationLogService.log_notification_delivery_failed"
    )
    @patch(
        "ech.notifications.services.notification_delivery_service."
        "DomainEventDispatcher.dispatch"
    )
    @patch(
        "ech.notifications.services.notification_delivery_service."
        "InAppProvider.deliver"
    )
    def test_dispatch_notification_failure_marks_failed(
        self,
        in_app_deliver_mock,
        dispatch_mock,
        log_delivery_failed_mock,
        mark_as_failed_mock,
    ):
        """Mark notification as failed when all delivery attempts fail."""
        notification = self.create_notification(
            status=Notification.STATUS_PENDING,
            channel=Notification.CHANNEL_IN_APP,
        )

        in_app_deliver_mock.side_effect = Exception("SMTP failure")

        with self.assertRaises(NotificationDeliveryFailedException):
            NotificationDeliveryService.dispatch_notification(
                notification=notification,
            )

        in_app_deliver_mock.assert_called_once_with(
            notification=notification,
        )

        mark_as_failed_mock.assert_called_once_with(
            notification=notification,
            failure_code="delivery_failed",
            failure_message="All delivery attempts failed.",
            performed_by=None,
            metadata={
                "failed_channels": [
                    NotificationDelivery.CHANNEL_IN_APP,
                ],
            },
        )

        log_delivery_failed_mock.assert_called_once()
        self.assertEqual(dispatch_mock.call_count, 2)

        # Transaction is rolled back after NotificationDeliveryFailedException,
        # so failed delivery/event records are not expected to remain persisted.
        self.assertEqual(NotificationDelivery.objects.count(), 0)
        self.assertEqual(NotificationEvent.objects.count(), 0)

    def test_dispatch_notification_raises_when_status_not_pending(self):
        """Raise exception when notification cannot be dispatched."""
        notification = self.create_notification(
            status=Notification.STATUS_READ,
        )

        with self.assertRaises(InvalidNotificationOperationException):
            NotificationDeliveryService.dispatch_notification(
                notification=notification,
            )

    def test_validate_can_dispatch_allows_pending(self):
        """Allow dispatch validation for pending notification."""
        notification = self.create_notification(
            status=Notification.STATUS_PENDING,
        )

        NotificationDeliveryService._validate_can_dispatch(
            notification=notification,
        )

    def test_validate_can_dispatch_raises_for_read(self):
        """Raise exception when notification already read."""
        notification = self.create_notification(
            status=Notification.STATUS_READ,
        )

        with self.assertRaises(InvalidNotificationOperationException):
            NotificationDeliveryService._validate_can_dispatch(
                notification=notification,
            )

    def test_validate_can_dispatch_raises_for_archived(self):
        """Raise exception when notification already archived."""
        notification = self.create_notification(
            status=Notification.STATUS_ARCHIVED,
        )

        with self.assertRaises(InvalidNotificationOperationException):
            NotificationDeliveryService._validate_can_dispatch(
                notification=notification,
            )

    def test_validate_can_dispatch_raises_for_cancelled(self):
        """Raise exception when notification cancelled."""
        notification = self.create_notification(
            status=Notification.STATUS_CANCELLED,
        )

        with self.assertRaises(InvalidNotificationOperationException):
            NotificationDeliveryService._validate_can_dispatch(
                notification=notification,
            )