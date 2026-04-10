import uuid

from django.core.cache import cache
from django.test import TestCase

from ech.users.models import CustomUser
from ech.notifications.models import (
    Notification,
    NotificationLifecycle,
)
from ech.notifications.selectors import (
    get_notification_by_id,
    list_management_notifications,
    list_recipient_notifications,
    list_recipient_notifications_by_status,
    search_notifications,
)


class NotificationCacheSelectorsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.recipient = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        cls.staff = CustomUser.objects.create_user(
            email="ops@company.com",
            password="StrongPassword123",
            user_name="Operations Staff",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        cls.notification = Notification.objects.create(
            recipient=cls.recipient,
            created_by=cls.staff,
            notification_type="order_shipped",
            title="Order shipped",
            message="Your order has been shipped.",
            status=Notification.STATUS_UNREAD,
            channel=Notification.CHANNEL_IN_APP,
            priority=Notification.PRIORITY_NORMAL,
            source_module="orders",
            source_event="order_shipped",
            source_object_id="ORDER-CACHE-001",
            metadata={"source": "unit-test"},
            idempotency_key=uuid.uuid4(),
        )

        NotificationLifecycle.objects.create(
            notification=cls.notification,
        )

    def setUp(self):
        cache.clear()

    def test_get_notification_by_id_uses_cached_detail_snapshot(self):
        """Return cached notification detail until cache is invalidated."""
        notification = get_notification_by_id(
            notification_id=self.notification.id,
        )
        self.assertEqual(notification.status, Notification.STATUS_UNREAD)

        Notification.objects.filter(id=self.notification.id).update(
            status=Notification.STATUS_READ
        )

        cached_notification = get_notification_by_id(
            notification_id=self.notification.id,
        )
        self.assertEqual(cached_notification.status, Notification.STATUS_UNREAD)

    def test_list_recipient_notifications_uses_cached_id_set(self):
        """Return cached recipient notification IDs until cache is invalidated."""
        first_result = list(
            list_recipient_notifications(recipient=self.recipient)
        )
        self.assertEqual(len(first_result), 1)

        new_notification = Notification.objects.create(
            recipient=self.recipient,
            created_by=self.staff,
            notification_type="payment_captured",
            title="Payment captured",
            message="Your payment has been captured.",
            status=Notification.STATUS_UNREAD,
            channel=Notification.CHANNEL_EMAIL,
            priority=Notification.PRIORITY_HIGH,
            source_module="payments",
            source_event="payment_captured",
            source_object_id="PAY-CACHE-001",
            metadata={"source": "unit-test"},
            idempotency_key=uuid.uuid4(),
        )

        NotificationLifecycle.objects.create(
            notification=new_notification,
        )

        second_result = list(
            list_recipient_notifications(recipient=self.recipient)
        )
        self.assertEqual(len(second_result), 1)

    def test_list_recipient_notifications_by_status_uses_cached_id_set(self):
        """Return cached filtered recipient notification IDs for repeated identical queries."""
        first_result = list(
            list_recipient_notifications_by_status(
                recipient=self.recipient,
                status=Notification.STATUS_UNREAD,
            )
        )
        second_result = list(
            list_recipient_notifications_by_status(
                recipient=self.recipient,
                status=Notification.STATUS_UNREAD,
            )
        )

        self.assertEqual(len(first_result), 1)
        self.assertEqual(len(second_result), 1)
        self.assertEqual(first_result[0].id, second_result[0].id)

    def test_list_management_notifications_uses_cached_id_set(self):
        """Return cached management notification IDs until cache is invalidated."""
        first_result = list(list_management_notifications())
        self.assertEqual(len(first_result), 1)

        new_notification = Notification.objects.create(
            recipient=self.recipient,
            created_by=self.staff,
            notification_type="review_approved",
            title="Review approved",
            message="A review has been approved.",
            status=Notification.STATUS_PENDING,
            channel=Notification.CHANNEL_IN_APP,
            priority=Notification.PRIORITY_NORMAL,
            source_module="reviews",
            source_event="review_approved",
            source_object_id="REVIEW-CACHE-001",
            metadata={"source": "unit-test"},
            idempotency_key=uuid.uuid4(),
        )

        NotificationLifecycle.objects.create(
            notification=new_notification,
        )

        second_result = list(list_management_notifications())
        self.assertEqual(len(second_result), 1)

    def test_search_notifications_uses_cached_result_ids(self):
        """Return cached notification search IDs for repeated identical queries."""
        first_result = list(
            search_notifications(query="ORDER-CACHE-001")
        )
        second_result = list(
            search_notifications(query="ORDER-CACHE-001")
        )

        self.assertEqual(len(first_result), 1)
        self.assertEqual(len(second_result), 1)
        self.assertEqual(first_result[0].id, second_result[0].id)