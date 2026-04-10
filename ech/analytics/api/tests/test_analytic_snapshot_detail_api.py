from datetime import timedelta

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
from ech.users.models import CustomUser


class AnalyticsSnapshotDetailApiTestCase(APITestCase):
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
            metadata={"source": "test-detail"},
        )

        cls.lifecycle = AnalyticsSnapshotLifecycle.objects.create(
            snapshot=cls.snapshot,
            generation_started_at=now - timedelta(days=2, minutes=5),
            generation_completed_at=now - timedelta(days=2),
        )

        cls.event = AnalyticsEvent.objects.create(
            snapshot=cls.snapshot,
            event_type=AnalyticsEvent.TYPE_SNAPSHOT_CREATED,
            performed_by=cls.analytics_staff,
            metadata={"reason": "initial_generation"},
        )

        cls.url = reverse(
            "analytics-api:analytics-snapshot-detail",
            kwargs={"snapshot_id": cls.snapshot.id},
        )

    def setUp(self):
        cache.clear()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_snapshot_detail_requires_authentication(self):
        """Reject snapshot detail for unauthenticated users."""
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_snapshot_detail_rejects_customer_user(self):
        """Reject snapshot detail access for customer users."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_snapshot_detail_allows_analytics_staff(self):
        """Allow analytics staff to retrieve snapshot detail."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.snapshot.id))
        self.assertEqual(
            response.data["generated_by"],
            self.analytics_staff.id,
        )
        self.assertEqual(
            response.data["generated_by_name"],
            self.analytics_staff.user_name,
        )
        self.assertEqual(
            response.data["generated_by_email"],
            self.analytics_staff.user_email,
        )

    def test_snapshot_detail_allows_admin(self):
        """Allow admin users to retrieve snapshot detail."""
        self.authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.snapshot.id))

    def test_snapshot_detail_returns_nested_lifecycle_and_events(self):
        """Return lifecycle and events in snapshot detail response."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("lifecycle", response.data)
        self.assertIsInstance(response.data["lifecycle"], dict)

        response_generation_started_at = parse_datetime(
            response.data["lifecycle"]["generation_started_at"]
        )
        response_generation_completed_at = parse_datetime(
            response.data["lifecycle"]["generation_completed_at"]
        )

        self.assertEqual(
            response_generation_started_at,
            self.lifecycle.generation_started_at,
        )
        self.assertEqual(
            response_generation_completed_at,
            self.lifecycle.generation_completed_at,
        )

        self.assertIn("events", response.data)
        self.assertEqual(len(response.data["events"]), 1)
        self.assertEqual(
            response.data["events"][0]["id"],
            str(self.event.id),
        )
        self.assertEqual(
            response.data["events"][0]["event_type"],
            AnalyticsEvent.TYPE_SNAPSHOT_CREATED,
        )
        self.assertEqual(
            response.data["events"][0]["performed_by"],
            self.analytics_staff.id,
        )

    def test_snapshot_detail_returns_full_snapshot_metrics(self):
        """Return the expected analytics metrics fields in detail response."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_orders"], 10)
        self.assertEqual(response.data["orders_pending"], 2)
        self.assertEqual(response.data["orders_processing"], 1)
        self.assertEqual(response.data["orders_shipped"], 3)
        self.assertEqual(response.data["orders_delivered"], 3)
        self.assertEqual(response.data["orders_cancelled"], 1)
        self.assertEqual(response.data["payments_captured"], 7)
        self.assertEqual(response.data["payments_failed"], 1)
        self.assertEqual(response.data["payments_refunded"], 1)
        self.assertEqual(response.data["shipments_in_transit"], 2)
        self.assertEqual(response.data["shipments_delivered"], 3)
        self.assertEqual(response.data["shipments_failed"], 1)
        self.assertEqual(response.data["products_sold"], 12)
        self.assertEqual(response.data["active_customers"], 5)
        self.assertEqual(response.data["new_customers"], 2)
        self.assertEqual(response.data["total_registered_users"], 20)
        self.assertEqual(response.data["total_reviews"], 8)
        self.assertEqual(response.data["average_rating"], "4.50")
        self.assertEqual(response.data["metadata"]["source"], "test-detail")

    def test_snapshot_detail_returns_404_for_nonexistent_snapshot(self):
        """Return 404 when snapshot does not exist."""
        self.authenticate(self.analytics_staff)

        url = reverse(
            "analytics-api:analytics-snapshot-detail",
            kwargs={"snapshot_id": "11111111-1111-1111-1111-111111111111"},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)