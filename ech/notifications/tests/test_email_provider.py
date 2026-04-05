from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from ech.notifications.exceptions import NotificationProviderException
from ech.notifications.models import Notification
from ech.notifications.providers.email_provider import EmailProvider


User = get_user_model()


class BaseEmailProviderFactoryMixin:
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

        data = {
            "recipient": recipient,
            "notification_type": "order_shipped",
            "title": "Order shipped",
            "message": "Your order has been shipped.",
            "status": Notification.STATUS_PENDING,
            "channel": Notification.CHANNEL_EMAIL,
            "priority": Notification.PRIORITY_NORMAL,
            "source_module": "orders",
            "source_event": "order_shipped",
            "source_object_id": "ORDER-001",
            "metadata": {"source": "unit-test"},
        }
        data.update(kwargs)
        return Notification.objects.create(**data)


class EmailProviderTestCase(BaseEmailProviderFactoryMixin, TestCase):
    @patch("ech.notifications.providers.email_provider.send_mail")
    def test_deliver_success_returns_expected_payload(self, send_mail_mock):
        """Send notification email successfully and return provider payload."""
        recipient = self.create_user(email="customer@test.com")
        notification = self.create_notification(recipient=recipient)

        send_mail_mock.return_value = 1

        result = EmailProvider.deliver(notification=notification)

        send_mail_mock.assert_called_once()
        self.assertEqual(result["status"], "sent")
        self.assertEqual(result["provider_name"], "email_provider")
        self.assertEqual(result["recipient_address"], "customer@test.com")
        self.assertIn("external_message_id", result)
        self.assertIn("metadata", result)

    @patch("ech.notifications.providers.email_provider.send_mail")
    def test_deliver_raises_provider_exception_when_send_mail_returns_zero(
        self,
        send_mail_mock,
    ):
        """Raise NotificationProviderException when email backend reports zero sent messages."""
        recipient = self.create_user(email="customer@test.com")
        notification = self.create_notification(recipient=recipient)

        send_mail_mock.return_value = 0

        with self.assertRaises(NotificationProviderException) as context:
            EmailProvider.deliver(notification=notification)

        self.assertEqual(
            str(context.exception),
            "Email delivery did not send exactly one message.",
        )

    @patch("ech.notifications.providers.email_provider.send_mail")
    def test_deliver_raises_provider_exception_when_backend_raises_error(
        self,
        send_mail_mock,
    ):
        """Raise NotificationProviderException when email backend fails."""
        recipient = self.create_user(email="customer@test.com")
        notification = self.create_notification(recipient=recipient)

        send_mail_mock.side_effect = Exception("SMTP backend failure")

        with self.assertRaises(NotificationProviderException):
            EmailProvider.deliver(notification=notification)

    @patch("ech.notifications.providers.email_provider.send_mail")
    def test_deliver_raises_provider_exception_when_recipient_email_is_missing(
        self,
        send_mail_mock,
    ):
        """Raise NotificationProviderException when recipient has no usable email address."""
        recipient = self.create_user(email="valid@test.com")
        recipient.email = ""
        notification = self.create_notification(recipient=recipient)

        send_mail_mock.return_value = 0

        with self.assertRaises(NotificationProviderException) as context:
            EmailProvider.deliver(notification=notification)

        self.assertEqual(
            str(context.exception),
            "Email delivery did not send exactly one message.",
        )
        send_mail_mock.assert_called_once()