import uuid
from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.admin_dashboard.exceptions import (
    AdminDashboardBulkOrderActionException,
)
from ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service import (
    AdminDashboardBulkOrderActionsService,
)
from ech.users.models import CustomUser


class AdminDashboardBulkOrderActionsApiTestCase(APITestCase):
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

        cls.support_staff = CustomUser.objects.create_user(
            email="support@company.com",
            password="StrongPassword123",
            user_name="Support Staff",
            role=CustomUser.ROLE_SUPPORT_STAFF,
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

        cls.admin = CustomUser.objects.create_user(
            email="admin@company.com",
            password="StrongPassword123",
            user_name="Admin User",
            role=CustomUser.ROLE_ADMIN,
            is_active=True,
            email_confirmed=True,
        )

        cls.url = reverse(
            "admin-dashboard-api:admin-dashboard-bulk-order-action"
        )

        cls.order_id_1 = uuid.UUID("11111111-1111-1111-1111-111111111111")
        cls.order_id_2 = uuid.UUID("22222222-2222-2222-2222-222222222222")

        cls.valid_payload = {
            "action_type": "mark_processing",
            "order_ids": [
                str(cls.order_id_1),
                str(cls.order_id_2),
            ],
        }

    def setUp(self):
        cache.clear()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_bulk_order_action_requires_authentication(self):
        """Reject bulk order actions for unauthenticated users."""
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_bulk_order_action_rejects_customer_user(self):
        """Reject bulk order actions for customer users."""
        self.authenticate(self.customer)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bulk_order_action_rejects_support_staff(self):
        """Reject bulk order actions for support staff."""
        self.authenticate(self.support_staff)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(
        AdminDashboardBulkOrderActionsService,
        "execute_bulk_action",
    )
    def test_bulk_order_action_allows_operations_staff(
        self,
        mocked_service,
    ):
        """Allow operations staff to execute bulk order actions."""
        mocked_service.return_value = {
            "action": "mark_processing",
            "processed_orders": [
                self.order_id_1,
                self.order_id_2,
            ],
            "total_processed": 2,
        }

        self.authenticate(self.operations_staff)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("action", response.data)
        self.assertIn("processed_orders", response.data)
        self.assertIn("total_processed", response.data)

        mocked_service.assert_called_once_with(
            action_type="mark_processing",
            order_ids=[
                self.order_id_1,
                self.order_id_2,
            ],
            performed_by=self.operations_staff,
        )

    @patch.object(
        AdminDashboardBulkOrderActionsService,
        "execute_bulk_action",
    )
    def test_bulk_order_action_allows_admin(
        self,
        mocked_service,
    ):
        """Allow admin users to execute bulk order actions."""
        mocked_service.return_value = {
            "action": "mark_processing",
            "processed_orders": [
                self.order_id_1,
            ],
            "total_processed": 1,
        }

        self.authenticate(self.admin)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mocked_service.assert_called_once_with(
            action_type="mark_processing",
            order_ids=[
                self.order_id_1,
                self.order_id_2,
            ],
            performed_by=self.admin,
        )

    def test_bulk_order_action_rejects_invalid_action_type(self):
        """Reject payloads with invalid bulk order action."""
        self.authenticate(self.admin)

        payload = {
            "action_type": "invalid_action",
            "order_ids": self.valid_payload["order_ids"],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("action_type", response.data)

    def test_bulk_order_action_requires_order_ids(self):
        """Reject payloads without order IDs."""
        self.authenticate(self.admin)

        payload = {
            "action_type": "mark_processing",
            "order_ids": [],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("order_ids", response.data)

    def test_bulk_order_action_rejects_invalid_order_id(self):
        """Reject payloads with invalid order UUID."""
        self.authenticate(self.admin)

        payload = {
            "action_type": "mark_processing",
            "order_ids": ["invalid-uuid"],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("order_ids", response.data)

    @patch.object(
        AdminDashboardBulkOrderActionsService,
        "execute_bulk_action",
        side_effect=AdminDashboardBulkOrderActionException(),
    )
    def test_bulk_order_action_returns_400_when_service_fails(
        self,
        mocked_service,
    ):
        """Return 400 when bulk order action service raises handled exception."""
        self.authenticate(self.admin)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

        mocked_service.assert_called_once_with(
            action_type="mark_processing",
            order_ids=[
                self.order_id_1,
                self.order_id_2,
            ],
            performed_by=self.admin,
        )