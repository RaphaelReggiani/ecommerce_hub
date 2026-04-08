from ech.analytics.exceptions import (
    AnalyticsCustomerUnavailableException,
)
from ech.analytics.selectors import (
    get_latest_analytics_snapshot_by_period_type,
    list_customers_for_analytics,
    list_orders_for_analytics,
)
from ech.analytics.services.analytic_log_service import (
    AnalyticsLogService,
)
from ech.analytics.services.cache_service import (
    AnalyticsCacheService,
)
from ech.analytics.utils.cache_keys import (
    customer_summary_cache_key,
)
from ech.analytics.utils.date_ranges import (
    get_period_range,
    get_previous_period_range,
)


class AnalyticsCustomerSummaryService:
    """
    Service responsible for customer analytics summary data.
    """

    @classmethod
    def get_summary(
        cls,
        *,
        period_type,
        period_start=None,
        period_end=None,
        performed_by=None,
    ):
        """
        Retrieve customer analytics summary for the requested period.

        Snapshot data is preferred when the latest snapshot matches the
        requested bounds. Otherwise, metrics are calculated in real time.
        """

        resolved_period_start, resolved_period_end = cls._resolve_period_bounds(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
        )

        customer_version = AnalyticsCacheService.get_customer_version()

        cache_key = customer_summary_cache_key(
            period_start=resolved_period_start,
            period_end=resolved_period_end,
            customer_version=customer_version,
        )

        def producer():
            snapshot = cls._get_matching_snapshot(
                period_type=period_type,
                period_start=resolved_period_start,
                period_end=resolved_period_end,
            )

            if snapshot is not None:
                payload = cls._build_summary_from_snapshot(snapshot=snapshot)
            else:
                payload = cls._build_summary_realtime(
                    period_start=resolved_period_start,
                    period_end=resolved_period_end,
                )

            AnalyticsLogService.log_customer_metrics_calculated(
                period_start=resolved_period_start,
                period_end=resolved_period_end,
                active_customers=payload["active_customers"],
                new_customers=payload["new_customers"],
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
            raise AnalyticsCustomerUnavailableException() from exc

    @classmethod
    def _resolve_period_bounds(
        cls,
        *,
        period_type,
        period_start,
        period_end,
    ):
        """
        Resolve customer summary period bounds.
        """

        if period_start is None and period_end is None:
            return get_period_range(period_type=period_type)

        if period_start is None or period_end is None:
            raise AnalyticsCustomerUnavailableException()

        return period_start, period_end

    @classmethod
    def _get_matching_snapshot(
        cls,
        *,
        period_type,
        period_start,
        period_end,
    ):
        """
        Return latest snapshot only if bounds match.
        """

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
    def _build_summary_from_snapshot(cls, *, snapshot):
        """
        Build customer summary payload from snapshot.
        """

        previous_snapshot = cls._get_previous_matching_snapshot(snapshot=snapshot)

        customer_growth = 0

        if previous_snapshot is not None:
            customer_growth = (
                snapshot.new_customers - previous_snapshot.new_customers
            )

        repeat_customer_rate = 0

        if snapshot.active_customers > 0:
            repeat_customer_rate = (
                (snapshot.active_customers - snapshot.new_customers)
                / snapshot.active_customers
            )

        return {
            "source": "snapshot",
            "snapshot_id": snapshot.id,
            "period_type": snapshot.period_type,
            "period_start": snapshot.period_start,
            "period_end": snapshot.period_end,
            "active_customers": snapshot.active_customers,
            "new_customers": snapshot.new_customers,
            "customer_growth": customer_growth,
            "repeat_customer_rate": repeat_customer_rate,
        }

    @classmethod
    def _get_previous_matching_snapshot(cls, *, snapshot):
        """
        Retrieve a previous snapshot matching the immediately previous period.
        """

        previous_start, previous_end = get_previous_period_range(
            period_start=snapshot.period_start,
            period_end=snapshot.period_end,
        )

        try:
            candidate = get_latest_analytics_snapshot_by_period_type(
                period_type=snapshot.period_type,
            )
        except Exception:
            return None

        if (
            candidate.period_start == previous_start
            and candidate.period_end == previous_end
        ):
            return candidate

        return None

    @classmethod
    def _build_summary_realtime(
        cls,
        *,
        period_start,
        period_end,
    ):
        """
        Build customer summary in real time from customers and orders.
        """

        orders = list(
            list_orders_for_analytics(
                period_start=period_start,
                period_end=period_end,
            )
        )

        new_customers = list(
            list_customers_for_analytics(
                period_start=period_start,
                period_end=period_end,
            )
        )

        active_customer_ids = {order.customer_id for order in orders}
        active_customers = len(active_customer_ids)
        new_customer_count = len(new_customers)

        repeat_customer_rate = 0
        if active_customers > 0:
            repeat_customer_rate = (
                (active_customers - new_customer_count) / active_customers
            )

        previous_start, previous_end = get_previous_period_range(
            period_start=period_start,
            period_end=period_end,
        )

        previous_new_customers = list(
            list_customers_for_analytics(
                period_start=previous_start,
                period_end=previous_end,
            )
        )

        customer_growth = new_customer_count - len(previous_new_customers)

        return {
            "source": "realtime",
            "snapshot_id": None,
            "period_type": None,
            "period_start": period_start,
            "period_end": period_end,
            "active_customers": active_customers,
            "new_customers": new_customer_count,
            "customer_growth": customer_growth,
            "repeat_customer_rate": repeat_customer_rate,
        }