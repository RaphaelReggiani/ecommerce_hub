from datetime import timedelta
import uuid

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import CustomUser
from ech.notifications.models import Notification


class NotificationListApiTestCase(APITestCase):

    def setUp(self):
        cache.clear()

        self.url = reverse("notifications-api:notification-list")

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

        self.notification_1 = self._create_notification(
            recipient=self.customer,
            status="unread",
            channel="in_app",
            notification_type="order_update",
            title="Order Update",
        )

        self.notification_2 = self._create_notification(
            recipient=self.customer,
            status="read",
            channel="email",
            notification_type="payment_update",
            title="Payment Update",
        )

        self._create_notification(
            recipient=self.other_customer,
            status="unread",
            channel="in_app",
            notification_type="review_update",
            title="Review Update",
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
        title,
    ):
        return Notification.objects.create(
            recipient=recipient,
            status=status,
            channel=channel,
            notification_type=notification_type,
            title=title,
            message="Test message",
            priority="normal",
            source_module="orders",
            source_event="event",
            source_object_id=str(uuid.uuid4()),
            scheduled_for=timezone.now() + timedelta(hours=1),
            idempotency_key=uuid.uuid4(),
        )

    def test_list_notifications_returns_unauthorized_for_unauthenticated_user(self):
        """Reject notification listing for unauthenticated users."""

        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_list_notifications_returns_only_authenticated_user_notifications(self):
        """Return only notifications belonging to the authenticated user."""

        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

        returned_ids = {item["id"] for item in response.data["results"]}

        self.assertIn(str(self.notification_1.id), returned_ids)
        self.assertIn(str(self.notification_2.id), returned_ids)

    def test_list_notifications_excludes_notifications_from_other_users(self):
        """Exclude notifications belonging to other users."""

        self.authenticate(self.customer)

        response = self.client.get(self.url)

        returned_recipient_ids = {
            item["recipient"] for item in response.data["results"]
        }

        self.assertEqual(returned_recipient_ids, {self.customer.id})

    def test_list_notifications_returns_empty_result_for_staff_without_notifications(self):
        """Return an empty notification list for staff users without notifications."""

        self.authenticate(self.support_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])

    def test_list_notifications_supports_status_filter(self):
        """Filter notifications by status."""

        self.authenticate(self.customer)

        response = self.client.get(self.url, {"status": "read"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.notification_2.id),
        )

    def test_list_notifications_supports_channel_filter(self):
        """Filter notifications by channel."""

        self.authenticate(self.customer)

        response = self.client.get(self.url, {"channel": "email"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["channel"],
            "email",
        )

    def test_list_notifications_supports_notification_type_filter(self):
        """Filter notifications by notification type."""

        self.authenticate(self.customer)

        response = self.client.get(self.url, {"notification_type": "payment"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_list_notifications_supports_pagination(self):
        """Paginate notification list results."""

        self.authenticate(self.customer)

        response = self.client.get(self.url, {"page_size": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 1)

        self.assertIn("count", response.data)
        self.assertIn("results", response.data)