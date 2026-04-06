import uuid
from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import CustomUser
from ech.notifications.models import (
    Notification,
    NotificationLifecycle,
)


class NotificationDispatchApiTestCase(APITestCase):

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
            "notifications-api:notification-dispatch",
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
            title="Dispatch Test",
            message="Test message",
            priority=Notification.PRIORITY_NORMAL,
            source_module="orders",
            source_event="order_created",
            source_object_id=str(uuid.uuid4()),
            idempotency_key=uuid.uuid4(),
        )

        NotificationLifecycle.objects.create(notification=notification)

        return notification

    def test_dispatch_requires_authentication(self):
        """Reject dispatch when user is not authenticated."""

        response = self.client.post(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_dispatch_rejects_customer_user(self):
        """Reject dispatch for customer users."""

        self.authenticate(self.customer)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch(
        "ech.notifications.api.views.NotificationDeliveryService.dispatch_notification"
    )
    def test_dispatch_allows_staff(self, mock_dispatch):
        """Allow staff users to dispatch notifications."""

        self.authenticate(self.support_staff)

        mock_dispatch.return_value = self.notification

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_dispatch.assert_called_once()

    @patch(
        "ech.notifications.api.views.NotificationDeliveryService.dispatch_notification"
    )
    def test_dispatch_allows_admin(self, mock_dispatch):
        """Allow admin users to dispatch notifications."""

        self.authenticate(self.admin)

        mock_dispatch.return_value = self.notification

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_dispatch.assert_called_once()

    @patch(
        "ech.notifications.api.views.NotificationDeliveryService.dispatch_notification"
    )
    def test_dispatch_is_idempotent_when_notification_is_not_pending(
        self,
        mock_dispatch,
    ):
        """Do not dispatch again when notification is no longer pending."""

        self.notification.status = Notification.STATUS_UNREAD
        self.notification.save(update_fields=["status"])

        self.authenticate(self.support_staff)

        response = self.client.post(self.url)

        self.notification.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.notification.status, Notification.STATUS_UNREAD)
        mock_dispatch.assert_not_called()

    def test_dispatch_returns_404_for_nonexistent_notification(self):
        """Return 404 when notification does not exist."""

        self.authenticate(self.support_staff)

        url = reverse(
            "notifications-api:notification-dispatch",
            kwargs={"notification_id": uuid.uuid4()},
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)