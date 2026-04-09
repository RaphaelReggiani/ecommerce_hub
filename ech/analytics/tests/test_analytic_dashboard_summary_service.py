from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from ech.analytics.exceptions import AnalyticsDashboardUnavailableException
from ech.analytics.models import AnalyticsSnapshot
from ech.analytics.services.analytic_dashboard_summary_service import (
    AnalyticsDashboardSummaryService,
)


class AnalyticsDashboardSummaryServiceTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.period_start = timezone.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        cls.period_end = cls.period_start + timedelta(days=1)

    def setUp(self):
        cache.clear()

    def _build_nested_payload(self, *, source="realtime"):
        return {
            "source": source,
            "snapshot_id": None,
            "period_type": None,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "orders": {
                "total_orders": 10,
                "orders_pending": 2,
                "orders_processing": 3,
                "orders_shipped": 1,
                "orders_delivered": 3,
                "orders_cancelled": 1,
            },
            "revenue": {
                "total_revenue": Decimal("500.00"),
                "total_refunds": Decimal("50.00"),
                "net_revenue": Decimal("450.00"),
            },
            "payments": {
                "payments_captured": 7,
                "payments_failed": 2,
                "payments_refunded": 1,
            },
            "shipping": {
                "shipments_in_transit": 2,
                "shipments_delivered": 5,
                "shipments_failed": 1,
            },
            "products": {
                "products_sold": 20,
                "top_product_id": None,
            },
            "customers": {
                "active_customers": 5,
                "new_customers": 2,
            },
            "users": {
                "total_registered_users": 12,
                "active_users": 10,
                "inactive_users": 2,
                "confirmed_users": 9,
                "unconfirmed_users": 3,
                "staff_users": 2,
                "customer_users": 10,
            },
            "reviews": {
                "total_reviews": 8,
                "approved_reviews": 6,
                "rejected_reviews": 1,
                "hidden_reviews": 1,
                "cancelled_reviews": 0,
                "verified_purchase_reviews": 4,
                "average_rating": Decimal("4.20"),
                "low_rated_products_count": 1,
                "high_rated_products_count": 2,
            },
        }

    def test_get_summary_returns_snapshot_payload_when_snapshot_matches_period(self):
        snapshot = AnalyticsSnapshot(
            id=123,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start,
            period_end=self.period_end,
            total_orders=10,
            orders_pending=2,
            orders_processing=3,
            orders_shipped=1,
            orders_delivered=3,
            orders_cancelled=1,
            total_revenue=Decimal("500.00"),
            total_refunds=Decimal("50.00"),
            net_revenue=Decimal("450.00"),
            payments_captured=7,
            payments_failed=2,
            payments_refunded=1,
            shipments_in_transit=2,
            shipments_delivered=5,
            shipments_failed=1,
            products_sold=20,
            top_product_id=None,
            active_customers=5,
            new_customers=2,
            total_registered_users=12,
            active_users=10,
            inactive_users=2,
            confirmed_users=9,
            unconfirmed_users=3,
            staff_users=2,
            customer_users=10,
            total_reviews=8,
            approved_reviews=6,
            rejected_reviews=1,
            hidden_reviews=1,
            cancelled_reviews=0,
            verified_purchase_reviews=4,
            average_rating=Decimal("4.20"),
            low_rated_products_count=1,
            high_rated_products_count=2,
        )

        with patch(
            "ech.analytics.services.analytic_dashboard_summary_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=snapshot,
        ), patch(
            "ech.analytics.services.analytic_dashboard_summary_service."
            "AnalyticsLogService.log_dashboard_generated"
        ) as log_mock:
            summary = AnalyticsDashboardSummaryService.get_summary(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(summary["source"], "snapshot")
        self.assertEqual(summary["snapshot_id"], 123)
        self.assertEqual(summary["orders"]["total_orders"], 10)
        self.assertEqual(summary["revenue"]["total_revenue"], Decimal("500.00"))
        self.assertEqual(summary["customers"]["active_customers"], 5)
        self.assertEqual(summary["users"]["total_registered_users"], 12)
        self.assertEqual(summary["reviews"]["average_rating"], Decimal("4.20"))

        log_mock.assert_called_once_with(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start,
            period_end=self.period_end,
            performed_by=None,
        )

    def test_get_summary_uses_realtime_payload_when_snapshot_does_not_match_period(self):
        mismatched_snapshot = AnalyticsSnapshot(
            id=456,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start - timedelta(days=1),
            period_end=self.period_end - timedelta(days=1),
        )

        realtime_payload = self._build_nested_payload(source="realtime")

        with patch(
            "ech.analytics.services.analytic_dashboard_summary_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=mismatched_snapshot,
        ), patch(
            "ech.analytics.services.analytic_dashboard_summary_service."
            "AnalyticsDashboardSummaryService._build_summary_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_dashboard_summary_service."
            "AnalyticsLogService.log_dashboard_generated"
        ):
            summary = AnalyticsDashboardSummaryService.get_summary(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(summary["source"], "realtime")
        self.assertEqual(summary["orders"]["total_orders"], 10)
        self.assertEqual(summary["revenue"]["net_revenue"], Decimal("450.00"))
        realtime_mock.assert_called_once_with(
            period_start=self.period_start,
            period_end=self.period_end,
        )

    def test_get_summary_uses_cache_for_identical_requests(self):
        realtime_payload = self._build_nested_payload(source="realtime")

        with patch(
            "ech.analytics.services.analytic_dashboard_summary_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_dashboard_summary_service."
            "AnalyticsDashboardSummaryService._build_summary_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_dashboard_summary_service."
            "AnalyticsLogService.log_dashboard_generated"
        ) as log_mock:
            result_1 = AnalyticsDashboardSummaryService.get_summary(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )
            result_2 = AnalyticsDashboardSummaryService.get_summary(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result_1, result_2)
        realtime_mock.assert_called_once()
        log_mock.assert_called_once()

    def test_get_summary_rebuilds_after_cache_clear(self):
        realtime_payload = self._build_nested_payload(source="realtime")

        with patch(
            "ech.analytics.services.analytic_dashboard_summary_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_dashboard_summary_service."
            "AnalyticsDashboardSummaryService._build_summary_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_dashboard_summary_service."
            "AnalyticsLogService.log_dashboard_generated"
        ):
            AnalyticsDashboardSummaryService.get_summary(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

            cache.clear()

            AnalyticsDashboardSummaryService.get_summary(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(realtime_mock.call_count, 2)

    def test_get_summary_returns_empty_realtime_metrics_structure(self):
        empty_payload = {
            "source": "realtime",
            "snapshot_id": None,
            "period_type": None,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "orders": {
                "total_orders": 0,
                "orders_pending": 0,
                "orders_processing": 0,
                "orders_shipped": 0,
                "orders_delivered": 0,
                "orders_cancelled": 0,
            },
            "revenue": {
                "total_revenue": Decimal("0.00"),
                "total_refunds": Decimal("0.00"),
                "net_revenue": Decimal("0.00"),
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
                "average_rating": Decimal("0.00"),
                "low_rated_products_count": 0,
                "high_rated_products_count": 0,
            },
        }

        with patch(
            "ech.analytics.services.analytic_dashboard_summary_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_dashboard_summary_service."
            "AnalyticsDashboardSummaryService._build_summary_realtime",
            return_value=empty_payload,
        ):
            summary = AnalyticsDashboardSummaryService.get_summary(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(summary["orders"]["total_orders"], 0)
        self.assertEqual(summary["revenue"]["total_revenue"], Decimal("0.00"))
        self.assertEqual(summary["customers"]["active_customers"], 0)
        self.assertEqual(summary["users"]["total_registered_users"], 0)
        self.assertEqual(summary["reviews"]["average_rating"], Decimal("0.00"))

    def test_resolve_period_bounds_raises_when_only_one_bound_is_provided(self):
        with self.assertRaises(AnalyticsDashboardUnavailableException):
            AnalyticsDashboardSummaryService._resolve_period_bounds(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=None,
            )

    def test_get_summary_raises_dashboard_unavailable_when_cache_layer_fails(self):
        with patch(
            "ech.analytics.services.analytic_dashboard_summary_service."
            "AnalyticsCacheService.get_or_set",
            side_effect=Exception("cache failure"),
        ):
            with self.assertRaises(AnalyticsDashboardUnavailableException):
                AnalyticsDashboardSummaryService.get_summary(
                    period_type=AnalyticsSnapshot.PERIOD_DAILY,
                    period_start=self.period_start,
                    period_end=self.period_end,
                )

    def test_get_matching_snapshot_returns_none_when_selector_raises(self):
        with patch(
            "ech.analytics.services.analytic_dashboard_summary_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("not found"),
        ):
            result = AnalyticsDashboardSummaryService._get_matching_snapshot(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertIsNone(result)

    def test_get_matching_snapshot_returns_none_when_bounds_do_not_match(self):
        snapshot = AnalyticsSnapshot(
            id=777,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start - timedelta(days=2),
            period_end=self.period_end - timedelta(days=2),
        )

        with patch(
            "ech.analytics.services.analytic_dashboard_summary_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=snapshot,
        ):
            result = AnalyticsDashboardSummaryService._get_matching_snapshot(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertIsNone(result)