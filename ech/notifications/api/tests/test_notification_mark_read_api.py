import uuid
from datetime import timedelta

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import CustomUser
from ech.notifications.models import (
    Notification,
    NotificationLifecycle,
)


class NotificationMarkReadApiTestCase(APITestCase):

    def setUp(self):
        cache.clear()

        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.other_customer = CustomUser.objects.create_user(
            email="other_customer@test.com",
            password="StrongPassword123",
            user_name="Other Customer",
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

        self.notification = self._create_notification(
            recipient=self.customer,
            status="unread",
        )

        self.url = reverse(
            "notifications-api:notification-mark-read",
            kwargs={"notification_id": self.notification.id},
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def _create_notification(self, *, recipient, status):
        notification = Notification.objects.create(
            recipient=recipient,
            status=status,
            channel="in_app",
            notification_type="order_update",
            title="Order Update",
            message="Test message",
            priority="normal",
            source_module="orders",
            source_event="order_created",
            source_object_id=str(uuid.uuid4()),
            scheduled_for=timezone.now() + timedelta(hours=1),
            idempotency_key=uuid.uuid4(),
        )

        NotificationLifecycle.objects.create(notification=notification)

        return notification

    def test_mark_read_returns_unauthorized_for_unauthenticated_user(self):
        """Reject mark-read operation for unauthenticated users."""

        response = self.client.post(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_mark_read_successfully_for_owner(self):
        """Allow notification owner to mark notification as read."""

        self.authenticate(self.customer)

        response = self.client.post(self.url)

        self.notification.refresh_from_db()
        self.notification.lifecycle.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.notification.status, "read")
        self.assertIsNotNone(self.notification.lifecycle.read_at)

    def test_mark_read_rejects_other_customer(self):
        """Reject mark-read when a different customer attempts the operation."""

        self.authenticate(self.other_customer)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_read_allows_staff(self):
        """Allow staff users to mark notification as read."""

        self.authenticate(self.support_staff)

        response = self.client.post(self.url)

        self.notification.refresh_from_db()
        self.notification.lifecycle.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.notification.status, "read")
        self.assertIsNotNone(self.notification.lifecycle.read_at)

    def test_mark_read_is_idempotent_when_already_read(self):
        """Ensure mark-read operation is idempotent."""

        self.notification.status = "read"
        self.notification.save(update_fields=["status"])

        self.authenticate(self.customer)

        response = self.client.post(self.url)

        self.notification.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.notification.status, "read")

    def test_mark_read_returns_404_for_nonexistent_notification(self):
        """Return 404 when notification does not exist."""

        self.authenticate(self.customer)

        url = reverse(
            "notifications-api:notification-mark-read",
            kwargs={"notification_id": uuid.uuid4()},
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)