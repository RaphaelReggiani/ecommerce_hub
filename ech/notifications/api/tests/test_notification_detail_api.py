import uuid
from datetime import timedelta

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import CustomUser
from ech.notifications.models import Notification


class NotificationDetailApiTestCase(APITestCase):

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

        self.admin = CustomUser.objects.create_user(
            email="admin@company.com",
            password="StrongPassword123",
            user_name="Admin User",
            role=CustomUser.ROLE_ADMIN,
            is_active=True,
            email_confirmed=True,
        )

        self.notification = self._create_notification(
            recipient=self.customer
        )

        self.url = reverse(
            "notifications-api:notification-detail",
            kwargs={"notification_id": self.notification.id},
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def _create_notification(self, *, recipient):
        return Notification.objects.create(
            recipient=recipient,
            status="unread",
            channel="in_app",
            notification_type="order_update",
            title="Order Update",
            message="Test notification message",
            priority="normal",
            source_module="orders",
            source_event="order_created",
            source_object_id=str(uuid.uuid4()),
            scheduled_for=timezone.now() + timedelta(hours=1),
            idempotency_key=uuid.uuid4(),
        )

    def test_notification_detail_returns_unauthorized_for_unauthenticated_user(self):
        """Reject notification detail access for unauthenticated users."""

        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_notification_detail_returns_notification_for_owner(self):
        """Allow notification owner to retrieve notification detail."""

        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.notification.id))
        self.assertEqual(response.data["recipient"], self.customer.id)

    def test_notification_detail_rejects_other_customer(self):
        """Reject access when another customer tries to access the notification."""

        self.authenticate(self.other_customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_notification_detail_allows_staff_access(self):
        """Allow staff users to access notification detail."""

        self.authenticate(self.support_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.notification.id))

    def test_notification_detail_allows_admin_access(self):
        """Allow admin users to access notification detail."""

        self.authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notification_detail_returns_404_for_nonexistent_notification(self):
        """Return 404 when notification does not exist."""

        self.authenticate(self.customer)

        url = reverse(
            "notifications-api:notification-detail",
            kwargs={"notification_id": uuid.uuid4()},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_notification_detail_response_contains_expected_fields(self):
        """Ensure response contains expected notification fields."""

        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("id", response.data)
        self.assertIn("recipient", response.data)
        self.assertIn("status", response.data)
        self.assertIn("channel", response.data)
        self.assertIn("notification_type", response.data)
        self.assertIn("title", response.data)
        self.assertIn("message", response.data)
        self.assertIn("priority", response.data)