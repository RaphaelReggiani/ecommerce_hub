from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.admin_dashboard.exceptions import (
    AdminDashboardSummaryUnavailableException,
)
from ech.admin_dashboard.services.admin_dashboard_summary_service import (
    AdminDashboardSummaryService,
)
from ech.users.models import CustomUser


class AdminDashboardSummaryApiTestCase(APITestCase):
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

        cls.url = reverse("admin-dashboard-api:admin-dashboard-summary")

    def setUp(self):
        cache.clear()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_summary_requires_authentication(self):
        """Reject summary access for unauthenticated users."""
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_summary_rejects_customer_user(self):
        """Reject summary access for customer users."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(
        AdminDashboardSummaryService,
        "get_summary",
    )
    def test_summary_allows_analytics_staff(
        self,
        mocked_service,
    ):
        """Allow analytics staff to retrieve admin dashboard summary."""
        mocked_service.return_value = {
            "orders": {
                "total_orders": 10,
                "pending_orders": 2,
                "processing_orders": 1,
                "shipped_orders": 3,
                "delivered_orders": 3,
                "cancelled_orders": 1,
            },
            "payments": {
                "total_payments": 8,
                "captured_payments": 6,
                "failed_payments": 1,
                "refunded_payments": 1,
                "partially_refunded_payments": 0,
            },
            "shipping": {
                "total_shipments": 7,
                "pending_shipments": 1,
                "in_transit_shipments": 2,
                "delivered_shipments": 3,
                "failed_shipments": 1,
                "returned_shipments": 0,
            },
            "users": {
                "total_users": 20,
                "active_users": 15,
                "inactive_users": 5,
                "staff_users": 3,
                "customer_users": 17,
                "confirmed_users": 18,
                "unconfirmed_users": 2,
            },
            "reviews": {
                "total_reviews": 8,
                "pending_reviews": 1,
                "approved_reviews": 5,
                "rejected_reviews": 1,
                "hidden_reviews": 1,
                "cancelled_reviews": 0,
            },
            "products": {
                "total_products": 12,
                "active_products": 10,
                "inactive_products": 2,
            },
        }

        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("orders", response.data)
        self.assertIn("payments", response.data)
        self.assertIn("shipping", response.data)
        self.assertIn("users", response.data)
        self.assertIn("reviews", response.data)
        self.assertIn("products", response.data)

        mocked_service.assert_called_once_with(
            performed_by=self.analytics_staff,
        )

    @patch.object(
        AdminDashboardSummaryService,
        "get_summary",
    )
    def test_summary_allows_operations_staff(
        self,
        mocked_service,
    ):
        """Allow operations staff to retrieve admin dashboard summary."""
        mocked_service.return_value = {
            "orders": {
                "total_orders": 0,
                "pending_orders": 0,
                "processing_orders": 0,
                "shipped_orders": 0,
                "delivered_orders": 0,
                "cancelled_orders": 0,
            },
            "payments": {
                "total_payments": 0,
                "captured_payments": 0,
                "failed_payments": 0,
                "refunded_payments": 0,
                "partially_refunded_payments": 0,
            },
            "shipping": {
                "total_shipments": 0,
                "pending_shipments": 0,
                "in_transit_shipments": 0,
                "delivered_shipments": 0,
                "failed_shipments": 0,
                "returned_shipments": 0,
            },
            "users": {
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "staff_users": 0,
                "customer_users": 0,
                "confirmed_users": 0,
                "unconfirmed_users": 0,
            },
            "reviews": {
                "total_reviews": 0,
                "pending_reviews": 0,
                "approved_reviews": 0,
                "rejected_reviews": 0,
                "hidden_reviews": 0,
                "cancelled_reviews": 0,
            },
            "products": {
                "total_products": 0,
                "active_products": 0,
                "inactive_products": 0,
            },
        }

        self.authenticate(self.operations_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mocked_service.assert_called_once_with(
            performed_by=self.operations_staff,
        )

    @patch.object(
        AdminDashboardSummaryService,
        "get_summary",
    )
    def test_summary_allows_admin(
        self,
        mocked_service,
    ):
        """Allow admin users to retrieve admin dashboard summary."""
        mocked_service.return_value = {
            "orders": {
                "total_orders": 0,
                "pending_orders": 0,
                "processing_orders": 0,
                "shipped_orders": 0,
                "delivered_orders": 0,
                "cancelled_orders": 0,
            },
            "payments": {
                "total_payments": 0,
                "captured_payments": 0,
                "failed_payments": 0,
                "refunded_payments": 0,
                "partially_refunded_payments": 0,
            },
            "shipping": {
                "total_shipments": 0,
                "pending_shipments": 0,
                "in_transit_shipments": 0,
                "delivered_shipments": 0,
                "failed_shipments": 0,
                "returned_shipments": 0,
            },
            "users": {
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "staff_users": 0,
                "customer_users": 0,
                "confirmed_users": 0,
                "unconfirmed_users": 0,
            },
            "reviews": {
                "total_reviews": 0,
                "pending_reviews": 0,
                "approved_reviews": 0,
                "rejected_reviews": 0,
                "hidden_reviews": 0,
                "cancelled_reviews": 0,
            },
            "products": {
                "total_products": 0,
                "active_products": 0,
                "inactive_products": 0,
            },
        }

        self.authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mocked_service.assert_called_once_with(
            performed_by=self.admin,
        )

    @patch.object(
        AdminDashboardSummaryService,
        "get_summary",
        side_effect=AdminDashboardSummaryUnavailableException(),
    )
    def test_summary_returns_400_when_service_fails(
        self,
        mocked_service,
    ):
        """Return 400 when summary service raises handled exception."""
        self.authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

        mocked_service.assert_called_once_with(
            performed_by=self.admin,
        )