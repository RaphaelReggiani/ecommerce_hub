from decimal import Decimal

from ech.analytics.exceptions import (
    AnalyticsSalesUnavailableException,
)
from ech.analytics.selectors import (
    get_latest_analytics_snapshot_by_period_type,
    list_orders_for_analytics,
    list_payments_for_analytics,
)
from ech.analytics.services.analytic_log_service import (
    AnalyticsLogService,
)
from ech.analytics.services.cache_service import (
    AnalyticsCacheService,
)
from ech.analytics.utils.cache_keys import (
    sales_overview_cache_key,
)
from ech.analytics.utils.date_ranges import (
    get_period_range,
)
from ech.orders.models import Order
from ech.payments.models import Payment


class AnalyticsSalesOverviewService:
    """
    Service responsible for sales analytics overview data.
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
        Retrieve the sales analytics overview for the requested period.

        Snapshot data is preferred when the latest snapshot matches the
        requested period bounds. Otherwise, metrics are calculated in real time.
        """

        resolved_period_start, resolved_period_end = cls._resolve_period_bounds(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
        )

        sales_version = AnalyticsCacheService.get_sales_version()
        cache_key = sales_overview_cache_key(
            period_start=resolved_period_start,
            period_end=resolved_period_end,
            sales_version=sales_version,
        )

        def producer():
            snapshot = cls._get_matching_snapshot(
                period_type=period_type,
                period_start=resolved_period_start,
                period_end=resolved_period_end,
            )

            if snapshot is not None:
                payload = cls._build_overview_from_snapshot(snapshot=snapshot)
            else:
                payload = cls._build_overview_realtime(
                    period_start=resolved_period_start,
                    period_end=resolved_period_end,
                )

            AnalyticsLogService.log_sales_metrics_calculated(
                period_start=resolved_period_start,
                period_end=resolved_period_end,
                total_orders=payload["total_orders"],
                total_revenue=payload["total_revenue"],
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
            raise AnalyticsSalesUnavailableException() from exc

    @classmethod
    def _resolve_period_bounds(
        cls,
        *,
        period_type,
        period_start,
        period_end,
    ):
        """
        Resolve sales overview period bounds.
        """

        if period_start is None and period_end is None:
            return get_period_range(period_type=period_type)

        if period_start is None or period_end is None:
            raise AnalyticsSalesUnavailableException()

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
    def _build_overview_from_snapshot(cls, *, snapshot):
        """
        Build sales overview payload from a materialized snapshot.
        """

        average_order_value = Decimal("0.00")

        if snapshot.total_orders > 0:
            average_order_value = snapshot.net_revenue / snapshot.total_orders

        return {
            "source": "snapshot",
            "snapshot_id": snapshot.id,
            "period_type": snapshot.period_type,
            "period_start": snapshot.period_start,
            "period_end": snapshot.period_end,
            "total_orders": snapshot.total_orders,
            "delivered_orders": snapshot.orders_delivered,
            "cancelled_orders": snapshot.orders_cancelled,
            "total_revenue": snapshot.total_revenue,
            "total_refunds": snapshot.total_refunds,
            "net_revenue": snapshot.net_revenue,
            "average_order_value": average_order_value,
            "payments_captured": snapshot.payments_captured,
            "payments_refunded": snapshot.payments_refunded,
        }

    @classmethod
    def _build_overview_realtime(
        cls,
        *,
        period_start,
        period_end,
    ):
        """
        Build sales overview in real time from operational tables.
        """

        orders = list(
            list_orders_for_analytics(
                period_start=period_start,
                period_end=period_end,
            )
        )
        payments = list(
            list_payments_for_analytics(
                period_start=period_start,
                period_end=period_end,
            )
        )

        total_orders = len(orders)

        delivered_orders = sum(
            1 for order in orders
            if order.status == Order.ORDER_STATUS_DELIVERED
        )

        cancelled_orders = sum(
            1 for order in orders
            if order.status == Order.ORDER_STATUS_CANCELLED
        )

        total_revenue = sum(
            (
                payment.amount
                for payment in payments
                if payment.status in {
                    Payment.PAYMENT_STATUS_CAPTURED,
                    Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED,
                    Payment.PAYMENT_STATUS_REFUNDED,
                }
            ),
            Decimal("0.00"),
        )

        total_refunds = sum(
            (payment.refunded_amount for payment in payments),
            Decimal("0.00"),
        )

        net_revenue = total_revenue - total_refunds

        average_order_value = Decimal("0.00")
        if total_orders > 0:
            average_order_value = net_revenue / total_orders

        payments_captured = sum(
            1 for payment in payments
            if payment.status == Payment.PAYMENT_STATUS_CAPTURED
        )

        payments_refunded = sum(
            1 for payment in payments
            if payment.refunded_amount > 0
        )

        return {
            "source": "realtime",
            "snapshot_id": None,
            "period_type": None,
            "period_start": period_start,
            "period_end": period_end,
            "total_orders": total_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "total_revenue": total_revenue,
            "total_refunds": total_refunds,
            "net_revenue": net_revenue,
            "average_order_value": average_order_value,
            "payments_captured": payments_captured,
            "payments_refunded": payments_refunded,
        }