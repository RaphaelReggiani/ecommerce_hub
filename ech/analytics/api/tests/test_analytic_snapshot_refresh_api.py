from datetime import timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from rest_framework import status
from rest_framework.test import APITestCase

from ech.analytics.models import (
    AnalyticsEvent,
    AnalyticsSnapshot,
    AnalyticsSnapshotLifecycle,
)
from ech.analytics.exceptions import AnalyticsSnapshotRefreshException
from ech.analytics.services.analytic_snapshot_refresh_service import (
    AnalyticsSnapshotRefreshService,
)
from ech.users.models import CustomUser


class AnalyticsSnapshotRefreshApiTestCase(APITestCase):
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

        now = timezone.now()

        cls.snapshot = AnalyticsSnapshot.objects.create(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=now - timedelta(days=2),
            period_end=now - timedelta(days=1),
            total_orders=10,
            orders_pending=2,
            orders_processing=1,
            orders_shipped=3,
            orders_delivered=3,
            orders_cancelled=1,
            total_revenue="1000.00",
            total_refunds="50.00",
            net_revenue="950.00",
            payments_captured=7,
            payments_failed=1,
            payments_refunded=1,
            shipments_in_transit=2,
            shipments_delivered=3,
            shipments_failed=1,
            products_sold=12,
            active_customers=5,
            new_customers=2,
            total_registered_users=20,
            active_users=15,
            inactive_users=5,
            confirmed_users=18,
            unconfirmed_users=2,
            staff_users=3,
            customer_users=17,
            total_reviews=8,
            approved_reviews=6,
            rejected_reviews=1,
            hidden_reviews=1,
            cancelled_reviews=0,
            verified_purchase_reviews=5,
            average_rating="4.50",
            low_rated_products_count=0,
            high_rated_products_count=2,
            generated_by=cls.analytics_staff,
            metadata={"source": "before-refresh"},
        )

        cls.lifecycle = AnalyticsSnapshotLifecycle.objects.create(
            snapshot=cls.snapshot,
            generation_started_at=now - timedelta(days=2, minutes=5),
            generation_completed_at=now - timedelta(days=2),
        )

        cls.url = reverse(
            "analytics-api:analytics-snapshot-refresh",
            kwargs={"snapshot_id": cls.snapshot.id},
        )

    def setUp(self):
        cache.clear()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_snapshot_refresh_requires_authentication(self):
        """Reject snapshot refresh for unauthenticated users."""
        response = self.client.post(self.url, {}, format="json")

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_snapshot_refresh_rejects_customer_user(self):
        """Reject snapshot refresh for customer users."""
        self.authenticate(self.customer)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_snapshot_refresh_allows_analytics_staff(self):
        """Allow analytics staff to refresh a snapshot."""
        self.authenticate(self.analytics_staff)

        payload = {
            "metadata": {
                "reason": "manual_refresh",
            }
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.snapshot.id))
        self.assertIn("lifecycle", response.data)

        refreshed_at = parse_datetime(response.data["lifecycle"]["refreshed_at"])
        self.assertIsNotNone(refreshed_at)

    def test_snapshot_refresh_allows_admin(self):
        """Allow admin users to refresh a snapshot."""
        self.authenticate(self.admin)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.snapshot.id))

    def test_snapshot_refresh_returns_404_for_nonexistent_snapshot(self):
        """Return 404 when snapshot does not exist."""
        self.authenticate(self.analytics_staff)

        url = reverse(
            "analytics-api:analytics-snapshot-refresh",
            kwargs={"snapshot_id": "11111111-1111-1111-1111-111111111111"},
        )

        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_snapshot_refresh_updates_lifecycle_refreshed_at(self):
        """Refresh operation should update lifecycle refreshed_at."""
        self.authenticate(self.analytics_staff)

        self.assertIsNone(self.lifecycle.refreshed_at)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lifecycle.refresh_from_db()
        self.assertIsNotNone(self.lifecycle.refreshed_at)

    def test_snapshot_refresh_creates_refresh_event(self):
        """Refresh operation should create a snapshot refreshed event."""
        self.authenticate(self.analytics_staff)

        initial_count = AnalyticsEvent.objects.filter(
            snapshot=self.snapshot,
            event_type=AnalyticsEvent.TYPE_SNAPSHOT_REFRESHED,
        ).count()

        response = self.client.post(
            self.url,
            {"metadata": {"source": "api-test"}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        final_count = AnalyticsEvent.objects.filter(
            snapshot=self.snapshot,
            event_type=AnalyticsEvent.TYPE_SNAPSHOT_REFRESHED,
        ).count()

        self.assertEqual(final_count, initial_count + 1)

    def test_snapshot_refresh_returns_updated_snapshot_detail_payload(self):
        """Refresh response should return full snapshot detail payload."""
        self.authenticate(self.analytics_staff)

        response = self.client.post(
            self.url,
            {"metadata": {"trigger": "detail-check"}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.snapshot.id))
        self.assertEqual(response.data["period_type"], self.snapshot.period_type)
        self.assertEqual(response.data["generated_by"], self.analytics_staff.id)
        self.assertIn("events", response.data)
        self.assertIn("lifecycle", response.data)
        self.assertIn("metadata", response.data)
        self.assertIn("total_orders", response.data)
        self.assertIn("total_revenue", response.data)
        self.assertIn("average_rating", response.data)

    @patch.object(
        AnalyticsSnapshotRefreshService,
        "refresh_snapshot",
        side_effect=AnalyticsSnapshotRefreshException(),
    )
    def test_snapshot_refresh_returns_400_when_refresh_service_fails(
        self,
        mocked_refresh,
    ):
        """Return 400 when refresh service raises a handled refresh exception."""
        self.authenticate(self.analytics_staff)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        mocked_refresh.assert_called_once()