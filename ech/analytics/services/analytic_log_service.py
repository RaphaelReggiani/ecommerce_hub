import logging


logger = logging.getLogger(__name__)


class AnalyticsLogService:
    """
    Service responsible for structured analytics domain logs.
    """

    @staticmethod
    def log_snapshot_created(*, snapshot, performed_by=None):
        """
        Log analytics snapshot creation.
        """

        logger.info(
            "Analytics snapshot created.",
            extra={
                "snapshot_id": str(snapshot.id),
                "period_type": snapshot.period_type,
                "period_start": snapshot.period_start.isoformat(),
                "period_end": snapshot.period_end.isoformat(),
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_snapshot_refreshed(*, snapshot, performed_by=None):
        """
        Log analytics snapshot refresh operation.
        """

        logger.info(
            "Analytics snapshot refreshed.",
            extra={
                "snapshot_id": str(snapshot.id),
                "period_type": snapshot.period_type,
                "period_start": snapshot.period_start.isoformat(),
                "period_end": snapshot.period_end.isoformat(),
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_snapshot_metrics_updated(
        *,
        snapshot,
        updated_fields=None,
        performed_by=None,
    ):
        """
        Log analytics snapshot metrics update.
        """

        logger.info(
            "Analytics snapshot metrics updated.",
            extra={
                "snapshot_id": str(snapshot.id),
                "period_type": snapshot.period_type,
                "updated_fields": updated_fields or [],
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_dashboard_generated(
        *,
        period_type,
        period_start,
        period_end,
        performed_by=None,
    ):
        """
        Log analytics dashboard generation.
        """

        logger.info(
            "Analytics dashboard generated.",
            extra={
                "period_type": period_type,
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_sales_metrics_calculated(
        *,
        period_start,
        period_end,
        total_orders,
        total_revenue,
        performed_by=None,
    ):
        """
        Log sales metrics calculation.
        """

        logger.info(
            "Sales analytics calculated.",
            extra={
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "total_orders": total_orders,
                "total_revenue": str(total_revenue),
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_payment_metrics_calculated(
        *,
        period_start,
        period_end,
        captured_payments,
        failed_payments,
        refunded_payments,
        performed_by=None,
    ):
        """
        Log payment analytics metrics calculation.
        """

        logger.info(
            "Payment analytics calculated.",
            extra={
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "captured_payments": captured_payments,
                "failed_payments": failed_payments,
                "refunded_payments": refunded_payments,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_shipping_metrics_calculated(
        *,
        period_start,
        period_end,
        shipments_delivered,
        shipments_failed,
        shipments_in_transit,
        performed_by=None,
    ):
        """
        Log shipping analytics metrics calculation.
        """

        logger.info(
            "Shipping analytics calculated.",
            extra={
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "shipments_delivered": shipments_delivered,
                "shipments_failed": shipments_failed,
                "shipments_in_transit": shipments_in_transit,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_product_metrics_calculated(
        *,
        period_start,
        period_end,
        products_sold,
        top_product_id=None,
        performed_by=None,
    ):
        """
        Log product analytics metrics calculation.
        """

        logger.info(
            "Product analytics calculated.",
            extra={
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "products_sold": products_sold,
                "top_product_id": str(top_product_id) if top_product_id else None,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_customer_metrics_calculated(
        *,
        period_start,
        period_end,
        active_customers,
        new_customers,
        performed_by=None,
    ):
        """
        Log customer analytics metrics calculation.
        """

        logger.info(
            "Customer analytics calculated.",
            extra={
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "active_customers": active_customers,
                "new_customers": new_customers,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_user_metrics_calculated(
        *,
        period_start,
        period_end,
        total_registered_users,
        active_users,
        performed_by=None,
    ):
        """
        Log user analytics metrics calculation.
        """

        logger.info(
            "User analytics calculated.",
            extra={
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "total_registered_users": total_registered_users,
                "active_users": active_users,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_review_metrics_calculated(
        *,
        period_start,
        period_end,
        total_reviews,
        average_rating,
        performed_by=None,
    ):
        """
        Log review analytics metrics calculation.
        """

        logger.info(
            "Review analytics calculated.",
            extra={
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "total_reviews": total_reviews,
                "average_rating": str(average_rating),
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @staticmethod
    def log_analytics_cache_invalidated(
        *,
        reason,
        performed_by=None,
    ):
        """
        Log analytics cache invalidation event.
        """

        logger.info(
            "Analytics cache invalidated.",
            extra={
                "reason": reason,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )