from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.admin_dashboard.exceptions import (
    AdminDashboardRecentActivityUnavailableException,
)
from ech.admin_dashboard.services.admin_dashboard_recent_activity_service import (
    AdminDashboardRecentActivityService,
)
from ech.users.models import CustomUser


class AdminDashboardRecentActivityApiTestCase(APITestCase):
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

        cls.analytics_staff = CustomUser.objects.create_user(
            email="analytics@company.com",
            password="StrongPassword123",
            user_name="Analytics Staff",
            role=CustomUser.ROLE_ANALYTICS_STAFF,
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

        cls.url = reverse("admin-dashboard-api:admin-dashboard-activity")

    def setUp(self):
        cache.clear()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_recent_activity_requires_authentication(self):
        """Reject recent activity access for unauthenticated users."""
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_recent_activity_rejects_customer_user(self):
        """Reject recent activity access for customer users."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(
        AdminDashboardRecentActivityService,
        "get_recent_activity",
    )
    def test_recent_activity_allows_analytics_staff(
        self,
        mocked_service,
    ):
        """Allow analytics staff to retrieve recent activity."""
        mocked_service.return_value = {
            "activities": [
                {
                    "source": "orders",
                    "type": "order",
                    "entity_id": "11111111-1111-1111-1111-111111111111",
                    "status": "pending",
                    "created_at": "2026-04-01T10:00:00Z",
                },
                {
                    "source": "admin_dashboard",
                    "type": "admin_action",
                    "entity_id": "22222222-2222-2222-2222-222222222222",
                    "action_type": "bulk_review_moderation",
                    "target_module": "reviews",
                    "created_at": "2026-04-01T09:00:00Z",
                },
            ],
            "total": 2,
            "limit": 50,
        }

        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("activities", response.data)
        self.assertIn("total", response.data)
        self.assertIn("limit", response.data)
        self.assertEqual(len(response.data["activities"]), 2)

        mocked_service.assert_called_once_with(
            limit=None,
            performed_by=self.analytics_staff,
        )

    @patch.object(
        AdminDashboardRecentActivityService,
        "get_recent_activity",
    )
    def test_recent_activity_allows_operations_staff(
        self,
        mocked_service,
    ):
        """Allow operations staff to retrieve recent activity."""
        mocked_service.return_value = {
            "activities": [],
            "total": 0,
            "limit": 50,
        }

        self.authenticate(self.operations_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mocked_service.assert_called_once_with(
            limit=None,
            performed_by=self.operations_staff,
        )

    @patch.object(
        AdminDashboardRecentActivityService,
        "get_recent_activity",
    )
    def test_recent_activity_allows_admin(
        self,
        mocked_service,
    ):
        """Allow admin users to retrieve recent activity."""
        mocked_service.return_value = {
            "activities": [],
            "total": 0,
            "limit": 50,
        }

        self.authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mocked_service.assert_called_once_with(
            limit=None,
            performed_by=self.admin,
        )

    @patch.object(
        AdminDashboardRecentActivityService,
        "get_recent_activity",
    )
    def test_recent_activity_accepts_limit_query_param(
        self,
        mocked_service,
    ):
        """Pass limit query param to service when provided."""
        mocked_service.return_value = {
            "activities": [],
            "total": 0,
            "limit": 10,
        }

        self.authenticate(self.admin)

        response = self.client.get(self.url, {"limit": 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mocked_service.assert_called_once_with(
            limit=10,
            performed_by=self.admin,
        )

    def test_recent_activity_rejects_invalid_limit(self):
        """Return 400 when limit is not a valid integer."""
        self.authenticate(self.admin)

        response = self.client.get(self.url, {"limit": "invalid"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("limit", response.data)

    def test_recent_activity_rejects_non_positive_limit(self):
        """Return 400 when limit is zero or negative."""
        self.authenticate(self.admin)

        response = self.client.get(self.url, {"limit": 0})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("limit", response.data)

    @patch.object(
        AdminDashboardRecentActivityService,
        "get_recent_activity",
        side_effect=AdminDashboardRecentActivityUnavailableException(),
    )
    def test_recent_activity_returns_400_when_service_fails(
        self,
        mocked_service,
    ):
        """Return 400 when recent activity service raises handled exception."""
        self.authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

        mocked_service.assert_called_once_with(
            limit=None,
            performed_by=self.admin,
        )