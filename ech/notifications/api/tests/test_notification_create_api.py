import uuid

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import CustomUser
from ech.notifications.models import Notification


class NotificationCreateApiTestCase(APITestCase):

    def setUp(self):
        cache.clear()

        self.url = reverse("notifications-api:notification-create")

        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.support_staff = CustomUser.objects.create_user(
            email="support@company.com",
            password="StrongPassword123",
            user_name="Support Staff",
            role=CustomUser.ROLE_SUPPORT_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        self.admin = CustomUser.objects.create_user(
            email="admin@company.com",
            password="StrongPassword123",
            user_name="Admin User",
            role=CustomUser.ROLE_ADMIN,
            is_active=True,
            email_confirmed=True,
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def _build_payload(self, **overrides):
        payload = {
            "recipient_id": self.customer.id,
            "channel": "in_app",
            "notification_type": "order_update",
            "title": "Order Update",
            "message": "Your order has been updated.",
            "priority": "normal",
            "source_module": "orders",
            "source_event": "order_updated",
            "source_object_id": str(uuid.uuid4()),
            "metadata": {"order_id": "12345"},
            "idempotency_key": str(uuid.uuid4()),
        }

        payload.update(overrides)
        return payload

    def test_create_notification_returns_unauthorized_for_unauthenticated_user(self):
        """Reject notification creation for unauthenticated users."""

        payload = self._build_payload()

        response = self.client.post(self.url, payload, format="json")

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

        self.assertEqual(Notification.objects.count(), 0)

    def test_create_notification_successfully_as_support_staff(self):
        """Allow notification creation for support staff users."""

        self.authenticate(self.support_staff)

        payload = self._build_payload()

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 1)

        notification = Notification.objects.select_related(
            "recipient"
        ).get()

        self.assertEqual(notification.recipient, self.customer)
        self.assertEqual(notification.channel, "in_app")
        self.assertEqual(notification.notification_type, "order_update")
        self.assertEqual(notification.title, "Order Update")
        self.assertEqual(notification.priority, "normal")

        self.assertEqual(
            str(notification.idempotency_key),
            payload["idempotency_key"],
        )

        self.assertEqual(response.data["id"], str(notification.id))

    def test_create_notification_successfully_as_admin(self):
        """Allow notification creation for admin users."""

        self.authenticate(self.admin)

        payload = self._build_payload()

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 1)

    def test_create_notification_rejects_customer_user(self):
        """Reject notification creation for customer users."""

        self.authenticate(self.customer)

        payload = self._build_payload()

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Notification.objects.count(), 0)

    def test_create_notification_rejects_invalid_recipient(self):
        """Reject notification creation when recipient does not exist."""

        self.authenticate(self.support_staff)

        payload = self._build_payload(recipient_id=999999)

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Notification.objects.count(), 0)

    def test_create_notification_is_idempotent(self):
        """Return the same notification for repeated idempotent requests."""

        self.authenticate(self.support_staff)

        idem_key = str(uuid.uuid4())

        payload = self._build_payload(idempotency_key=idem_key)

        first_response = self.client.post(self.url, payload, format="json")
        second_response = self.client.post(self.url, payload, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)

        self.assertIn(
            second_response.status_code,
            {status.HTTP_200_OK, status.HTTP_201_CREATED},
        )

        self.assertEqual(Notification.objects.count(), 1)

        notification = Notification.objects.get()

        self.assertEqual(
            str(notification.idempotency_key),
            idem_key,
        )

    def test_create_notification_rejects_missing_required_fields(self):
        """Reject notification creation when required fields are missing."""

        self.authenticate(self.support_staff)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Notification.objects.count(), 0)