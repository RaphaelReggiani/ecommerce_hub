from ech.admin_dashboard.exceptions import (
    AdminDashboardOperationalMetricsUnavailableException,
)

from ech.admin_dashboard.selectors import (
    get_order_operational_metrics,
    get_payment_operational_metrics,
    get_shipping_operational_metrics,
    get_review_operational_metrics,
    get_notification_operational_metrics,
    get_product_operational_metrics,
)

from ech.admin_dashboard.services.cache_service import (
    AdminDashboardCacheService,
)

from ech.admin_dashboard.services.admin_dashboard_log_service import (
    AdminDashboardLogService,
)

from ech.admin_dashboard.utils.cache_keys import (
    admin_dashboard_operational_metrics_cache_key,
)

from ech.admin_dashboard.utils.metric_builders import (
    build_operational_metrics_payload,
)


class AdminDashboardOperationalMetricsService:
    """
    Service responsible for operational monitoring metrics.

    These metrics highlight operational problems that may
    require administrative attention across orders, payments,
    shipping, reviews, notifications, and products.
    """

    @classmethod
    def get_operational_metrics(cls, *, performed_by=None):
        """
        Return operational dashboard metrics.
        """

        operational_version = (
            AdminDashboardCacheService.get_operational_metrics_version()
        )

        cache_key = admin_dashboard_operational_metrics_cache_key(
            operational_version=operational_version,
        )

        def producer():
            order_metrics = get_order_operational_metrics()
            payment_metrics = get_payment_operational_metrics()
            shipping_metrics = get_shipping_operational_metrics()
            review_metrics = get_review_operational_metrics()
            notification_metrics = get_notification_operational_metrics()
            product_metrics = get_product_operational_metrics()

            payload = build_operational_metrics_payload(
                order_metrics=order_metrics,
                payment_metrics=payment_metrics,
                shipping_metrics=shipping_metrics,
                review_metrics=review_metrics,
                notification_metrics=notification_metrics,
                product_metrics=product_metrics,
            )

            AdminDashboardLogService.log_dashboard_access(
                user=performed_by,
            )

            return payload

        try:
            return AdminDashboardCacheService.get_or_set(
                key=cache_key,
                producer=producer,
                timeout=None,
            )

        except Exception as exc:
            raise AdminDashboardOperationalMetricsUnavailableException() from exc