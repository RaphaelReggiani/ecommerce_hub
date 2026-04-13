from datetime import timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from ech.analytics.exceptions import AnalyticsCustomerUnavailableException
from ech.analytics.models import AnalyticsSnapshot
from ech.analytics.services.analytic_customer_summary_service import (
    AnalyticsCustomerSummaryService,
)


class AnalyticsCustomerSummaryServiceTestCase(TestCase):
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
            "active_customers": 17,
            "new_customers": 12,
            "customer_growth": 4,
            "repeat_customer_rate": 5 / 17,
        }

    def test_get_summary_returns_snapshot_data_when_available(self):
        """Ensure customer summary returns snapshot metrics when a matching snapshot exists for the requested period."""
        snapshot = AnalyticsSnapshot(
            id=801,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start,
            period_end=self.period_end,
            active_customers=17,
            new_customers=12,
        )
        previous_snapshot = AnalyticsSnapshot(
            id=800,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start - timedelta(days=1),
            period_end=self.period_end - timedelta(days=1),
            active_customers=10,
            new_customers=8,
        )

        with patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=snapshot,
        ), patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "AnalyticsCustomerSummaryService._get_previous_matching_snapshot",
            return_value=previous_snapshot,
        ), patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "AnalyticsLogService.log_customer_metrics_calculated"
        ) as log_mock:
            result = AnalyticsCustomerSummaryService.get_summary(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["source"], "snapshot")
        self.assertEqual(result["snapshot_id"], 801)
        self.assertEqual(result["active_customers"], 17)
        self.assertEqual(result["new_customers"], 12)
        self.assertEqual(result["customer_growth"], 4)
        self.assertAlmostEqual(result["repeat_customer_rate"], 5 / 17)

        log_mock.assert_called_once_with(
            period_start=self.period_start,
            period_end=self.period_end,
            active_customers=17,
            new_customers=12,
            performed_by=None,
        )

    def test_get_summary_uses_realtime_when_snapshot_mismatch(self):
        """Ensure customer summary falls back to realtime metrics when the available snapshot does not match the requested period."""
        mismatched_snapshot = AnalyticsSnapshot(
            id=802,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start - timedelta(days=1),
            period_end=self.period_end - timedelta(days=1),
        )

        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=mismatched_snapshot,
        ), patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "AnalyticsCustomerSummaryService._build_summary_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "AnalyticsLogService.log_customer_metrics_calculated"
        ):
            result = AnalyticsCustomerSummaryService.get_summary(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["source"], "realtime")
        self.assertEqual(result["active_customers"], 17)
        self.assertEqual(result["new_customers"], 12)
        self.assertEqual(result["customer_growth"], 4)
        self.assertAlmostEqual(result["repeat_customer_rate"], 5 / 17)

        realtime_mock.assert_called_once_with(
            period_start=self.period_start,
            period_end=self.period_end,
        )

    def test_get_summary_uses_cache(self):
        """Ensure customer summary reuses cached realtime metrics for repeated requests within the same period."""
        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "AnalyticsCustomerSummaryService._build_summary_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "AnalyticsLogService.log_customer_metrics_calculated"
        ):
            result_1 = AnalyticsCustomerSummaryService.get_summary(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

            result_2 = AnalyticsCustomerSummaryService.get_summary(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result_1, result_2)
        realtime_mock.assert_called_once()

    def test_get_summary_rebuilds_after_cache_clear(self):
        """Ensure customer summary rebuilds realtime metrics after the cache is cleared."""
        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "AnalyticsCustomerSummaryService._build_summary_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "AnalyticsLogService.log_customer_metrics_calculated"
        ):
            AnalyticsCustomerSummaryService.get_summary(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

            cache.clear()

            AnalyticsCustomerSummaryService.get_summary(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(realtime_mock.call_count, 2)

    def test_get_summary_handles_empty_metrics(self):
        """Ensure customer summary correctly handles periods with zero customers and zero derived metrics."""
        empty_payload = {
            "source": "realtime",
            "snapshot_id": None,
            "period_type": None,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "active_customers": 0,
            "new_customers": 0,
            "customer_growth": 0,
            "repeat_customer_rate": 0,
        }

        with patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "AnalyticsCustomerSummaryService._build_summary_realtime",
            return_value=empty_payload,
        ), patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "AnalyticsLogService.log_customer_metrics_calculated"
        ):
            result = AnalyticsCustomerSummaryService.get_summary(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["active_customers"], 0)
        self.assertEqual(result["new_customers"], 0)
        self.assertEqual(result["customer_growth"], 0)
        self.assertEqual(result["repeat_customer_rate"], 0)

    def test_get_summary_raises_when_cache_layer_fails(self):
        """Ensure customer summary raises an unavailable exception when the cache layer fails."""
        with patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "AnalyticsCacheService.get_or_set",
            side_effect=Exception("cache failure"),
        ):
            with self.assertRaises(AnalyticsCustomerUnavailableException):
                AnalyticsCustomerSummaryService.get_summary(
                    period_type=AnalyticsSnapshot.PERIOD_DAILY,
                    period_start=self.period_start,
                    period_end=self.period_end,
                )

    def test_resolve_period_bounds_raises_when_only_one_bound_is_provided(self):
        """Ensure period bound resolution fails when only one customer summary bound is provided."""
        with self.assertRaises(AnalyticsCustomerUnavailableException):
            AnalyticsCustomerSummaryService._resolve_period_bounds(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=None,
            )

    def test_get_matching_snapshot_returns_none_when_selector_raises(self):
        """Ensure matching snapshot lookup returns None when the snapshot selector raises an exception."""
        with patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("not found"),
        ):
            result = AnalyticsCustomerSummaryService._get_matching_snapshot(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertIsNone(result)

    def test_get_matching_snapshot_returns_none_when_bounds_do_not_match(self):
        """Ensure matching snapshot lookup returns None when snapshot bounds do not match the requested customer summary period."""
        snapshot = AnalyticsSnapshot(
            id=777,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start - timedelta(days=2),
            period_end=self.period_end - timedelta(days=2),
        )

        with patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=snapshot,
        ):
            result = AnalyticsCustomerSummaryService._get_matching_snapshot(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertIsNone(result)

    def test_build_summary_from_snapshot_handles_no_previous_snapshot(self):
        """Ensure snapshot-based customer summary computes growth and repeat rate correctly when no previous snapshot exists."""
        snapshot = AnalyticsSnapshot(
            id=901,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start,
            period_end=self.period_end,
            active_customers=0,
            new_customers=0,
        )

        with patch(
            "ech.analytics.services.analytic_customer_summary_service."
            "AnalyticsCustomerSummaryService._get_previous_matching_snapshot",
            return_value=None,
        ):
            result = AnalyticsCustomerSummaryService._build_summary_from_snapshot(
                snapshot=snapshot,
            )

        self.assertEqual(result["source"], "snapshot")
        self.assertEqual(result["snapshot_id"], 901)
        self.assertEqual(result["active_customers"], 0)
        self.assertEqual(result["new_customers"], 0)
        self.assertEqual(result["customer_growth"], 0)
        self.assertEqual(result["repeat_customer_rate"], 0)