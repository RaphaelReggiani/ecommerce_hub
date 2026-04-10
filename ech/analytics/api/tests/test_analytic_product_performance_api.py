from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.analytics.exceptions import AnalyticsProductUnavailableException
from ech.analytics.services.analytic_product_performance_service import (
    AnalyticsProductPerformanceService,
)
from ech.users.models import CustomUser


class AnalyticsProductPerformanceApiTestCase(APITestCase):
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

        cls.url = reverse("analytics-api:analytics-product-performance")

        cls.valid_params = {
            "period_type": "daily",
            "period_start": "2024-01-01T00:00:00Z",
            "period_end": "2024-01-02T00:00:00Z",
        }

    def setUp(self):
        cache.clear()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_product_performance_requires_authentication(self):
        """Reject product performance access for unauthenticated users."""
        response = self.client.get(self.url, self.valid_params)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_product_performance_rejects_customer_user(self):
        """Reject product performance access for customer users."""
        self.authenticate(self.customer)

        response = self.client.get(self.url, self.valid_params)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(
        AnalyticsProductPerformanceService,
        "get_performance",
    )
    def test_product_performance_returns_data_for_analytics_staff(
        self,
        mocked_service,
    ):
        """Allow analytics staff to retrieve product performance."""
        mocked_service.return_value = {
            "source": "snapshot",
            "snapshot_id": None,
            "period_type": "daily",
            "period_start": "2024-01-01T00:00:00Z",
            "period_end": "2024-01-02T00:00:00Z",
            "products_sold": 12,
            "top_product_id": None,
        }

        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url, self.valid_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["source"], "snapshot")
        self.assertEqual(response.data["products_sold"], 12)
        self.assertIsNone(response.data["top_product_id"])

        mocked_service.assert_called_once()

    @patch.object(
        AnalyticsProductPerformanceService,
        "get_performance",
    )
    def test_product_performance_allows_admin(
        self,
        mocked_service,
    ):
        """Allow admin users to retrieve product performance."""
        mocked_service.return_value = {
            "source": "snapshot",
            "snapshot_id": None,
            "period_type": "daily",
            "period_start": "2024-01-01T00:00:00Z",
            "period_end": "2024-01-02T00:00:00Z",
            "products_sold": 0,
            "top_product_id": None,
        }

        self.authenticate(self.admin)

        response = self.client.get(self.url, self.valid_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_performance_requires_period_type(self):
        """Reject request when period_type is missing."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_product_performance_rejects_invalid_period_start(self):
        """Reject request when period_start has invalid datetime format."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(
            self.url,
            {
                "period_type": "daily",
                "period_start": "invalid-datetime",
                "period_end": "2024-01-02T00:00:00Z",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("period_start", response.data)

    def test_product_performance_rejects_invalid_period_end(self):
        """Reject request when period_end has invalid datetime format."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(
            self.url,
            {
                "period_type": "daily",
                "period_start": "2024-01-01T00:00:00Z",
                "period_end": "invalid-datetime",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("period_end", response.data)

    @patch.object(
        AnalyticsProductPerformanceService,
        "get_performance",
        side_effect=AnalyticsProductUnavailableException(),
    )
    def test_product_performance_returns_400_when_service_fails(
        self,
        mocked_service,
    ):
        """Return 400 when product performance service raises handled exception."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url, self.valid_params)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

        mocked_service.assert_called_once()