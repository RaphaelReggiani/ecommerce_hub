from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.notifications.exceptions import (
    InvalidNotificationOperationException,
    InvalidNotificationStateTransitionException,
    NotificationAlreadyArchivedException,
    NotificationAlreadyCancelledException,
    NotificationAlreadyReadException,
)
from ech.notifications.models import (
    Notification,
    NotificationEvent,
    NotificationLifecycle,
)
from ech.notifications.services.notification_status_service import (
    NotificationStatusService,
)


User = get_user_model()


class BaseNotificationStatusFactoryMixin:
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


class NotificationStatusServiceTestCase(
    BaseNotificationStatusFactoryMixin,
    TestCase,
):
    @patch(
        "ech.notifications.services.notification_status_service."
        "NotificationCacheService.invalidate_after_mutation"
    )
    @patch(
        "ech.notifications.services.notification_status_service."
        "DomainEventDispatcher.dispatch"
    )
    @patch(
        "ech.notifications.services.notification_status_service."
        "NotificationLogService.log_notification_status_changed"
    )
    @patch(
        "ech.notifications.services.notification_status_service."
        "NotificationStatusChangedEvent"
    )
    def test_update_status_success_creates_events_and_updates_lifecycle(
        self,
        notification_status_changed_event_mock,
        log_status_changed_mock,
        dispatch_mock,
        invalidate_after_mutation_mock,
    ):
        """Update notification status successfully with events and lifecycle timestamp."""
        notification = self.create_notification(status=Notification.STATUS_PENDING)
        performed_by = self.create_user(
            email="ops@company.com",
            user_name="Operations User",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        with self.captureOnCommitCallbacks(execute=True):
            updated_notification = NotificationStatusService.update_status(
                notification=notification,
                new_status=Notification.STATUS_UNREAD,
                performed_by=performed_by,
                metadata={"source": "unit-test"},
            )

        updated_notification.refresh_from_db()
        updated_notification.lifecycle.refresh_from_db()

        self.assertEqual(updated_notification.status, Notification.STATUS_UNREAD)
        self.assertEqual(updated_notification.failure_code, "")
        self.assertEqual(updated_notification.failure_message, "")
        self.assertIsNone(updated_notification.lifecycle.read_at)
        self.assertIsNone(updated_notification.lifecycle.archived_at)

        events = list(updated_notification.events.order_by("created_at"))
        self.assertEqual(len(events), 1)

        self.assertEqual(events[0].event_type, NotificationEvent.TYPE_STATUS_CHANGED)
        self.assertEqual(events[0].performed_by, performed_by)
        self.assertEqual(
            events[0].metadata,
            {
                "previous_status": Notification.STATUS_PENDING,
                "new_status": Notification.STATUS_UNREAD,
                "source": "unit-test",
            },
        )

        log_status_changed_mock.assert_called_once_with(
            notification=updated_notification,
            previous_status=Notification.STATUS_PENDING,
            new_status=Notification.STATUS_UNREAD,
            performed_by=performed_by,
        )

        notification_status_changed_event_mock.assert_called_once_with(
            notification_id=updated_notification.id,
            previous_status=Notification.STATUS_PENDING,
            new_status=Notification.STATUS_UNREAD,
            performed_by_id=performed_by.id,
        )
        dispatch_mock.assert_called_once_with(
            notification_status_changed_event_mock.return_value
        )

        invalidate_after_mutation_mock.assert_called_once_with(
            notification_id=updated_notification.id,
            recipient_id=updated_notification.recipient_id,
        )

    @patch(
        "ech.notifications.services.notification_status_service."
        "NotificationCacheService.invalidate_after_mutation"
    )
    @patch(
        "ech.notifications.services.notification_status_service."
        "DomainEventDispatcher.dispatch"
    )
    @patch(
        "ech.notifications.services.notification_status_service."
        "NotificationLogService.log_notification_status_changed"
    )
    def test_update_status_success_without_metadata(
        self,
        log_status_changed_mock,
        dispatch_mock,
        invalidate_after_mutation_mock,
    ):
        """Update notification status successfully without optional metadata."""
        notification = self.create_notification(status=Notification.STATUS_UNREAD)

        with self.captureOnCommitCallbacks(execute=True):
            updated_notification = NotificationStatusService.update_status(
                notification=notification,
                new_status=Notification.STATUS_READ,
            )

        updated_notification.refresh_from_db()
        updated_notification.lifecycle.refresh_from_db()

        self.assertEqual(updated_notification.status, Notification.STATUS_READ)
        self.assertIsNotNone(updated_notification.lifecycle.read_at)

        events = list(updated_notification.events.order_by("created_at"))
        self.assertEqual(len(events), 2)

        self.assertEqual(
            events[0].metadata,
            {
                "previous_status": Notification.STATUS_UNREAD,
                "new_status": Notification.STATUS_READ,
            },
        )
        self.assertEqual(events[1].metadata, {})

        log_status_changed_mock.assert_called_once()
        dispatch_mock.assert_called_once()
        invalidate_after_mutation_mock.assert_called_once()

    def test_update_status_raises_when_notification_is_already_cancelled(self):
        """Raise NotificationAlreadyCancelledException for cancelled notification."""
        notification = self.create_notification(status=Notification.STATUS_CANCELLED)

        with self.assertRaises(NotificationAlreadyCancelledException):
            NotificationStatusService.update_status(
                notification=notification,
                new_status=Notification.STATUS_UNREAD,
            )

        notification.refresh_from_db()
        self.assertEqual(notification.status, Notification.STATUS_CANCELLED)
        self.assertEqual(NotificationEvent.objects.count(), 0)

    def test_update_status_raises_for_invalid_transition(self):
        """Raise InvalidNotificationStateTransitionException for invalid status change."""
        notification = self.create_notification(status=Notification.STATUS_PENDING)

        with self.assertRaises(InvalidNotificationStateTransitionException):
            NotificationStatusService.update_status(
                notification=notification,
                new_status=Notification.STATUS_READ,
            )

        notification.refresh_from_db()
        self.assertEqual(notification.status, Notification.STATUS_PENDING)
        self.assertEqual(NotificationEvent.objects.count(), 0)

    def test_update_status_sets_failure_fields_when_marking_failed(self):
        """Persist failure code and failure message when marking failed."""
        notification = self.create_notification(status=Notification.STATUS_PENDING)

        with self.captureOnCommitCallbacks(execute=True):
            updated_notification = NotificationStatusService.update_status(
                notification=notification,
                new_status=Notification.STATUS_FAILED,
                metadata={
                    "failure_code": "provider_error",
                    "failure_message": "SMTP timeout",
                },
            )

        updated_notification.refresh_from_db()
        updated_notification.lifecycle.refresh_from_db()

        self.assertEqual(updated_notification.status, Notification.STATUS_FAILED)
        self.assertEqual(updated_notification.failure_code, "provider_error")
        self.assertEqual(updated_notification.failure_message, "SMTP timeout")
        self.assertIsNotNone(updated_notification.lifecycle.failed_at)

        events = list(updated_notification.events.order_by("created_at"))
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].event_type, NotificationEvent.TYPE_STATUS_CHANGED)
        self.assertEqual(events[1].event_type, NotificationEvent.TYPE_FAILED)

    def test_update_status_clears_failure_fields_when_leaving_non_failed_transition(self):
        """Clear failure fields when updating to a non-failed status."""
        notification = self.create_notification(
            status=Notification.STATUS_UNREAD,
            failure_code="old_error",
            failure_message="Old message",
        )

        with self.captureOnCommitCallbacks(execute=True):
            updated_notification = NotificationStatusService.update_status(
                notification=notification,
                new_status=Notification.STATUS_READ,
            )

        updated_notification.refresh_from_db()

        self.assertEqual(updated_notification.failure_code, "")
        self.assertEqual(updated_notification.failure_message, "")

    def test_mark_as_read_success(self):
        """Mark unread notification as read successfully."""
        notification = self.create_notification(status=Notification.STATUS_UNREAD)

        with self.captureOnCommitCallbacks(execute=True):
            updated_notification = NotificationStatusService.mark_as_read(
                notification=notification,
            )

        updated_notification.refresh_from_db()
        self.assertEqual(updated_notification.status, Notification.STATUS_READ)

    def test_mark_as_read_raises_when_already_read(self):
        """Raise NotificationAlreadyReadException when already read."""
        notification = self.create_notification(status=Notification.STATUS_READ)

        with self.assertRaises(NotificationAlreadyReadException):
            NotificationStatusService.mark_as_read(notification=notification)

    def test_archive_success(self):
        """Archive unread notification successfully."""
        notification = self.create_notification(status=Notification.STATUS_UNREAD)

        with self.captureOnCommitCallbacks(execute=True):
            updated_notification = NotificationStatusService.archive(
                notification=notification,
            )

        updated_notification.refresh_from_db()
        updated_notification.lifecycle.refresh_from_db()

        self.assertEqual(updated_notification.status, Notification.STATUS_ARCHIVED)
        self.assertIsNotNone(updated_notification.lifecycle.archived_at)

    def test_archive_raises_when_already_archived(self):
        """Raise NotificationAlreadyArchivedException when already archived."""
        notification = self.create_notification(status=Notification.STATUS_ARCHIVED)

        with self.assertRaises(NotificationAlreadyArchivedException):
            NotificationStatusService.archive(notification=notification)

    def test_mark_as_unread_from_read_success(self):
        """Restore read notification to unread and clear read_at."""
        notification = self.create_notification(status=Notification.STATUS_READ)
        notification.lifecycle.read_at = timezone.now()
        notification.lifecycle.save(update_fields=["read_at", "updated_at"])

        with self.captureOnCommitCallbacks(execute=True):
            updated_notification = NotificationStatusService.mark_as_unread(
                notification=notification,
            )

        updated_notification.refresh_from_db()
        updated_notification.lifecycle.refresh_from_db()

        self.assertEqual(updated_notification.status, Notification.STATUS_UNREAD)
        self.assertIsNone(updated_notification.lifecycle.read_at)

    def test_mark_as_unread_from_archived_success(self):
        """Restore archived notification to unread and clear archived_at."""
        notification = self.create_notification(status=Notification.STATUS_ARCHIVED)
        notification.lifecycle.archived_at = timezone.now()
        notification.lifecycle.save(update_fields=["archived_at", "updated_at"])

        with self.captureOnCommitCallbacks(execute=True):
            updated_notification = NotificationStatusService.mark_as_unread(
                notification=notification,
            )

        updated_notification.refresh_from_db()
        updated_notification.lifecycle.refresh_from_db()

        self.assertEqual(updated_notification.status, Notification.STATUS_UNREAD)
        self.assertIsNone(updated_notification.lifecycle.archived_at)

    def test_mark_as_unread_raises_for_invalid_source_status(self):
        """Raise InvalidNotificationOperationException for invalid unread restore."""
        notification = self.create_notification(status=Notification.STATUS_PENDING)

        with self.assertRaises(InvalidNotificationOperationException):
            NotificationStatusService.mark_as_unread(notification=notification)

    def test_mark_as_failed_success(self):
        """Mark pending notification as failed successfully."""
        notification = self.create_notification(status=Notification.STATUS_PENDING)

        with self.captureOnCommitCallbacks(execute=True):
            updated_notification = NotificationStatusService.mark_as_failed(
                notification=notification,
                failure_code="provider_error",
                failure_message="Delivery failed",
            )

        updated_notification.refresh_from_db()

        self.assertEqual(updated_notification.status, Notification.STATUS_FAILED)
        self.assertEqual(updated_notification.failure_code, "provider_error")
        self.assertEqual(updated_notification.failure_message, "Delivery failed")

    def test_mark_as_unread_after_dispatch_success(self):
        """Move pending notification to unread after dispatch."""
        notification = self.create_notification(status=Notification.STATUS_PENDING)

        with self.captureOnCommitCallbacks(execute=True):
            updated_notification = (
                NotificationStatusService.mark_as_unread_after_dispatch(
                    notification=notification,
                )
            )

        updated_notification.refresh_from_db()
        self.assertEqual(updated_notification.status, Notification.STATUS_UNREAD)

    def test_mark_as_unread_after_dispatch_raises_for_invalid_status(self):
        """Raise InvalidNotificationOperationException when dispatch promotion is invalid."""
        notification = self.create_notification(status=Notification.STATUS_READ)

        with self.assertRaises(InvalidNotificationOperationException):
            NotificationStatusService.mark_as_unread_after_dispatch(
                notification=notification,
            )

    def test_validate_terminal_status_allows_non_terminal_status(self):
        """Allow status validation for non-terminal notification."""
        notification = self.create_notification(status=Notification.STATUS_UNREAD)

        NotificationStatusService._validate_terminal_status(
            notification=notification,
        )

    def test_validate_terminal_status_raises_for_cancelled_status(self):
        """Raise NotificationAlreadyCancelledException for cancelled notification."""
        notification = self.create_notification(status=Notification.STATUS_CANCELLED)

        with self.assertRaises(NotificationAlreadyCancelledException):
            NotificationStatusService._validate_terminal_status(
                notification=notification,
            )

    def test_validate_transition_allows_supported_transition(self):
        """Allow a valid notification status transition."""
        NotificationStatusService._validate_transition(
            current_status=Notification.STATUS_PENDING,
            new_status=Notification.STATUS_UNREAD,
        )

    def test_validate_transition_raises_for_unsupported_transition(self):
        """Raise InvalidNotificationStateTransitionException for unsupported transition."""
        with self.assertRaises(InvalidNotificationStateTransitionException):
            NotificationStatusService._validate_transition(
                current_status=Notification.STATUS_PENDING,
                new_status=Notification.STATUS_ARCHIVED,
            )

    def test_update_lifecycle_timestamp_updates_expected_field(self):
        """Update lifecycle timestamp field mapped to the new status."""
        notification = self.create_notification(status=Notification.STATUS_UNREAD)

        before_call = timezone.now()
        NotificationStatusService._update_lifecycle_timestamp(
            notification=notification,
            previous_status=Notification.STATUS_UNREAD,
            new_status=Notification.STATUS_READ,
        )
        notification.lifecycle.refresh_from_db()

        self.assertIsNotNone(notification.lifecycle.read_at)
        self.assertGreaterEqual(notification.lifecycle.read_at, before_call)

    def test_update_lifecycle_timestamp_clears_read_at_when_returning_to_unread(self):
        """Clear read_at when notification moves from read to unread."""
        notification = self.create_notification(status=Notification.STATUS_READ)
        notification.lifecycle.read_at = timezone.now()
        notification.lifecycle.save(update_fields=["read_at", "updated_at"])

        NotificationStatusService._update_lifecycle_timestamp(
            notification=notification,
            previous_status=Notification.STATUS_READ,
            new_status=Notification.STATUS_UNREAD,
        )
        notification.lifecycle.refresh_from_db()

        self.assertIsNone(notification.lifecycle.read_at)

    def test_update_lifecycle_timestamp_clears_archived_at_when_returning_to_unread(self):
        """Clear archived_at when notification moves from archived to unread."""
        notification = self.create_notification(status=Notification.STATUS_ARCHIVED)
        notification.lifecycle.archived_at = timezone.now()
        notification.lifecycle.save(update_fields=["archived_at", "updated_at"])

        NotificationStatusService._update_lifecycle_timestamp(
            notification=notification,
            previous_status=Notification.STATUS_ARCHIVED,
            new_status=Notification.STATUS_UNREAD,
        )
        notification.lifecycle.refresh_from_db()

        self.assertIsNone(notification.lifecycle.archived_at)

    def test_update_lifecycle_timestamp_does_nothing_for_unmapped_status(self):
        """Do nothing when new status has no lifecycle field mapping."""
        notification = self.create_notification(status=Notification.STATUS_PENDING)

        NotificationStatusService._update_lifecycle_timestamp(
            notification=notification,
            previous_status=Notification.STATUS_PENDING,
            new_status="unknown_status",
        )
        notification.lifecycle.refresh_from_db()

        self.assertIsNone(notification.lifecycle.read_at)
        self.assertIsNone(notification.lifecycle.archived_at)
        self.assertIsNone(notification.lifecycle.cancelled_at)
        self.assertIsNone(notification.lifecycle.failed_at)

    def test_create_status_change_event_creates_general_and_specific_events(self):
        """Create generic and specific notification status change events."""
        notification = self.create_notification(status=Notification.STATUS_UNREAD)
        performed_by = self.create_user(
            email="ops2@company.com",
            user_name="Operations User 2",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        NotificationStatusService._create_status_change_event(
            notification=notification,
            previous_status=Notification.STATUS_UNREAD,
            new_status=Notification.STATUS_READ,
            performed_by=performed_by,
            metadata={"source": "manual"},
        )

        events = list(notification.events.order_by("created_at"))
        self.assertEqual(len(events), 2)

        self.assertEqual(events[0].event_type, NotificationEvent.TYPE_STATUS_CHANGED)
        self.assertEqual(
            events[0].metadata,
            {
                "previous_status": Notification.STATUS_UNREAD,
                "new_status": Notification.STATUS_READ,
                "source": "manual",
            },
        )
        self.assertEqual(events[0].performed_by, performed_by)

        self.assertEqual(events[1].event_type, NotificationEvent.TYPE_READ)
        self.assertEqual(events[1].metadata, {"source": "manual"})
        self.assertEqual(events[1].performed_by, performed_by)

    def test_create_status_change_event_creates_only_general_event_for_unmapped_status(self):
        """Create only generic event when status has no specific event mapping."""
        notification = self.create_notification(status=Notification.STATUS_PENDING)

        NotificationStatusService._create_status_change_event(
            notification=notification,
            previous_status=Notification.STATUS_PENDING,
            new_status="custom_status",
            metadata={"source": "manual"},
        )

        events = list(notification.events.order_by("created_at"))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, NotificationEvent.TYPE_STATUS_CHANGED)
        self.assertEqual(
            events[0].metadata,
            {
                "previous_status": Notification.STATUS_PENDING,
                "new_status": "custom_status",
                "source": "manual",
            },
        )

    def test_allowed_transitions_cover_expected_lifecycle_flow(self):
        """Expose expected allowed transitions for notification lifecycle."""
        self.assertEqual(
            NotificationStatusService.ALLOWED_TRANSITIONS[
                Notification.STATUS_PENDING
            ],
            {
                Notification.STATUS_UNREAD,
                Notification.STATUS_FAILED,
                Notification.STATUS_CANCELLED,
            },
        )
        self.assertEqual(
            NotificationStatusService.ALLOWED_TRANSITIONS[
                Notification.STATUS_UNREAD
            ],
            {
                Notification.STATUS_READ,
                Notification.STATUS_ARCHIVED,
                Notification.STATUS_CANCELLED,
            },
        )
        self.assertEqual(
            NotificationStatusService.ALLOWED_TRANSITIONS[
                Notification.STATUS_READ
            ],
            {
                Notification.STATUS_UNREAD,
                Notification.STATUS_ARCHIVED,
            },
        )
        self.assertEqual(
            NotificationStatusService.ALLOWED_TRANSITIONS[
                Notification.STATUS_ARCHIVED
            ],
            {
                Notification.STATUS_UNREAD,
            },
        )
        self.assertEqual(
            NotificationStatusService.ALLOWED_TRANSITIONS[
                Notification.STATUS_FAILED
            ],
            {
                Notification.STATUS_CANCELLED,
            },
        )
        self.assertEqual(
            NotificationStatusService.ALLOWED_TRANSITIONS[
                Notification.STATUS_CANCELLED
            ],
            set(),
        )

    def test_event_type_map_contains_expected_specific_events(self):
        """Map notification statuses to expected specific audit event types."""
        self.assertEqual(
            NotificationStatusService.EVENT_TYPE_MAP[Notification.STATUS_READ],
            NotificationEvent.TYPE_READ,
        )
        self.assertEqual(
            NotificationStatusService.EVENT_TYPE_MAP[Notification.STATUS_ARCHIVED],
            NotificationEvent.TYPE_ARCHIVED,
        )
        self.assertEqual(
            NotificationStatusService.EVENT_TYPE_MAP[Notification.STATUS_CANCELLED],
            NotificationEvent.TYPE_CANCELLED,
        )
        self.assertEqual(
            NotificationStatusService.EVENT_TYPE_MAP[Notification.STATUS_FAILED],
            NotificationEvent.TYPE_FAILED,
        )

    def test_lifecycle_field_map_contains_expected_status_timestamps(self):
        """Map notification statuses to expected lifecycle timestamp fields."""
        self.assertEqual(
            NotificationStatusService.LIFECYCLE_FIELD_MAP[Notification.STATUS_READ],
            "read_at",
        )
        self.assertEqual(
            NotificationStatusService.LIFECYCLE_FIELD_MAP[
                Notification.STATUS_ARCHIVED
            ],
            "archived_at",
        )
        self.assertEqual(
            NotificationStatusService.LIFECYCLE_FIELD_MAP[
                Notification.STATUS_CANCELLED
            ],
            "cancelled_at",
        )
        self.assertEqual(
            NotificationStatusService.LIFECYCLE_FIELD_MAP[
                Notification.STATUS_FAILED
            ],
            "failed_at",
        )