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


class NotificationManagementDetailApiTestCase(APITestCase):

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

        self.staff = CustomUser.objects.create_user(
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
            created_by=self.admin,
        )

        self.url = reverse(
            "notifications-api:notification-management-detail",
            kwargs={"notification_id": self.notification.id},
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def _create_notification(self, *, recipient, created_by=None):
        notification = Notification.objects.create(
            recipient=recipient,
            created_by=created_by,
            status="unread",
            channel="in_app",
            notification_type="order_update",
            title="Test Notification",
            message="Test message",
            priority="normal",
            source_module="orders",
            source_event="event",
            source_object_id=str(uuid.uuid4()),
            scheduled_for=timezone.now() + timedelta(hours=1),
            idempotency_key=uuid.uuid4(),
        )

        NotificationLifecycle.objects.create(notification=notification)

        return notification

    def test_management_detail_requires_authentication(self):
        """Reject management detail for unauthenticated users."""

        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_management_detail_rejects_customer_user(self):
        """Reject management detail access for customer users."""

        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_management_detail_allows_staff_user(self):
        """Allow staff users to access notification management detail."""

        self.authenticate(self.staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.notification.id))
        self.assertEqual(response.data["recipient"], self.customer.id)

    def test_management_detail_allows_admin_user(self):
        """Allow admin users to access notification management detail."""

        self.authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.notification.id))
        self.assertEqual(response.data["recipient"], self.customer.id)

    def test_management_detail_returns_404_for_nonexistent_notification(self):
        """Return 404 when notification does not exist."""

        self.authenticate(self.staff)

        url = reverse(
            "notifications-api:notification-management-detail",
            kwargs={"notification_id": uuid.uuid4()},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_management_detail_returns_expected_fields(self):
        """Return expected fields in notification management detail response."""

        self.authenticate(self.staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("id", response.data)
        self.assertIn("recipient", response.data)
        self.assertIn("created_by", response.data)
        self.assertIn("status", response.data)
        self.assertIn("channel", response.data)
        self.assertIn("notification_type", response.data)
        self.assertIn("title", response.data)
        self.assertIn("message", response.data)
        self.assertIn("priority", response.data)
        self.assertIn("source_module", response.data)
        self.assertIn("source_event", response.data)
        self.assertIn("source_object_id", response.data)
        self.assertIn("scheduled_for", response.data)
        self.assertIn("lifecycle", response.data)
        self.assertIn("events", response.data)
        self.assertIn("deliveries", response.data)