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


class NotificationCancelApiTestCase(APITestCase):

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

        self.notification = self._create_notification(
            recipient=self.customer,
            status=Notification.STATUS_PENDING,
        )

        self.url = reverse(
            "notifications-api:notification-cancel",
            kwargs={"notification_id": self.notification.id},
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def _create_notification(self, *, recipient, status):
        notification = Notification.objects.create(
            recipient=recipient,
            status=status,
            channel=Notification.CHANNEL_IN_APP,
            notification_type="order_update",
            title="Cancel Test",
            message="Test message",
            priority=Notification.PRIORITY_NORMAL,
            source_module="orders",
            source_event="order_created",
            source_object_id=str(uuid.uuid4()),
            scheduled_for=timezone.now() + timedelta(hours=1),
            idempotency_key=uuid.uuid4(),
        )

        NotificationLifecycle.objects.create(notification=notification)

        return notification

    def test_cancel_notification_returns_unauthorized_for_unauthenticated_user(self):
        """Reject notification cancellation for unauthenticated users."""

        response = self.client.post(self.url, {}, format="json")

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_cancel_notification_rejects_customer_user(self):
        """Reject notification cancellation for customer users."""

        self.authenticate(self.customer)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cancel_notification_successfully_as_support_staff(self):
        """Allow notification cancellation by support staff."""

        self.authenticate(self.support_staff)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.notification.refresh_from_db()
        self.notification.lifecycle.refresh_from_db()

        self.assertEqual(
            self.notification.status,
            Notification.STATUS_CANCELLED,
        )
        self.assertIsNotNone(self.notification.lifecycle.cancelled_at)

    def test_cancel_notification_successfully_as_admin(self):
        """Allow notification cancellation by admin users."""

        self.authenticate(self.admin)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.notification.refresh_from_db()
        self.notification.lifecycle.refresh_from_db()

        self.assertEqual(
            self.notification.status,
            Notification.STATUS_CANCELLED,
        )
        self.assertIsNotNone(self.notification.lifecycle.cancelled_at)

    def test_cancel_notification_is_idempotent_when_already_cancelled(self):
        """Return success when notification is already cancelled."""

        self.authenticate(self.support_staff)

        self.notification.status = Notification.STATUS_CANCELLED
        self.notification.save(update_fields=["status"])

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.notification.refresh_from_db()
        self.assertEqual(
            self.notification.status,
            Notification.STATUS_CANCELLED,
        )

    def test_cancel_notification_rejects_read_notification(self):
        """Reject cancellation when notification is already read."""

        self.authenticate(self.support_staff)

        self.notification.status = Notification.STATUS_READ
        self.notification.save(update_fields=["status"])

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_notification_rejects_archived_notification(self):
        """Reject cancellation when notification is already archived."""

        self.authenticate(self.support_staff)

        self.notification.status = Notification.STATUS_ARCHIVED
        self.notification.save(update_fields=["status"])

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_notification_returns_404_for_nonexistent_notification(self):
        """Return 404 when notification does not exist."""

        self.authenticate(self.support_staff)

        url = reverse(
            "notifications-api:notification-cancel",
            kwargs={"notification_id": uuid.uuid4()},
        )

        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)