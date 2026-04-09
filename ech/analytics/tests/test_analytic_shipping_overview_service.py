from datetime import timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from ech.analytics.exceptions import AnalyticsShippingUnavailableException
from ech.analytics.models import AnalyticsSnapshot
from ech.analytics.services.analytic_shipping_overview_service import (
    AnalyticsShippingOverviewService,
)


class AnalyticsShippingOverviewServiceTestCase(TestCase):
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
            "in_transit_shipments": 12,
            "delivered_shipments": 8,
            "failed_shipments": 2,
            "delivered_rate": 0.4,
            "failed_rate": 0.1,
        }

    def test_get_overview_returns_snapshot_data_when_available(self):
        snapshot = AnalyticsSnapshot(
            id=501,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start,
            period_end=self.period_end,
            shipments_in_transit=12,
            shipments_delivered=8,
            shipments_failed=2,
        )

        with patch(
            "ech.analytics.services.analytic_shipping_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=snapshot,
        ), patch(
            "ech.analytics.services.analytic_shipping_overview_service."
            "AnalyticsLogService.log_shipping_metrics_calculated"
        ) as log_mock:
            result = AnalyticsShippingOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["source"], "snapshot")
        self.assertEqual(result["snapshot_id"], 501)
        self.assertEqual(result["in_transit_shipments"], 12)
        self.assertEqual(result["delivered_shipments"], 8)
        self.assertEqual(result["failed_shipments"], 2)
        self.assertAlmostEqual(result["delivered_rate"], 8 / 22)

        log_mock.assert_called_once_with(
            period_start=self.period_start,
            period_end=self.period_end,
            shipments_delivered=8,
            shipments_failed=2,
            shipments_in_transit=12,
            performed_by=None,
        )

    def test_get_overview_uses_realtime_when_snapshot_mismatch(self):
        mismatched_snapshot = AnalyticsSnapshot(
            id=502,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start - timedelta(days=1),
            period_end=self.period_end - timedelta(days=1),
        )

        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_shipping_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=mismatched_snapshot,
        ), patch(
            "ech.analytics.services.analytic_shipping_overview_service."
            "AnalyticsShippingOverviewService._build_overview_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_shipping_overview_service."
            "AnalyticsLogService.log_shipping_metrics_calculated"
        ):
            result = AnalyticsShippingOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["source"], "realtime")
        self.assertEqual(result["in_transit_shipments"], 12)
        self.assertEqual(result["delivered_shipments"], 8)
        self.assertEqual(result["failed_shipments"], 2)
        self.assertAlmostEqual(result["delivered_rate"], 0.4)
        self.assertAlmostEqual(result["failed_rate"], 0.1)

        realtime_mock.assert_called_once_with(
            period_start=self.period_start,
            period_end=self.period_end,
        )

    def test_get_overview_uses_cache(self):
        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_shipping_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_shipping_overview_service."
            "AnalyticsShippingOverviewService._build_overview_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_shipping_overview_service."
            "AnalyticsLogService.log_shipping_metrics_calculated"
        ):
            result_1 = AnalyticsShippingOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

            result_2 = AnalyticsShippingOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result_1, result_2)
        realtime_mock.assert_called_once()

    def test_get_overview_rebuilds_after_cache_clear(self):
        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_shipping_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_shipping_overview_service."
            "AnalyticsShippingOverviewService._build_overview_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_shipping_overview_service."
            "AnalyticsLogService.log_shipping_metrics_calculated"
        ):
            AnalyticsShippingOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

            cache.clear()

            AnalyticsShippingOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(realtime_mock.call_count, 2)

    def test_get_overview_handles_empty_metrics(self):
        empty_payload = {
            "source": "realtime",
            "snapshot_id": None,
            "period_type": None,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "in_transit_shipments": 0,
            "delivered_shipments": 0,
            "failed_shipments": 0,
            "delivered_rate": 0,
            "failed_rate": 0,
        }

        with patch(
            "ech.analytics.services.analytic_shipping_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_shipping_overview_service."
            "AnalyticsShippingOverviewService._build_overview_realtime",
            return_value=empty_payload,
        ), patch(
            "ech.analytics.services.analytic_shipping_overview_service."
            "AnalyticsLogService.log_shipping_metrics_calculated"
        ):
            result = AnalyticsShippingOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["in_transit_shipments"], 0)
        self.assertEqual(result["delivered_shipments"], 0)
        self.assertEqual(result["failed_shipments"], 0)
        self.assertEqual(result["delivered_rate"], 0)
        self.assertEqual(result["failed_rate"], 0)

    def test_get_overview_raises_when_cache_layer_fails(self):
        with patch(
            "ech.analytics.services.analytic_shipping_overview_service."
            "AnalyticsCacheService.get_or_set",
            side_effect=Exception("cache failure"),
        ):
            with self.assertRaises(AnalyticsShippingUnavailableException):
                AnalyticsShippingOverviewService.get_overview(
                    period_type=AnalyticsSnapshot.PERIOD_DAILY,
                    period_start=self.period_start,
                    period_end=self.period_end,
                )

    def test_resolve_period_bounds_raises_when_only_one_bound_is_provided(self):
        with self.assertRaises(AnalyticsShippingUnavailableException):
            AnalyticsShippingOverviewService._resolve_period_bounds(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=None,
            )

    def test_get_matching_snapshot_returns_none_when_selector_raises(self):
        with patch(
            "ech.analytics.services.analytic_shipping_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("not found"),
        ):
            result = AnalyticsShippingOverviewService._get_matching_snapshot(
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
            "ech.analytics.services.analytic_shipping_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=snapshot,
        ):
            result = AnalyticsShippingOverviewService._get_matching_snapshot(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertIsNone(result)

    def test_build_overview_from_snapshot_handles_zero_shipping_operations(self):
        snapshot = AnalyticsSnapshot(
            id=601,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start,
            period_end=self.period_end,
            shipments_in_transit=0,
            shipments_delivered=0,
            shipments_failed=0,
        )

        result = AnalyticsShippingOverviewService._build_overview_from_snapshot(
            snapshot=snapshot,
        )

        self.assertEqual(result["source"], "snapshot")
        self.assertEqual(result["in_transit_shipments"], 0)
        self.assertEqual(result["delivered_shipments"], 0)
        self.assertEqual(result["failed_shipments"], 0)
        self.assertEqual(result["delivered_rate"], 0)