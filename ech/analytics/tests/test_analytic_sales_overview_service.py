from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from ech.analytics.exceptions import AnalyticsSalesUnavailableException
from ech.analytics.models import AnalyticsSnapshot
from ech.analytics.services.analytic_sales_overview_service import (
    AnalyticsSalesOverviewService,
)


class AnalyticsSalesOverviewServiceTestCase(TestCase):
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

    def _build_realtime_payload(self):
        return {
            "source": "realtime",
            "snapshot_id": None,
            "period_type": None,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "total_orders": 12,
            "delivered_orders": 4,
            "cancelled_orders": 1,
            "total_revenue": Decimal("800.00"),
            "total_refunds": Decimal("100.00"),
            "net_revenue": Decimal("700.00"),
            "average_order_value": Decimal("58.33"),
            "payments_captured": 7,
            "payments_refunded": 2,
        }

    def test_get_overview_returns_snapshot_data_when_available(self):
        """Ensure sales overview returns snapshot metrics when a matching snapshot exists for the requested period."""
        snapshot = AnalyticsSnapshot(
            id=101,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start,
            period_end=self.period_end,
            total_orders=12,
            orders_delivered=4,
            orders_cancelled=1,
            total_revenue=Decimal("800.00"),
            total_refunds=Decimal("100.00"),
            net_revenue=Decimal("700.00"),
            payments_captured=7,
            payments_refunded=2,
        )

        with patch(
            "ech.analytics.services.analytic_sales_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=snapshot,
        ), patch(
            "ech.analytics.services.analytic_sales_overview_service."
            "AnalyticsLogService.log_sales_metrics_calculated"
        ) as log_mock:
            result = AnalyticsSalesOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["source"], "snapshot")
        self.assertEqual(result["snapshot_id"], 101)
        self.assertEqual(result["total_orders"], 12)
        self.assertEqual(result["delivered_orders"], 4)
        self.assertEqual(result["cancelled_orders"], 1)
        self.assertEqual(result["total_revenue"], Decimal("800.00"))
        self.assertEqual(result["total_refunds"], Decimal("100.00"))
        self.assertEqual(result["net_revenue"], Decimal("700.00"))
        self.assertEqual(result["average_order_value"], Decimal("58.33333333333333333333333333"))
        self.assertEqual(result["payments_captured"], 7)
        self.assertEqual(result["payments_refunded"], 2)

        log_mock.assert_called_once_with(
            period_start=self.period_start,
            period_end=self.period_end,
            total_orders=12,
            total_revenue=Decimal("800.00"),
            performed_by=None,
        )

    def test_get_overview_uses_realtime_when_snapshot_mismatch(self):
        """Ensure sales overview falls back to realtime metrics when the available snapshot does not match the requested period."""
        mismatched_snapshot = AnalyticsSnapshot(
            id=55,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start - timedelta(days=1),
            period_end=self.period_end - timedelta(days=1),
        )

        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_sales_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=mismatched_snapshot,
        ), patch(
            "ech.analytics.services.analytic_sales_overview_service."
            "AnalyticsSalesOverviewService._build_overview_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_sales_overview_service."
            "AnalyticsLogService.log_sales_metrics_calculated"
        ):
            result = AnalyticsSalesOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["source"], "realtime")
        self.assertEqual(result["total_orders"], 12)
        self.assertEqual(result["net_revenue"], Decimal("700.00"))
        self.assertEqual(result["average_order_value"], Decimal("58.33"))
        realtime_mock.assert_called_once_with(
            period_start=self.period_start,
            period_end=self.period_end,
        )

    def test_get_overview_uses_cache(self):
        """Ensure sales overview reuses cached realtime metrics and avoids recalculating or relogging on repeated requests."""
        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_sales_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_sales_overview_service."
            "AnalyticsSalesOverviewService._build_overview_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_sales_overview_service."
            "AnalyticsLogService.log_sales_metrics_calculated"
        ) as log_mock:
            result_1 = AnalyticsSalesOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )
            result_2 = AnalyticsSalesOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result_1, result_2)
        realtime_mock.assert_called_once()
        log_mock.assert_called_once()

    def test_get_overview_rebuilds_after_cache_clear(self):
        """Ensure sales overview rebuilds realtime metrics after the cache is cleared."""
        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_sales_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_sales_overview_service."
            "AnalyticsSalesOverviewService._build_overview_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_sales_overview_service."
            "AnalyticsLogService.log_sales_metrics_calculated"
        ):
            AnalyticsSalesOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

            cache.clear()

            AnalyticsSalesOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(realtime_mock.call_count, 2)

    def test_get_overview_handles_empty_metrics(self):
        """Ensure sales overview correctly handles periods with zero orders, revenue, refunds, and payment metrics."""
        empty_payload = {
            "source": "realtime",
            "snapshot_id": None,
            "period_type": None,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "total_orders": 0,
            "delivered_orders": 0,
            "cancelled_orders": 0,
            "total_revenue": Decimal("0.00"),
            "total_refunds": Decimal("0.00"),
            "net_revenue": Decimal("0.00"),
            "average_order_value": Decimal("0.00"),
            "payments_captured": 0,
            "payments_refunded": 0,
        }

        with patch(
            "ech.analytics.services.analytic_sales_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_sales_overview_service."
            "AnalyticsSalesOverviewService._build_overview_realtime",
            return_value=empty_payload,
        ):
            result = AnalyticsSalesOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["total_orders"], 0)
        self.assertEqual(result["total_revenue"], Decimal("0.00"))
        self.assertEqual(result["net_revenue"], Decimal("0.00"))
        self.assertEqual(result["average_order_value"], Decimal("0.00"))
        self.assertEqual(result["payments_captured"], 0)
        self.assertEqual(result["payments_refunded"], 0)

    def test_get_overview_raises_when_cache_layer_fails(self):
        """Ensure sales overview raises an unavailable exception when the cache layer fails."""
        with patch(
            "ech.analytics.services.analytic_sales_overview_service."
            "AnalyticsCacheService.get_or_set",
            side_effect=Exception("cache failure"),
        ):
            with self.assertRaises(AnalyticsSalesUnavailableException):
                AnalyticsSalesOverviewService.get_overview(
                    period_type=AnalyticsSnapshot.PERIOD_DAILY,
                    period_start=self.period_start,
                    period_end=self.period_end,
                )

    def test_resolve_period_bounds_raises_when_only_one_bound_is_provided(self):
        """Ensure period bound resolution fails when only one sales overview bound is provided."""
        with self.assertRaises(AnalyticsSalesUnavailableException):
            AnalyticsSalesOverviewService._resolve_period_bounds(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=None,
            )

    def test_get_matching_snapshot_returns_none_when_selector_raises(self):
        """Ensure matching snapshot lookup returns None when the snapshot selector raises an exception."""
        with patch(
            "ech.analytics.services.analytic_sales_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("not found"),
        ):
            result = AnalyticsSalesOverviewService._get_matching_snapshot(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertIsNone(result)

    def test_get_matching_snapshot_returns_none_when_bounds_do_not_match(self):
        """Ensure matching snapshot lookup returns None when snapshot bounds do not match the requested sales period."""
        snapshot = AnalyticsSnapshot(
            id=777,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start - timedelta(days=2),
            period_end=self.period_end - timedelta(days=2),
        )

        with patch(
            "ech.analytics.services.analytic_sales_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=snapshot,
        ):
            result = AnalyticsSalesOverviewService._get_matching_snapshot(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertIsNone(result)