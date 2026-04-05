from datetime import timedelta
from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from ech.notifications.exceptions import (
    NotificationCreationException,
    NotificationIdempotencyConflictException,
)
from ech.notifications.models import (
    Notification,
    NotificationEvent,
    NotificationLifecycle,
)
from ech.notifications.services.notification_creation_service import (
    NotificationCreationService,
)


User = get_user_model()


class BaseNotificationCreationFactoryMixin:
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

    def create_existing_notification(self, **kwargs):
        recipient = kwargs.pop("recipient", None) or self.create_user()
        created_by = kwargs.pop("created_by", None)

        data = {
            "recipient": recipient,
            "created_by": created_by,
            "notification_type": kwargs.get(
                "notification_type",
                "order_shipped",
            ),
            "title": kwargs.get(
                "title",
                "Your order has been shipped",
            ),
            "message": kwargs.get(
                "message",
                "Your order is on the way.",
            ),
            "status": kwargs.get(
                "status",
                Notification.STATUS_PENDING,
            ),
            "channel": kwargs.get(
                "channel",
                Notification.CHANNEL_IN_APP,
            ),
            "priority": kwargs.get(
                "priority",
                Notification.PRIORITY_NORMAL,
            ),
            "source_module": kwargs.get("source_module", "orders"),
            "source_event": kwargs.get("source_event", "order_shipped"),
            "source_object_id": kwargs.get(
                "source_object_id",
                "ORDER-001",
            ),
            "scheduled_for": kwargs.get(
                "scheduled_for",
                timezone.now() + timedelta(hours=1),
            ),
            "idempotency_key": kwargs.get("idempotency_key"),
            "metadata": kwargs.get("metadata", {"source": "unit-test"}),
        }

        notification = Notification.objects.create(**data)
        NotificationLifecycle.objects.create(notification=notification)
        return notification


class NotificationCreationServiceTestCase(
    BaseNotificationCreationFactoryMixin,
    TestCase,
):
    @patch(
        "ech.notifications.services.notification_creation_service."
        "NotificationCacheService.invalidate_after_mutation"
    )
    @patch(
        "ech.notifications.services.notification_creation_service."
        "DomainEventDispatcher.dispatch"
    )
    @patch(
        "ech.notifications.services.notification_creation_service."
        "NotificationLogService.log_notification_created"
    )
    @patch(
        "ech.notifications.services.notification_creation_service."
        "NotificationCreatedEvent"
    )
    def test_create_notification_success(
        self,
        notification_created_event_mock,
        log_notification_created_mock,
        dispatch_mock,
        invalidate_after_mutation_mock,
    ):
        """Create notification aggregate and related records successfully."""
        recipient = self.create_user()
        created_by = self.create_user(
            email="support@company.com",
            user_name="Support User",
            role=User.ROLE_SUPPORT_STAFF,
        )
        performed_by = self.create_user(
            email="admin@company.com",
            user_name="Admin User",
            role=User.ROLE_ADMIN,
        )
        scheduled_for = timezone.now() + timedelta(hours=4)
        idempotency_key = uuid.uuid4()

        with self.captureOnCommitCallbacks(execute=True):
            notification = NotificationCreationService.create_notification(
                recipient=recipient,
                created_by=created_by,
                notification_type="order_shipped",
                title="Your order has been shipped",
                message="Your order is on the way.",
                channel=Notification.CHANNEL_EMAIL,
                priority=Notification.PRIORITY_HIGH,
                source_module="orders",
                source_event="order_shipped",
                source_object_id="ORDER-123",
                scheduled_for=scheduled_for,
                metadata={"source": "unit-test"},
                idempotency_key=idempotency_key,
                performed_by=performed_by,
            )

        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(NotificationLifecycle.objects.count(), 1)
        self.assertEqual(NotificationEvent.objects.count(), 1)

        self.assertEqual(notification.recipient, recipient)
        self.assertEqual(notification.created_by, created_by)
        self.assertEqual(notification.notification_type, "order_shipped")
        self.assertEqual(notification.title, "Your order has been shipped")
        self.assertEqual(notification.message, "Your order is on the way.")
        self.assertEqual(notification.status, Notification.STATUS_PENDING)
        self.assertEqual(notification.channel, Notification.CHANNEL_EMAIL)
        self.assertEqual(notification.priority, Notification.PRIORITY_HIGH)
        self.assertEqual(notification.source_module, "orders")
        self.assertEqual(notification.source_event, "order_shipped")
        self.assertEqual(notification.source_object_id, "ORDER-123")
        self.assertEqual(notification.scheduled_for, scheduled_for)
        self.assertEqual(notification.metadata, {"source": "unit-test"})
        self.assertEqual(notification.idempotency_key, idempotency_key)

        self.assertIsNotNone(notification.lifecycle)

        event = notification.events.get()
        self.assertEqual(event.event_type, NotificationEvent.TYPE_CREATED)
        self.assertEqual(event.performed_by, performed_by)
        self.assertEqual(
            event.metadata,
            {
                "recipient_id": str(recipient.id),
                "created_by_id": str(created_by.id),
                "notification_type": "order_shipped",
                "channel": Notification.CHANNEL_EMAIL,
                "priority": Notification.PRIORITY_HIGH,
                "source_module": "orders",
                "source_event": "order_shipped",
                "source_object_id": "ORDER-123",
                "scheduled_for": scheduled_for.isoformat(),
                "idempotency_key": str(idempotency_key),
                "metadata": {"source": "unit-test"},
            },
        )

        log_notification_created_mock.assert_called_once_with(
            notification=notification,
            performed_by=performed_by,
        )

        notification_created_event_mock.assert_called_once_with(
            notification_id=notification.id,
            recipient_id=recipient.id,
            notification_type="order_shipped",
            channel=Notification.CHANNEL_EMAIL,
            performed_by_id=performed_by.id,
        )
        dispatch_mock.assert_called_once_with(
            notification_created_event_mock.return_value
        )

        invalidate_after_mutation_mock.assert_called_once_with(
            notification_id=notification.id,
            recipient_id=recipient.id,
        )

    @patch(
        "ech.notifications.services.notification_creation_service."
        "NotificationCacheService.invalidate_after_mutation"
    )
    @patch(
        "ech.notifications.services.notification_creation_service."
        "DomainEventDispatcher.dispatch"
    )
    @patch(
        "ech.notifications.services.notification_creation_service."
        "NotificationLogService.log_notification_created"
    )
    @patch(
        "ech.notifications.services.notification_creation_service."
        "NotificationCreatedEvent"
    )
    def test_create_notification_success_with_optional_fields_omitted(
        self,
        notification_created_event_mock,
        log_notification_created_mock,
        dispatch_mock,
        invalidate_after_mutation_mock,
    ):
        """Create notification successfully when optional fields are omitted."""
        recipient = self.create_user()

        with self.captureOnCommitCallbacks(execute=True):
            notification = NotificationCreationService.create_notification(
                recipient=recipient,
                notification_type="generic_alert",
                title="Hello",
                message="This is a message.",
            )

        self.assertEqual(notification.status, Notification.STATUS_PENDING)
        self.assertEqual(notification.channel, Notification.CHANNEL_IN_APP)
        self.assertEqual(notification.priority, Notification.PRIORITY_NORMAL)
        self.assertEqual(notification.source_module, "")
        self.assertEqual(notification.source_event, "")
        self.assertEqual(notification.source_object_id, "")
        self.assertIsNone(notification.scheduled_for)
        self.assertIsNone(notification.idempotency_key)
        self.assertEqual(notification.metadata, {})

        event = notification.events.get()
        self.assertEqual(
            event.metadata,
            {
                "recipient_id": str(recipient.id),
                "created_by_id": None,
                "notification_type": "generic_alert",
                "channel": Notification.CHANNEL_IN_APP,
                "priority": Notification.PRIORITY_NORMAL,
                "source_module": "",
                "source_event": "",
                "source_object_id": "",
                "scheduled_for": None,
                "idempotency_key": None,
                "metadata": {},
            },
        )

        log_notification_created_mock.assert_called_once_with(
            notification=notification,
            performed_by=None,
        )

        notification_created_event_mock.assert_called_once_with(
            notification_id=notification.id,
            recipient_id=recipient.id,
            notification_type="generic_alert",
            channel=Notification.CHANNEL_IN_APP,
            performed_by_id=None,
        )
        dispatch_mock.assert_called_once_with(
            notification_created_event_mock.return_value
        )

        invalidate_after_mutation_mock.assert_called_once_with(
            notification_id=notification.id,
            recipient_id=recipient.id,
        )

    @patch(
        "ech.notifications.services.notification_creation_service."
        "NotificationCacheService.invalidate_after_mutation"
    )
    @patch(
        "ech.notifications.services.notification_creation_service."
        "DomainEventDispatcher.dispatch"
    )
    @patch(
        "ech.notifications.services.notification_creation_service."
        "NotificationLogService.log_notification_created"
    )
    @patch(
        "ech.notifications.services.notification_creation_service."
        "NotificationCreatedEvent"
    )
    def test_create_notification_reuses_existing_notification_for_same_idempotency_and_payload(
        self,
        notification_created_event_mock,
        log_notification_created_mock,
        dispatch_mock,
        invalidate_after_mutation_mock,
    ):
        """Reuse existing notification when idempotency key is replayed with same payload."""
        recipient = self.create_user()
        created_by = self.create_user(
            email="support@company.com",
            user_name="Support User",
            role=User.ROLE_SUPPORT_STAFF,
        )
        idempotency_key = uuid.uuid4()
        scheduled_for = timezone.now() + timedelta(hours=3)

        with self.captureOnCommitCallbacks(execute=True):
            first_notification = NotificationCreationService.create_notification(
                recipient=recipient,
                created_by=created_by,
                notification_type="order_shipped",
                title="Replay-safe title",
                message="Replay-safe body",
                channel=Notification.CHANNEL_IN_APP,
                priority=Notification.PRIORITY_NORMAL,
                source_module="orders",
                source_event="order_shipped",
                source_object_id="ORDER-REPLAY-001",
                scheduled_for=scheduled_for,
                metadata={"source": "unit-test"},
                idempotency_key=idempotency_key,
            )

        second_notification = NotificationCreationService.create_notification(
            recipient=recipient,
            created_by=created_by,
            notification_type="order_shipped",
            title="Replay-safe title",
            message="Replay-safe body",
            channel=Notification.CHANNEL_IN_APP,
            priority=Notification.PRIORITY_NORMAL,
            source_module="orders",
            source_event="order_shipped",
            source_object_id="ORDER-REPLAY-001",
            scheduled_for=scheduled_for,
            metadata={"source": "unit-test"},
            idempotency_key=idempotency_key,
        )

        self.assertEqual(first_notification, second_notification)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(NotificationLifecycle.objects.count(), 1)
        self.assertEqual(NotificationEvent.objects.count(), 1)

        log_notification_created_mock.assert_called_once()
        notification_created_event_mock.assert_called_once()
        dispatch_mock.assert_called_once()
        invalidate_after_mutation_mock.assert_called_once()

    @patch(
        "ech.notifications.services.notification_creation_service."
        "DomainEventDispatcher.dispatch"
    )
    @patch(
        "ech.notifications.services.notification_creation_service."
        "NotificationLogService.log_notification_created"
    )
    def test_create_notification_raises_conflict_for_same_idempotency_with_different_payload(
        self,
        log_notification_created_mock,
        dispatch_mock,
    ):
        """Raise NotificationIdempotencyConflictException for reused key with different payload."""
        recipient = self.create_user()
        idempotency_key = uuid.uuid4()

        NotificationCreationService.create_notification(
            recipient=recipient,
            notification_type="order_shipped",
            title="Original title",
            message="Original body",
            channel=Notification.CHANNEL_IN_APP,
            priority=Notification.PRIORITY_NORMAL,
            source_module="orders",
            source_event="order_shipped",
            source_object_id="ORDER-CONFLICT-001",
            metadata={"source": "unit-test"},
            idempotency_key=idempotency_key,
        )

        with self.assertRaises(NotificationIdempotencyConflictException):
            NotificationCreationService.create_notification(
                recipient=recipient,
                notification_type="payment_captured",
                title="Different title",
                message="Different body",
                channel=Notification.CHANNEL_EMAIL,
                priority=Notification.PRIORITY_HIGH,
                source_module="payments",
                source_event="payment_captured",
                source_object_id="PAY-CONFLICT-999",
                metadata={"source": "changed"},
                idempotency_key=idempotency_key,
            )

        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(NotificationLifecycle.objects.count(), 1)
        self.assertEqual(NotificationEvent.objects.count(), 1)
        log_notification_created_mock.assert_called_once()
        dispatch_mock.assert_called_once()

    def test_create_notification_raises_exception_when_recipient_is_missing(self):
        """Raise NotificationCreationException when recipient is missing."""
        with self.assertRaises(NotificationCreationException) as context:
            NotificationCreationService.create_notification(
                recipient=None,
                notification_type="order_shipped",
                title="Title",
                message="Message",
            )

        self.assertEqual(
            str(context.exception),
            "Notification recipient is required.",
        )

    def test_create_notification_raises_exception_when_notification_type_is_missing(self):
        """Raise NotificationCreationException when notification_type is missing."""
        with self.assertRaises(NotificationCreationException) as context:
            NotificationCreationService.create_notification(
                recipient=self.create_user(),
                notification_type="",
                title="Title",
                message="Message",
            )

        self.assertEqual(
            str(context.exception),
            "Notification type is required.",
        )

    def test_create_notification_raises_exception_when_title_is_missing(self):
        """Raise NotificationCreationException when title is missing."""
        with self.assertRaises(NotificationCreationException) as context:
            NotificationCreationService.create_notification(
                recipient=self.create_user(),
                notification_type="order_shipped",
                title="",
                message="Message",
            )

        self.assertEqual(
            str(context.exception),
            "Notification title is required.",
        )

    def test_create_notification_raises_exception_when_message_is_missing(self):
        """Raise NotificationCreationException when message is missing."""
        with self.assertRaises(NotificationCreationException) as context:
            NotificationCreationService.create_notification(
                recipient=self.create_user(),
                notification_type="order_shipped",
                title="Title",
                message="",
            )

        self.assertEqual(
            str(context.exception),
            "Notification message is required.",
        )

    def test_create_notification_returns_resolved_notification_after_integrity_conflict(self):
        """Return resolved notification when concurrent integrity conflict is recoverable."""
        recipient = self.create_user()
        created_by = self.create_user(
            email="support@company.com",
            user_name="Support User",
            role=User.ROLE_SUPPORT_STAFF,
        )
        idempotency_key = uuid.uuid4()

        resolved_notification = self.create_existing_notification(
            recipient=recipient,
            created_by=created_by,
            idempotency_key=idempotency_key,
        )

        with patch(
            "ech.notifications.services.notification_creation_service."
            "NotificationCreationService._get_notification_by_idempotency_key"
        ) as get_by_idempotency_mock, patch(
            "ech.notifications.services.notification_creation_service."
            "Notification.objects.create"
        ) as notification_create_mock, patch(
            "ech.notifications.services.notification_creation_service."
            "NotificationCreationService._resolve_integrity_conflict"
        ) as resolve_integrity_conflict_mock:
            get_by_idempotency_mock.return_value = None
            notification_create_mock.side_effect = IntegrityError(
                "unique constraint"
            )
            resolve_integrity_conflict_mock.return_value = resolved_notification

            result = NotificationCreationService.create_notification(
                recipient=recipient,
                created_by=created_by,
                notification_type="order_shipped",
                title="Your order has been shipped",
                message="Your order is on the way.",
                idempotency_key=idempotency_key,
            )

        self.assertEqual(result, resolved_notification)
        get_by_idempotency_mock.assert_called_once_with(
            idempotency_key=idempotency_key,
        )
        resolve_integrity_conflict_mock.assert_called_once()

    def test_create_notification_raises_creation_exception_when_conflict_cannot_be_resolved(
        self,
    ):
        """Raise NotificationCreationException when integrity conflict cannot be resolved."""
        recipient = self.create_user()
        idempotency_key = uuid.uuid4()

        with patch(
            "ech.notifications.services.notification_creation_service."
            "NotificationCreationService._get_notification_by_idempotency_key"
        ) as get_by_idempotency_mock, patch(
            "ech.notifications.services.notification_creation_service."
            "Notification.objects.create"
        ) as notification_create_mock, patch(
            "ech.notifications.services.notification_creation_service."
            "NotificationCreationService._resolve_integrity_conflict"
        ) as resolve_integrity_conflict_mock:
            get_by_idempotency_mock.return_value = None
            notification_create_mock.side_effect = IntegrityError(
                "unique constraint"
            )
            resolve_integrity_conflict_mock.return_value = None

            with self.assertRaises(NotificationCreationException):
                NotificationCreationService.create_notification(
                    recipient=recipient,
                    notification_type="order_shipped",
                    title="Title",
                    message="Message",
                    idempotency_key=idempotency_key,
                )

    def test_get_notification_by_idempotency_key_returns_matching_notification(self):
        """Return existing notification when idempotency key matches."""
        recipient = self.create_user()
        idempotency_key = uuid.uuid4()
        notification = self.create_existing_notification(
            recipient=recipient,
            idempotency_key=idempotency_key,
        )

        result = NotificationCreationService._get_notification_by_idempotency_key(
            idempotency_key=idempotency_key,
        )

        self.assertEqual(result, notification)

    def test_get_notification_by_idempotency_key_returns_none_for_unknown_key(self):
        """Return none when idempotency key does not exist."""
        result = NotificationCreationService._get_notification_by_idempotency_key(
            idempotency_key=uuid.uuid4(),
        )

        self.assertIsNone(result)

    def test_resolve_integrity_conflict_returns_existing_notification_for_same_idempotent_request(
        self,
    ):
        """Return existing notification when conflict matches same idempotent payload."""
        recipient = self.create_user()
        created_by = self.create_user(
            email="support@company.com",
            user_name="Support User",
            role=User.ROLE_SUPPORT_STAFF,
        )
        idempotency_key = uuid.uuid4()
        scheduled_for = timezone.now() + timedelta(hours=2)

        notification = self.create_existing_notification(
            recipient=recipient,
            created_by=created_by,
            notification_type="order_shipped",
            title="Your order has been shipped",
            message="Your order is on the way.",
            channel=Notification.CHANNEL_EMAIL,
            priority=Notification.PRIORITY_HIGH,
            source_module="orders",
            source_event="order_shipped",
            source_object_id="ORDER-RESOLVE-001",
            scheduled_for=scheduled_for,
            idempotency_key=idempotency_key,
            metadata={"source": "unit-test"},
        )

        result = NotificationCreationService._resolve_integrity_conflict(
            recipient=recipient,
            created_by=created_by,
            notification_type="order_shipped",
            title="Your order has been shipped",
            message="Your order is on the way.",
            channel=Notification.CHANNEL_EMAIL,
            priority=Notification.PRIORITY_HIGH,
            source_module="orders",
            source_event="order_shipped",
            source_object_id="ORDER-RESOLVE-001",
            scheduled_for=scheduled_for,
            metadata={"source": "unit-test"},
            idempotency_key=idempotency_key,
        )

        self.assertEqual(result, notification)

    def test_resolve_integrity_conflict_raises_conflict_for_mismatched_idempotent_payload(
        self,
    ):
        """Raise NotificationIdempotencyConflictException for mismatched payload."""
        recipient = self.create_user()
        idempotency_key = uuid.uuid4()

        self.create_existing_notification(
            recipient=recipient,
            notification_type="order_shipped",
            title="Original title",
            message="Original body",
            channel=Notification.CHANNEL_IN_APP,
            priority=Notification.PRIORITY_NORMAL,
            source_module="orders",
            source_event="order_shipped",
            source_object_id="ORDER-MISMATCH-001",
            scheduled_for=timezone.now() + timedelta(hours=1),
            idempotency_key=idempotency_key,
            metadata={"source": "unit-test"},
        )

        with self.assertRaises(NotificationIdempotencyConflictException):
            NotificationCreationService._resolve_integrity_conflict(
                recipient=recipient,
                created_by=None,
                notification_type="payment_captured",
                title="Different title",
                message="Different body",
                channel=Notification.CHANNEL_EMAIL,
                priority=Notification.PRIORITY_HIGH,
                source_module="payments",
                source_event="payment_captured",
                source_object_id="PAY-MISMATCH-999",
                scheduled_for=timezone.now() + timedelta(hours=10),
                metadata={"source": "changed"},
                idempotency_key=idempotency_key,
            )

    def test_validate_idempotent_reuse_accepts_equivalent_payload(self):
        """Accept idempotent reuse when notification payload matches exactly."""
        recipient = self.create_user()
        created_by = self.create_user(
            email="support@company.com",
            user_name="Support User",
            role=User.ROLE_SUPPORT_STAFF,
        )
        scheduled_for = timezone.now() + timedelta(hours=2)

        notification = self.create_existing_notification(
            recipient=recipient,
            created_by=created_by,
            notification_type="order_shipped",
            title="Replay title",
            message="Replay body",
            channel=Notification.CHANNEL_EMAIL,
            priority=Notification.PRIORITY_HIGH,
            source_module="orders",
            source_event="order_shipped",
            source_object_id="ORDER-VALIDATE-001",
            scheduled_for=scheduled_for,
            metadata={"source": "unit-test"},
        )

        NotificationCreationService._validate_idempotent_reuse(
            notification=notification,
            recipient=recipient,
            created_by=created_by,
            notification_type="order_shipped",
            title="Replay title",
            message="Replay body",
            channel=Notification.CHANNEL_EMAIL,
            priority=Notification.PRIORITY_HIGH,
            source_module="orders",
            source_event="order_shipped",
            source_object_id="ORDER-VALIDATE-001",
            scheduled_for=scheduled_for,
            metadata={"source": "unit-test"},
        )

    def test_validate_idempotent_reuse_raises_for_different_payload(self):
        """Raise NotificationIdempotencyConflictException when payload differs."""
        recipient = self.create_user()

        notification = self.create_existing_notification(
            recipient=recipient,
            notification_type="order_shipped",
            title="Original title",
            message="Original body",
            channel=Notification.CHANNEL_IN_APP,
            priority=Notification.PRIORITY_NORMAL,
            source_module="orders",
            source_event="order_shipped",
            source_object_id="ORDER-DIFF-001",
            scheduled_for=timezone.now() + timedelta(hours=1),
            metadata={"source": "unit-test"},
        )

        with self.assertRaises(NotificationIdempotencyConflictException):
            NotificationCreationService._validate_idempotent_reuse(
                notification=notification,
                recipient=recipient,
                created_by=None,
                notification_type="payment_captured",
                title="Different title",
                message="Different body",
                channel=Notification.CHANNEL_EMAIL,
                priority=Notification.PRIORITY_HIGH,
                source_module="payments",
                source_event="payment_captured",
                source_object_id="PAY-DIFF-999",
                scheduled_for=timezone.now() + timedelta(hours=8),
                metadata={"source": "changed"},
            )

    def test_normalized_payload_strips_text_fields_and_normalizes_metadata(self):
        """Normalize payload values for stable persistence and idempotency comparison."""
        scheduled_for = timezone.now() + timedelta(hours=2)

        normalized = NotificationCreationService._normalized_payload(
            notification_type="  order_shipped  ",
            title="  Hello  ",
            message="  Body  ",
            channel=Notification.CHANNEL_IN_APP,
            priority=Notification.PRIORITY_NORMAL,
            source_module="  orders  ",
            source_event="  order_shipped  ",
            source_object_id="  ORDER-001  ",
            scheduled_for=scheduled_for,
            metadata=None,
        )

        self.assertEqual(normalized["notification_type"], "order_shipped")
        self.assertEqual(normalized["title"], "Hello")
        self.assertEqual(normalized["message"], "Body")
        self.assertEqual(normalized["source_module"], "orders")
        self.assertEqual(normalized["source_event"], "order_shipped")
        self.assertEqual(normalized["source_object_id"], "ORDER-001")
        self.assertEqual(normalized["scheduled_for"], scheduled_for)
        self.assertEqual(normalized["metadata"], {})

    def test_normalized_metadata_returns_empty_dict_when_none(self):
        """Normalize missing metadata to an empty dictionary."""
        normalized = NotificationCreationService._normalized_metadata(
            metadata=None,
        )

        self.assertEqual(normalized, {})