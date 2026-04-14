from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.admin_dashboard.exceptions import (
    AdminDashboardOperationalMetricsUnavailableException,
)
from ech.admin_dashboard.services.admin_dashboard_operational_metrics_service import (
    AdminDashboardOperationalMetricsService,
)
from ech.users.models import CustomUser


class AdminDashboardOperationalMetricsApiTestCase(APITestCase):

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

        cls.url = reverse(
            "admin-dashboard-api:admin-dashboard-operational-metrics"
        )

    def setUp(self):
        cache.clear()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_operational_metrics_requires_authentication(self):
        """Reject access for unauthenticated users."""
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_operational_metrics_rejects_customer_user(self):
        """Reject access for customer users."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(
        AdminDashboardOperationalMetricsService,
        "get_operational_metrics",
    )
    def test_operational_metrics_allows_analytics_staff(
        self,
        mocked_service,
    ):
        """Allow analytics staff to retrieve operational metrics."""

        mocked_service.return_value = {
            "orders": {
                "pending_orders": 5,
                "processing_orders": 2,
                "cancelled_orders": 1,
            },
            "payments": {
                "failed_payments": 2,
                "processing_payments": 1,
                "refunded_payments": 1,
            },
            "shipping": {
                "delayed_shipments": 1,
                "failed_shipments": 0,
                "in_transit_shipments": 3,
            },
            "reviews": {
                "pending_moderation": 2,
                "flagged_reviews": 1,
                "hidden_reviews": 0,
            },
            "notifications": {
                "failed_notifications": 1,
                "pending_notifications": 2,
                "unread_notifications": 3,
            },
            "products": {
                "low_stock_products": 4,
                "out_of_stock_products": 1,
                "products_without_images": 2,
            },
        }

        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("orders", response.data)
        self.assertIn("payments", response.data)
        self.assertIn("shipping", response.data)
        self.assertIn("reviews", response.data)
        self.assertIn("notifications", response.data)
        self.assertIn("products", response.data)

        mocked_service.assert_called_once_with(
            performed_by=self.analytics_staff
        )

    @patch.object(
        AdminDashboardOperationalMetricsService,
        "get_operational_metrics",
    )
    def test_operational_metrics_allows_operations_staff(
        self,
        mocked_service,
    ):
        """Allow operations staff to retrieve operational metrics."""

        mocked_service.return_value = {
            "orders": {
                "pending_orders": 0,
                "processing_orders": 0,
                "cancelled_orders": 0,
            },
            "payments": {
                "failed_payments": 0,
                "processing_payments": 0,
                "refunded_payments": 0,
            },
            "shipping": {
                "delayed_shipments": 0,
                "failed_shipments": 0,
                "in_transit_shipments": 0,
            },
            "reviews": {
                "pending_moderation": 0,
                "flagged_reviews": 0,
                "hidden_reviews": 0,
            },
            "notifications": {
                "failed_notifications": 0,
                "pending_notifications": 0,
                "unread_notifications": 0,
            },
            "products": {
                "low_stock_products": 0,
                "out_of_stock_products": 0,
                "products_without_images": 0,
            },
        }

        self.authenticate(self.operations_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mocked_service.assert_called_once_with(
            performed_by=self.operations_staff
        )

    @patch.object(
        AdminDashboardOperationalMetricsService,
        "get_operational_metrics",
    )
    def test_operational_metrics_allows_admin(
        self,
        mocked_service,
    ):
        """Allow admin users to retrieve operational metrics."""

        mocked_service.return_value = {
            "orders": {
                "pending_orders": 0,
                "processing_orders": 0,
                "cancelled_orders": 0,
            },
            "payments": {
                "failed_payments": 0,
                "processing_payments": 0,
                "refunded_payments": 0,
            },
            "shipping": {
                "delayed_shipments": 0,
                "failed_shipments": 0,
                "in_transit_shipments": 0,
            },
            "reviews": {
                "pending_moderation": 0,
                "flagged_reviews": 0,
                "hidden_reviews": 0,
            },
            "notifications": {
                "failed_notifications": 0,
                "pending_notifications": 0,
                "unread_notifications": 0,
            },
            "products": {
                "low_stock_products": 0,
                "out_of_stock_products": 0,
                "products_without_images": 0,
            },
        }

        self.authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mocked_service.assert_called_once_with(
            performed_by=self.admin
        )

    @patch.object(
        AdminDashboardOperationalMetricsService,
        "get_operational_metrics",
        side_effect=AdminDashboardOperationalMetricsUnavailableException(),
    )
    def test_operational_metrics_returns_400_when_service_fails(
        self,
        mocked_service,
    ):
        """Return 400 when service raises handled exception."""

        self.authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("detail", response.data)

        mocked_service.assert_called_once_with(
            performed_by=self.admin
        )