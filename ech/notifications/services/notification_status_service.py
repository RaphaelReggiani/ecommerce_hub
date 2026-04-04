from django.db import transaction
from django.utils import timezone

from ech.notifications.domain_events.dispatcher import DomainEventDispatcher
from ech.notifications.domain_events.events import NotificationStatusChangedEvent
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
)
from ech.notifications.services.cache_service import (
    NotificationCacheService,
)
from ech.notifications.services.notification_log_service import (
    NotificationLogService,
)


class NotificationStatusService:
    """
    Service responsible for notification status transitions.
    """

    ALLOWED_TRANSITIONS = {
        Notification.STATUS_PENDING: {
            Notification.STATUS_UNREAD,
            Notification.STATUS_FAILED,
            Notification.STATUS_CANCELLED,
        },
        Notification.STATUS_UNREAD: {
            Notification.STATUS_READ,
            Notification.STATUS_ARCHIVED,
            Notification.STATUS_CANCELLED,
        },
        Notification.STATUS_READ: {
            Notification.STATUS_UNREAD,
            Notification.STATUS_ARCHIVED,
        },
        Notification.STATUS_ARCHIVED: {
            Notification.STATUS_UNREAD,
        },
        Notification.STATUS_FAILED: {
            Notification.STATUS_CANCELLED,
        },
        Notification.STATUS_CANCELLED: set(),
    }

    EVENT_TYPE_MAP = {
        Notification.STATUS_READ: NotificationEvent.TYPE_READ,
        Notification.STATUS_ARCHIVED: NotificationEvent.TYPE_ARCHIVED,
        Notification.STATUS_CANCELLED: NotificationEvent.TYPE_CANCELLED,
        Notification.STATUS_FAILED: NotificationEvent.TYPE_FAILED,
    }

    LIFECYCLE_FIELD_MAP = {
        Notification.STATUS_READ: "read_at",
        Notification.STATUS_ARCHIVED: "archived_at",
        Notification.STATUS_CANCELLED: "cancelled_at",
        Notification.STATUS_FAILED: "failed_at",
    }

    @classmethod
    @transaction.atomic
    def update_status(
        cls,
        *,
        notification,
        new_status,
        performed_by=None,
        metadata=None,
    ):
        """
        Update notification status in a controlled and auditable way.
        """

        current_status = notification.status

        cls._validate_terminal_status(notification=notification)
        cls._validate_transition(
            current_status=current_status,
            new_status=new_status,
        )

        notification.status = new_status
        update_fields = ["status", "updated_at"]

        if new_status == Notification.STATUS_FAILED:
            notification.failure_code = (
                (metadata or {}).get("failure_code", "")
            )
            notification.failure_message = (
                (metadata or {}).get("failure_message", "")
            )
            update_fields.extend(["failure_code", "failure_message"])
        else:
            if notification.failure_code:
                notification.failure_code = ""
                update_fields.append("failure_code")

            if notification.failure_message:
                notification.failure_message = ""
                update_fields.append("failure_message")

        notification.save(update_fields=update_fields)

        cls._update_lifecycle_timestamp(
            notification=notification,
            previous_status=current_status,
            new_status=new_status,
        )

        cls._create_status_change_event(
            notification=notification,
            previous_status=current_status,
            new_status=new_status,
            performed_by=performed_by,
            metadata=metadata,
        )

        NotificationLogService.log_notification_status_changed(
            notification=notification,
            previous_status=current_status,
            new_status=new_status,
            performed_by=performed_by,
        )

        DomainEventDispatcher.dispatch(
            NotificationStatusChangedEvent(
                notification_id=notification.id,
                previous_status=current_status,
                new_status=new_status,
                performed_by_id=getattr(performed_by, "id", None),
            )
        )

        transaction.on_commit(
            lambda: NotificationCacheService.invalidate_after_mutation(
                notification_id=notification.id,
                recipient_id=notification.recipient_id,
            )
        )

        return notification

    @classmethod
    def mark_as_read(
        cls,
        *,
        notification,
        performed_by=None,
        metadata=None,
    ):
        """
        Mark a notification as read.
        """

        if notification.status == Notification.STATUS_READ:
            raise NotificationAlreadyReadException()

        return cls.update_status(
            notification=notification,
            new_status=Notification.STATUS_READ,
            performed_by=performed_by,
            metadata=metadata,
        )

    @classmethod
    def archive(
        cls,
        *,
        notification,
        performed_by=None,
        metadata=None,
    ):
        """
        Archive a notification.
        """

        if notification.status == Notification.STATUS_ARCHIVED:
            raise NotificationAlreadyArchivedException()

        return cls.update_status(
            notification=notification,
            new_status=Notification.STATUS_ARCHIVED,
            performed_by=performed_by,
            metadata=metadata,
        )

    @classmethod
    def mark_as_unread(
        cls,
        *,
        notification,
        performed_by=None,
        metadata=None,
    ):
        """
        Restore a notification to unread state.
        """

        if notification.status not in {
            Notification.STATUS_READ,
            Notification.STATUS_ARCHIVED,
        }:
            raise InvalidNotificationOperationException()

        return cls.update_status(
            notification=notification,
            new_status=Notification.STATUS_UNREAD,
            performed_by=performed_by,
            metadata=metadata,
        )

    @classmethod
    def mark_as_failed(
        cls,
        *,
        notification,
        failure_code="",
        failure_message="",
        performed_by=None,
        metadata=None,
    ):
        """
        Mark a notification as failed.
        """

        merged_metadata = {
            **(metadata or {}),
            "failure_code": failure_code,
            "failure_message": failure_message,
        }

        return cls.update_status(
            notification=notification,
            new_status=Notification.STATUS_FAILED,
            performed_by=performed_by,
            metadata=merged_metadata,
        )

    @classmethod
    def mark_as_unread_after_dispatch(
        cls,
        *,
        notification,
        performed_by=None,
        metadata=None,
    ):
        """
        Move a pending notification to unread after successful dispatch.
        """

        if notification.status != Notification.STATUS_PENDING:
            raise InvalidNotificationOperationException()

        return cls.update_status(
            notification=notification,
            new_status=Notification.STATUS_UNREAD,
            performed_by=performed_by,
            metadata=metadata,
        )

    @classmethod
    def _validate_terminal_status(cls, *, notification):
        """
        Prevent changes to terminal notification states.
        """

        if notification.status == Notification.STATUS_CANCELLED:
            raise NotificationAlreadyCancelledException()

    @classmethod
    def _validate_transition(cls, *, current_status, new_status):
        """
        Validate whether the status transition is allowed.
        """

        allowed_statuses = cls.ALLOWED_TRANSITIONS.get(
            current_status,
            set(),
        )

        if new_status not in allowed_statuses:
            raise InvalidNotificationStateTransitionException()

    @classmethod
    def _update_lifecycle_timestamp(
        cls,
        *,
        notification,
        previous_status,
        new_status,
    ):
        """
        Update the lifecycle timestamp associated with the new status.
        """

        lifecycle = notification.lifecycle
        lifecycle_field = cls.LIFECYCLE_FIELD_MAP.get(new_status)

        if lifecycle_field:
            setattr(lifecycle, lifecycle_field, timezone.now())

        if new_status == Notification.STATUS_UNREAD:
            if previous_status == Notification.STATUS_READ:
                lifecycle.read_at = None

            if previous_status == Notification.STATUS_ARCHIVED:
                lifecycle.archived_at = None

            lifecycle.save(
                update_fields=["read_at", "archived_at", "updated_at"]
            )
            return

        update_fields = ["updated_at"]

        if lifecycle_field:
            update_fields.insert(0, lifecycle_field)

        lifecycle.save(update_fields=update_fields)

    @classmethod
    def _create_status_change_event(
        cls,
        *,
        notification,
        previous_status,
        new_status,
        performed_by=None,
        metadata=None,
    ):
        """
        Create audit trail records for notification status transition.
        """

        NotificationEvent.objects.create(
            notification=notification,
            event_type=NotificationEvent.TYPE_STATUS_CHANGED,
            performed_by=performed_by,
            metadata={
                "previous_status": previous_status,
                "new_status": new_status,
                **(metadata or {}),
            },
        )

        specific_event_type = cls.EVENT_TYPE_MAP.get(new_status)

        if specific_event_type:
            NotificationEvent.objects.create(
                notification=notification,
                event_type=specific_event_type,
                performed_by=performed_by,
                metadata=metadata or {},
            )