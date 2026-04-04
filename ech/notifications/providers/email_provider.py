from django.conf import settings
from django.core.mail import send_mail

from ech.notifications.exceptions import (
    NotificationProviderException,
)
from ech.notifications.models import (
    NotificationDelivery,
)


class EmailProvider:
    """
    Provider responsible for email notification delivery.

    This provider sends the notification content through Django's
    email backend and returns a standardized payload for the
    delivery service.

    It does not persist NotificationDelivery records directly.
    That responsibility belongs to the delivery service.
    """

    PROVIDER_NAME = "email_provider"

    @classmethod
    def deliver(cls, *, notification):
        """
        Deliver a notification through the email channel.

        Args:
            notification: Notification instance.

        Returns:
            dict: Standardized provider result payload.

        Raises:
            NotificationProviderException:
                If the notification cannot be delivered.
        """

        cls._validate_notification(notification=notification)

        recipient_email = notification.recipient.user_email.strip().lower()

        subject = cls._build_subject(notification=notification)
        body = cls._build_body(notification=notification)
        from_email = cls._get_from_email()

        try:
            sent_count = send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
        except Exception as exc:
            raise NotificationProviderException(
                f"Email delivery failed: {str(exc)}"
            ) from exc

        if sent_count != 1:
            raise NotificationProviderException(
                "Email delivery did not send exactly one message."
            )

        return {
            "status": NotificationDelivery.STATUS_SENT,
            "provider_name": cls.PROVIDER_NAME,
            "recipient_address": recipient_email,
            "external_message_id": "",
            "metadata": {
                "delivery_mode": "email",
                "notification_id": str(notification.id),
                "recipient_id": str(notification.recipient_id),
                "subject": subject,
                "from_email": from_email,
            },
        }

    @staticmethod
    def _validate_notification(*, notification):
        """
        Validate whether the notification is eligible for email delivery.
        """

        if notification is None:
            raise NotificationProviderException(
                "Notification instance is required for email delivery."
            )

        if not getattr(notification, "id", None):
            raise NotificationProviderException(
                "Notification must be persisted before email delivery."
            )

        if not getattr(notification, "recipient", None):
            raise NotificationProviderException(
                "Notification recipient is required for email delivery."
            )

        recipient_email = getattr(notification.recipient, "user_email", "")

        if not recipient_email:
            raise NotificationProviderException(
                "Recipient email is required for email delivery."
            )

        if not getattr(notification, "title", None):
            raise NotificationProviderException(
                "Notification title is required for email delivery."
            )

        if not getattr(notification, "message", None):
            raise NotificationProviderException(
                "Notification message is required for email delivery."
            )

    @staticmethod
    def _build_subject(*, notification):
        """
        Build the email subject from notification data.
        """
        return notification.title.strip()

    @staticmethod
    def _build_body(*, notification):
        """
        Build the plain-text email body from notification data.
        """
        return notification.message.strip()

    @staticmethod
    def _get_from_email():
        """
        Resolve the sender email address from Django settings.
        """

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "").strip()

        if not from_email:
            raise NotificationProviderException(
                "DEFAULT_FROM_EMAIL is not configured."
            )

        return from_email