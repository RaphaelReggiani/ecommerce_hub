from ech.notifications.exceptions import (
    NotificationProviderException,
)
from ech.notifications.models import (
    NotificationDelivery,
)


class InAppProvider:
    """
    Provider responsible for in-app notification delivery.

    In the in-app channel, delivery means the notification is
    successfully available to the recipient within the application
    inbox/notification center.

    This provider does not persist NotificationDelivery records
    directly. That responsibility belongs to the delivery service.
    """

    PROVIDER_NAME = "in_app_provider"

    @classmethod
    def deliver(cls, *, notification):
        """
        Deliver a notification through the in-app channel.

        Args:
            notification: Notification instance.

        Returns:
            dict: Standardized provider result payload.

        Raises:
            NotificationProviderException:
                If the notification cannot be delivered.
        """

        cls._validate_notification(notification=notification)

        return {
            "status": NotificationDelivery.STATUS_DELIVERED,
            "provider_name": cls.PROVIDER_NAME,
            "recipient_address": "",
            "external_message_id": "",
            "metadata": {
                "delivery_mode": "in_app",
                "notification_id": str(notification.id),
                "recipient_id": str(notification.recipient_id),
            },
        }

    @staticmethod
    def _validate_notification(*, notification):
        """
        Validate whether the notification is eligible for in-app delivery.
        """

        if notification is None:
            raise NotificationProviderException(
                "Notification instance is required for in-app delivery."
            )

        if not getattr(notification, "id", None):
            raise NotificationProviderException(
                "Notification must be persisted before in-app delivery."
            )

        if not getattr(notification, "recipient_id", None):
            raise NotificationProviderException(
                "Notification recipient is required for in-app delivery."
            )

        if not getattr(notification, "title", None):
            raise NotificationProviderException(
                "Notification title is required for in-app delivery."
            )

        if not getattr(notification, "message", None):
            raise NotificationProviderException(
                "Notification message is required for in-app delivery."
            )