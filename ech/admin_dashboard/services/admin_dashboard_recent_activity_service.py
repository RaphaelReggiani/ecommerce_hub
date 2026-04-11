from ech.admin_dashboard.exceptions import (
    AdminDashboardRecentActivityUnavailableException,
)

from ech.admin_dashboard.selectors import (
    get_recent_order_activity,
    get_recent_payment_activity,
    get_recent_shipping_activity,
    get_recent_review_activity,
    get_recent_notification_activity,
    get_recent_admin_activity,
    get_recent_product_activity,
)

from ech.admin_dashboard.services.cache_service import (
    AdminDashboardCacheService,
)

from ech.admin_dashboard.services.admin_dashboard_log_service import (
    AdminDashboardLogService,
)

from ech.admin_dashboard.utils.cache_keys import (
    admin_dashboard_recent_activity_cache_key,
)

from ech.admin_dashboard.utils.metric_builders import (
    build_recent_activity_payload,
)


class AdminDashboardRecentActivityService:
    """
    Service responsible for aggregating the recent
    operational activity feed for the admin dashboard.

    This feed consolidates events across multiple modules
    to provide administrators with real-time system visibility.
    """

    DEFAULT_ACTIVITY_LIMIT = 50

    @classmethod
    def get_recent_activity(
        cls,
        *,
        limit=None,
        performed_by=None,
    ):
        """
        Return recent activity feed for the admin dashboard.
        """

        activity_limit = limit or cls.DEFAULT_ACTIVITY_LIMIT

        activity_version = (
            AdminDashboardCacheService.get_activity_feed_version()
        )

        cache_key = admin_dashboard_recent_activity_cache_key(
            activity_version=activity_version,
            limit=activity_limit,
        )

        def producer():
            order_activity = get_recent_order_activity(limit=activity_limit)
            payment_activity = get_recent_payment_activity(limit=activity_limit)
            shipping_activity = get_recent_shipping_activity(limit=activity_limit)
            review_activity = get_recent_review_activity(limit=activity_limit)
            notification_activity = get_recent_notification_activity(limit=activity_limit)
            admin_activity = get_recent_admin_activity(limit=activity_limit)
            product_activity = get_recent_product_activity(limit=activity_limit)

            payload = build_recent_activity_payload(
                order_activity=order_activity,
                payment_activity=payment_activity,
                shipping_activity=shipping_activity,
                review_activity=review_activity,
                notification_activity=notification_activity,
                admin_activity=admin_activity,
                product_activity=product_activity,
                limit=activity_limit,
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
            raise AdminDashboardRecentActivityUnavailableException() from exc