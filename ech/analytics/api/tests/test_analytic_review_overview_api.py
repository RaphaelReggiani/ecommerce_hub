from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.analytics.exceptions import AnalyticsReviewUnavailableException
from ech.analytics.services.analytic_review_overview_service import (
    AnalyticsReviewOverviewService,
)
from ech.users.models import CustomUser


class AnalyticsReviewOverviewApiTestCase(APITestCase):
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

        cls.url = reverse("analytics-api:analytics-review-overview")

        cls.valid_params = {
            "period_type": "daily",
            "period_start": "2024-01-01T00:00:00Z",
            "period_end": "2024-01-02T00:00:00Z",
        }

    def setUp(self):
        cache.clear()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_review_overview_requires_authentication(self):
        """Reject review overview access for unauthenticated users."""
        response = self.client.get(self.url, self.valid_params)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_review_overview_rejects_customer_user(self):
        """Reject review overview access for customer users."""
        self.authenticate(self.customer)

        response = self.client.get(self.url, self.valid_params)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(
        AnalyticsReviewOverviewService,
        "get_overview",
    )
    def test_review_overview_returns_data_for_analytics_staff(
        self,
        mocked_service,
    ):
        """Allow analytics staff to retrieve review overview."""
        mocked_service.return_value = {
            "source": "snapshot",
            "snapshot_id": None,
            "period_type": "daily",
            "period_start": "2024-01-01T00:00:00Z",
            "period_end": "2024-01-02T00:00:00Z",
            "total_reviews": 8,
            "approved_reviews": 6,
            "rejected_reviews": 1,
            "hidden_reviews": 0,
            "cancelled_reviews": 1,
            "verified_purchase_reviews": 5,
            "average_rating": "4.50",
            "low_rated_products_count": 1,
            "high_rated_products_count": 3,
        }

        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url, self.valid_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["source"], "snapshot")
        self.assertEqual(response.data["total_reviews"], 8)
        self.assertEqual(response.data["approved_reviews"], 6)
        self.assertEqual(response.data["rejected_reviews"], 1)
        self.assertEqual(response.data["hidden_reviews"], 0)
        self.assertEqual(response.data["cancelled_reviews"], 1)
        self.assertEqual(response.data["verified_purchase_reviews"], 5)
        self.assertEqual(response.data["average_rating"], "4.50")
        self.assertEqual(response.data["low_rated_products_count"], 1)
        self.assertEqual(response.data["high_rated_products_count"], 3)

        mocked_service.assert_called_once()

    @patch.object(
        AnalyticsReviewOverviewService,
        "get_overview",
    )
    def test_review_overview_allows_admin(
        self,
        mocked_service,
    ):
        """Allow admin users to retrieve review overview."""
        mocked_service.return_value = {
            "source": "snapshot",
            "snapshot_id": None,
            "period_type": "daily",
            "period_start": "2024-01-01T00:00:00Z",
            "period_end": "2024-01-02T00:00:00Z",
            "total_reviews": 0,
            "approved_reviews": 0,
            "rejected_reviews": 0,
            "hidden_reviews": 0,
            "cancelled_reviews": 0,
            "verified_purchase_reviews": 0,
            "average_rating": "0.00",
            "low_rated_products_count": 0,
            "high_rated_products_count": 0,
        }

        self.authenticate(self.admin)

        response = self.client.get(self.url, self.valid_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_review_overview_requires_period_type(self):
        """Reject request when period_type is missing."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_overview_rejects_invalid_period_start(self):
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

    def test_review_overview_rejects_invalid_period_end(self):
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
        AnalyticsReviewOverviewService,
        "get_overview",
        side_effect=AnalyticsReviewUnavailableException(),
    )
    def test_review_overview_returns_400_when_service_fails(
        self,
        mocked_service,
    ):
        """Return 400 when review overview service raises handled exception."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url, self.valid_params)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

        mocked_service.assert_called_once()