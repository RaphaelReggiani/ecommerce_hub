from django.db import transaction
from django.utils import timezone

from ech.notifications.domain_events.dispatcher import DomainEventDispatcher
from ech.notifications.domain_events.events import (
    NotificationDeliveryFailedEvent,
    NotificationDeliverySucceededEvent,
    NotificationDispatchedEvent,
)
from ech.notifications.exceptions import (
    InvalidNotificationOperationException,
    NotificationDeliveryChannelNotSupportedException,
    NotificationDeliveryFailedException,
    NotificationProviderException,
)
from ech.notifications.models import (
    Notification,
    NotificationDelivery,
    NotificationEvent,
)
from ech.notifications.providers.email_provider import EmailProvider
from ech.notifications.providers.in_app_provider import InAppProvider
from ech.notifications.services.notification_log_service import (
    NotificationLogService,
)
from ech.notifications.services.notification_status_service import (
    NotificationStatusService,
)


class NotificationDeliveryService:
    """
    Service responsible for notification delivery orchestration.

    This service resolves the intended notification channel strategy,
    delegates delivery to the appropriate provider(s), persists
    NotificationDelivery records, updates aggregate state, creates
    operational audit events, and emits domain events.

    Supported strategies:
    - in_app
    - email
    - both
    """

    CHANNEL_PROVIDER_MAP = {
        NotificationDelivery.CHANNEL_IN_APP: InAppProvider,
        NotificationDelivery.CHANNEL_EMAIL: EmailProvider,
    }

    @classmethod
    @transaction.atomic
    def dispatch_notification(
        cls,
        *,
        notification,
        performed_by=None,
        metadata=None,
    ):
        """
        Dispatch a notification according to its configured channel strategy.

        Args:
            notification: Notification instance.
            performed_by: Optional user performing the action.
            metadata: Optional metadata for audit/event trail.

        Returns:
            Notification: Updated notification instance.

        Raises:
            InvalidNotificationOperationException:
                If notification cannot be dispatched from the current state.
            NotificationDeliveryChannelNotSupportedException:
                If an unsupported channel is configured.
            NotificationDeliveryFailedException:
                If no delivery succeeds.
        """

        cls._validate_can_dispatch(notification=notification)

        channels = cls._resolve_channels(notification=notification)

        successful_deliveries = []
        failed_deliveries = []

        for channel in channels:
            delivery = cls._create_pending_delivery(
                notification=notification,
                channel=channel,
                performed_by=performed_by,
                metadata=metadata,
            )

            try:
                provider_result = cls._deliver_via_provider(
                    notification=notification,
                    channel=channel,
                )

                cls._mark_delivery_succeeded(
                    delivery=delivery,
                    provider_result=provider_result,
                    performed_by=performed_by,
                )

                cls._create_delivery_success_event(
                    notification=notification,
                    delivery=delivery,
                    performed_by=performed_by,
                    metadata=provider_result.get("metadata"),
                )

                NotificationLogService.log_notification_delivery_succeeded(
                    notification=notification,
                    delivery=delivery,
                    performed_by=performed_by,
                )

                DomainEventDispatcher.dispatch(
                    NotificationDeliverySucceededEvent(
                        notification_id=notification.id,
                        delivery_id=delivery.id,
                        recipient_id=notification.recipient_id,
                        channel=delivery.channel,
                        performed_by_id=getattr(performed_by, "id", None),
                    )
                )

                successful_deliveries.append(delivery)

            except NotificationDeliveryChannelNotSupportedException:
                raise

            except Exception as exc:
                cls._mark_delivery_failed(
                    delivery=delivery,
                    failure_code=exc.__class__.__name__,
                    failure_message=str(exc),
                    performed_by=performed_by,
                )

                cls._create_delivery_failed_event(
                    notification=notification,
                    delivery=delivery,
                    performed_by=performed_by,
                    metadata={
                        "failure_code": exc.__class__.__name__,
                        "failure_message": str(exc),
                    },
                )

                NotificationLogService.log_notification_delivery_failed(
                    notification=notification,
                    delivery=delivery,
                    performed_by=performed_by,
                )

                DomainEventDispatcher.dispatch(
                    NotificationDeliveryFailedEvent(
                        notification_id=notification.id,
                        delivery_id=delivery.id,
                        recipient_id=notification.recipient_id,
                        channel=delivery.channel,
                        performed_by_id=getattr(performed_by, "id", None),
                    )
                )

                failed_deliveries.append(delivery)

        cls._create_dispatch_event(
            notification=notification,
            performed_by=performed_by,
            metadata={
                "channels": channels,
                "successful_delivery_ids": [
                    str(delivery.id) for delivery in successful_deliveries
                ],
                "failed_delivery_ids": [
                    str(delivery.id) for delivery in failed_deliveries
                ],
                **(metadata or {}),
            },
        )

        DomainEventDispatcher.dispatch(
            NotificationDispatchedEvent(
                notification_id=notification.id,
                recipient_id=notification.recipient_id,
                channel=notification.channel,
                performed_by_id=getattr(performed_by, "id", None),
            )
        )

        if successful_deliveries:
            NotificationLogService.log_notification_dispatched(
                notification=notification,
                performed_by=performed_by,
            )

            return cls._promote_notification_after_successful_dispatch(
                notification=notification,
                performed_by=performed_by,
                metadata={
                    "successful_channels": [
                        delivery.channel for delivery in successful_deliveries
                    ],
                    **(metadata or {}),
                },
            )

        NotificationStatusService.mark_as_failed(
            notification=notification,
            failure_code="delivery_failed",
            failure_message="All delivery attempts failed.",
            performed_by=performed_by,
            metadata={
                "failed_channels": [
                    delivery.channel for delivery in failed_deliveries
                ],
                **(metadata or {}),
            },
        )

        raise NotificationDeliveryFailedException()

    @classmethod
    def _validate_can_dispatch(cls, *, notification):
        """
        Validate whether the notification can be dispatched.
        """

        if notification.status != Notification.STATUS_PENDING:
            raise InvalidNotificationOperationException()

    @classmethod
    def _resolve_channels(cls, *, notification):
        """
        Resolve the concrete channels to use from the aggregate strategy.
        """

        if notification.channel == Notification.CHANNEL_IN_APP:
            return [NotificationDelivery.CHANNEL_IN_APP]

        if notification.channel == Notification.CHANNEL_EMAIL:
            return [NotificationDelivery.CHANNEL_EMAIL]

        if notification.channel == Notification.CHANNEL_BOTH:
            return [
                NotificationDelivery.CHANNEL_IN_APP,
                NotificationDelivery.CHANNEL_EMAIL,
            ]

        raise NotificationDeliveryChannelNotSupportedException()

    @classmethod
    def _create_pending_delivery(
        cls,
        *,
        notification,
        channel,
        performed_by=None,
        metadata=None,
    ):
        """
        Create a pending delivery record before provider execution.
        """

        return NotificationDelivery.objects.create(
            notification=notification,
            channel=channel,
            status=NotificationDelivery.STATUS_PENDING,
            provider_name="",
            recipient_address="",
            external_message_id="",
            metadata=metadata or {},
            performed_by=performed_by,
        )

    @classmethod
    def _deliver_via_provider(
        cls,
        *,
        notification,
        channel,
    ):
        """
        Execute delivery through the configured provider for a channel.
        """

        provider_class = cls.CHANNEL_PROVIDER_MAP.get(channel)

        if not provider_class:
            raise NotificationDeliveryChannelNotSupportedException()

        provider_result = provider_class.deliver(
            notification=notification,
        )

        if not isinstance(provider_result, dict):
            raise NotificationProviderException(
                "Notification provider must return a dictionary payload."
            )

        return provider_result

    @classmethod
    def _mark_delivery_succeeded(
        cls,
        *,
        delivery,
        provider_result,
        performed_by=None,
    ):
        """
        Persist successful delivery outcome.
        """

        delivery.status = provider_result.get(
            "status",
            NotificationDelivery.STATUS_DELIVERED,
        )
        delivery.provider_name = provider_result.get("provider_name", "")
        delivery.recipient_address = provider_result.get("recipient_address", "")
        delivery.external_message_id = provider_result.get(
            "external_message_id",
            "",
        )
        delivery.metadata = provider_result.get("metadata", {}) or {}
        delivery.processed_at = timezone.now()
        delivery.performed_by = performed_by or delivery.performed_by

        delivery.save(
            update_fields=[
                "status",
                "provider_name",
                "recipient_address",
                "external_message_id",
                "metadata",
                "processed_at",
                "performed_by",
            ]
        )

    @classmethod
    def _mark_delivery_failed(
        cls,
        *,
        delivery,
        failure_code,
        failure_message,
        performed_by=None,
    ):
        """
        Persist failed delivery outcome.
        """

        delivery.status = NotificationDelivery.STATUS_FAILED
        delivery.failure_code = failure_code or ""
        delivery.failure_message = failure_message or ""
        delivery.processed_at = timezone.now()
        delivery.performed_by = performed_by or delivery.performed_by

        delivery.save(
            update_fields=[
                "status",
                "failure_code",
                "failure_message",
                "processed_at",
                "performed_by",
            ]
        )

    @classmethod
    def _promote_notification_after_successful_dispatch(
        cls,
        *,
        notification,
        performed_by=None,
        metadata=None,
    ):
        """
        Move the notification to unread state after at least one
        successful delivery.
        """

        notification.lifecycle.dispatched_at = timezone.now()
        notification.lifecycle.save(
            update_fields=["dispatched_at", "updated_at"]
        )

        return NotificationStatusService.mark_as_unread_after_dispatch(
            notification=notification,
            performed_by=performed_by,
            metadata=metadata,
        )

    @classmethod
    def _create_dispatch_event(
        cls,
        *,
        notification,
        performed_by=None,
        metadata=None,
    ):
        """
        Create aggregate dispatch audit event.
        """

        NotificationEvent.objects.create(
            notification=notification,
            event_type=NotificationEvent.TYPE_DISPATCHED,
            performed_by=performed_by,
            metadata=metadata or {},
        )

    @classmethod
    def _create_delivery_success_event(
        cls,
        *,
        notification,
        delivery,
        performed_by=None,
        metadata=None,
    ):
        """
        Create audit event for successful delivery.
        """

        NotificationEvent.objects.create(
            notification=notification,
            event_type=NotificationEvent.TYPE_DELIVERY_SENT,
            performed_by=performed_by,
            metadata={
                "delivery_id": str(delivery.id),
                "channel": delivery.channel,
                **(metadata or {}),
            },
        )

    @classmethod
    def _create_delivery_failed_event(
        cls,
        *,
        notification,
        delivery,
        performed_by=None,
        metadata=None,
    ):
        """
        Create audit event for failed delivery.
        """

        NotificationEvent.objects.create(
            notification=notification,
            event_type=NotificationEvent.TYPE_DELIVERY_FAILED,
            performed_by=performed_by,
            metadata={
                "delivery_id": str(delivery.id),
                "channel": delivery.channel,
                **(metadata or {}),
            },
        )