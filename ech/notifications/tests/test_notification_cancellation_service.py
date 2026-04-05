from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from ech.notifications.exceptions import (
    NotificationAlreadyArchivedException,
    NotificationAlreadyCancelledException,
    NotificationAlreadyReadException,
)
from ech.notifications.models import Notification
from ech.notifications.services.notification_cancellation_service import (
    NotificationCancellationService,
)


User = get_user_model()


class BaseNotificationCancellationFactoryMixin:
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
        return Notification.objects.create(**data)


class NotificationCancellationServiceTestCase(
    BaseNotificationCancellationFactoryMixin,
    TestCase,
):
    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "DomainEventDispatcher.dispatch"
    )
    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "NotificationLogService.log_notification_cancelled"
    )
    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "NotificationStatusService.update_status"
    )
    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "NotificationCancelledEvent"
    )
    def test_cancel_notification_success(
        self,
        notification_cancelled_event_mock,
        update_status_mock,
        log_notification_cancelled_mock,
        dispatch_mock,
    ):
        """Cancel a notification successfully when business rules allow it."""
        notification = self.create_notification(status=Notification.STATUS_PENDING)
        performed_by = self.create_user(
            email="ops@company.com",
            user_name="Operations User",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        update_status_mock.return_value = notification

        result = NotificationCancellationService.cancel_notification(
            notification=notification,
            performed_by=performed_by,
            metadata={"source": "unit-test"},
        )

        self.assertEqual(result, notification)

        update_status_mock.assert_called_once_with(
            notification=notification,
            new_status=Notification.STATUS_CANCELLED,
            performed_by=performed_by,
            metadata={
                "action": "notification_cancelled",
                "source": "unit-test",
            },
        )

        log_notification_cancelled_mock.assert_called_once_with(
            notification=notification,
            performed_by=performed_by,
        )

        notification_cancelled_event_mock.assert_called_once_with(
            notification_id=notification.id,
            recipient_id=notification.recipient_id,
            performed_by_id=performed_by.id,
        )
        dispatch_mock.assert_called_once_with(
            notification_cancelled_event_mock.return_value
        )

    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "DomainEventDispatcher.dispatch"
    )
    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "NotificationLogService.log_notification_cancelled"
    )
    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "NotificationStatusService.update_status"
    )
    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "NotificationCancelledEvent"
    )
    def test_cancel_notification_success_without_metadata(
        self,
        notification_cancelled_event_mock,
        update_status_mock,
        log_notification_cancelled_mock,
        dispatch_mock,
    ):
        """Cancel a notification successfully with default cancellation metadata."""
        notification = self.create_notification(status=Notification.STATUS_UNREAD)
        update_status_mock.return_value = notification

        result = NotificationCancellationService.cancel_notification(
            notification=notification,
        )

        self.assertEqual(result, notification)

        update_status_mock.assert_called_once_with(
            notification=notification,
            new_status=Notification.STATUS_CANCELLED,
            performed_by=None,
            metadata={"action": "notification_cancelled"},
        )

        log_notification_cancelled_mock.assert_called_once_with(
            notification=notification,
            performed_by=None,
        )

        notification_cancelled_event_mock.assert_called_once_with(
            notification_id=notification.id,
            recipient_id=notification.recipient_id,
            performed_by_id=None,
        )
        dispatch_mock.assert_called_once_with(
            notification_cancelled_event_mock.return_value
        )

    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "DomainEventDispatcher.dispatch"
    )
    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "NotificationLogService.log_notification_cancelled"
    )
    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "NotificationStatusService.update_status"
    )
    def test_cancel_notification_does_not_call_side_effects_when_already_cancelled(
        self,
        update_status_mock,
        log_notification_cancelled_mock,
        dispatch_mock,
    ):
        """Do not execute side effects when notification is already cancelled."""
        notification = self.create_notification(status=Notification.STATUS_CANCELLED)

        with self.assertRaises(NotificationAlreadyCancelledException):
            NotificationCancellationService.cancel_notification(
                notification=notification
            )

        update_status_mock.assert_not_called()
        log_notification_cancelled_mock.assert_not_called()
        dispatch_mock.assert_not_called()

    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "DomainEventDispatcher.dispatch"
    )
    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "NotificationLogService.log_notification_cancelled"
    )
    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "NotificationStatusService.update_status"
    )
    def test_cancel_notification_does_not_call_side_effects_when_already_read(
        self,
        update_status_mock,
        log_notification_cancelled_mock,
        dispatch_mock,
    ):
        """Do not execute side effects when notification is already read."""
        notification = self.create_notification(status=Notification.STATUS_READ)

        with self.assertRaises(NotificationAlreadyReadException):
            NotificationCancellationService.cancel_notification(
                notification=notification
            )

        update_status_mock.assert_not_called()
        log_notification_cancelled_mock.assert_not_called()
        dispatch_mock.assert_not_called()

    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "DomainEventDispatcher.dispatch"
    )
    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "NotificationLogService.log_notification_cancelled"
    )
    @patch(
        "ech.notifications.services.notification_cancellation_service."
        "NotificationStatusService.update_status"
    )
    def test_cancel_notification_does_not_call_side_effects_when_already_archived(
        self,
        update_status_mock,
        log_notification_cancelled_mock,
        dispatch_mock,
    ):
        """Do not execute side effects when notification is already archived."""
        notification = self.create_notification(status=Notification.STATUS_ARCHIVED)

        with self.assertRaises(NotificationAlreadyArchivedException):
            NotificationCancellationService.cancel_notification(
                notification=notification
            )

        update_status_mock.assert_not_called()
        log_notification_cancelled_mock.assert_not_called()
        dispatch_mock.assert_not_called()

    def test_validate_can_be_cancelled_allows_pending_status(self):
        """Allow cancellation validation for pending notification."""
        notification = self.create_notification(status=Notification.STATUS_PENDING)

        NotificationCancellationService._validate_can_be_cancelled(
            notification=notification,
        )

    def test_validate_can_be_cancelled_allows_unread_status(self):
        """Allow cancellation validation for unread notification."""
        notification = self.create_notification(status=Notification.STATUS_UNREAD)

        NotificationCancellationService._validate_can_be_cancelled(
            notification=notification,
        )

    def test_validate_can_be_cancelled_allows_failed_status(self):
        """Allow cancellation validation for failed notification."""
        notification = self.create_notification(status=Notification.STATUS_FAILED)

        NotificationCancellationService._validate_can_be_cancelled(
            notification=notification,
        )

    def test_validate_can_be_cancelled_raises_for_cancelled_status(self):
        """Raise NotificationAlreadyCancelledException for cancelled notification."""
        notification = self.create_notification(status=Notification.STATUS_CANCELLED)

        with self.assertRaises(NotificationAlreadyCancelledException):
            NotificationCancellationService._validate_can_be_cancelled(
                notification=notification,
            )

    def test_validate_can_be_cancelled_raises_for_read_status(self):
        """Raise NotificationAlreadyReadException for read notification."""
        notification = self.create_notification(status=Notification.STATUS_READ)

        with self.assertRaises(NotificationAlreadyReadException):
            NotificationCancellationService._validate_can_be_cancelled(
                notification=notification,
            )

    def test_validate_can_be_cancelled_raises_for_archived_status(self):
        """Raise NotificationAlreadyArchivedException for archived notification."""
        notification = self.create_notification(status=Notification.STATUS_ARCHIVED)

        with self.assertRaises(NotificationAlreadyArchivedException):
            NotificationCancellationService._validate_can_be_cancelled(
                notification=notification,
            )