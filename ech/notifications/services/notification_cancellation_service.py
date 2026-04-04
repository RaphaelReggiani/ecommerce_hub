from django.db import transaction

from ech.notifications.domain_events.dispatcher import DomainEventDispatcher
from ech.notifications.domain_events.events import NotificationCancelledEvent
from ech.notifications.exceptions import (
    NotificationAlreadyArchivedException,
    NotificationAlreadyCancelledException,
    NotificationAlreadyReadException,
)
from ech.notifications.models import Notification
from ech.notifications.services.notification_log_service import (
    NotificationLogService,
)
from ech.notifications.services.notification_status_service import (
    NotificationStatusService,
)


class NotificationCancellationService:
    """
    Service responsible for notification cancellation operations.

    In the notifications domain, cancellation means the notification
    is no longer considered valid for active delivery or active user
    interaction, while preserving full auditability.

    This is intentionally different from other sub-apps such as
    shipping or orders, because notifications are UX-facing and
    operationally ephemeral rather than physical/business entities.
    """

    @classmethod
    @transaction.atomic
    def cancel_notification(
        cls,
        *,
        notification,
        performed_by=None,
        metadata=None,
    ):
        """
        Cancel a notification when business rules allow it.

        Args:
            notification: Notification instance.
            performed_by: Optional user performing the action.
            metadata: Optional metadata for audit/event trail.

        Returns:
            Notification: Updated cancelled notification instance.

        Raises:
            NotificationAlreadyCancelledException:
                If the notification is already cancelled.
            NotificationAlreadyReadException:
                If the notification has already been read.
            NotificationAlreadyArchivedException:
                If the notification has already been archived.
        """

        cls._validate_can_be_cancelled(notification=notification)

        cancellation_metadata = {
            "action": "notification_cancelled",
            **(metadata or {}),
        }

        cancelled_notification = NotificationStatusService.update_status(
            notification=notification,
            new_status=Notification.STATUS_CANCELLED,
            performed_by=performed_by,
            metadata=cancellation_metadata,
        )

        NotificationLogService.log_notification_cancelled(
            notification=cancelled_notification,
            performed_by=performed_by,
        )

        DomainEventDispatcher.dispatch(
            NotificationCancelledEvent(
                notification_id=cancelled_notification.id,
                recipient_id=cancelled_notification.recipient_id,
                performed_by_id=getattr(performed_by, "id", None),
            )
        )

        return cancelled_notification

    @classmethod
    def _validate_can_be_cancelled(cls, *, notification):
        """
        Validate whether the notification can be cancelled.
        """

        if notification.status == Notification.STATUS_CANCELLED:
            raise NotificationAlreadyCancelledException()

        if notification.status == Notification.STATUS_READ:
            raise NotificationAlreadyReadException()

        if notification.status == Notification.STATUS_ARCHIVED:
            raise NotificationAlreadyArchivedException()