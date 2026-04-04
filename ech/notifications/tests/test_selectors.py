import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.notifications.exceptions import (
    NotificationAccessDeniedException,
    NotificationNotFoundException,
)
from ech.notifications.models import (
    Notification,
    NotificationDelivery,
    NotificationEvent,
    NotificationLifecycle,
)
from ech.notifications.selectors import (
    notification_base_queryset,
    get_notification_by_id,
    get_notification_with_related,
    get_recipient_notification,
    get_management_notification,
    list_recipient_notifications,
    list_recipient_notifications_by_status,
    list_recipient_notifications_by_type,
    list_unread_recipient_notifications,
    list_archived_recipient_notifications,
    list_notifications_by_status,
    list_notifications_by_channel,
    list_notifications_by_priority,
    list_management_notifications,
    list_recent_notifications,
    search_notifications,
)


User = get_user_model()


class BaseNotificationSelectorFactoryMixin:
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

    def create_notification_with_related_data(self, **kwargs):
        notification = self.create_notification(**kwargs)

        NotificationLifecycle.objects.create(
            notification=notification,
            dispatched_at=timezone.now(),
        )

        NotificationDelivery.objects.create(
            notification=notification,
            channel=NotificationDelivery.CHANNEL_IN_APP,
            status=NotificationDelivery.STATUS_DELIVERED,
            provider_name="in_app_provider",
            processed_at=timezone.now(),
        )

        NotificationEvent.objects.create(
            notification=notification,
            event_type=NotificationEvent.TYPE_CREATED,
        )

        return notification


class NotificationBaseQuerysetTestCase(
    BaseNotificationSelectorFactoryMixin,
    TestCase,
):
    def test_notification_base_queryset_applies_select_and_prefetch_related(self):
        """Apply select_related and prefetch_related to notification base queryset."""
        queryset = notification_base_queryset()

        self.assertEqual(
            queryset.query.select_related,
            {
                "recipient": {},
                "created_by": {},
                "lifecycle": {},
            },
        )
        self.assertEqual(
            set(queryset._prefetch_related_lookups),
            {"deliveries", "events"},
        )


class NotificationRetrievalSelectorTestCase(
    BaseNotificationSelectorFactoryMixin,
    TestCase,
):
    def test_get_notification_by_id_returns_matching_notification(self):
        """Return a notification by identifier using the optimized queryset."""
        notification = self.create_notification_with_related_data()

        result = get_notification_by_id(notification_id=notification.id)

        self.assertEqual(result, notification)
        self.assertIsNotNone(result.lifecycle)
        self.assertEqual(result.deliveries.count(), 1)
        self.assertEqual(result.events.count(), 1)

    def test_get_notification_by_id_raises_not_found_for_unknown_notification(self):
        """Raise NotificationNotFoundException for an unknown notification id."""
        with self.assertRaises(NotificationNotFoundException):
            get_notification_by_id(notification_id=uuid.uuid4())

    def test_get_notification_with_related_returns_matching_notification(self):
        """Return a notification using compatibility selector."""
        notification = self.create_notification_with_related_data()

        result = get_notification_with_related(notification_id=notification.id)

        self.assertEqual(result, notification)

    def test_get_recipient_notification_returns_recipient_owned_notification(self):
        """Return a notification when it belongs to the given recipient."""
        recipient = self.create_user()
        notification = self.create_notification(
            recipient=recipient,
        )

        result = get_recipient_notification(
            notification_id=notification.id,
            recipient=recipient,
        )

        self.assertEqual(result, notification)

    def test_get_recipient_notification_raises_not_found_for_unknown_notification(self):
        """Raise NotificationNotFoundException when notification does not exist."""
        recipient = self.create_user()

        with self.assertRaises(NotificationNotFoundException):
            get_recipient_notification(
                notification_id=uuid.uuid4(),
                recipient=recipient,
            )

    def test_get_recipient_notification_raises_access_denied_for_other_recipient(self):
        """Raise NotificationAccessDeniedException when notification belongs to another recipient."""
        owner = self.create_user()
        another_recipient = self.create_user()
        notification = self.create_notification(recipient=owner)

        with self.assertRaises(NotificationAccessDeniedException):
            get_recipient_notification(
                notification_id=notification.id,
                recipient=another_recipient,
            )

    def test_get_management_notification_returns_matching_notification(self):
        """Return a notification by identifier for management use."""
        notification = self.create_notification_with_related_data()

        result = get_management_notification(notification_id=notification.id)

        self.assertEqual(result, notification)


class NotificationListSelectorTestCase(
    BaseNotificationSelectorFactoryMixin,
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
            status=Notification.STATUS_PENDING,
            channel=Notification.CHANNEL_IN_APP,
            priority=Notification.PRIORITY_NORMAL,
            notification_type="order_shipped",
            source_module="orders",
            source_event="order_shipped",
            source_object_id="ORDER-001",
        )

        self.notification_2 = self.create_notification(
            recipient=self.recipient_1,
            created_by=self.created_by_2,
            status=Notification.STATUS_UNREAD,
            channel=Notification.CHANNEL_EMAIL,
            priority=Notification.PRIORITY_HIGH,
            notification_type="payment_captured",
            source_module="payments",
            source_event="payment_captured",
            source_object_id="PAY-002",
        )

        self.notification_3 = self.create_notification(
            recipient=self.recipient_2,
            created_by=self.created_by_1,
            status=Notification.STATUS_ARCHIVED,
            channel=Notification.CHANNEL_BOTH,
            priority=Notification.PRIORITY_CRITICAL,
            notification_type="review_approved",
            source_module="reviews",
            source_event="review_approved",
            source_object_id="REV-003",
        )

    def test_list_recipient_notifications_returns_only_recipient_notifications(self):
        """List only notifications belonging to the given recipient."""
        result = list_recipient_notifications(recipient=self.recipient_1)

        self.assertEqual(result.count(), 2)
        self.assertEqual(list(result), [self.notification_2, self.notification_1])

    def test_list_recipient_notifications_by_status_filters_recipient_notifications(self):
        """List recipient notifications filtered by a specific status."""
        result = list_recipient_notifications_by_status(
            recipient=self.recipient_1,
            status=Notification.STATUS_UNREAD,
        )

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.notification_2)

    def test_list_recipient_notifications_by_type_filters_recipient_notifications(self):
        """List recipient notifications filtered by notification type."""
        result = list_recipient_notifications_by_type(
            recipient=self.recipient_1,
            notification_type="order_shipped",
        )

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.notification_1)

    def test_list_unread_recipient_notifications_returns_only_unread_items(self):
        """List only unread notifications for a recipient."""
        result = list_unread_recipient_notifications(
            recipient=self.recipient_1,
        )

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.notification_2)

    def test_list_archived_recipient_notifications_returns_only_archived_items(self):
        """List only archived notifications for a recipient."""
        result = list_archived_recipient_notifications(
            recipient=self.recipient_2,
        )

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.notification_3)

    def test_list_management_notifications_returns_all_notifications(self):
        """List all notifications for management in descending creation order."""
        result = list_management_notifications()

        self.assertEqual(result.count(), 3)
        self.assertEqual(
            list(result),
            [self.notification_3, self.notification_2, self.notification_1],
        )

    def test_list_notifications_by_status_filters_management_queryset(self):
        """List notifications filtered by status for management use."""
        result = list_notifications_by_status(
            status=Notification.STATUS_PENDING,
        )

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.notification_1)

    def test_list_notifications_by_channel_filters_queryset(self):
        """List notifications filtered by channel."""
        result = list_notifications_by_channel(
            channel=Notification.CHANNEL_EMAIL,
        )

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.notification_2)

    def test_list_notifications_by_priority_filters_queryset(self):
        """List notifications filtered by priority."""
        result = list_notifications_by_priority(
            priority=Notification.PRIORITY_CRITICAL,
        )

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.notification_3)

    def test_list_recent_notifications_returns_ordered_queryset(self):
        """List recent notifications ordered by newest created_at first."""
        result = list_recent_notifications()

        self.assertEqual(
            list(result),
            [self.notification_3, self.notification_2, self.notification_1],
        )

    def test_search_notifications_matches_title(self):
        """Search notifications by partial title."""
        self.notification_1.title = "Special Search Title"
        self.notification_1.save(update_fields=["title"])

        result = search_notifications(query="Search Title")

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.notification_1)

    def test_search_notifications_matches_message(self):
        """Search notifications by partial message."""
        self.notification_2.message = "Payment search body text"
        self.notification_2.save(update_fields=["message"])

        result = search_notifications(query="search body")

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.notification_2)

    def test_search_notifications_matches_notification_type(self):
        """Search notifications by partial notification type."""
        result = search_notifications(query="review")

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.notification_3)

    def test_search_notifications_matches_source_module(self):
        """Search notifications by partial source module."""
        result = search_notifications(query="payment")

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.notification_2)

    def test_search_notifications_matches_source_event(self):
        """Search notifications by partial source event."""
        result = search_notifications(query="approved")

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.notification_3)

    def test_search_notifications_matches_source_object_id(self):
        """Search notifications by partial source object id."""
        result = search_notifications(query="ORDER-001")

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.notification_1)

    def test_search_notifications_returns_ordered_results(self):
        """Return matching search results ordered by newest created_at first."""
        self.notification_2.title = "Shared Search Title"
        self.notification_2.save(update_fields=["title"])

        self.notification_3.title = "Shared Search Title"
        self.notification_3.save(update_fields=["title"])

        result = search_notifications(query="Shared Search Title")

        self.assertEqual(list(result), [self.notification_3, self.notification_2])