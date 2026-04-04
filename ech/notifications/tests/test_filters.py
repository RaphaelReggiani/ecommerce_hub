import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.notifications.filters import (
    NotificationFilter,
    NotificationManagementFilter,
)
from ech.notifications.models import Notification


User = get_user_model()


class BaseNotificationFilterFactoryMixin:
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
            "source_object_id": str(uuid.uuid4()),
            "scheduled_for": timezone.now() + timedelta(hours=2),
            "metadata": {"source": "unit-test"},
        }
        data.update(kwargs)

        return Notification.objects.create(**data)


class NotificationFilterTestCase(BaseNotificationFilterFactoryMixin, TestCase):
    def setUp(self):
        self.recipient = self.create_user()

        self.notification_1 = self.create_notification(
            recipient=self.recipient,
            status=Notification.STATUS_PENDING,
            channel=Notification.CHANNEL_IN_APP,
            priority=Notification.PRIORITY_NORMAL,
            notification_type="order_shipped",
            source_module="orders",
        )

        self.notification_2 = self.create_notification(
            recipient=self.recipient,
            status=Notification.STATUS_UNREAD,
            channel=Notification.CHANNEL_EMAIL,
            priority=Notification.PRIORITY_HIGH,
            notification_type="payment_captured",
            source_module="payments",
        )

    def test_filter_by_status(self):
        """Filter notifications by exact status."""
        queryset = Notification.objects.all()

        filtered = NotificationFilter(
            {"status": Notification.STATUS_PENDING},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.notification_1)

    def test_filter_by_channel(self):
        """Filter notifications by exact channel."""
        queryset = Notification.objects.all()

        filtered = NotificationFilter(
            {"channel": Notification.CHANNEL_EMAIL},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.notification_2)

    def test_filter_by_priority(self):
        """Filter notifications by exact priority."""
        queryset = Notification.objects.all()

        filtered = NotificationFilter(
            {"priority": Notification.PRIORITY_HIGH},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.notification_2)

    def test_filter_by_notification_type_icontains(self):
        """Filter notifications using partial notification type match."""
        queryset = Notification.objects.all()

        filtered = NotificationFilter(
            {"notification_type": "order"},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.notification_1)

    def test_filter_by_source_module_icontains(self):
        """Filter notifications using partial source module match."""
        queryset = Notification.objects.all()

        filtered = NotificationFilter(
            {"source_module": "pay"},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.notification_2)

    def test_filter_created_after(self):
        """Filter notifications created after a given datetime."""
        queryset = Notification.objects.all()
        past = timezone.now() - timedelta(days=1)

        filtered = NotificationFilter(
            {"created_after": past},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 2)

    def test_filter_created_before(self):
        """Filter notifications created before a given datetime."""
        queryset = Notification.objects.all()
        future = timezone.now() + timedelta(days=1)

        filtered = NotificationFilter(
            {"created_before": future},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 2)

    def test_filter_scheduled_after(self):
        """Filter notifications scheduled after a given datetime."""
        queryset = Notification.objects.all()
        cutoff = timezone.now() + timedelta(minutes=30)

        filtered = NotificationFilter(
            {"scheduled_after": cutoff},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 2)

    def test_filter_scheduled_before(self):
        """Filter notifications scheduled before a given datetime."""
        queryset = Notification.objects.all()
        future = timezone.now() + timedelta(days=1)

        filtered = NotificationFilter(
            {"scheduled_before": future},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 2)


class NotificationManagementFilterTestCase(
    BaseNotificationFilterFactoryMixin,
    TestCase,
):
    def setUp(self):
        self.recipient_1 = self.create_user()
        self.recipient_2 = self.create_user()

        self.created_by_1 = self.create_user(
            email="support1@company.com",
            user_name="Support One",
            role=User.ROLE_SUPPORT_STAFF,
        )
        self.created_by_2 = self.create_user(
            email="admin1@company.com",
            user_name="Admin One",
            role=User.ROLE_ADMIN,
        )

        self.notification_1 = self.create_notification(
            recipient=self.recipient_1,
            created_by=self.created_by_1,
            notification_type="order_shipped",
            source_module="orders",
            source_event="order_shipped",
            source_object_id="ORDER-AAA",
            status=Notification.STATUS_PENDING,
            channel=Notification.CHANNEL_IN_APP,
            priority=Notification.PRIORITY_NORMAL,
        )

        self.notification_2 = self.create_notification(
            recipient=self.recipient_2,
            created_by=self.created_by_2,
            notification_type="payment_captured",
            source_module="payments",
            source_event="payment_captured",
            source_object_id="PAY-BBB",
            status=Notification.STATUS_UNREAD,
            channel=Notification.CHANNEL_EMAIL,
            priority=Notification.PRIORITY_HIGH,
        )

    def test_filter_by_status(self):
        """Filter management notifications by exact status."""
        queryset = Notification.objects.all()

        filtered = NotificationManagementFilter(
            {"status": Notification.STATUS_UNREAD},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.notification_2)

    def test_filter_by_channel(self):
        """Filter management notifications by exact channel."""
        queryset = Notification.objects.all()

        filtered = NotificationManagementFilter(
            {"channel": Notification.CHANNEL_IN_APP},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.notification_1)

    def test_filter_by_priority(self):
        """Filter management notifications by exact priority."""
        queryset = Notification.objects.all()

        filtered = NotificationManagementFilter(
            {"priority": Notification.PRIORITY_HIGH},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.notification_2)

    def test_filter_by_notification_type(self):
        """Filter management notifications using partial notification type."""
        queryset = Notification.objects.all()

        filtered = NotificationManagementFilter(
            {"notification_type": "payment"},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.notification_2)

    def test_filter_by_source_module(self):
        """Filter management notifications using partial source module."""
        queryset = Notification.objects.all()

        filtered = NotificationManagementFilter(
            {"source_module": "order"},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.notification_1)

    def test_filter_by_source_event(self):
        """Filter management notifications using partial source event."""
        queryset = Notification.objects.all()

        filtered = NotificationManagementFilter(
            {"source_event": "captured"},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.notification_2)

    def test_filter_by_source_object_id(self):
        """Filter management notifications using partial source object id."""
        queryset = Notification.objects.all()

        filtered = NotificationManagementFilter(
            {"source_object_id": "AAA"},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.notification_1)

    def test_filter_by_recipient_id(self):
        """Filter management notifications by recipient id."""
        queryset = Notification.objects.all()

        filtered = NotificationManagementFilter(
            {"recipient_id": self.recipient_1.id},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.notification_1)

    def test_filter_by_created_by_id(self):
        """Filter management notifications by created_by id."""
        queryset = Notification.objects.all()

        filtered = NotificationManagementFilter(
            {"created_by_id": self.created_by_2.id},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.notification_2)

    def test_filter_created_after(self):
        """Filter management notifications created after a given datetime."""
        queryset = Notification.objects.all()
        past = timezone.now() - timedelta(days=1)

        filtered = NotificationManagementFilter(
            {"created_after": past},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 2)

    def test_filter_created_before(self):
        """Filter management notifications created before a given datetime."""
        queryset = Notification.objects.all()
        future = timezone.now() + timedelta(days=1)

        filtered = NotificationManagementFilter(
            {"created_before": future},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 2)

    def test_filter_scheduled_after(self):
        """Filter management notifications scheduled after a given datetime."""
        queryset = Notification.objects.all()
        cutoff = timezone.now() + timedelta(minutes=30)

        filtered = NotificationManagementFilter(
            {"scheduled_after": cutoff},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 2)

    def test_filter_scheduled_before(self):
        """Filter management notifications scheduled before a given datetime."""
        queryset = Notification.objects.all()
        future = timezone.now() + timedelta(days=1)

        filtered = NotificationManagementFilter(
            {"scheduled_before": future},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 2)

    def test_filter_combined_filters(self):
        """Apply multiple management filters simultaneously."""
        queryset = Notification.objects.all()

        filtered = NotificationManagementFilter(
            {
                "recipient_id": self.recipient_1.id,
                "source_object_id": "AAA",
            },
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.notification_1)