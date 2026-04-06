import uuid
from datetime import timedelta

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import CustomUser
from ech.notifications.models import Notification


class NotificationManagementListApiTestCase(APITestCase):

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

        self.url = reverse("notifications-api:notification-management-list")

        self.notification_1 = self._create_notification(
            recipient=self.customer,
            status="unread",
            channel="in_app",
            notification_type="order_update",
        )

        self.notification_2 = self._create_notification(
            recipient=self.customer,
            status="read",
            channel="email",
            notification_type="payment_update",
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def _create_notification(
        self,
        *,
        recipient,
        status,
        channel,
        notification_type,
    ):
        return Notification.objects.create(
            recipient=recipient,
            status=status,
            channel=channel,
            notification_type=notification_type,
            title="Test Notification",
            message="Test message",
            priority="normal",
            source_module="orders",
            source_event="event",
            source_object_id=str(uuid.uuid4()),
            scheduled_for=timezone.now() + timedelta(hours=1),
            idempotency_key=uuid.uuid4(),
        )

    def test_management_list_requires_authentication(self):
        """Reject management list for unauthenticated users."""

        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_management_list_rejects_customer_user(self):
        """Reject management list access for customer users."""

        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_management_list_returns_all_notifications_for_staff(self):
        """Allow staff users to list all notifications."""

        self.authenticate(self.staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_management_list_returns_all_notifications_for_admin(self):
        """Allow admin users to list all notifications."""

        self.authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_management_list_supports_status_filter(self):
        """Filter notifications by status."""

        self.authenticate(self.staff)

        response = self.client.get(self.url, {"status": "unread"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_management_list_supports_channel_filter(self):
        """Filter notifications by channel."""

        self.authenticate(self.staff)

        response = self.client.get(self.url, {"channel": "email"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_management_list_supports_notification_type_filter(self):
        """Filter notifications by notification type."""

        self.authenticate(self.staff)

        response = self.client.get(self.url, {"notification_type": "payment"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_management_list_supports_pagination(self):
        """Verify management list pagination."""

        self.authenticate(self.staff)

        response = self.client.get(self.url, {"page_size": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)