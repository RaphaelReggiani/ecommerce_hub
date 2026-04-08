from ech.analytics.exceptions import (
    AnalyticsOrderUnavailableException,
)
from ech.analytics.selectors import (
    get_latest_analytics_snapshot_by_period_type,
    list_orders_for_analytics,
)
from ech.analytics.services.cache_service import (
    AnalyticsCacheService,
)
from ech.analytics.utils.cache_keys import (
    order_funnel_cache_key,
)
from ech.analytics.utils.date_ranges import (
    get_period_range,
)
from ech.orders.models import Order


class AnalyticsOrderFunnelService:
    """
    Service responsible for order funnel analytics data.
    """

    @classmethod
    def get_funnel(
        cls,
        *,
        period_type,
        period_start=None,
        period_end=None,
        performed_by=None,
    ):
        """
        Retrieve order funnel analytics for the requested period.

        Snapshot data is preferred when the latest snapshot matches the
        requested bounds. Otherwise, metrics are calculated in real time.
        """

        resolved_period_start, resolved_period_end = cls._resolve_period_bounds(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
        )

        funnel_version = AnalyticsCacheService.get_order_funnel_version()
        cache_key = order_funnel_cache_key(
            period_start=resolved_period_start,
            period_end=resolved_period_end,
            funnel_version=funnel_version,
        )

        def producer():
            snapshot = cls._get_matching_snapshot(
                period_type=period_type,
                period_start=resolved_period_start,
                period_end=resolved_period_end,
            )

            if snapshot is not None:
                return cls._build_funnel_from_snapshot(snapshot=snapshot)

            return cls._build_funnel_realtime(
                period_start=resolved_period_start,
                period_end=resolved_period_end,
            )

        try:
            return AnalyticsCacheService.get_or_set(
                key=cache_key,
                producer=producer,
                timeout=None,
            )
        except Exception as exc:
            raise AnalyticsOrderUnavailableException() from exc

    @classmethod
    def _resolve_period_bounds(
        cls,
        *,
        period_type,
        period_start,
        period_end,
    ):
        """
        Resolve order funnel period bounds.
        """

        if period_start is None and period_end is None:
            return get_period_range(period_type=period_type)

        if period_start is None or period_end is None:
            raise AnalyticsOrderUnavailableException()

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
        Return the latest snapshot only if it matches the requested period.
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
    def _build_funnel_from_snapshot(cls, *, snapshot):
        """
        Build order funnel payload from a materialized snapshot.
        """

        total_orders = snapshot.total_orders

        delivered_rate = 0
        cancelled_rate = 0

        if total_orders > 0:
            delivered_rate = snapshot.orders_delivered / total_orders
            cancelled_rate = snapshot.orders_cancelled / total_orders

        return {
            "source": "snapshot",
            "snapshot_id": snapshot.id,
            "period_type": snapshot.period_type,
            "period_start": snapshot.period_start,
            "period_end": snapshot.period_end,
            "total_orders": snapshot.total_orders,
            "pending_orders": snapshot.orders_pending,
            "processing_orders": snapshot.orders_processing,
            "shipped_orders": snapshot.orders_shipped,
            "delivered_orders": snapshot.orders_delivered,
            "cancelled_orders": snapshot.orders_cancelled,
            "delivered_rate": delivered_rate,
            "cancelled_rate": cancelled_rate,
        }

    @classmethod
    def _build_funnel_realtime(
        cls,
        *,
        period_start,
        period_end,
    ):
        """
        Build order funnel in real time from order records.
        """

        orders = list(
            list_orders_for_analytics(
                period_start=period_start,
                period_end=period_end,
            )
        )

        total_orders = len(orders)

        pending_orders = sum(
            1 for order in orders
            if order.status == Order.ORDER_STATUS_PENDING
        )

        processing_orders = sum(
            1 for order in orders
            if order.status == Order.ORDER_STATUS_PROCESSING
        )

        shipped_orders = sum(
            1 for order in orders
            if order.status == Order.ORDER_STATUS_SHIPPED
        )

        delivered_orders = sum(
            1 for order in orders
            if order.status == Order.ORDER_STATUS_DELIVERED
        )

        cancelled_orders = sum(
            1 for order in orders
            if order.status == Order.ORDER_STATUS_CANCELLED
        )

        delivered_rate = 0
        cancelled_rate = 0

        if total_orders > 0:
            delivered_rate = delivered_orders / total_orders
            cancelled_rate = cancelled_orders / total_orders

        return {
            "source": "realtime",
            "snapshot_id": None,
            "period_type": None,
            "period_start": period_start,
            "period_end": period_end,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "processing_orders": processing_orders,
            "shipped_orders": shipped_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "delivered_rate": delivered_rate,
            "cancelled_rate": cancelled_rate,
        }