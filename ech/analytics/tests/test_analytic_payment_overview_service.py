from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from ech.analytics.exceptions import AnalyticsPaymentUnavailableException
from ech.analytics.models import AnalyticsSnapshot
from ech.analytics.services.analytic_payment_overview_service import (
    AnalyticsPaymentOverviewService,
)


class AnalyticsPaymentOverviewServiceTestCase(TestCase):
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
            "captured_payments": 15,
            "failed_payments": 3,
            "refunded_payments": 2,
            "total_refunded_amount": Decimal("120.00"),
            "net_revenue": Decimal("880.00"),
            "capture_rate": 0.75,
            "failure_rate": 0.15,
            "refund_rate": 0.10,
        }

    def test_get_overview_returns_snapshot_data_when_available(self):
        snapshot = AnalyticsSnapshot(
            id=401,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start,
            period_end=self.period_end,
            payments_captured=15,
            payments_failed=3,
            payments_refunded=2,
            total_refunds=Decimal("120.00"),
            net_revenue=Decimal("880.00"),
        )

        with patch(
            "ech.analytics.services.analytic_payment_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=snapshot,
        ), patch(
            "ech.analytics.services.analytic_payment_overview_service."
            "AnalyticsLogService.log_payment_metrics_calculated"
        ) as log_mock:
            result = AnalyticsPaymentOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["source"], "snapshot")
        self.assertEqual(result["snapshot_id"], 401)
        self.assertEqual(result["captured_payments"], 15)
        self.assertEqual(result["failed_payments"], 3)
        self.assertEqual(result["refunded_payments"], 2)
        self.assertEqual(result["total_refunded_amount"], Decimal("120.00"))
        self.assertEqual(result["net_revenue"], Decimal("880.00"))
        self.assertAlmostEqual(result["capture_rate"], 0.75)
        self.assertAlmostEqual(result["failure_rate"], 0.15)
        self.assertAlmostEqual(result["refund_rate"], 0.10)

        log_mock.assert_called_once_with(
            period_start=self.period_start,
            period_end=self.period_end,
            captured_payments=15,
            failed_payments=3,
            refunded_payments=2,
            performed_by=None,
        )

    def test_get_overview_uses_realtime_when_snapshot_mismatch(self):
        mismatched_snapshot = AnalyticsSnapshot(
            id=402,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start - timedelta(days=1),
            period_end=self.period_end - timedelta(days=1),
        )

        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_payment_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=mismatched_snapshot,
        ), patch(
            "ech.analytics.services.analytic_payment_overview_service."
            "AnalyticsPaymentOverviewService._build_overview_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_payment_overview_service."
            "AnalyticsLogService.log_payment_metrics_calculated"
        ):
            result = AnalyticsPaymentOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["source"], "realtime")
        self.assertEqual(result["captured_payments"], 15)
        self.assertEqual(result["failed_payments"], 3)
        self.assertEqual(result["refunded_payments"], 2)
        self.assertEqual(result["total_refunded_amount"], Decimal("120.00"))
        self.assertEqual(result["net_revenue"], Decimal("880.00"))
        self.assertAlmostEqual(result["capture_rate"], 0.75)
        self.assertAlmostEqual(result["failure_rate"], 0.15)
        self.assertAlmostEqual(result["refund_rate"], 0.10)

        realtime_mock.assert_called_once_with(
            period_start=self.period_start,
            period_end=self.period_end,
        )

    def test_get_overview_uses_cache(self):
        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_payment_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_payment_overview_service."
            "AnalyticsPaymentOverviewService._build_overview_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_payment_overview_service."
            "AnalyticsLogService.log_payment_metrics_calculated"
        ) as log_mock:
            result_1 = AnalyticsPaymentOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

            result_2 = AnalyticsPaymentOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result_1, result_2)
        realtime_mock.assert_called_once()
        log_mock.assert_called_once()

    def test_get_overview_rebuilds_after_cache_clear(self):
        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_payment_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_payment_overview_service."
            "AnalyticsPaymentOverviewService._build_overview_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_payment_overview_service."
            "AnalyticsLogService.log_payment_metrics_calculated"
        ):
            AnalyticsPaymentOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

            cache.clear()

            AnalyticsPaymentOverviewService.get_overview(
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
            "captured_payments": 0,
            "failed_payments": 0,
            "refunded_payments": 0,
            "total_refunded_amount": Decimal("0.00"),
            "net_revenue": Decimal("0.00"),
            "capture_rate": 0,
            "failure_rate": 0,
            "refund_rate": 0,
        }

        with patch(
            "ech.analytics.services.analytic_payment_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_payment_overview_service."
            "AnalyticsPaymentOverviewService._build_overview_realtime",
            return_value=empty_payload,
        ), patch(
            "ech.analytics.services.analytic_payment_overview_service."
            "AnalyticsLogService.log_payment_metrics_calculated"
        ):
            result = AnalyticsPaymentOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["captured_payments"], 0)
        self.assertEqual(result["failed_payments"], 0)
        self.assertEqual(result["refunded_payments"], 0)
        self.assertEqual(result["total_refunded_amount"], Decimal("0.00"))
        self.assertEqual(result["net_revenue"], Decimal("0.00"))
        self.assertEqual(result["capture_rate"], 0)
        self.assertEqual(result["failure_rate"], 0)
        self.assertEqual(result["refund_rate"], 0)

    def test_get_overview_raises_when_cache_layer_fails(self):
        with patch(
            "ech.analytics.services.analytic_payment_overview_service."
            "AnalyticsCacheService.get_or_set",
            side_effect=Exception("cache failure"),
        ):
            with self.assertRaises(AnalyticsPaymentUnavailableException):
                AnalyticsPaymentOverviewService.get_overview(
                    period_type=AnalyticsSnapshot.PERIOD_DAILY,
                    period_start=self.period_start,
                    period_end=self.period_end,
                )

    def test_resolve_period_bounds_raises_when_only_one_bound_is_provided(self):
        with self.assertRaises(AnalyticsPaymentUnavailableException):
            AnalyticsPaymentOverviewService._resolve_period_bounds(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=None,
            )

    def test_get_matching_snapshot_returns_none_when_selector_raises(self):
        with patch(
            "ech.analytics.services.analytic_payment_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("not found"),
        ):
            result = AnalyticsPaymentOverviewService._get_matching_snapshot(
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
            "ech.analytics.services.analytic_payment_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=snapshot,
        ):
            result = AnalyticsPaymentOverviewService._get_matching_snapshot(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertIsNone(result)

    def test_build_overview_from_snapshot_handles_zero_payment_operations(self):
        snapshot = AnalyticsSnapshot(
            id=501,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start,
            period_end=self.period_end,
            payments_captured=0,
            payments_failed=0,
            payments_refunded=0,
            total_refunds=Decimal("0.00"),
            net_revenue=Decimal("0.00"),
        )

        result = AnalyticsPaymentOverviewService._build_overview_from_snapshot(
            snapshot=snapshot,
        )

        self.assertEqual(result["source"], "snapshot")
        self.assertEqual(result["captured_payments"], 0)
        self.assertEqual(result["failed_payments"], 0)
        self.assertEqual(result["refunded_payments"], 0)
        self.assertEqual(result["total_refunded_amount"], Decimal("0.00"))
        self.assertEqual(result["net_revenue"], Decimal("0.00"))
        self.assertEqual(result["capture_rate"], 0)
        self.assertEqual(result["failure_rate"], 0)
        self.assertEqual(result["refund_rate"], 0)