import logging


logger = logging.getLogger(__name__)


class NotificationLogService:
    """
    Service responsible for structured notification domain logs.
    """

    @staticmethod
    def log_notification_created(*, notification, performed_by=None):
        """
        Log notification creation.
        """

        logger.info(
            "Notification created.",
            extra={
                "notification_id": str(notification.id),
                "recipient_id": str(notification.recipient_id),
                "created_by_id": (
                    str(notification.created_by_id)
                    if notification.created_by_id
                    else None
                ),
                "notification_type": notification.notification_type,
                "status": notification.status,
                "channel": notification.channel,
                "priority": notification.priority,
                "source_module": notification.source_module,
                "source_event": notification.source_event,
                "source_object_id": notification.source_object_id,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_notification_status_changed(
        *,
        notification,
        previous_status,
        new_status,
        performed_by=None,
    ):
        """
        Log notification status transition.
        """

        logger.info(
            "Notification status changed.",
            extra={
                "notification_id": str(notification.id),
                "recipient_id": str(notification.recipient_id),
                "created_by_id": (
                    str(notification.created_by_id)
                    if notification.created_by_id
                    else None
                ),
                "notification_type": notification.notification_type,
                "previous_status": previous_status,
                "new_status": new_status,
                "channel": notification.channel,
                "priority": notification.priority,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_notification_cancelled(*, notification, performed_by=None):
        """
        Log notification cancellation.
        """

        logger.info(
            "Notification cancelled.",
            extra={
                "notification_id": str(notification.id),
                "recipient_id": str(notification.recipient_id),
                "created_by_id": (
                    str(notification.created_by_id)
                    if notification.created_by_id
                    else None
                ),
                "notification_type": notification.notification_type,
                "status": notification.status,
                "channel": notification.channel,
                "priority": notification.priority,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_notification_dispatched(*, notification, performed_by=None):
        """
        Log notification dispatch.
        """

        logger.info(
            "Notification dispatched.",
            extra={
                "notification_id": str(notification.id),
                "recipient_id": str(notification.recipient_id),
                "created_by_id": (
                    str(notification.created_by_id)
                    if notification.created_by_id
                    else None
                ),
                "notification_type": notification.notification_type,
                "status": notification.status,
                "channel": notification.channel,
                "priority": notification.priority,
                "scheduled_for": (
                    notification.scheduled_for.isoformat()
                    if notification.scheduled_for
                    else None
                ),
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_notification_delivery_succeeded(
        *,
        notification,
        delivery,
        performed_by=None,
    ):
        """
        Log successful notification delivery.
        """

        logger.info(
            "Notification delivery succeeded.",
            extra={
                "notification_id": str(notification.id),
                "recipient_id": str(notification.recipient_id),
                "created_by_id": (
                    str(notification.created_by_id)
                    if notification.created_by_id
                    else None
                ),
                "notification_type": notification.notification_type,
                "delivery_id": str(delivery.id),
                "delivery_channel": delivery.channel,
                "delivery_status": delivery.status,
                "provider_name": delivery.provider_name,
                "recipient_address": delivery.recipient_address,
                "external_message_id": delivery.external_message_id,
                "processed_at": (
                    delivery.processed_at.isoformat()
                    if delivery.processed_at
                    else None
                ),
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_notification_delivery_failed(
        *,
        notification,
        delivery,
        performed_by=None,
    ):
        """
        Log failed notification delivery.
        """

        logger.warning(
            "Notification delivery failed.",
            extra={
                "notification_id": str(notification.id),
                "recipient_id": str(notification.recipient_id),
                "created_by_id": (
                    str(notification.created_by_id)
                    if notification.created_by_id
                    else None
                ),
                "notification_type": notification.notification_type,
                "delivery_id": str(delivery.id),
                "delivery_channel": delivery.channel,
                "delivery_status": delivery.status,
                "provider_name": delivery.provider_name,
                "recipient_address": delivery.recipient_address,
                "failure_code": delivery.failure_code,
                "failure_message": delivery.failure_message,
                "processed_at": (
                    delivery.processed_at.isoformat()
                    if delivery.processed_at
                    else None
                ),
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )