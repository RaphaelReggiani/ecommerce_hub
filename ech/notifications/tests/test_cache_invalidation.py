import uuid
from unittest.mock import patch

from django.core.cache import cache
from django.test import TransactionTestCase

from ech.users.models import CustomUser
from ech.notifications.models import (
    Notification,
    NotificationLifecycle,
)
from ech.notifications.selectors import (
    get_notification_by_id,
    list_management_notifications,
    list_recipient_notifications,
)
from ech.notifications.services.notification_creation_service import (
    NotificationCreationService,
)
from ech.notifications.services.notification_status_service import (
    NotificationStatusService,
)
from ech.notifications.services.notification_cancellation_service import (
    NotificationCancellationService,
)
from ech.notifications.services.notification_delivery_service import (
    NotificationDeliveryService,
)


class NotificationCacheInvalidationTestCase(TransactionTestCase):
    def setUp(self):
        cache.clear()

        self.recipient = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.staff = CustomUser.objects.create_user(
            email="ops@company.com",
            password="StrongPassword123",
            user_name="Operations Staff",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        self.notification = Notification.objects.create(
            recipient=self.recipient,
            created_by=self.staff,
            notification_type="order_shipped",
            title="Order shipped",
            message="Your order has been shipped.",
            status=Notification.STATUS_PENDING,
            channel=Notification.CHANNEL_IN_APP,
            priority=Notification.PRIORITY_NORMAL,
            source_module="orders",
            source_event="order_shipped",
            source_object_id="ORDER-001",
            metadata={"source": "unit-test"},
            idempotency_key=uuid.uuid4(),
        )

        NotificationLifecycle.objects.create(
            notification=self.notification,
        )

    def test_creation_service_invalidates_recipient_and_management_lists(self):
        """Invalidate recipient and management list caches after notification creation."""
        recipient_before = list(
            list_recipient_notifications(recipient=self.recipient)
        )
        management_before = list(
            list_management_notifications()
        )

        self.assertEqual(len(recipient_before), 1)
        self.assertEqual(len(management_before), 1)

        NotificationCreationService.create_notification(
            recipient=self.recipient,
            created_by=self.staff,
            notification_type="payment_captured",
            title="Payment captured",
            message="Your payment has been captured.",
            channel=Notification.CHANNEL_EMAIL,
            priority=Notification.PRIORITY_HIGH,
            source_module="payments",
            source_event="payment_captured",
            source_object_id="PAY-001",
            metadata={"source": "unit-test"},
            idempotency_key=uuid.uuid4(),
            performed_by=self.staff,
        )

        recipient_after = list(
            list_recipient_notifications(recipient=self.recipient)
        )
        management_after = list(
            list_management_notifications()
        )

        self.assertEqual(len(recipient_after), 2)
        self.assertEqual(len(management_after), 2)

    def test_status_service_invalidates_detail_cache(self):
        """Invalidate notification detail cache after status transition."""
        cached_notification = get_notification_by_id(
            notification_id=self.notification.id
        )
        self.assertEqual(cached_notification.status, Notification.STATUS_PENDING)

        NotificationStatusService.update_status(
            notification=self.notification,
            new_status=Notification.STATUS_UNREAD,
            performed_by=self.staff,
        )

        fresh_notification = get_notification_by_id(
            notification_id=self.notification.id
        )
        self.assertEqual(fresh_notification.status, Notification.STATUS_UNREAD)

    def test_cancellation_service_invalidates_detail_cache(self):
        """Invalidate notification detail cache after notification cancellation."""
        cached_notification = get_notification_by_id(
            notification_id=self.notification.id
        )
        self.assertEqual(cached_notification.status, Notification.STATUS_PENDING)

        NotificationCancellationService.cancel_notification(
            notification=self.notification,
            performed_by=self.staff,
        )

        fresh_notification = get_notification_by_id(
            notification_id=self.notification.id
        )
        self.assertEqual(fresh_notification.status, Notification.STATUS_CANCELLED)

    @patch(
        "ech.notifications.services.notification_delivery_service."
        "InAppProvider.deliver"
    )
    def test_delivery_service_invalidates_detail_cache_after_successful_dispatch(
        self,
        in_app_deliver_mock,
    ):
        """Invalidate notification detail cache after successful notification dispatch."""
        cached_notification = get_notification_by_id(
            notification_id=self.notification.id
        )
        self.assertEqual(cached_notification.status, Notification.STATUS_PENDING)

        in_app_deliver_mock.return_value = {
            "status": "delivered",
            "provider_name": "in_app_provider",
            "recipient_address": "",
            "external_message_id": "",
            "metadata": {"provider": "in-app"},
        }

        NotificationDeliveryService.dispatch_notification(
            notification=self.notification,
            performed_by=self.staff,
        )

        fresh_notification = get_notification_by_id(
            notification_id=self.notification.id
        )
        self.assertEqual(fresh_notification.status, Notification.STATUS_UNREAD)