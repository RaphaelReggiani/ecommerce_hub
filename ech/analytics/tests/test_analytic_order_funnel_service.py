from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from ech.analytics.exceptions import AnalyticsOrderUnavailableException
from ech.analytics.models import AnalyticsSnapshot
from ech.analytics.services.analytic_order_funnel_service import (
    AnalyticsOrderFunnelService,
)


class AnalyticsOrderFunnelServiceTestCase(TestCase):
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
            "total_orders": 20,
            "pending_orders": 5,
            "processing_orders": 4,
            "shipped_orders": 3,
            "delivered_orders": 6,
            "cancelled_orders": 2,
            "delivered_rate": Decimal("0.30"),
            "cancelled_rate": Decimal("0.10"),
        }

    def test_get_funnel_returns_snapshot_data_when_available(self):
        snapshot = AnalyticsSnapshot(
            id=201,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start,
            period_end=self.period_end,
            total_orders=20,
            orders_pending=5,
            orders_processing=4,
            orders_shipped=3,
            orders_delivered=6,
            orders_cancelled=2,
        )

        with patch(
            "ech.analytics.services.analytic_order_funnel_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=snapshot,
        ):
            result = AnalyticsOrderFunnelService.get_funnel(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

            self.assertEqual(result["source"], "snapshot")
            self.assertEqual(result["snapshot_id"], 201)
            self.assertEqual(result["total_orders"], 20)
            self.assertEqual(result["pending_orders"], 5)
            self.assertEqual(result["processing_orders"], 4)
            self.assertEqual(result["shipped_orders"], 3)
            self.assertEqual(result["delivered_orders"], 6)
            self.assertEqual(result["cancelled_orders"], 2)
            self.assertAlmostEqual(result["delivered_rate"], 0.3)
            self.assertAlmostEqual(result["cancelled_rate"], 0.1)

    def test_get_funnel_uses_realtime_when_snapshot_mismatch(self):
        mismatched_snapshot = AnalyticsSnapshot(
            id=202,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start - timedelta(days=1),
            period_end=self.period_end - timedelta(days=1),
        )

        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_order_funnel_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=mismatched_snapshot,
        ), patch(
            "ech.analytics.services.analytic_order_funnel_service."
            "AnalyticsOrderFunnelService._build_funnel_realtime",
            return_value=realtime_payload,
        ) as realtime_mock:
            result = AnalyticsOrderFunnelService.get_funnel(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["source"], "realtime")
        self.assertEqual(result["total_orders"], 20)
        self.assertEqual(result["delivered_orders"], 6)
        self.assertEqual(result["delivered_rate"], Decimal("0.30"))
        self.assertEqual(result["cancelled_rate"], Decimal("0.10"))

        realtime_mock.assert_called_once_with(
            period_start=self.period_start,
            period_end=self.period_end,
        )

    def test_get_funnel_uses_cache(self):
        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_order_funnel_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_order_funnel_service."
            "AnalyticsOrderFunnelService._build_funnel_realtime",
            return_value=realtime_payload,
        ) as realtime_mock:
            result_1 = AnalyticsOrderFunnelService.get_funnel(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )
            result_2 = AnalyticsOrderFunnelService.get_funnel(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result_1, result_2)
        realtime_mock.assert_called_once()

    def test_get_funnel_rebuilds_after_cache_clear(self):
        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_order_funnel_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_order_funnel_service."
            "AnalyticsOrderFunnelService._build_funnel_realtime",
            return_value=realtime_payload,
        ) as realtime_mock:
            AnalyticsOrderFunnelService.get_funnel(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

            cache.clear()

            AnalyticsOrderFunnelService.get_funnel(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(realtime_mock.call_count, 2)

    def test_get_funnel_handles_empty_metrics(self):
        empty_payload = {
            "source": "realtime",
            "snapshot_id": None,
            "period_type": None,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "total_orders": 0,
            "pending_orders": 0,
            "processing_orders": 0,
            "shipped_orders": 0,
            "delivered_orders": 0,
            "cancelled_orders": 0,
            "delivered_rate": Decimal("0.00"),
            "cancelled_rate": Decimal("0.00"),
        }

        with patch(
            "ech.analytics.services.analytic_order_funnel_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_order_funnel_service."
            "AnalyticsOrderFunnelService._build_funnel_realtime",
            return_value=empty_payload,
        ):
            result = AnalyticsOrderFunnelService.get_funnel(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["total_orders"], 0)
        self.assertEqual(result["pending_orders"], 0)
        self.assertEqual(result["delivered_rate"], Decimal("0.00"))
        self.assertEqual(result["cancelled_rate"], Decimal("0.00"))

    def test_get_funnel_raises_when_cache_layer_fails(self):
        with patch(
            "ech.analytics.services.analytic_order_funnel_service."
            "AnalyticsCacheService.get_or_set",
            side_effect=Exception("cache failure"),
        ):
            with self.assertRaises(AnalyticsOrderUnavailableException):
                AnalyticsOrderFunnelService.get_funnel(
                    period_type=AnalyticsSnapshot.PERIOD_DAILY,
                    period_start=self.period_start,
                    period_end=self.period_end,
                )

    def test_resolve_period_bounds_raises_when_only_one_bound_is_provided(self):
        with self.assertRaises(AnalyticsOrderUnavailableException):
            AnalyticsOrderFunnelService._resolve_period_bounds(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=None,
            )

    def test_get_matching_snapshot_returns_none_when_selector_raises(self):
        with patch(
            "ech.analytics.services.analytic_order_funnel_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("not found"),
        ):
            result = AnalyticsOrderFunnelService._get_matching_snapshot(
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
            "ech.analytics.services.analytic_order_funnel_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=snapshot,
        ):
            result = AnalyticsOrderFunnelService._get_matching_snapshot(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertIsNone(result)

    def test_build_funnel_from_snapshot_handles_zero_total_orders(self):
        snapshot = AnalyticsSnapshot(
            id=301,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start,
            period_end=self.period_end,
            total_orders=0,
            orders_pending=0,
            orders_processing=0,
            orders_shipped=0,
            orders_delivered=0,
            orders_cancelled=0,
        )

        result = AnalyticsOrderFunnelService._build_funnel_from_snapshot(
            snapshot=snapshot,
        )

        self.assertEqual(result["source"], "snapshot")
        self.assertEqual(result["total_orders"], 0)
        self.assertEqual(result["pending_orders"], 0)
        self.assertEqual(result["processing_orders"], 0)
        self.assertEqual(result["shipped_orders"], 0)
        self.assertEqual(result["delivered_orders"], 0)
        self.assertEqual(result["cancelled_orders"], 0)
        self.assertEqual(result["delivered_rate"], 0)
        self.assertEqual(result["cancelled_rate"], 0)