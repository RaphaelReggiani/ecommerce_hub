import uuid
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import patch, call

from django.test import SimpleTestCase

from ech.admin_dashboard.exceptions import (
    AdminDashboardReviewBulkModerationException,
)
from ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service import (
    AdminDashboardBulkReviewModerationService,
)


class AdminDashboardBulkReviewModerationServiceTestCase(SimpleTestCase):
    def _build_review(self, review_id=None):
        """Build a lightweight review-like object for service tests."""
        return SimpleNamespace(id=review_id or uuid.uuid4())

    def _build_user(self, user_id=None):
        """Build a lightweight user-like object for service tests."""
        return SimpleNamespace(id=user_id or 99)

    def test_execute_bulk_moderation_raises_for_invalid_action(self):
        """Raise exception when moderation action is not allowed."""
        with self.assertRaises(AdminDashboardReviewBulkModerationException) as context:
            AdminDashboardBulkReviewModerationService.execute_bulk_moderation(
                moderation_action="invalid_action",
                review_ids=[uuid.uuid4()],
                performed_by=None,
                reason="test",
            )

        self.assertEqual(
            str(context.exception),
            "Invalid moderation action: invalid_action",
        )

    def test_execute_bulk_moderation_raises_for_empty_review_ids(self):
        """Raise exception when review id list is empty."""
        with self.assertRaises(AdminDashboardReviewBulkModerationException) as context:
            AdminDashboardBulkReviewModerationService.execute_bulk_moderation(
                moderation_action="approve",
                review_ids=[],
                performed_by=None,
                reason="test",
            )

        self.assertEqual(
            str(context.exception),
            "Review ID list cannot be empty.",
        )

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.transaction.atomic",
        return_value=nullcontext(),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.Review.objects"
    )
    def test_execute_bulk_moderation_raises_when_no_valid_reviews_are_found(
        self,
        review_objects_mock,
        atomic_mock,
    ):
        """Raise wrapped bulk moderation exception when no matching reviews are found."""
        review_objects_mock.select_for_update.return_value.filter.return_value = []

        with self.assertRaises(AdminDashboardReviewBulkModerationException) as context:
            AdminDashboardBulkReviewModerationService.execute_bulk_moderation(
                moderation_action="approve",
                review_ids=[uuid.uuid4()],
                performed_by=None,
                reason="test reason",
            )

        self.assertEqual(
            str(context.exception),
            "Bulk review moderation failed.",
        )

        review_objects_mock.select_for_update.assert_called_once_with()
        review_objects_mock.select_for_update.return_value.filter.assert_called_once()

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.transaction.atomic",
        return_value=nullcontext(),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.AdminDashboardCacheService.invalidate_alerts_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.AdminDashboardCacheService.invalidate_activity_feed_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.AdminDashboardCacheService.invalidate_operational_metrics_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.AdminDashboardCacheService.invalidate_dashboard_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.AdminDashboardLogService.log_bulk_review_moderation"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.ReviewsModerationService.moderate_review"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.Review.objects"
    )
    def test_execute_bulk_moderation_processes_reviews_successfully(
        self,
        review_objects_mock,
        moderate_review_mock,
        log_mock,
        invalidate_dashboard_mock,
        invalidate_operational_mock,
        invalidate_activity_mock,
        invalidate_alerts_mock,
        atomic_mock,
    ):
        """Moderate all returned reviews successfully and invalidate related caches."""
        performed_by = self._build_user(user_id=10)
        review_1 = self._build_review()
        review_2 = self._build_review()
        review_ids = [review_1.id, review_2.id]

        review_objects_mock.select_for_update.return_value.filter.return_value = [
            review_1,
            review_2,
        ]

        result = AdminDashboardBulkReviewModerationService.execute_bulk_moderation(
            moderation_action="approve",
            review_ids=review_ids,
            performed_by=performed_by,
            reason="approved in bulk",
        )

        self.assertEqual(
            result,
            {
                "moderation_action": "approve",
                "processed_reviews": [review_1.id, review_2.id],
                "total_processed": 2,
            },
        )

        review_objects_mock.select_for_update.assert_called_once_with()
        review_objects_mock.select_for_update.return_value.filter.assert_called_once_with(
            id__in=review_ids,
        )

        moderate_review_mock.assert_has_calls(
            [
                call(
                    review=review_1,
                    action="approve",
                    performed_by=performed_by,
                    reason="approved in bulk",
                ),
                call(
                    review=review_2,
                    action="approve",
                    performed_by=performed_by,
                    reason="approved in bulk",
                ),
            ]
        )
        self.assertEqual(moderate_review_mock.call_count, 2)

        log_mock.assert_called_once_with(
            moderation_action="approve",
            review_ids=[review_1.id, review_2.id],
            performed_by=performed_by,
        )

        invalidate_dashboard_mock.assert_called_once_with()
        invalidate_operational_mock.assert_called_once_with()
        invalidate_activity_mock.assert_called_once_with()
        invalidate_alerts_mock.assert_called_once_with()

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.transaction.atomic",
        return_value=nullcontext(),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.AdminDashboardLogService.log_bulk_review_moderation"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.ReviewsModerationService.moderate_review"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.Review.objects"
    )
    def test_execute_bulk_moderation_passes_empty_reason_to_moderation_service(
        self,
        review_objects_mock,
        moderate_review_mock,
        log_mock,
        atomic_mock,
    ):
        """Pass an empty reason through to the moderation service when omitted."""
        review = self._build_review()

        review_objects_mock.select_for_update.return_value.filter.return_value = [
            review,
        ]

        result = AdminDashboardBulkReviewModerationService.execute_bulk_moderation(
            moderation_action="hide",
            review_ids=[review.id],
            performed_by=None,
            reason="",
        )

        self.assertEqual(
            result,
            {
                "moderation_action": "hide",
                "processed_reviews": [review.id],
                "total_processed": 1,
            },
        )

        moderate_review_mock.assert_called_once_with(
            review=review,
            action="hide",
            performed_by=None,
            reason="",
        )
        log_mock.assert_called_once_with(
            moderation_action="hide",
            review_ids=[review.id],
            performed_by=None,
        )

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.transaction.atomic",
        return_value=nullcontext(),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.ReviewsModerationService.moderate_review",
        side_effect=Exception("moderation failure"),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.Review.objects"
    )
    def test_execute_bulk_moderation_wraps_moderation_errors(
        self,
        review_objects_mock,
        moderate_review_mock,
        atomic_mock,
    ):
        """Wrap internal moderation errors with the default bulk moderation exception."""
        review = self._build_review()

        review_objects_mock.select_for_update.return_value.filter.return_value = [
            review,
        ]

        with self.assertRaises(AdminDashboardReviewBulkModerationException) as context:
            AdminDashboardBulkReviewModerationService.execute_bulk_moderation(
                moderation_action="reject",
                review_ids=[review.id],
                performed_by=None,
                reason="policy violation",
            )

        self.assertEqual(
            str(context.exception),
            "Bulk review moderation failed.",
        )
        moderate_review_mock.assert_called_once_with(
            review=review,
            action="reject",
            performed_by=None,
            reason="policy violation",
        )

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.transaction.atomic",
        return_value=nullcontext(),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.AdminDashboardCacheService.invalidate_alerts_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.AdminDashboardCacheService.invalidate_activity_feed_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.AdminDashboardCacheService.invalidate_operational_metrics_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.AdminDashboardCacheService.invalidate_dashboard_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.AdminDashboardLogService.log_bulk_review_moderation",
        side_effect=Exception("log failure"),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.ReviewsModerationService.moderate_review"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service.Review.objects"
    )
    def test_execute_bulk_moderation_wraps_log_errors(
        self,
        review_objects_mock,
        moderate_review_mock,
        log_mock,
        invalidate_dashboard_mock,
        invalidate_operational_mock,
        invalidate_activity_mock,
        invalidate_alerts_mock,
        atomic_mock,
    ):
        """Wrap logging failures with the default bulk moderation exception."""
        review = self._build_review()

        review_objects_mock.select_for_update.return_value.filter.return_value = [
            review,
        ]

        with self.assertRaises(AdminDashboardReviewBulkModerationException) as context:
            AdminDashboardBulkReviewModerationService.execute_bulk_moderation(
                moderation_action="restore",
                review_ids=[review.id],
                performed_by=None,
                reason="restore in bulk",
            )

        self.assertEqual(
            str(context.exception),
            "Bulk review moderation failed.",
        )

        moderate_review_mock.assert_called_once_with(
            review=review,
            action="restore",
            performed_by=None,
            reason="restore in bulk",
        )

        invalidate_dashboard_mock.assert_not_called()
        invalidate_operational_mock.assert_not_called()
        invalidate_activity_mock.assert_not_called()
        invalidate_alerts_mock.assert_not_called()