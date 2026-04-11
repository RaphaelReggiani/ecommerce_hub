from ech.admin_dashboard.exceptions import (
    AdminDashboardSummaryUnavailableException,
)

from ech.admin_dashboard.selectors import (
    get_orders_summary_metrics,
    get_payments_summary_metrics,
    get_shipping_summary_metrics,
    get_users_summary_metrics,
    get_reviews_summary_metrics,
    get_products_summary_metrics,
)

from ech.admin_dashboard.services.cache_service import (
    AdminDashboardCacheService,
)

from ech.admin_dashboard.services.admin_dashboard_log_service import (
    AdminDashboardLogService,
)

from ech.admin_dashboard.utils.cache_keys import (
    admin_dashboard_summary_cache_key,
)

from ech.admin_dashboard.utils.metric_builders import (
    build_admin_dashboard_summary_payload,
)


class AdminDashboardSummaryService:
    """
    Service responsible for generating the operational
    admin dashboard summary.

    This summary aggregates operational metrics from
    multiple modules such as orders, payments, shipping,
    users, reviews, and products.

    The result is cached to avoid repeated heavy queries.
    """

    @classmethod
    def get_summary(cls, *, performed_by=None):
        """
        Return the admin dashboard summary.
        """

        dashboard_version = AdminDashboardCacheService.get_dashboard_version()

        cache_key = admin_dashboard_summary_cache_key(
            dashboard_version=dashboard_version,
        )

        def producer():
            orders_metrics = get_orders_summary_metrics()
            payments_metrics = get_payments_summary_metrics()
            shipping_metrics = get_shipping_summary_metrics()
            users_metrics = get_users_summary_metrics()
            reviews_metrics = get_reviews_summary_metrics()
            products_metrics = get_products_summary_metrics()

            payload = build_admin_dashboard_summary_payload(
                orders_metrics=orders_metrics,
                payments_metrics=payments_metrics,
                shipping_metrics=shipping_metrics,
                users_metrics=users_metrics,
                reviews_metrics=reviews_metrics,
                products_metrics=products_metrics,
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
            raise AdminDashboardSummaryUnavailableException() from exc