from datetime import timedelta
import uuid

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from ech.notifications.models import (
    Notification,
    NotificationDelivery,
    NotificationEvent,
    NotificationLifecycle,
)


User = get_user_model()


class BaseNotificationModelFactoryMixin:
    def create_user(self, **kwargs):
        unique_suffix = uuid.uuid4().hex[:8]

        data = {
            "email": f"user_{unique_suffix}@test.com",
            "password": "StrongPassword123",
            "user_name": f"Test User {unique_suffix}",
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
            "title": "Your order has been shipped",
            "message": "Your order is on the way.",
            "status": Notification.STATUS_PENDING,
            "channel": Notification.CHANNEL_IN_APP,
            "priority": Notification.PRIORITY_NORMAL,
            "source_module": "orders",
            "source_event": "order_shipped",
            "source_object_id": str(uuid.uuid4()),
            "scheduled_for": timezone.now() + timedelta(hours=1),
            "metadata": {"source": "unit-test"},
        }
        data.update(kwargs)
        return Notification.objects.create(**data)

    def create_delivery(self, **kwargs):
        notification = kwargs.pop("notification", None) or self.create_notification()
        performed_by = kwargs.pop("performed_by", None)

        data = {
            "notification": notification,
            "channel": NotificationDelivery.CHANNEL_IN_APP,
            "status": NotificationDelivery.STATUS_PENDING,
            "provider_name": "in_app_provider",
            "recipient_address": "",
            "external_message_id": "",
            "failure_code": "",
            "failure_message": "",
            "metadata": {"source": "unit-test"},
            "performed_by": performed_by,
            "processed_at": timezone.now(),
        }
        data.update(kwargs)
        return NotificationDelivery.objects.create(**data)


class NotificationModelTestCase(BaseNotificationModelFactoryMixin, TestCase):
    def test_notification_creation_success(self):
        """Create a notification successfully with operational fields."""
        recipient = self.create_user()
        created_by = self.create_user(
            email="support@company.com",
            user_name="Support User",
            role=User.ROLE_SUPPORT_STAFF,
        )

        notification = self.create_notification(
            recipient=recipient,
            created_by=created_by,
        )

        self.assertIsInstance(notification.id, uuid.UUID)
        self.assertEqual(notification.recipient, recipient)
        self.assertEqual(notification.created_by, created_by)
        self.assertEqual(notification.notification_type, "order_shipped")
        self.assertEqual(notification.title, "Your order has been shipped")
        self.assertEqual(notification.message, "Your order is on the way.")
        self.assertEqual(notification.status, Notification.STATUS_PENDING)
        self.assertEqual(notification.channel, Notification.CHANNEL_IN_APP)
        self.assertEqual(notification.priority, Notification.PRIORITY_NORMAL)
        self.assertEqual(notification.source_module, "orders")
        self.assertEqual(notification.source_event, "order_shipped")
        self.assertIsNotNone(notification.scheduled_for)
        self.assertEqual(notification.metadata, {"source": "unit-test"})
        self.assertEqual(notification.failure_code, "")
        self.assertEqual(notification.failure_message, "")
        self.assertIsNotNone(notification.created_at)
        self.assertIsNotNone(notification.updated_at)

    def test_notification_defaults_are_applied(self):
        """Apply notification default values when optional fields are omitted."""
        notification = Notification.objects.create(
            recipient=self.create_user(),
            notification_type="generic_alert",
            title="Hello",
            message="This is a message.",
        )

        self.assertIsNone(notification.created_by)
        self.assertEqual(notification.status, Notification.STATUS_PENDING)
        self.assertEqual(notification.channel, Notification.CHANNEL_IN_APP)
        self.assertEqual(notification.priority, Notification.PRIORITY_NORMAL)
        self.assertEqual(notification.source_module, "")
        self.assertEqual(notification.source_event, "")
        self.assertEqual(notification.source_object_id, "")
        self.assertIsNone(notification.scheduled_for)
        self.assertIsNone(notification.idempotency_key)
        self.assertEqual(notification.failure_code, "")
        self.assertEqual(notification.failure_message, "")
        self.assertIsNone(notification.metadata)

    def test_notification_string_representation(self):
        """Return notification identifier and recipient in string representation."""
        notification = self.create_notification()
        self.assertEqual(
            str(notification),
            f"Notification {notification.id} - {notification.recipient_id}",
        )

    def test_notification_related_names_work_correctly(self):
        """Expose notifications through recipient and created_by related names."""
        recipient = self.create_user()
        created_by = self.create_user(
            email="admin@company.com",
            user_name="Admin User",
            role=User.ROLE_ADMIN,
        )

        notification = self.create_notification(
            recipient=recipient,
            created_by=created_by,
        )

        self.assertIn(notification, recipient.notifications.all())
        self.assertIn(notification, created_by.created_notifications.all())

    def test_notification_ordering_by_created_at_desc(self):
        """Order notifications by newest created_at first."""
        first = self.create_notification()
        second = self.create_notification(recipient=self.create_user())

        notifications = list(Notification.objects.all())

        self.assertEqual(notifications[0], second)
        self.assertEqual(notifications[1], first)

    def test_notification_idempotency_key_must_be_unique(self):
        """Prevent duplicate idempotency keys across notifications."""
        idempotency_key = uuid.uuid4()
        self.create_notification(idempotency_key=idempotency_key)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_notification(
                    recipient=self.create_user(),
                    idempotency_key=idempotency_key,
                )

    def test_notification_meta_ordering_is_configured(self):
        """Configure notification default ordering by created_at descending."""
        self.assertEqual(Notification._meta.ordering, ["-created_at"])

    def test_notification_meta_indexes_are_configured(self):
        """Configure notification indexes for operational queries."""
        index_names = {index.name for index in Notification._meta.indexes}

        self.assertIn("not_rec_created_idx", index_names)
        self.assertIn("not_status_idx", index_names)
        self.assertIn("not_chan_idx", index_names)
        self.assertIn("not_sched_idx", index_names)
        self.assertIn("not_src_ref_idx", index_names)

    def test_notification_status_choices_include_expected_values(self):
        """Expose all supported notification statuses."""
        choices = dict(Notification.STATUS_CHOICES)

        self.assertIn(Notification.STATUS_PENDING, choices)
        self.assertIn(Notification.STATUS_UNREAD, choices)
        self.assertIn(Notification.STATUS_READ, choices)
        self.assertIn(Notification.STATUS_ARCHIVED, choices)
        self.assertIn(Notification.STATUS_CANCELLED, choices)
        self.assertIn(Notification.STATUS_FAILED, choices)

    def test_notification_channel_choices_include_expected_values(self):
        """Expose all supported notification channels."""
        choices = dict(Notification.CHANNEL_CHOICES)

        self.assertIn(Notification.CHANNEL_IN_APP, choices)
        self.assertIn(Notification.CHANNEL_EMAIL, choices)
        self.assertIn(Notification.CHANNEL_BOTH, choices)

    def test_notification_priority_choices_include_expected_values(self):
        """Expose all supported notification priorities."""
        choices = dict(Notification.PRIORITY_CHOICES)

        self.assertIn(Notification.PRIORITY_LOW, choices)
        self.assertIn(Notification.PRIORITY_NORMAL, choices)
        self.assertIn(Notification.PRIORITY_HIGH, choices)
        self.assertIn(Notification.PRIORITY_CRITICAL, choices)

    def test_notification_field_metadata_is_configured(self):
        """Configure optional notification field metadata correctly."""
        source_module_field = Notification._meta.get_field("source_module")
        source_event_field = Notification._meta.get_field("source_event")
        source_object_id_field = Notification._meta.get_field("source_object_id")
        scheduled_for_field = Notification._meta.get_field("scheduled_for")
        metadata_field = Notification._meta.get_field("metadata")

        self.assertTrue(source_module_field.blank)
        self.assertTrue(source_event_field.blank)
        self.assertTrue(source_object_id_field.blank)

        self.assertTrue(scheduled_for_field.null)
        self.assertTrue(scheduled_for_field.blank)

        self.assertTrue(metadata_field.null)
        self.assertTrue(metadata_field.blank)


class NotificationLifecycleModelTestCase(BaseNotificationModelFactoryMixin, TestCase):
    def test_notification_lifecycle_creation_success(self):
        """Create notification lifecycle timestamps successfully."""
        notification = self.create_notification()
        now = timezone.now()

        lifecycle = NotificationLifecycle.objects.create(
            notification=notification,
            dispatched_at=now,
            read_at=now,
        )

        self.assertEqual(lifecycle.notification, notification)
        self.assertEqual(lifecycle.dispatched_at, now)
        self.assertEqual(lifecycle.read_at, now)
        self.assertIsNone(lifecycle.archived_at)
        self.assertIsNone(lifecycle.cancelled_at)
        self.assertIsNone(lifecycle.failed_at)
        self.assertIsNotNone(lifecycle.created_at)
        self.assertIsNotNone(lifecycle.updated_at)

    def test_notification_lifecycle_string_representation(self):
        """Return notification identifier in lifecycle string representation."""
        notification = self.create_notification()
        lifecycle = NotificationLifecycle.objects.create(notification=notification)

        self.assertEqual(
            str(lifecycle),
            f"Lifecycle for Notification {notification.id}",
        )

    def test_notification_lifecycle_related_name_works_correctly(self):
        """Expose lifecycle through notification one-to-one related name."""
        notification = self.create_notification()
        lifecycle = NotificationLifecycle.objects.create(notification=notification)

        self.assertEqual(notification.lifecycle, lifecycle)


class NotificationDeliveryModelTestCase(BaseNotificationModelFactoryMixin, TestCase):
    def test_notification_delivery_creation_success(self):
        """Create a notification delivery successfully."""
        notification = self.create_notification()
        operator = self.create_user(
            email="ops@company.com",
            user_name="Operations User",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        delivery = NotificationDelivery.objects.create(
            notification=notification,
            channel=NotificationDelivery.CHANNEL_EMAIL,
            status=NotificationDelivery.STATUS_SENT,
            provider_name="email_provider",
            recipient_address="customer@test.com",
            external_message_id="msg-123",
            metadata={"backend": "smtp"},
            performed_by=operator,
            processed_at=timezone.now(),
        )

        self.assertEqual(delivery.notification, notification)
        self.assertEqual(delivery.channel, NotificationDelivery.CHANNEL_EMAIL)
        self.assertEqual(delivery.status, NotificationDelivery.STATUS_SENT)
        self.assertEqual(delivery.provider_name, "email_provider")
        self.assertEqual(delivery.recipient_address, "customer@test.com")
        self.assertEqual(delivery.external_message_id, "msg-123")
        self.assertEqual(delivery.metadata, {"backend": "smtp"})
        self.assertEqual(delivery.performed_by, operator)
        self.assertIsNotNone(delivery.created_at)

    def test_notification_delivery_defaults_are_applied(self):
        """Apply delivery default values when optional fields are omitted."""
        notification = self.create_notification()
        delivery = NotificationDelivery.objects.create(
            notification=notification,
            channel=NotificationDelivery.CHANNEL_IN_APP,
        )

        self.assertEqual(delivery.status, NotificationDelivery.STATUS_PENDING)
        self.assertEqual(delivery.provider_name, "")
        self.assertEqual(delivery.recipient_address, "")
        self.assertEqual(delivery.external_message_id, "")
        self.assertEqual(delivery.failure_code, "")
        self.assertEqual(delivery.failure_message, "")
        self.assertIsNone(delivery.metadata)
        self.assertIsNone(delivery.performed_by)
        self.assertIsNone(delivery.processed_at)

    def test_notification_delivery_string_representation(self):
        """Return delivery channel and notification identifier in string representation."""
        delivery = self.create_delivery()

        self.assertEqual(
            str(delivery),
            f"{delivery.channel} delivery - {delivery.notification_id}",
        )

    def test_notification_delivery_ordering_by_created_at_desc(self):
        """Order deliveries by newest created_at first."""
        notification = self.create_notification()
        first = NotificationDelivery.objects.create(
            notification=notification,
            channel=NotificationDelivery.CHANNEL_IN_APP,
        )
        second = NotificationDelivery.objects.create(
            notification=notification,
            channel=NotificationDelivery.CHANNEL_EMAIL,
        )

        deliveries = list(NotificationDelivery.objects.all())

        self.assertEqual(deliveries[0], second)
        self.assertEqual(deliveries[1], first)

    def test_notification_delivery_related_name_works_correctly(self):
        """Expose deliveries through notification related name."""
        notification = self.create_notification()
        delivery = NotificationDelivery.objects.create(
            notification=notification,
            channel=NotificationDelivery.CHANNEL_IN_APP,
        )

        self.assertIn(delivery, notification.deliveries.all())

    def test_notification_delivery_meta_is_configured(self):
        """Configure delivery ordering and indexes correctly."""
        self.assertEqual(NotificationDelivery._meta.ordering, ["-created_at"])

        index_names = {index.name for index in NotificationDelivery._meta.indexes}
        self.assertIn("notdel_not_cre_idx", index_names)
        self.assertIn("notdel_ch_st_idx", index_names)

    def test_notification_delivery_channel_choices_include_expected_values(self):
        """Expose all supported delivery channels."""
        choices = dict(NotificationDelivery.CHANNEL_CHOICES)

        self.assertIn(NotificationDelivery.CHANNEL_IN_APP, choices)
        self.assertIn(NotificationDelivery.CHANNEL_EMAIL, choices)

    def test_notification_delivery_status_choices_include_expected_values(self):
        """Expose all supported delivery statuses."""
        choices = dict(NotificationDelivery.STATUS_CHOICES)

        self.assertIn(NotificationDelivery.STATUS_PENDING, choices)
        self.assertIn(NotificationDelivery.STATUS_SENT, choices)
        self.assertIn(NotificationDelivery.STATUS_DELIVERED, choices)
        self.assertIn(NotificationDelivery.STATUS_FAILED, choices)
        self.assertIn(NotificationDelivery.STATUS_CANCELLED, choices)

    def test_notification_delivery_field_metadata_is_configured(self):
        """Configure optional delivery field metadata correctly."""
        external_message_id_field = NotificationDelivery._meta.get_field(
            "external_message_id"
        )
        metadata_field = NotificationDelivery._meta.get_field("metadata")
        processed_at_field = NotificationDelivery._meta.get_field("processed_at")

        self.assertTrue(external_message_id_field.blank)
        self.assertTrue(metadata_field.null)
        self.assertTrue(metadata_field.blank)
        self.assertTrue(processed_at_field.null)
        self.assertTrue(processed_at_field.blank)


class NotificationEventModelTestCase(BaseNotificationModelFactoryMixin, TestCase):
    def test_notification_event_creation_success(self):
        """Create a notification audit event successfully."""
        notification = self.create_notification()
        operator = self.create_user(
            email="support@company.com",
            user_name="Support User",
            role=User.ROLE_SUPPORT_STAFF,
        )

        event = NotificationEvent.objects.create(
            notification=notification,
            event_type=NotificationEvent.TYPE_CREATED,
            performed_by=operator,
            metadata={"source": "unit-test"},
        )

        self.assertEqual(event.notification, notification)
        self.assertEqual(event.event_type, NotificationEvent.TYPE_CREATED)
        self.assertEqual(event.performed_by, operator)
        self.assertEqual(event.metadata, {"source": "unit-test"})
        self.assertIsNotNone(event.created_at)

    def test_notification_event_string_representation(self):
        """Return event type and notification identifier in string representation."""
        notification = self.create_notification()
        event = NotificationEvent.objects.create(
            notification=notification,
            event_type=NotificationEvent.TYPE_DISPATCHED,
        )

        self.assertEqual(
            str(event),
            f"{NotificationEvent.TYPE_DISPATCHED} - {notification.id}",
        )

    def test_notification_event_ordering_by_created_at_desc(self):
        """Order notification events by newest created_at first."""
        notification = self.create_notification()
        first = NotificationEvent.objects.create(
            notification=notification,
            event_type=NotificationEvent.TYPE_CREATED,
        )
        second = NotificationEvent.objects.create(
            notification=notification,
            event_type=NotificationEvent.TYPE_DISPATCHED,
        )

        events = list(NotificationEvent.objects.all())

        self.assertEqual(events[0], second)
        self.assertEqual(events[1], first)

    def test_notification_event_related_name_works_correctly(self):
        """Expose events through notification related name."""
        notification = self.create_notification()
        event = NotificationEvent.objects.create(
            notification=notification,
            event_type=NotificationEvent.TYPE_CREATED,
        )

        self.assertIn(event, notification.events.all())

    def test_notification_event_meta_is_configured(self):
        """Configure event ordering and indexes correctly."""
        self.assertEqual(NotificationEvent._meta.ordering, ["-created_at"])

        index_names = {index.name for index in NotificationEvent._meta.indexes}
        self.assertIn("notevt_not_cre_idx", index_names)

    def test_notification_event_choices_include_expected_values(self):
        """Expose all supported notification event types."""
        choices = dict(NotificationEvent.EVENT_TYPE_CHOICES)

        self.assertIn(NotificationEvent.TYPE_CREATED, choices)
        self.assertIn(NotificationEvent.TYPE_STATUS_CHANGED, choices)
        self.assertIn(NotificationEvent.TYPE_DISPATCHED, choices)
        self.assertIn(NotificationEvent.TYPE_READ, choices)
        self.assertIn(NotificationEvent.TYPE_ARCHIVED, choices)
        self.assertIn(NotificationEvent.TYPE_CANCELLED, choices)
        self.assertIn(NotificationEvent.TYPE_FAILED, choices)
        self.assertIn(NotificationEvent.TYPE_DELIVERY_SENT, choices)
        self.assertIn(NotificationEvent.TYPE_DELIVERY_FAILED, choices)