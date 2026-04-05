import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from ech.notifications.models import Notification
from ech.notifications.providers.in_app_provider import InAppProvider


User = get_user_model()


class BaseInAppProviderFactoryMixin:
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
            "channel": Notification.CHANNEL_IN_APP,
            "priority": Notification.PRIORITY_NORMAL,
            "source_module": "orders",
            "source_event": "order_shipped",
            "source_object_id": "ORDER-001",
            "metadata": {"source": "unit-test"},
        }
        data.update(kwargs)
        return Notification.objects.create(**data)


class InAppProviderTestCase(BaseInAppProviderFactoryMixin, TestCase):
    def test_deliver_returns_expected_payload(self):
        """Return structured payload for successful in-app delivery."""
        recipient = self.create_user()
        notification = self.create_notification(recipient=recipient)

        result = InAppProvider.deliver(notification=notification)

        self.assertEqual(result["status"], "delivered")
        self.assertEqual(result["provider_name"], "in_app_provider")
        self.assertEqual(result["recipient_address"], "")
        self.assertIn("external_message_id", result)
        self.assertIn("metadata", result)

    def test_deliver_returns_string_external_message_id(self):
        """Return external message id as a string, even if blank."""
        notification = self.create_notification()

        result = InAppProvider.deliver(notification=notification)

        self.assertIsInstance(result["external_message_id"], str)

    def test_deliver_returns_metadata_dictionary(self):
        """Return metadata as a dictionary."""
        notification = self.create_notification()

        result = InAppProvider.deliver(notification=notification)

        self.assertIsInstance(result["metadata"], dict)

    def test_deliver_is_deterministic_in_contract_shape(self):
        """Always return the expected payload keys for in-app delivery."""
        notification = self.create_notification()

        result = InAppProvider.deliver(notification=notification)

        self.assertEqual(
            set(result.keys()),
            {
                "status",
                "provider_name",
                "recipient_address",
                "external_message_id",
                "metadata",
            },
        )