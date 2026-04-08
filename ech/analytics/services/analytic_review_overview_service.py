from collections import defaultdict
from decimal import Decimal

from ech.analytics.constants.constants import (
    ANALYTIC_HIGH_RATING_THRESHOLD,
    ANALYTIC_LOW_RATING_THRESHOLD,
)
from ech.analytics.exceptions import (
    AnalyticsReviewUnavailableException,
)
from ech.analytics.selectors import (
    get_latest_analytics_snapshot_by_period_type,
    list_reviews_for_analytics,
)
from ech.analytics.services.analytic_log_service import (
    AnalyticsLogService,
)
from ech.analytics.services.cache_service import (
    AnalyticsCacheService,
)
from ech.analytics.utils.cache_keys import (
    review_overview_cache_key,
)
from ech.analytics.utils.date_ranges import (
    get_period_range,
)
from ech.reviews.models import Review


class AnalyticsReviewOverviewService:
    """
    Service responsible for review analytics overview data.
    """

    @classmethod
    def get_overview(
        cls,
        *,
        period_type,
        period_start=None,
        period_end=None,
        performed_by=None,
    ):
        """
        Retrieve review analytics overview for the requested period.
        """

        resolved_period_start, resolved_period_end = cls._resolve_period_bounds(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
        )

        review_version = AnalyticsCacheService.get_review_version()
        cache_key = review_overview_cache_key(
            period_start=resolved_period_start,
            period_end=resolved_period_end,
            review_version=review_version,
        )

        def producer():
            snapshot = cls._get_matching_snapshot(
                period_type=period_type,
                period_start=resolved_period_start,
                period_end=resolved_period_end,
            )

            reviews = list(
                list_reviews_for_analytics(
                    period_start=resolved_period_start,
                    period_end=resolved_period_end,
                )
            )

            if snapshot is not None:
                payload = cls._build_overview_from_snapshot(
                    snapshot=snapshot,
                    reviews=reviews,
                )
            else:
                payload = cls._build_overview_realtime(
                    period_start=resolved_period_start,
                    period_end=resolved_period_end,
                    reviews=reviews,
                )

            AnalyticsLogService.log_review_metrics_calculated(
                period_start=resolved_period_start,
                period_end=resolved_period_end,
                total_reviews=payload["total_reviews"],
                average_rating=payload["average_rating"],
                performed_by=performed_by,
            )

            return payload

        try:
            return AnalyticsCacheService.get_or_set(
                key=cache_key,
                producer=producer,
                timeout=None,
            )
        except Exception as exc:
            raise AnalyticsReviewUnavailableException() from exc

    @classmethod
    def _resolve_period_bounds(
        cls,
        *,
        period_type,
        period_start,
        period_end,
    ):
        if period_start is None and period_end is None:
            return get_period_range(period_type=period_type)

        if period_start is None or period_end is None:
            raise AnalyticsReviewUnavailableException()

        return period_start, period_end

    @classmethod
    def _get_matching_snapshot(
        cls,
        *,
        period_type,
        period_start,
        period_end,
    ):
        try:
            snapshot = get_latest_analytics_snapshot_by_period_type(
                period_type=period_type,
            )
        except Exception:
            return None

        if (
            snapshot.period_start == period_start
            and snapshot.period_end == period_end
        ):
            return snapshot

        return None

    @classmethod
    def _build_overview_from_snapshot(
        cls,
        *,
        snapshot,
        reviews,
    ):
        low_rated_products, high_rated_products = cls._build_rated_product_lists(
            reviews=reviews,
        )

        return {
            "source": "snapshot",
            "snapshot_id": snapshot.id,
            "period_type": snapshot.period_type,
            "period_start": snapshot.period_start,
            "period_end": snapshot.period_end,
            "total_reviews": snapshot.total_reviews,
            "approved_reviews": snapshot.approved_reviews,
            "rejected_reviews": snapshot.rejected_reviews,
            "hidden_reviews": snapshot.hidden_reviews,
            "cancelled_reviews": snapshot.cancelled_reviews,
            "verified_purchase_reviews": snapshot.verified_purchase_reviews,
            "average_rating": snapshot.average_rating,
            "low_rated_products_count": snapshot.low_rated_products_count,
            "high_rated_products_count": snapshot.high_rated_products_count,
            "low_rated_products": low_rated_products,
            "high_rated_products": high_rated_products,
        }

    @classmethod
    def _build_overview_realtime(
        cls,
        *,
        period_start,
        period_end,
        reviews,
    ):
        approved_reviews = [
            review for review in reviews
            if review.status == Review.REVIEW_STATUS_APPROVED
        ]

        total_reviews = len(reviews)
        approved_count = len(approved_reviews)

        rejected_count = sum(
            1 for review in reviews
            if review.status == Review.REVIEW_STATUS_REJECTED
        )

        hidden_count = sum(
            1 for review in reviews
            if review.status == Review.REVIEW_STATUS_HIDDEN
        )

        cancelled_count = sum(
            1 for review in reviews
            if review.status == Review.REVIEW_STATUS_CANCELLED
        )

        verified_purchase_reviews = sum(
            1 for review in reviews
            if review.is_verified_purchase
        )

        average_rating = Decimal("0.00")
        if approved_count > 0:
            average_rating = (
                sum(
                    Decimal(str(review.rating))
                    for review in approved_reviews
                ) / approved_count
            ).quantize(Decimal("0.01"))

        low_rated_products, high_rated_products = cls._build_rated_product_lists(
            reviews=reviews,
        )

        return {
            "source": "realtime",
            "snapshot_id": None,
            "period_type": None,
            "period_start": period_start,
            "period_end": period_end,
            "total_reviews": total_reviews,
            "approved_reviews": approved_count,
            "rejected_reviews": rejected_count,
            "hidden_reviews": hidden_count,
            "cancelled_reviews": cancelled_count,
            "verified_purchase_reviews": verified_purchase_reviews,
            "average_rating": average_rating,
            "low_rated_products_count": len(low_rated_products),
            "high_rated_products_count": len(high_rated_products),
            "low_rated_products": low_rated_products,
            "high_rated_products": high_rated_products,
        }

    @classmethod
    def _build_rated_product_lists(cls, *, reviews):
        approved_reviews = [
            review for review in reviews
            if review.status == Review.REVIEW_STATUS_APPROVED
        ]

        product_rating_map = defaultdict(list)

        for review in approved_reviews:
            product_rating_map[review.product_id].append(review.rating)

        low_rated_products = []
        high_rated_products = []

        for product_id, ratings in product_rating_map.items():
            average_rating = sum(ratings) / len(ratings)

            payload = {
                "product_id": product_id,
                "average_rating": round(average_rating, 2),
                "total_reviews": len(ratings),
            }

            if average_rating <= ANALYTIC_LOW_RATING_THRESHOLD:
                low_rated_products.append(payload)

            if average_rating >= ANALYTIC_HIGH_RATING_THRESHOLD:
                high_rated_products.append(payload)

        low_rated_products.sort(
            key=lambda item: (item["average_rating"], -item["total_reviews"])
        )
        high_rated_products.sort(
            key=lambda item: (-item["average_rating"], -item["total_reviews"])
        )

        return low_rated_products, high_rated_products