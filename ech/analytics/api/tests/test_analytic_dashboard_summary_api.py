from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.analytics.exceptions import AnalyticsDashboardUnavailableException
from ech.analytics.services.analytic_dashboard_summary_service import (
    AnalyticsDashboardSummaryService,
)
from ech.users.models import CustomUser


class AnalyticsDashboardSummaryApiTestCase(APITestCase):
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

        cls.admin = CustomUser.objects.create_user(
            email="admin@company.com",
            password="StrongPassword123",
            user_name="Admin User",
            role=CustomUser.ROLE_ADMIN,
            is_active=True,
            email_confirmed=True,
        )

        cls.url = reverse("analytics-api:analytics-dashboard")

        cls.valid_params = {
            "period_type": "daily",
            "period_start": "2024-01-01T00:00:00Z",
            "period_end": "2024-01-02T00:00:00Z",
        }

    def setUp(self):
        cache.clear()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_dashboard_requires_authentication(self):
        """Reject dashboard access for unauthenticated users."""
        response = self.client.get(self.url, self.valid_params)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_dashboard_rejects_customer_user(self):
        """Reject dashboard access for customer users."""
        self.authenticate(self.customer)

        response = self.client.get(self.url, self.valid_params)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(
        AnalyticsDashboardSummaryService,
        "get_summary",
    )
    def test_dashboard_returns_summary_for_analytics_staff(
        self,
        mocked_service,
    ):
        """Allow analytics staff to retrieve dashboard summary."""
        mocked_service.return_value = {
            "source": "snapshot",
            "snapshot_id": None,
            "period_type": "daily",
            "period_start": "2024-01-01T00:00:00Z",
            "period_end": "2024-01-02T00:00:00Z",
            "orders": {
                "total_orders": 10,
                "orders_pending": 2,
                "orders_processing": 1,
                "orders_shipped": 3,
                "orders_delivered": 3,
                "orders_cancelled": 1,
            },
            "revenue": {
                "total_revenue": "1000.00",
                "total_refunds": "50.00",
                "net_revenue": "950.00",
            },
            "payments": {
                "payments_captured": 7,
                "payments_failed": 1,
                "payments_refunded": 1,
            },
            "shipping": {
                "shipments_in_transit": 2,
                "shipments_delivered": 3,
                "shipments_failed": 1,
            },
            "products": {
                "products_sold": 12,
                "top_product_id": None,
            },
            "customers": {
                "active_customers": 5,
                "new_customers": 2,
            },
            "users": {
                "total_registered_users": 20,
                "active_users": 15,
                "inactive_users": 5,
                "confirmed_users": 18,
                "unconfirmed_users": 2,
                "staff_users": 3,
                "customer_users": 17,
            },
            "reviews": {
                "total_reviews": 8,
                "approved_reviews": 6,
                "rejected_reviews": 1,
                "hidden_reviews": 1,
                "cancelled_reviews": 0,
                "verified_purchase_reviews": 5,
                "average_rating": "4.50",
                "low_rated_products_count": 0,
                "high_rated_products_count": 2,
            },
        }

        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url, self.valid_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("orders", response.data)
        self.assertIn("revenue", response.data)
        self.assertIn("payments", response.data)
        self.assertIn("shipping", response.data)
        self.assertIn("products", response.data)
        self.assertIn("customers", response.data)
        self.assertIn("users", response.data)
        self.assertIn("reviews", response.data)

        mocked_service.assert_called_once()

    @patch.object(
        AnalyticsDashboardSummaryService,
        "get_summary",
    )
    def test_dashboard_allows_admin(
        self,
        mocked_service,
    ):
        """Allow admin users to retrieve dashboard."""
        mocked_service.return_value = {
            "source": "snapshot",
            "snapshot_id": None,
            "period_type": "daily",
            "period_start": "2024-01-01T00:00:00Z",
            "period_end": "2024-01-02T00:00:00Z",
            "orders": {
                "total_orders": 0,
                "orders_pending": 0,
                "orders_processing": 0,
                "orders_shipped": 0,
                "orders_delivered": 0,
                "orders_cancelled": 0,
            },
            "revenue": {
                "total_revenue": "0.00",
                "total_refunds": "0.00",
                "net_revenue": "0.00",
            },
            "payments": {
                "payments_captured": 0,
                "payments_failed": 0,
                "payments_refunded": 0,
            },
            "shipping": {
                "shipments_in_transit": 0,
                "shipments_delivered": 0,
                "shipments_failed": 0,
            },
            "products": {
                "products_sold": 0,
                "top_product_id": None,
            },
            "customers": {
                "active_customers": 0,
                "new_customers": 0,
            },
            "users": {
                "total_registered_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "confirmed_users": 0,
                "unconfirmed_users": 0,
                "staff_users": 0,
                "customer_users": 0,
            },
            "reviews": {
                "total_reviews": 0,
                "approved_reviews": 0,
                "rejected_reviews": 0,
                "hidden_reviews": 0,
                "cancelled_reviews": 0,
                "verified_purchase_reviews": 0,
                "average_rating": "0.00",
                "low_rated_products_count": 0,
                "high_rated_products_count": 0,
            },
        }

        self.authenticate(self.admin)

        response = self.client.get(self.url, self.valid_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dashboard_requires_period_type(self):
        """Reject request when period_type is missing."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch.object(
        AnalyticsDashboardSummaryService,
        "get_summary",
        side_effect=AnalyticsDashboardUnavailableException(),
    )
    def test_dashboard_returns_400_when_service_fails(
        self,
        mocked_service,
    ):
        """Return 400 when dashboard service raises handled exception."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url, self.valid_params)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

        mocked_service.assert_called_once()