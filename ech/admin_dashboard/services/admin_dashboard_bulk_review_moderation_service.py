from django.db import transaction

from ech.admin_dashboard.exceptions import (
    AdminDashboardReviewBulkModerationException,
)

from ech.admin_dashboard.services.admin_dashboard_log_service import (
    AdminDashboardLogService,
)

from ech.admin_dashboard.services.cache_service import (
    AdminDashboardCacheService,
)

from ech.reviews.models import Review
from ech.reviews.services.review_moderation_service import (
    ReviewsModerationService,
)


class AdminDashboardBulkReviewModerationService:
    """
    Service responsible for executing bulk review moderation
    operations from the admin dashboard.
    """

    ALLOWED_ACTIONS = {
        "approve",
        "reject",
        "hide",
        "restore",
    }

    @classmethod
    def execute_bulk_moderation(
        cls,
        *,
        moderation_action,
        review_ids,
        performed_by=None,
        reason="",
    ):
        """
        Execute a bulk review moderation action.
        """

        if moderation_action not in cls.ALLOWED_ACTIONS:
            raise AdminDashboardReviewBulkModerationException(
                f"Invalid moderation action: {moderation_action}"
            )

        if not review_ids:
            raise AdminDashboardReviewBulkModerationException(
                "Review ID list cannot be empty."
            )

        try:
            with transaction.atomic():
                reviews = list(
                    Review.objects.select_for_update().filter(
                        id__in=review_ids,
                    )
                )

                if not reviews:
                    raise AdminDashboardReviewBulkModerationException(
                        "No valid reviews found for bulk moderation."
                    )

                processed_review_ids = []

                for review in reviews:
                    ReviewsModerationService.moderate_review(
                        review=review,
                        action=moderation_action,
                        performed_by=performed_by,
                        reason=reason,
                    )
                    processed_review_ids.append(review.id)

                AdminDashboardLogService.log_bulk_review_moderation(
                    moderation_action=moderation_action,
                    review_ids=processed_review_ids,
                    performed_by=performed_by,
                )

                AdminDashboardCacheService.invalidate_dashboard_cache()
                AdminDashboardCacheService.invalidate_operational_metrics_cache()
                AdminDashboardCacheService.invalidate_activity_feed_cache()
                AdminDashboardCacheService.invalidate_alerts_cache()

                return {
                    "moderation_action": moderation_action,
                    "processed_reviews": processed_review_ids,
                    "total_processed": len(processed_review_ids),
                }

        except Exception as exc:
            raise AdminDashboardReviewBulkModerationException() from exc