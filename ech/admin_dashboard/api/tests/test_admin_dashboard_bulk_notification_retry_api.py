import uuid
from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.admin_dashboard.exceptions import (
    AdminDashboardNotificationRetryException,
)
from ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service import (
    AdminDashboardBulkNotificationRetryService,
)
from ech.users.models import CustomUser


class AdminDashboardBulkNotificationRetryApiTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        cls.operations_staff = CustomUser.objects.create_user(
            email="operations@company.com",
            password="StrongPassword123",
            user_name="Operations Staff",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        cls.support_staff = CustomUser.objects.create_user(
            email="support@company.com",
            password="StrongPassword123",
            user_name="Support Staff",
            role=CustomUser.ROLE_SUPPORT_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        cls.admin = CustomUser.objects.create_user(
            email="admin@company.com",
            password="StrongPassword123",
            user_name="Admin User",
            role=CustomUser.ROLE_ADMIN,
            is_active=True,
            email_confirmed=True,
        )

        cls.url = reverse(
            "admin-dashboard-api:admin-dashboard-notification-retry"
        )

        cls.notification_id_1 = uuid.UUID(
            "11111111-1111-1111-1111-111111111111"
        )
        cls.notification_id_2 = uuid.UUID(
            "22222222-2222-2222-2222-222222222222"
        )

        cls.valid_payload = {
            "notification_ids": [
                str(cls.notification_id_1),
                str(cls.notification_id_2),
            ],
        }

    def setUp(self):
        cache.clear()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_bulk_notification_retry_requires_authentication(self):
        """Reject bulk notification retry for unauthenticated users."""
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_bulk_notification_retry_rejects_customer_user(self):
        """Reject bulk notification retry for customer users."""
        self.authenticate(self.customer)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bulk_notification_retry_rejects_operations_staff(self):
        """Reject bulk notification retry for operations staff."""
        self.authenticate(self.operations_staff)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(
        AdminDashboardBulkNotificationRetryService,
        "retry_notifications",
    )
    def test_bulk_notification_retry_allows_support_staff(
        self,
        mocked_service,
    ):
        """Allow support staff to retry failed notifications."""
        mocked_service.return_value = {
            "retried_notifications": [
                self.notification_id_1,
                self.notification_id_2,
            ],
            "total_retried": 2,
        }

        self.authenticate(self.support_staff)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("retried_notifications", response.data)
        self.assertIn("total_retried", response.data)

        mocked_service.assert_called_once_with(
            notification_ids=[
                self.notification_id_1,
                self.notification_id_2,
            ],
            performed_by=self.support_staff,
        )

    @patch.object(
        AdminDashboardBulkNotificationRetryService,
        "retry_notifications",
    )
    def test_bulk_notification_retry_allows_admin(
        self,
        mocked_service,
    ):
        """Allow admin users to retry failed notifications."""
        mocked_service.return_value = {
            "retried_notifications": [
                self.notification_id_1,
            ],
            "total_retried": 1,
        }

        self.authenticate(self.admin)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mocked_service.assert_called_once_with(
            notification_ids=[
                self.notification_id_1,
                self.notification_id_2,
            ],
            performed_by=self.admin,
        )

    def test_bulk_notification_retry_requires_notification_ids(self):
        """Reject payloads without notification IDs."""
        self.authenticate(self.admin)

        payload = {
            "notification_ids": [],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("notification_ids", response.data)

    def test_bulk_notification_retry_rejects_invalid_notification_id(self):
        """Reject payloads with invalid notification UUID."""
        self.authenticate(self.admin)

        payload = {
            "notification_ids": ["invalid-uuid"],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("notification_ids", response.data)

    @patch.object(
        AdminDashboardBulkNotificationRetryService,
        "retry_notifications",
        side_effect=AdminDashboardNotificationRetryException(),
    )
    def test_bulk_notification_retry_returns_400_when_service_fails(
        self,
        mocked_service,
    ):
        """Return 400 when bulk notification retry service raises handled exception."""
        self.authenticate(self.admin)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

        mocked_service.assert_called_once_with(
            notification_ids=[
                self.notification_id_1,
                self.notification_id_2,
            ],
            performed_by=self.admin,
        )