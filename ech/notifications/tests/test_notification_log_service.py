from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from ech.notifications.models import (
    Notification,
    NotificationDelivery,
)
from ech.notifications.services.notification_log_service import (
    NotificationLogService,
)


User = get_user_model()


class BaseNotificationLoggingFactoryMixin:
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

    def create_delivery(self, **kwargs):
        notification = kwargs.pop("notification")
        performed_by = kwargs.pop("performed_by", None)

        data = {
            "notification": notification,
            "channel": NotificationDelivery.CHANNEL_IN_APP,
            "status": NotificationDelivery.STATUS_DELIVERED,
            "provider_name": "in_app_provider",
            "recipient_address": "",
            "external_message_id": "",
            "failure_code": "",
            "failure_message": "",
            "metadata": {"provider": "in-app"},
            "performed_by": performed_by,
        }
        data.update(kwargs)
        return NotificationDelivery.objects.create(**data)


class NotificationLogServiceTestCase(
    BaseNotificationLoggingFactoryMixin,
    TestCase,
):
    @patch("ech.notifications.services.notification_log_service.logger.info")
    def test_log_notification_created_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log notification creation with expected structured payload."""
        created_by = self.create_user(
            email="support@company.com",
            user_name="Support User",
            role=User.ROLE_SUPPORT_STAFF,
        )
        notification = self.create_notification(created_by=created_by)
        performed_by = self.create_user(
            email="ops@company.com",
            user_name="Operations User",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        NotificationLogService.log_notification_created(
            notification=notification,
            performed_by=performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Notification created.",
            extra={
                "notification_id": str(notification.id),
                "recipient_id": str(notification.recipient_id),
                "created_by_id": str(notification.created_by_id),
                "notification_type": notification.notification_type,
                "status": notification.status,
                "channel": notification.channel,
                "priority": notification.priority,
                "source_module": notification.source_module,
                "source_event": notification.source_event,
                "source_object_id": notification.source_object_id,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @patch("ech.notifications.services.notification_log_service.logger.info")
    def test_log_notification_created_logs_none_when_created_by_and_performed_by_missing(
        self,
        logger_info_mock,
    ):
        """Log notification creation with null creator and performer when omitted."""
        notification = self.create_notification(created_by=None)

        NotificationLogService.log_notification_created(
            notification=notification,
            performed_by=None,
        )

        logger_info_mock.assert_called_once_with(
            "Notification created.",
            extra={
                "notification_id": str(notification.id),
                "recipient_id": str(notification.recipient_id),
                "created_by_id": None,
                "notification_type": notification.notification_type,
                "status": notification.status,
                "channel": notification.channel,
                "priority": notification.priority,
                "source_module": notification.source_module,
                "source_event": notification.source_event,
                "source_object_id": notification.source_object_id,
                "performed_by_id": None,
            },
        )

    @patch("ech.notifications.services.notification_log_service.logger.info")
    def test_log_notification_status_changed_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log notification status transition with previous and new status."""
        created_by = self.create_user(
            email="support2@company.com",
            user_name="Support User 2",
            role=User.ROLE_SUPPORT_STAFF,
        )
        notification = self.create_notification(
            created_by=created_by,
            status=Notification.STATUS_READ,
            channel=Notification.CHANNEL_EMAIL,
            priority=Notification.PRIORITY_HIGH,
        )
        performed_by = self.create_user(
            email="ops2@company.com",
            user_name="Operations User 2",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        NotificationLogService.log_notification_status_changed(
            notification=notification,
            previous_status=Notification.STATUS_UNREAD,
            new_status=Notification.STATUS_READ,
            performed_by=performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Notification status changed.",
            extra={
                "notification_id": str(notification.id),
                "recipient_id": str(notification.recipient_id),
                "created_by_id": str(notification.created_by_id),
                "notification_type": notification.notification_type,
                "previous_status": Notification.STATUS_UNREAD,
                "new_status": Notification.STATUS_READ,
                "channel": notification.channel,
                "priority": notification.priority,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @patch("ech.notifications.services.notification_log_service.logger.info")
    def test_log_notification_cancelled_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log notification cancellation with current status."""
        created_by = self.create_user(
            email="support3@company.com",
            user_name="Support User 3",
            role=User.ROLE_SUPPORT_STAFF,
        )
        notification = self.create_notification(
            created_by=created_by,
            status=Notification.STATUS_CANCELLED,
            channel=Notification.CHANNEL_EMAIL,
            priority=Notification.PRIORITY_CRITICAL,
        )
        performed_by = self.create_user(
            email="ops3@company.com",
            user_name="Operations User 3",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        NotificationLogService.log_notification_cancelled(
            notification=notification,
            performed_by=performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Notification cancelled.",
            extra={
                "notification_id": str(notification.id),
                "recipient_id": str(notification.recipient_id),
                "created_by_id": str(notification.created_by_id),
                "notification_type": notification.notification_type,
                "status": notification.status,
                "channel": notification.channel,
                "priority": notification.priority,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @patch("ech.notifications.services.notification_log_service.logger.info")
    def test_log_notification_dispatched_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log notification dispatch with scheduling metadata."""
        created_by = self.create_user(
            email="support4@company.com",
            user_name="Support User 4",
            role=User.ROLE_SUPPORT_STAFF,
        )
        notification = self.create_notification(
            created_by=created_by,
            status=Notification.STATUS_UNREAD,
            channel=Notification.CHANNEL_EMAIL,
            priority=Notification.PRIORITY_HIGH,
        )
        performed_by = self.create_user(
            email="ops4@company.com",
            user_name="Operations User 4",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        NotificationLogService.log_notification_dispatched(
            notification=notification,
            performed_by=performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Notification dispatched.",
            extra={
                "notification_id": str(notification.id),
                "recipient_id": str(notification.recipient_id),
                "created_by_id": str(notification.created_by_id),
                "notification_type": notification.notification_type,
                "status": notification.status,
                "channel": notification.channel,
                "priority": notification.priority,
                "scheduled_for": (
                    notification.scheduled_for.isoformat()
                    if notification.scheduled_for
                    else None
                ),
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @patch("ech.notifications.services.notification_log_service.logger.info")
    def test_log_notification_delivery_succeeded_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log successful notification delivery with provider details."""
        created_by = self.create_user(
            email="support5@company.com",
            user_name="Support User 5",
            role=User.ROLE_SUPPORT_STAFF,
        )
        notification = self.create_notification(
            created_by=created_by,
            channel=Notification.CHANNEL_EMAIL,
        )
        performed_by = self.create_user(
            email="ops5@company.com",
            user_name="Operations User 5",
            role=User.ROLE_OPERATIONS_STAFF,
        )
        delivery = self.create_delivery(
            notification=notification,
            channel=NotificationDelivery.CHANNEL_EMAIL,
            status=NotificationDelivery.STATUS_DELIVERED,
            provider_name="email_provider",
            recipient_address="customer@test.com",
            external_message_id="msg-123",
            performed_by=performed_by,
        )

        NotificationLogService.log_notification_delivery_succeeded(
            notification=notification,
            delivery=delivery,
            performed_by=performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Notification delivery succeeded.",
            extra={
                "notification_id": str(notification.id),
                "recipient_id": str(notification.recipient_id),
                "created_by_id": str(notification.created_by_id),
                "notification_type": notification.notification_type,
                "delivery_id": str(delivery.id),
                "delivery_channel": delivery.channel,
                "delivery_status": delivery.status,
                "provider_name": delivery.provider_name,
                "recipient_address": delivery.recipient_address,
                "external_message_id": delivery.external_message_id,
                "processed_at": (
                    delivery.processed_at.isoformat()
                    if delivery.processed_at
                    else None
                ),
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @patch("ech.notifications.services.notification_log_service.logger.warning")
    def test_log_notification_delivery_failed_logs_expected_payload(
        self,
        logger_warning_mock,
    ):
        """Log failed notification delivery with failure details."""
        created_by = self.create_user(
            email="support6@company.com",
            user_name="Support User 6",
            role=User.ROLE_SUPPORT_STAFF,
        )
        notification = self.create_notification(
            created_by=created_by,
            channel=Notification.CHANNEL_EMAIL,
        )
        performed_by = self.create_user(
            email="ops6@company.com",
            user_name="Operations User 6",
            role=User.ROLE_OPERATIONS_STAFF,
        )
        delivery = self.create_delivery(
            notification=notification,
            channel=NotificationDelivery.CHANNEL_EMAIL,
            status=NotificationDelivery.STATUS_FAILED,
            provider_name="email_provider",
            recipient_address="customer@test.com",
            failure_code="SMTP_TIMEOUT",
            failure_message="SMTP timeout while sending email.",
            performed_by=performed_by,
        )

        NotificationLogService.log_notification_delivery_failed(
            notification=notification,
            delivery=delivery,
            performed_by=performed_by,
        )

        logger_warning_mock.assert_called_once_with(
            "Notification delivery failed.",
            extra={
                "notification_id": str(notification.id),
                "recipient_id": str(notification.recipient_id),
                "created_by_id": str(notification.created_by_id),
                "notification_type": notification.notification_type,
                "delivery_id": str(delivery.id),
                "delivery_channel": delivery.channel,
                "delivery_status": delivery.status,
                "provider_name": delivery.provider_name,
                "recipient_address": delivery.recipient_address,
                "failure_code": delivery.failure_code,
                "failure_message": delivery.failure_message,
                "processed_at": (
                    delivery.processed_at.isoformat()
                    if delivery.processed_at
                    else None
                ),
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )