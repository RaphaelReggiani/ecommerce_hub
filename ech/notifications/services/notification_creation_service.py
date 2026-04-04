from django.db import IntegrityError, transaction

from ech.notifications.domain_events.dispatcher import DomainEventDispatcher
from ech.notifications.domain_events.events import NotificationCreatedEvent
from ech.notifications.exceptions import (
    NotificationCreationException,
    NotificationIdempotencyConflictException,
)
from ech.notifications.models import (
    Notification,
    NotificationEvent,
    NotificationLifecycle,
)
from ech.notifications.services.cache_service import (
    NotificationCacheService,
)
from ech.notifications.services.notification_log_service import (
    NotificationLogService,
)


class NotificationCreationService:
    """
    Service responsible for notification creation.

    Creates the notification aggregate root plus its initial related
    records such as lifecycle and audit event.

    Idempotency behavior:
    - If the same idempotency_key is reused with the same logical payload,
      the existing notification is returned.
    - If the same idempotency_key is reused with a different payload,
      a NotificationIdempotencyConflictException is raised.
    """

    @classmethod
    @transaction.atomic
    def create_notification(
        cls,
        *,
        recipient,
        notification_type,
        title,
        message,
        channel=Notification.CHANNEL_IN_APP,
        priority=Notification.PRIORITY_NORMAL,
        source_module="",
        source_event="",
        source_object_id="",
        scheduled_for=None,
        metadata=None,
        idempotency_key=None,
        created_by=None,
        performed_by=None,
    ):
        """
        Create a notification.

        Args:
            recipient: Notification recipient instance.
            notification_type: Business notification type.
            title: Notification title.
            message: Notification message body.
            channel: Intended delivery channel strategy.
            priority: Notification priority.
            source_module: Optional source module reference.
            source_event: Optional source event reference.
            source_object_id: Optional source object reference.
            scheduled_for: Optional deferred dispatch datetime.
            metadata: Optional flexible context payload.
            idempotency_key: Optional idempotency key.
            created_by: Optional creator user.
            performed_by: Optional user performing the action.

        Returns:
            Notification: Created notification instance, or the existing one
            if the same idempotency key is replayed with an equivalent payload.

        Raises:
            NotificationIdempotencyConflictException:
                If the same idempotency key is reused with a different payload.
            NotificationCreationException:
                If notification creation fails unexpectedly.
        """

        cls._validate_required_fields(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
        )

        normalized_payload = cls._normalized_payload(
            notification_type=notification_type,
            title=title,
            message=message,
            channel=channel,
            priority=priority,
            source_module=source_module,
            source_event=source_event,
            source_object_id=source_object_id,
            scheduled_for=scheduled_for,
            metadata=metadata,
        )

        if idempotency_key:
            existing_notification = cls._get_notification_by_idempotency_key(
                idempotency_key=idempotency_key,
            )
            if existing_notification:
                cls._validate_idempotent_reuse(
                    notification=existing_notification,
                    recipient=recipient,
                    created_by=created_by,
                    **normalized_payload,
                )
                return existing_notification

        try:
            notification = Notification.objects.create(
                recipient=recipient,
                created_by=created_by,
                notification_type=normalized_payload["notification_type"],
                title=normalized_payload["title"],
                message=normalized_payload["message"],
                status=Notification.STATUS_PENDING,
                channel=normalized_payload["channel"],
                priority=normalized_payload["priority"],
                source_module=normalized_payload["source_module"],
                source_event=normalized_payload["source_event"],
                source_object_id=normalized_payload["source_object_id"],
                scheduled_for=normalized_payload["scheduled_for"],
                idempotency_key=idempotency_key,
                metadata=normalized_payload["metadata"],
            )

            NotificationLifecycle.objects.create(
                notification=notification,
            )

            NotificationEvent.objects.create(
                notification=notification,
                event_type=NotificationEvent.TYPE_CREATED,
                performed_by=performed_by,
                metadata={
                    "recipient_id": str(recipient.id),
                    "created_by_id": (
                        str(created_by.id) if created_by else None
                    ),
                    "notification_type": notification.notification_type,
                    "channel": notification.channel,
                    "priority": notification.priority,
                    "source_module": notification.source_module,
                    "source_event": notification.source_event,
                    "source_object_id": notification.source_object_id,
                    "scheduled_for": (
                        notification.scheduled_for.isoformat()
                        if notification.scheduled_for
                        else None
                    ),
                    "idempotency_key": (
                        str(idempotency_key) if idempotency_key else None
                    ),
                    "metadata": normalized_payload["metadata"],
                },
            )

            NotificationLogService.log_notification_created(
                notification=notification,
                performed_by=performed_by,
            )

            DomainEventDispatcher.dispatch(
                NotificationCreatedEvent(
                    notification_id=notification.id,
                    recipient_id=recipient.id,
                    notification_type=notification.notification_type,
                    channel=notification.channel,
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

        except IntegrityError as exc:
            resolved_notification = cls._resolve_integrity_conflict(
                recipient=recipient,
                created_by=created_by,
                idempotency_key=idempotency_key,
                **normalized_payload,
            )

            if resolved_notification:
                return resolved_notification

            raise NotificationCreationException() from exc

    @staticmethod
    def _get_notification_by_idempotency_key(*, idempotency_key):
        """
        Retrieve an existing notification by idempotency key.
        """
        return (
            Notification.objects.select_related(
                "recipient",
                "created_by",
                "lifecycle",
            )
            .prefetch_related(
                "deliveries",
                "events",
            )
            .filter(idempotency_key=idempotency_key)
            .first()
        )

    @classmethod
    def _resolve_integrity_conflict(
        cls,
        *,
        recipient,
        created_by,
        notification_type,
        title,
        message,
        channel,
        priority,
        source_module,
        source_event,
        source_object_id,
        scheduled_for,
        metadata,
        idempotency_key,
    ):
        """
        Resolve conflicts raised during concurrent creation attempts.

        Returns:
            Notification | None: Existing notification to reuse, if resolvable.

        Raises:
            NotificationIdempotencyConflictException:
                If the idempotency key was reused with different payload.
        """
        if idempotency_key:
            existing_notification = cls._get_notification_by_idempotency_key(
                idempotency_key=idempotency_key,
            )
            if existing_notification:
                cls._validate_idempotent_reuse(
                    notification=existing_notification,
                    recipient=recipient,
                    created_by=created_by,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    channel=channel,
                    priority=priority,
                    source_module=source_module,
                    source_event=source_event,
                    source_object_id=source_object_id,
                    scheduled_for=scheduled_for,
                    metadata=metadata,
                )
                return existing_notification

        return None

    @classmethod
    def _validate_idempotent_reuse(
        cls,
        *,
        notification,
        recipient,
        created_by,
        notification_type,
        title,
        message,
        channel,
        priority,
        source_module,
        source_event,
        source_object_id,
        scheduled_for,
        metadata,
    ):
        """
        Ensure an existing notification associated with the same idempotency key
        represents the same logical create request.
        """
        same_payload = all(
            [
                notification.recipient_id == recipient.id,
                notification.created_by_id == getattr(created_by, "id", None),
                notification.notification_type == notification_type,
                notification.title == title,
                notification.message == message,
                notification.channel == channel,
                notification.priority == priority,
                (notification.source_module or "") == (source_module or ""),
                (notification.source_event or "") == (source_event or ""),
                (notification.source_object_id or "")
                == (source_object_id or ""),
                notification.scheduled_for == scheduled_for,
                cls._normalized_metadata(metadata=notification.metadata)
                == cls._normalized_metadata(metadata=metadata),
            ]
        )

        if not same_payload:
            raise NotificationIdempotencyConflictException()

    @staticmethod
    def _validate_required_fields(
        *,
        recipient,
        notification_type,
        title,
        message,
    ):
        """
        Validate required notification creation fields.
        """

        if not recipient:
            raise NotificationCreationException(
                "Notification recipient is required."
            )

        if not notification_type or not str(notification_type).strip():
            raise NotificationCreationException(
                "Notification type is required."
            )

        if not title or not str(title).strip():
            raise NotificationCreationException(
                "Notification title is required."
            )

        if not message or not str(message).strip():
            raise NotificationCreationException(
                "Notification message is required."
            )

    @classmethod
    def _normalized_payload(
        cls,
        *,
        notification_type,
        title,
        message,
        channel,
        priority,
        source_module,
        source_event,
        source_object_id,
        scheduled_for,
        metadata,
    ):
        """
        Normalize payload values for stable persistence and
        idempotency comparison.
        """
        return {
            "notification_type": str(notification_type).strip(),
            "title": str(title).strip(),
            "message": str(message).strip(),
            "channel": channel,
            "priority": priority,
            "source_module": (source_module or "").strip(),
            "source_event": (source_event or "").strip(),
            "source_object_id": str(source_object_id).strip()
            if source_object_id not in (None, "")
            else "",
            "scheduled_for": scheduled_for,
            "metadata": cls._normalized_metadata(metadata=metadata),
        }

    @staticmethod
    def _normalized_metadata(*, metadata):
        """
        Normalize optional metadata for stable idempotency comparison.
        """
        return metadata or {}