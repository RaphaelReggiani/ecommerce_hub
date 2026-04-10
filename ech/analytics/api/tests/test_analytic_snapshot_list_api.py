from datetime import timedelta

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from ech.analytics.models import (
    AnalyticsSnapshot,
    AnalyticsSnapshotLifecycle,
)
from ech.users.models import CustomUser


class AnalyticsSnapshotListApiTestCase(APITestCase):
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

        cls.url = reverse("analytics-api:analytics-snapshot-list")

        now = timezone.now()

        cls.snapshot_1 = cls._create_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=now - timedelta(days=2),
            period_end=now - timedelta(days=1),
            total_orders=10,
            total_revenue="1000.00",
            average_rating="4.50",
            active_customers=5,
            total_registered_users=20,
            total_reviews=8,
            generated_by=cls.analytics_staff,
        )

        cls.snapshot_2 = cls._create_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_WEEKLY,
            period_start=now - timedelta(days=14),
            period_end=now - timedelta(days=7),
            total_orders=4,
            total_revenue="250.00",
            average_rating="3.20",
            active_customers=2,
            total_registered_users=12,
            total_reviews=3,
            generated_by=cls.admin,
        )

    def setUp(self):
        cache.clear()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    @classmethod
    def _create_snapshot(
        cls,
        *,
        period_type,
        period_start,
        period_end,
        total_orders,
        total_revenue,
        average_rating,
        active_customers,
        total_registered_users,
        total_reviews,
        generated_by,
    ):
        snapshot = AnalyticsSnapshot.objects.create(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
            total_orders=total_orders,
            total_revenue=total_revenue,
            total_refunds="50.00",
            net_revenue="950.00",
            products_sold=12,
            active_customers=active_customers,
            new_customers=1,
            total_registered_users=total_registered_users,
            active_users=10,
            inactive_users=2,
            confirmed_users=9,
            unconfirmed_users=3,
            staff_users=2,
            customer_users=10,
            total_reviews=total_reviews,
            approved_reviews=2,
            rejected_reviews=1,
            hidden_reviews=0,
            cancelled_reviews=0,
            verified_purchase_reviews=2,
            average_rating=average_rating,
            low_rated_products_count=0,
            high_rated_products_count=1,
            generated_by=generated_by,
            metadata={"source": "test"},
        )

        AnalyticsSnapshotLifecycle.objects.create(snapshot=snapshot)
        return snapshot

    def test_snapshot_list_requires_authentication(self):
        """Reject snapshot list for unauthenticated users."""
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_snapshot_list_rejects_customer_user(self):
        """Reject snapshot list access for customer users."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_snapshot_list_returns_all_snapshots_for_analytics_staff(self):
        """Allow analytics staff users to list all snapshots."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_snapshot_list_returns_all_snapshots_for_admin(self):
        """Allow admin users to list all snapshots."""
        self.authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_snapshot_list_supports_period_type_filter(self):
        """Filter snapshots by period type."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(
            self.url,
            {"period_type": AnalyticsSnapshot.PERIOD_DAILY},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_snapshot_list_supports_generated_by_filter(self):
        """Filter snapshots by generated_by user id."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(
            self.url,
            {"generated_by": self.analytics_staff.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_snapshot_list_supports_total_revenue_min_filter(self):
        """Filter snapshots by minimum total revenue."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(
            self.url,
            {"total_revenue_min": "500.00"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_snapshot_list_supports_average_rating_max_filter(self):
        """Filter snapshots by maximum average rating."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(
            self.url,
            {"average_rating_max": "3.50"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_snapshot_list_supports_pagination(self):
        """Verify snapshot list pagination."""
        self.authenticate(self.analytics_staff)

        response = self.client.get(self.url, {"page_size": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)