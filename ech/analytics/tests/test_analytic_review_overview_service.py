from datetime import timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from ech.analytics.exceptions import AnalyticsReviewUnavailableException
from ech.analytics.models import AnalyticsSnapshot
from ech.analytics.services.analytic_review_overview_service import (
    AnalyticsReviewOverviewService,
)


class AnalyticsReviewOverviewServiceTestCase(TestCase):

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
            "total_reviews": 50,
            "average_rating": 4.2,
            "approved_reviews": 40,
            "pending_reviews": 7,
            "rejected_reviews": 3,
        }

    def test_get_overview_returns_snapshot_data_when_available(self):
        """Ensure review overview returns snapshot metrics when a matching snapshot exists for the requested period."""
        snapshot = AnalyticsSnapshot(
            id=501,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start,
            period_end=self.period_end,
        )
        snapshot.total_reviews = 50
        snapshot.average_rating = 4.2
        snapshot.approved_reviews = 40
        snapshot.rejected_reviews = 3

        with patch(
            "ech.analytics.services.analytic_review_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=snapshot,
        ), patch(
            "ech.analytics.services.analytic_review_overview_service."
            "AnalyticsLogService.log_review_metrics_calculated"
        ) as log_mock:

            result = AnalyticsReviewOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["source"], "snapshot")
        self.assertEqual(result["snapshot_id"], 501)

        self.assertEqual(result["total_reviews"], 50)
        self.assertEqual(result["average_rating"], 4.2)
        self.assertEqual(result["approved_reviews"], 40)
        self.assertEqual(result["rejected_reviews"], 3)

        log_mock.assert_called_once()

    def test_get_overview_uses_realtime_when_snapshot_mismatch(self):
        """Ensure review overview falls back to realtime metrics when the available snapshot does not match the requested period."""
        mismatched_snapshot = AnalyticsSnapshot(
            id=502,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start - timedelta(days=1),
            period_end=self.period_end - timedelta(days=1),
        )

        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_review_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            return_value=mismatched_snapshot,
        ), patch(
            "ech.analytics.services.analytic_review_overview_service."
            "AnalyticsReviewOverviewService._build_overview_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_review_overview_service."
            "AnalyticsLogService.log_review_metrics_calculated"
        ):

            result = AnalyticsReviewOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["source"], "realtime")
        self.assertEqual(result["total_reviews"], 50)
        self.assertEqual(result["average_rating"], 4.2)
        self.assertEqual(result["approved_reviews"], 40)
        self.assertEqual(result["pending_reviews"], 7)
        self.assertEqual(result["rejected_reviews"], 3)

        realtime_mock.assert_called_once()

    def test_get_overview_uses_cache(self):
        """Ensure review overview reuses cached realtime metrics on repeated requests for the same period."""
        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_review_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_review_overview_service."
            "AnalyticsReviewOverviewService._build_overview_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_review_overview_service."
            "AnalyticsLogService.log_review_metrics_calculated"
        ):

            result_1 = AnalyticsReviewOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

            result_2 = AnalyticsReviewOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result_1, result_2)
        realtime_mock.assert_called_once()

    def test_get_overview_rebuilds_after_cache_clear(self):
        """Ensure review overview rebuilds realtime metrics after the cache is cleared."""
        realtime_payload = self._build_realtime_payload()

        with patch(
            "ech.analytics.services.analytic_review_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_review_overview_service."
            "AnalyticsReviewOverviewService._build_overview_realtime",
            return_value=realtime_payload,
        ) as realtime_mock, patch(
            "ech.analytics.services.analytic_review_overview_service."
            "AnalyticsLogService.log_review_metrics_calculated"
        ):

            AnalyticsReviewOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

            cache.clear()

            AnalyticsReviewOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(realtime_mock.call_count, 2)

    def test_get_overview_handles_empty_metrics(self):
        """Ensure review overview correctly handles periods with zero review metrics."""
        empty_payload = {
            "source": "realtime",
            "snapshot_id": None,
            "period_type": None,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "total_reviews": 0,
            "average_rating": 0,
            "approved_reviews": 0,
            "pending_reviews": 0,
            "rejected_reviews": 0,
        }

        with patch(
            "ech.analytics.services.analytic_review_overview_service."
            "get_latest_analytics_snapshot_by_period_type",
            side_effect=Exception("no snapshot"),
        ), patch(
            "ech.analytics.services.analytic_review_overview_service."
            "AnalyticsReviewOverviewService._build_overview_realtime",
            return_value=empty_payload,
        ), patch(
            "ech.analytics.services.analytic_review_overview_service."
            "AnalyticsLogService.log_review_metrics_calculated"
        ):

            result = AnalyticsReviewOverviewService.get_overview(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(result["total_reviews"], 0)
        self.assertEqual(result["average_rating"], 0)
        self.assertEqual(result["approved_reviews"], 0)
        self.assertEqual(result["pending_reviews"], 0)
        self.assertEqual(result["rejected_reviews"], 0)

    def test_get_overview_raises_when_cache_layer_fails(self):
        """Ensure review overview raises an unavailable exception when the cache layer fails."""
        with patch(
            "ech.analytics.services.analytic_review_overview_service."
            "AnalyticsCacheService.get_or_set",
            side_effect=Exception("cache failure"),
        ):

            with self.assertRaises(AnalyticsReviewUnavailableException):
                AnalyticsReviewOverviewService.get_overview(
                    period_type=AnalyticsSnapshot.PERIOD_DAILY,
                    period_start=self.period_start,
                    period_end=self.period_end,
                )

    def test_resolve_period_bounds_raises_when_only_one_bound_is_provided(self):
        """Ensure period bound resolution fails when only one review overview bound is provided."""
        with self.assertRaises(AnalyticsReviewUnavailableException):
            AnalyticsReviewOverviewService._resolve_period_bounds(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=None,
            )