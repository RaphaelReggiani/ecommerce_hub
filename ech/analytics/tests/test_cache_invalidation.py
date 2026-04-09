import uuid
from datetime import timedelta
from decimal import Decimal

from django.core.cache import cache
from django.test import TransactionTestCase
from django.utils import timezone

from ech.analytics.models import (
    AnalyticsSnapshot,
    AnalyticsSnapshotLifecycle,
)
from ech.analytics.selectors import (
    get_analytics_snapshot_by_id,
    get_latest_analytics_snapshot_by_period_type,
    list_analytics_snapshots,
    list_analytics_snapshots_by_period_type,
    search_analytics_snapshots,
)
from ech.analytics.services.analytic_snapshot_generation_service import (
    AnalyticsSnapshotGenerationService,
)
from ech.analytics.services.analytic_snapshot_refresh_service import (
    AnalyticsSnapshotRefreshService,
)
from ech.orders.models import Order
from ech.users.models import CustomUser


class AnalyticsCacheInvalidationTestCase(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        cache.clear()

        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.staff = CustomUser.objects.create_user(
            email="analytics.staff@company.com",
            password="StrongPassword123",
            user_name="Analytics Staff",
            role=CustomUser.ROLE_ANALYTICS_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        self.base_start = timezone.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        self.base_end = self.base_start + timedelta(days=1)

    def _create_order_in_period(self, *, created_at=None, customer=None):
        order = Order.objects.create(
            customer=customer or self.customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )

        Order.objects.filter(id=order.id).update(
            created_at=created_at or (self.base_start + timedelta(hours=1)),
        )
        order.refresh_from_db()
        return order

    def _create_snapshot(self, **kwargs):
        data = {
            "period_type": AnalyticsSnapshot.PERIOD_DAILY,
            "period_start": self.base_start,
            "period_end": self.base_end,
            "generated_by": self.staff,
            "total_orders": 0,
            "orders_pending": 0,
            "orders_processing": 0,
            "orders_shipped": 0,
            "orders_delivered": 0,
            "orders_cancelled": 0,
            "total_revenue": Decimal("0.00"),
            "total_refunds": Decimal("0.00"),
            "net_revenue": Decimal("0.00"),
            "payments_captured": 0,
            "payments_failed": 0,
            "payments_refunded": 0,
            "shipments_in_transit": 0,
            "shipments_delivered": 0,
            "shipments_failed": 0,
            "products_sold": 0,
            "top_product_id": None,
            "active_customers": 0,
            "new_customers": 0,
            "total_registered_users": 0,
            "active_users": 0,
            "inactive_users": 0,
            "confirmed_users": 0,
            "unconfirmed_users": 0,
            "staff_users": 0,
            "customer_users": 0,
            "total_reviews": 0,
            "approved_reviews": 0,
            "rejected_reviews": 0,
            "hidden_reviews": 0,
            "cancelled_reviews": 0,
            "verified_purchase_reviews": 0,
            "average_rating": Decimal("0.00"),
            "low_rated_products_count": 0,
            "high_rated_products_count": 0,
            "metadata": {"source": "cache-invalidation"},
        }
        data.update(kwargs)

        snapshot = AnalyticsSnapshot.objects.create(**data)
        AnalyticsSnapshotLifecycle.objects.create(
            snapshot=snapshot,
            generation_started_at=timezone.now(),
            generation_completed_at=timezone.now(),
        )
        return snapshot

    def test_generation_service_invalidates_management_list_cache(self):
        """Invalidate cached management snapshot list after snapshot generation."""
        before = list(list_analytics_snapshots())
        self.assertEqual(len(before), 0)

        AnalyticsSnapshotGenerationService.generate_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.base_start,
            period_end=self.base_end,
            performed_by=self.staff,
            idempotency_key=uuid.uuid4(),
            metadata={"source": "generation-list-cache"},
        )

        after = list(list_analytics_snapshots())
        self.assertEqual(len(after), 1)

    def test_generation_service_invalidates_period_type_list_cache(self):
        """Invalidate cached period-filtered snapshot list after snapshot generation."""
        before = list(
            list_analytics_snapshots_by_period_type(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
            )
        )
        self.assertEqual(len(before), 0)

        AnalyticsSnapshotGenerationService.generate_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.base_start,
            period_end=self.base_end,
            performed_by=self.staff,
            idempotency_key=uuid.uuid4(),
            metadata={"source": "generation-period-cache"},
        )

        after = list(
            list_analytics_snapshots_by_period_type(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
            )
        )
        self.assertEqual(len(after), 1)

    def test_generation_service_invalidates_search_cache(self):
        """Invalidate cached search results after snapshot generation."""
        before = list(search_analytics_snapshots(query="search-cache-shared"))
        self.assertEqual(len(before), 0)

        AnalyticsSnapshotGenerationService.generate_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.base_start,
            period_end=self.base_end,
            performed_by=self.staff,
            idempotency_key=uuid.uuid4(),
            metadata={
                "source": "search-cache-shared",
                "label": "search-cache-shared",
            },
        )

        after = list(search_analytics_snapshots(query="search-cache-shared"))
        self.assertEqual(len(after), 1)

    def test_generation_service_invalidates_latest_snapshot_cache(self):
        """Invalidate cached latest snapshot lookup after newer snapshot generation."""
        old_snapshot = self._create_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.base_start,
            period_end=self.base_end,
        )

        cached_latest = get_latest_analytics_snapshot_by_period_type(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
        )
        self.assertEqual(cached_latest.id, old_snapshot.id)

        new_start = self.base_start + timedelta(days=1)
        new_end = self.base_end + timedelta(days=1)

        new_snapshot = AnalyticsSnapshotGenerationService.generate_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=new_start,
            period_end=new_end,
            performed_by=self.staff,
            idempotency_key=uuid.uuid4(),
            metadata={"source": "latest-cache"},
        )

        fresh_latest = get_latest_analytics_snapshot_by_period_type(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
        )
        self.assertEqual(fresh_latest.id, new_snapshot.id)
        self.assertNotEqual(fresh_latest.id, old_snapshot.id)

    def test_refresh_service_invalidates_detail_cache(self):
        """Invalidate snapshot detail cache after snapshot refresh."""
        snapshot = AnalyticsSnapshotGenerationService.generate_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.base_start,
            period_end=self.base_end,
            performed_by=self.staff,
            idempotency_key=uuid.uuid4(),
            metadata={"source": "refresh-detail-cache"},
        )

        cached_snapshot = get_analytics_snapshot_by_id(snapshot_id=snapshot.id)
        self.assertEqual(cached_snapshot.total_orders, 0)

        self._create_order_in_period()

        AnalyticsSnapshotRefreshService.refresh_snapshot(
            snapshot=snapshot,
            performed_by=self.staff,
            metadata={"source": "refresh-detail-cache"},
        )

        fresh_snapshot = get_analytics_snapshot_by_id(snapshot_id=snapshot.id)
        self.assertEqual(fresh_snapshot.total_orders, 1)

    def test_refresh_service_invalidates_latest_snapshot_cache_metrics(self):
        """Invalidate cached latest snapshot object after refresh updates metrics."""
        snapshot = AnalyticsSnapshotGenerationService.generate_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.base_start,
            period_end=self.base_end,
            performed_by=self.staff,
            idempotency_key=uuid.uuid4(),
            metadata={"source": "refresh-latest-cache"},
        )

        cached_latest = get_latest_analytics_snapshot_by_period_type(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
        )
        self.assertEqual(cached_latest.total_orders, 0)

        self._create_order_in_period()

        AnalyticsSnapshotRefreshService.refresh_snapshot(
            snapshot=snapshot,
            performed_by=self.staff,
            metadata={"source": "refresh-latest-cache"},
        )

        fresh_latest = get_latest_analytics_snapshot_by_period_type(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
        )
        self.assertEqual(fresh_latest.total_orders, 1)