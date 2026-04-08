from collections import defaultdict
from decimal import Decimal

from ech.analytics.constants.constants import (
    ANALYTIC_HIGH_RATING_THRESHOLD,
    ANALYTIC_LOW_RATING_THRESHOLD,
)
from ech.analytics.exceptions import (
    AnalyticsDashboardUnavailableException,
)
from ech.analytics.selectors import (
    get_latest_analytics_snapshot_by_period_type,
    list_customers_for_analytics,
    list_orders_for_analytics,
    list_payments_for_analytics,
    list_reviews_for_analytics,
    list_shipments_for_analytics,
    list_users_for_analytics,
)
from ech.analytics.services.analytic_log_service import (
    AnalyticsLogService,
)
from ech.analytics.services.cache_service import (
    AnalyticsCacheService,
)
from ech.analytics.utils.cache_keys import (
    dashboard_summary_cache_key,
)
from ech.analytics.utils.date_ranges import (
    get_period_range,
)
from ech.orders.models import Order
from ech.payments.models import Payment
from ech.reviews.models import Review
from ech.shipping.models import Shipment
from ech.users.models import CustomUser


class AnalyticsDashboardSummaryService:
    """
    Service responsible for consolidated analytics dashboard summaries.
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
        Retrieve a consolidated analytics dashboard summary.

        If explicit period bounds are not provided, the service resolves
        them from the requested period type.

        Snapshot data is preferred when the latest snapshot matches the
        requested bounds. Otherwise, the summary is calculated in real time.
        """

        resolved_period_start, resolved_period_end = cls._resolve_period_bounds(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
        )

        dashboard_version = AnalyticsCacheService.get_dashboard_version()
        cache_key = dashboard_summary_cache_key(
            period_start=resolved_period_start,
            period_end=resolved_period_end,
            dashboard_version=dashboard_version,
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

            AnalyticsLogService.log_dashboard_generated(
                period_type=period_type,
                period_start=resolved_period_start,
                period_end=resolved_period_end,
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
            raise AnalyticsDashboardUnavailableException() from exc

    @classmethod
    def _resolve_period_bounds(
        cls,
        *,
        period_type,
        period_start,
        period_end,
    ):
        """
        Resolve summary period bounds.
        """

        if period_start is None and period_end is None:
            return get_period_range(period_type=period_type)

        if period_start is None or period_end is None:
            raise AnalyticsDashboardUnavailableException()

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
    def _build_summary_from_snapshot(cls, *, snapshot):
        """
        Build dashboard summary payload from a materialized snapshot.
        """

        return {
            "source": "snapshot",
            "snapshot_id": snapshot.id,
            "period_type": snapshot.period_type,
            "period_start": snapshot.period_start,
            "period_end": snapshot.period_end,
            "orders": {
                "total_orders": snapshot.total_orders,
                "orders_pending": snapshot.orders_pending,
                "orders_processing": snapshot.orders_processing,
                "orders_shipped": snapshot.orders_shipped,
                "orders_delivered": snapshot.orders_delivered,
                "orders_cancelled": snapshot.orders_cancelled,
            },
            "revenue": {
                "total_revenue": snapshot.total_revenue,
                "total_refunds": snapshot.total_refunds,
                "net_revenue": snapshot.net_revenue,
            },
            "payments": {
                "payments_captured": snapshot.payments_captured,
                "payments_failed": snapshot.payments_failed,
                "payments_refunded": snapshot.payments_refunded,
            },
            "shipping": {
                "shipments_in_transit": snapshot.shipments_in_transit,
                "shipments_delivered": snapshot.shipments_delivered,
                "shipments_failed": snapshot.shipments_failed,
            },
            "products": {
                "products_sold": snapshot.products_sold,
                "top_product_id": snapshot.top_product_id,
            },
            "customers": {
                "active_customers": snapshot.active_customers,
                "new_customers": snapshot.new_customers,
            },
            "users": {
                "total_registered_users": snapshot.total_registered_users,
                "active_users": snapshot.active_users,
                "inactive_users": snapshot.inactive_users,
                "confirmed_users": snapshot.confirmed_users,
                "unconfirmed_users": snapshot.unconfirmed_users,
                "staff_users": snapshot.staff_users,
                "customer_users": snapshot.customer_users,
            },
            "reviews": {
                "total_reviews": snapshot.total_reviews,
                "approved_reviews": snapshot.approved_reviews,
                "rejected_reviews": snapshot.rejected_reviews,
                "hidden_reviews": snapshot.hidden_reviews,
                "cancelled_reviews": snapshot.cancelled_reviews,
                "verified_purchase_reviews": snapshot.verified_purchase_reviews,
                "average_rating": snapshot.average_rating,
                "low_rated_products_count": snapshot.low_rated_products_count,
                "high_rated_products_count": snapshot.high_rated_products_count,
            },
        }

    @classmethod
    def _build_summary_realtime(
        cls,
        *,
        period_start,
        period_end,
    ):
        """
        Build dashboard summary in real time from operational tables.
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
        shipments = list(
            list_shipments_for_analytics(
                period_start=period_start,
                period_end=period_end,
            )
        )
        reviews = list(
            list_reviews_for_analytics(
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
        users = list(
            list_users_for_analytics(
                period_end=period_end,
            )
        )

        active_customer_ids = {order.customer_id for order in orders}

        products_sold = 0
        product_quantities = {}

        for order in orders:
            for item in order.items.all():
                products_sold += item.quantity
                product_quantities[item.product_id] = (
                    product_quantities.get(item.product_id, 0) + item.quantity
                )

        top_product_id = None
        if product_quantities:
            top_product_id = max(
                product_quantities,
                key=product_quantities.get,
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

        approved_reviews = [
            review for review in reviews
            if review.status == Review.REVIEW_STATUS_APPROVED
        ]

        average_rating = Decimal("0.00")
        if approved_reviews:
            average_rating = (
                sum(
                    Decimal(str(review.rating))
                    for review in approved_reviews
                ) / len(approved_reviews)
            ).quantize(Decimal("0.01"))

        product_rating_map = defaultdict(list)

        for review in approved_reviews:
            product_rating_map[review.product_id].append(review.rating)

        low_rated_products_count = 0
        high_rated_products_count = 0

        for ratings in product_rating_map.values():
            product_average = sum(ratings) / len(ratings)

            if product_average <= ANALYTIC_LOW_RATING_THRESHOLD:
                low_rated_products_count += 1

            if product_average >= ANALYTIC_HIGH_RATING_THRESHOLD:
                high_rated_products_count += 1

        return {
            "source": "realtime",
            "snapshot_id": None,
            "period_type": None,
            "period_start": period_start,
            "period_end": period_end,
            "orders": {
                "total_orders": len(orders),
                "orders_pending": sum(
                    1 for order in orders
                    if order.status == Order.ORDER_STATUS_PENDING
                ),
                "orders_processing": sum(
                    1 for order in orders
                    if order.status == Order.ORDER_STATUS_PROCESSING
                ),
                "orders_shipped": sum(
                    1 for order in orders
                    if order.status == Order.ORDER_STATUS_SHIPPED
                ),
                "orders_delivered": sum(
                    1 for order in orders
                    if order.status == Order.ORDER_STATUS_DELIVERED
                ),
                "orders_cancelled": sum(
                    1 for order in orders
                    if order.status == Order.ORDER_STATUS_CANCELLED
                ),
            },
            "revenue": {
                "total_revenue": total_revenue,
                "total_refunds": total_refunds,
                "net_revenue": net_revenue,
            },
            "payments": {
                "payments_captured": sum(
                    1 for payment in payments
                    if payment.status == Payment.PAYMENT_STATUS_CAPTURED
                ),
                "payments_failed": sum(
                    1 for payment in payments
                    if payment.status == Payment.PAYMENT_STATUS_FAILED
                ),
                "payments_refunded": sum(
                    1 for payment in payments
                    if payment.refunded_amount > 0
                ),
            },
            "shipping": {
                "shipments_in_transit": sum(
                    1 for shipment in shipments
                    if shipment.status == Shipment.STATUS_IN_TRANSIT
                ),
                "shipments_delivered": sum(
                    1 for shipment in shipments
                    if shipment.status == Shipment.STATUS_DELIVERED
                ),
                "shipments_failed": sum(
                    1 for shipment in shipments
                    if shipment.status == Shipment.STATUS_FAILED
                ),
            },
            "products": {
                "products_sold": products_sold,
                "top_product_id": top_product_id,
            },
            "customers": {
                "active_customers": len(active_customer_ids),
                "new_customers": len(new_customers),
            },
            "users": {
                "total_registered_users": len(users),
                "active_users": sum(
                    1 for user in users
                    if user.is_active
                ),
                "inactive_users": sum(
                    1 for user in users
                    if not user.is_active
                ),
                "confirmed_users": sum(
                    1 for user in users
                    if user.email_confirmed
                ),
                "unconfirmed_users": sum(
                    1 for user in users
                    if not user.email_confirmed
                ),
                "staff_users": sum(
                    1 for user in users
                    if user.user_role != CustomUser.ROLE_CUSTOMER_USER
                ),
                "customer_users": sum(
                    1 for user in users
                    if user.user_role == CustomUser.ROLE_CUSTOMER_USER
                ),
            },
            "reviews": {
                "total_reviews": len(reviews),
                "approved_reviews": len(approved_reviews),
                "rejected_reviews": sum(
                    1 for review in reviews
                    if review.status == Review.REVIEW_STATUS_REJECTED
                ),
                "hidden_reviews": sum(
                    1 for review in reviews
                    if review.status == Review.REVIEW_STATUS_HIDDEN
                ),
                "cancelled_reviews": sum(
                    1 for review in reviews
                    if review.status == Review.REVIEW_STATUS_CANCELLED
                ),
                "verified_purchase_reviews": sum(
                    1 for review in reviews
                    if review.is_verified_purchase
                ),
                "average_rating": average_rating,
                "low_rated_products_count": low_rated_products_count,
                "high_rated_products_count": high_rated_products_count,
            },
        }