import uuid
from datetime import timedelta
from decimal import Decimal

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from ech.analytics.models import (
    AnalyticsEvent,
    AnalyticsSnapshot,
    AnalyticsSnapshotLifecycle,
)
from ech.analytics.selectors import (
    get_analytics_snapshot_by_id,
    get_latest_analytics_snapshot_by_period_type,
    list_analytics_snapshots,
    list_analytics_snapshots_by_period_type,
    list_analytics_snapshots_by_period_range,
    search_analytics_snapshots,
)
from ech.users.models import CustomUser


class AnalyticsCacheSelectorsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = CustomUser.objects.create_user(
            email="analytics.staff@company.com",
            password="StrongPassword123",
            user_name="Analytics Staff",
            role=CustomUser.ROLE_ANALYTICS_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        cls.base_start = timezone.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        cls.daily_snapshot = cls.create_snapshot_with_related(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=cls.base_start,
            period_end=cls.base_start + timedelta(days=1),
            generated_by=cls.staff,
            total_orders=10,
            total_revenue=Decimal("1000.00"),
            metadata={"source": "cache-test", "label": "daily-cache"},
        )

        cls.weekly_snapshot = cls.create_snapshot_with_related(
            period_type=AnalyticsSnapshot.PERIOD_WEEKLY,
            period_start=cls.base_start + timedelta(days=7),
            period_end=cls.base_start + timedelta(days=14),
            generated_by=cls.staff,
            total_orders=50,
            total_revenue=Decimal("7000.00"),
            metadata={"source": "cache-test", "label": "weekly-cache"},
        )

    def setUp(self):
        cache.clear()

    @classmethod
    def create_snapshot_with_related(
        cls,
        *,
        period_type,
        period_start,
        period_end,
        generated_by,
        total_orders,
        total_revenue,
        metadata,
    ):
        snapshot = AnalyticsSnapshot.objects.create(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
            total_orders=total_orders,
            orders_pending=1,
            orders_processing=2,
            orders_shipped=2,
            orders_delivered=4,
            orders_cancelled=1,
            total_revenue=total_revenue,
            total_refunds=Decimal("100.00"),
            net_revenue=total_revenue - Decimal("100.00"),
            payments_captured=7,
            payments_failed=1,
            payments_refunded=1,
            shipments_in_transit=2,
            shipments_delivered=4,
            shipments_failed=1,
            products_sold=15,
            top_product_id=uuid.uuid4(),
            active_customers=8,
            new_customers=3,
            total_registered_users=30,
            active_users=25,
            inactive_users=5,
            confirmed_users=24,
            unconfirmed_users=6,
            staff_users=5,
            customer_users=25,
            total_reviews=12,
            approved_reviews=8,
            rejected_reviews=1,
            hidden_reviews=1,
            cancelled_reviews=2,
            verified_purchase_reviews=7,
            average_rating=Decimal("4.25"),
            low_rated_products_count=1,
            high_rated_products_count=3,
            generated_by=generated_by,
            metadata=metadata,
        )

        AnalyticsSnapshotLifecycle.objects.create(
            snapshot=snapshot,
            generation_started_at=timezone.now(),
            generation_completed_at=timezone.now(),
        )
        AnalyticsEvent.objects.create(
            snapshot=snapshot,
            event_type=AnalyticsEvent.TYPE_SNAPSHOT_CREATED,
        )

        return snapshot

    def test_get_analytics_snapshot_by_id_uses_cached_detail_snapshot(self):
        """Return cached snapshot detail until cache is invalidated."""
        snapshot = get_analytics_snapshot_by_id(snapshot_id=self.daily_snapshot.id)
        self.assertEqual(snapshot.total_orders, 10)

        AnalyticsSnapshot.objects.filter(id=self.daily_snapshot.id).update(
            total_orders=999,
        )

        cached_snapshot = get_analytics_snapshot_by_id(
            snapshot_id=self.daily_snapshot.id,
        )
        self.assertEqual(cached_snapshot.total_orders, 10)

    def test_get_latest_analytics_snapshot_by_period_type_uses_cached_latest_snapshot(self):
        """Return cached latest snapshot for repeated identical period queries."""
        latest_snapshot = get_latest_analytics_snapshot_by_period_type(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
        )
        self.assertEqual(latest_snapshot.id, self.daily_snapshot.id)

        newer_snapshot = self.create_snapshot_with_related(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.base_start + timedelta(days=1),
            period_end=self.base_start + timedelta(days=2),
            generated_by=self.staff,
            total_orders=99,
            total_revenue=Decimal("9999.00"),
            metadata={"source": "cache-test", "label": "newer-daily"},
        )

        cached_latest = get_latest_analytics_snapshot_by_period_type(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
        )
        self.assertEqual(cached_latest.id, self.daily_snapshot.id)
        self.assertNotEqual(cached_latest.id, newer_snapshot.id)

    def test_list_analytics_snapshots_uses_cached_id_set(self):
        """Return cached management snapshot IDs until cache is invalidated."""
        first_result = list(list_analytics_snapshots())
        self.assertEqual(len(first_result), 2)

        self.create_snapshot_with_related(
            period_type=AnalyticsSnapshot.PERIOD_MONTHLY,
            period_start=self.base_start + timedelta(days=30),
            period_end=self.base_start + timedelta(days=60),
            generated_by=self.staff,
            total_orders=70,
            total_revenue=Decimal("12000.00"),
            metadata={"source": "cache-test", "label": "monthly-cache"},
        )

        second_result = list(list_analytics_snapshots())
        self.assertEqual(len(second_result), 2)

    def test_list_analytics_snapshots_by_period_type_uses_cached_id_set(self):
        """Return cached filtered snapshot IDs for repeated identical period type queries."""
        first_result = list(
            list_analytics_snapshots_by_period_type(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
            )
        )
        self.assertEqual(len(first_result), 1)
        self.assertEqual(first_result[0].id, self.daily_snapshot.id)

        self.create_snapshot_with_related(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.base_start + timedelta(days=2),
            period_end=self.base_start + timedelta(days=3),
            generated_by=self.staff,
            total_orders=88,
            total_revenue=Decimal("8800.00"),
            metadata={"source": "cache-test", "label": "second-daily"},
        )

        second_result = list(
            list_analytics_snapshots_by_period_type(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
            )
        )
        self.assertEqual(len(second_result), 1)
        self.assertEqual(second_result[0].id, self.daily_snapshot.id)

    def test_list_analytics_snapshots_by_period_range_uses_cached_id_set(self):
        """Return cached snapshot IDs for repeated identical period range queries."""
        period_start = self.base_start
        period_end = self.base_start + timedelta(days=14)

        first_result = list(
            list_analytics_snapshots_by_period_range(
                period_start=period_start,
                period_end=period_end,
            )
        )
        self.assertEqual(len(first_result), 2)

        self.create_snapshot_with_related(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.base_start + timedelta(days=3),
            period_end=self.base_start + timedelta(days=4),
            generated_by=self.staff,
            total_orders=22,
            total_revenue=Decimal("2200.00"),
            metadata={"source": "cache-test", "label": "range-added"},
        )

        second_result = list(
            list_analytics_snapshots_by_period_range(
                period_start=period_start,
                period_end=period_end,
            )
        )
        self.assertEqual(len(second_result), 2)

    def test_search_analytics_snapshots_uses_cached_result_ids(self):
        """Return cached snapshot search IDs for repeated identical queries."""
        first_result = list(search_analytics_snapshots(query="weekly-cache"))
        second_result = list(search_analytics_snapshots(query="weekly-cache"))

        self.assertEqual(len(first_result), 1)
        self.assertEqual(len(second_result), 1)
        self.assertEqual(first_result[0].id, second_result[0].id)

    def test_search_analytics_snapshots_returns_stale_results_until_invalidation(self):
        """Return cached search result IDs even after a new matching snapshot is created."""
        first_result = list(search_analytics_snapshots(query="cache-shared"))
        self.assertEqual(len(first_result), 0)

        self.create_snapshot_with_related(
            period_type=AnalyticsSnapshot.PERIOD_MONTHLY,
            period_start=self.base_start + timedelta(days=90),
            period_end=self.base_start + timedelta(days=120),
            generated_by=self.staff,
            total_orders=120,
            total_revenue=Decimal("22000.00"),
            metadata={"source": "cache-shared", "label": "shared-search"},
        )

        second_result = list(search_analytics_snapshots(query="cache-shared"))
        self.assertEqual(len(second_result), 0)