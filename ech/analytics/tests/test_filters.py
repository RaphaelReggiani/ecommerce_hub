import uuid
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.analytics.filters import (
    AnalyticsSnapshotFilter,
    AnalyticsSnapshotManagementFilter,
)
from ech.analytics.models import AnalyticsSnapshot


User = get_user_model()


class BaseAnalyticsFilterFactoryMixin:
    def create_user(self, **kwargs):
        suffix = uuid.uuid4().hex[:8]

        data = {
            "email": f"user_{suffix}@test.com",
            "password": "StrongPassword123",
            "user_name": f"User {suffix}",
            "role": User.ROLE_CUSTOMER_USER,
            "is_active": True,
            "email_confirmed": True,
        }
        data.update(kwargs)
        return User.objects.create_user(**data)

    def create_staff_user(self, **kwargs):
        suffix = uuid.uuid4().hex[:8]

        data = {
            "email": f"staff_{suffix}@company.com",
            "password": "StrongPassword123",
            "user_name": f"Staff {suffix}",
            "role": User.ROLE_ANALYTICS_STAFF,
            "is_active": True,
            "email_confirmed": True,
        }
        data.update(kwargs)
        return User.objects.create_user(**data)

    def create_snapshot(self, **kwargs):
        generated_by = kwargs.pop("generated_by", None) or self.create_staff_user()

        now = timezone.now()
        period_start = kwargs.pop(
            "period_start",
            now.replace(hour=0, minute=0, second=0, microsecond=0),
        )
        period_end = kwargs.pop(
            "period_end",
            period_start + timedelta(days=1),
        )

        data = {
            "period_type": AnalyticsSnapshot.PERIOD_DAILY,
            "period_start": period_start,
            "period_end": period_end,
            "generated_by": generated_by,
            "total_orders": 10,
            "orders_pending": 2,
            "orders_processing": 2,
            "orders_shipped": 2,
            "orders_delivered": 3,
            "orders_cancelled": 1,
            "total_revenue": Decimal("1000.00"),
            "total_refunds": Decimal("100.00"),
            "net_revenue": Decimal("900.00"),
            "payments_captured": 8,
            "payments_failed": 1,
            "payments_refunded": 1,
            "shipments_in_transit": 2,
            "shipments_delivered": 5,
            "shipments_failed": 1,
            "products_sold": 20,
            "active_customers": 7,
            "new_customers": 3,
            "total_registered_users": 50,
            "active_users": 45,
            "inactive_users": 5,
            "confirmed_users": 40,
            "unconfirmed_users": 10,
            "staff_users": 5,
            "customer_users": 45,
            "total_reviews": 12,
            "approved_reviews": 8,
            "rejected_reviews": 1,
            "hidden_reviews": 1,
            "cancelled_reviews": 2,
            "verified_purchase_reviews": 6,
            "average_rating": Decimal("4.25"),
            "low_rated_products_count": 1,
            "high_rated_products_count": 3,
            "metadata": {"source": "unit-test"},
        }
        data.update(kwargs)

        return AnalyticsSnapshot.objects.create(**data)


class AnalyticsSnapshotFilterTestCase(BaseAnalyticsFilterFactoryMixin, TestCase):
    def setUp(self):
        self.staff_1 = self.create_staff_user(
            email="staff1@company.com",
        )
        self.staff_2 = self.create_staff_user(
            email="staff2@company.com",
        )

        now = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        self.snapshot_1 = self.create_snapshot(
            generated_by=self.staff_1,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=now,
            period_end=now + timedelta(days=1),
            total_revenue=Decimal("1000.00"),
            total_orders=10,
            active_customers=7,
            total_reviews=12,
        )

        self.snapshot_2 = self.create_snapshot(
            generated_by=self.staff_2,
            period_type=AnalyticsSnapshot.PERIOD_WEEKLY,
            period_start=now + timedelta(days=7),
            period_end=now + timedelta(days=14),
            total_revenue=Decimal("5000.00"),
            total_orders=40,
            active_customers=20,
            total_reviews=30,
        )

    def test_filter_by_period_type(self):
        """Filter snapshots by exact period type."""
        queryset = AnalyticsSnapshot.objects.all()

        filtered = AnalyticsSnapshotFilter(
            {"period_type": AnalyticsSnapshot.PERIOD_DAILY},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.snapshot_1)

    def test_filter_by_period_start_after(self):
        """Filter snapshots by period start lower bound."""
        queryset = AnalyticsSnapshot.objects.all()

        filtered = AnalyticsSnapshotFilter(
            {"period_start_after": self.snapshot_2.period_start - timedelta(hours=1)},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.snapshot_2)

    def test_filter_by_period_end_before(self):
        """Filter snapshots by period end upper bound."""
        queryset = AnalyticsSnapshot.objects.all()

        filtered = AnalyticsSnapshotFilter(
            {"period_end_before": self.snapshot_1.period_end + timedelta(hours=1)},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.snapshot_1)

    def test_filter_by_generated_by(self):
        """Filter snapshots by generating user id."""
        queryset = AnalyticsSnapshot.objects.all()

        filtered = AnalyticsSnapshotFilter(
            {"generated_by": str(self.staff_1.id)},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.snapshot_1)

    def test_filter_by_revenue_min(self):
        """Filter snapshots by minimum total revenue."""
        queryset = AnalyticsSnapshot.objects.all()

        filtered = AnalyticsSnapshotFilter(
            {"total_revenue_min": Decimal("2000.00")},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.snapshot_2)

    def test_filter_by_revenue_max(self):
        """Filter snapshots by maximum total revenue."""
        queryset = AnalyticsSnapshot.objects.all()

        filtered = AnalyticsSnapshotFilter(
            {"total_revenue_max": Decimal("2000.00")},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.snapshot_1)

    def test_filter_by_orders_min(self):
        """Filter snapshots by minimum total orders."""
        queryset = AnalyticsSnapshot.objects.all()

        filtered = AnalyticsSnapshotFilter(
            {"total_orders_min": 20},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.snapshot_2)

    def test_filter_by_average_rating_min(self):
        """Filter snapshots by minimum average rating."""
        queryset = AnalyticsSnapshot.objects.all()

        filtered = AnalyticsSnapshotFilter(
            {"average_rating_min": Decimal("4.00")},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 2)

    def test_filter_by_average_rating_max(self):
        """Filter snapshots by maximum average rating."""
        queryset = AnalyticsSnapshot.objects.all()

        self.snapshot_2.average_rating = Decimal("2.50")
        self.snapshot_2.save(update_fields=["average_rating", "updated_at"])

        filtered = AnalyticsSnapshotFilter(
            {"average_rating_max": Decimal("3.00")},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.snapshot_2)


class AnalyticsSnapshotManagementFilterTestCase(
    BaseAnalyticsFilterFactoryMixin,
    TestCase,
):
    def setUp(self):
        self.staff_1 = self.create_staff_user(
            email="manager1@company.com",
        )
        self.staff_2 = self.create_staff_user(
            email="manager2@company.com",
        )

        now = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        self.snapshot_1 = self.create_snapshot(
            generated_by=self.staff_1,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=now,
            period_end=now + timedelta(days=1),
            total_revenue=Decimal("1500.00"),
            total_orders=12,
            active_customers=9,
            total_registered_users=60,
            total_reviews=14,
            metadata={"source": "scheduled-job"},
        )

        self.snapshot_2 = self.create_snapshot(
            generated_by=self.staff_2,
            period_type=AnalyticsSnapshot.PERIOD_MONTHLY,
            period_start=now + timedelta(days=30),
            period_end=now + timedelta(days=60),
            total_revenue=Decimal("9000.00"),
            total_orders=80,
            active_customers=50,
            total_registered_users=200,
            total_reviews=70,
            metadata={"source": "manual-refresh"},
        )

    def test_filter_by_metadata_source(self):
        """Filter snapshots using metadata content."""
        queryset = AnalyticsSnapshot.objects.all()

        filtered = AnalyticsSnapshotManagementFilter(
            {"metadata": "manual"},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.snapshot_2)

    def test_filter_by_active_customers_min(self):
        """Filter snapshots by minimum active customers."""
        queryset = AnalyticsSnapshot.objects.all()

        filtered = AnalyticsSnapshotManagementFilter(
            {"active_customers_min": 20},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.snapshot_2)

    def test_filter_by_registered_users_min(self):
        """Filter snapshots by minimum registered users."""
        queryset = AnalyticsSnapshot.objects.all()

        filtered = AnalyticsSnapshotManagementFilter(
            {"total_registered_users_min": 100},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.snapshot_2)

    def test_filter_by_reviews_min(self):
        """Filter snapshots by minimum total reviews."""
        queryset = AnalyticsSnapshot.objects.all()

        filtered = AnalyticsSnapshotManagementFilter(
            {"total_reviews_min": 20},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.snapshot_2)

    def test_filter_combined_filters(self):
        """Apply multiple management filters simultaneously."""
        queryset = AnalyticsSnapshot.objects.all()

        filtered = AnalyticsSnapshotManagementFilter(
            {
                "period_type": AnalyticsSnapshot.PERIOD_DAILY,
                "generated_by": str(self.staff_1.id),
                "total_revenue_max": Decimal("2000.00"),
            },
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.snapshot_1)