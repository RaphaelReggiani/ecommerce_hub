from ech.admin_dashboard.exceptions import (
    AdminDashboardOperationalAlertsUnavailableException,
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
    admin_dashboard_alerts_cache_key,
)

from ech.admin_dashboard.utils.metric_builders import (
    build_admin_dashboard_alerts_payload,
)


class AdminDashboardAlertsService:
    """
    Service responsible for detecting operational alerts
    that require administrative attention.

    Alerts are derived from operational metrics across
    multiple modules.
    """

    @classmethod
    def get_alerts(cls, *, performed_by=None):
        """
        Return dashboard operational alerts.
        """

        alerts_version = AdminDashboardCacheService.get_alerts_version()

        cache_key = admin_dashboard_alerts_cache_key(
            alerts_version=alerts_version,
        )

        def producer():
            order_metrics = get_order_operational_metrics()
            payment_metrics = get_payment_operational_metrics()
            shipping_metrics = get_shipping_operational_metrics()
            review_metrics = get_review_operational_metrics()
            notification_metrics = get_notification_operational_metrics()
            product_metrics = get_product_operational_metrics()

            payload = build_admin_dashboard_alerts_payload(
                order_metrics=order_metrics,
                payment_metrics=payment_metrics,
                shipping_metrics=shipping_metrics,
                review_metrics=review_metrics,
                notification_metrics=notification_metrics,
                product_metrics=product_metrics,
            )

            if payload.get("alerts"):
                AdminDashboardLogService.log_dashboard_alert(
                    alert_type="operational_alerts_generated",
                    alert_message="Operational alerts detected in admin dashboard",
                    metadata={
                        "alerts_count": len(payload["alerts"]),
                        "performed_by_id": getattr(performed_by, "id", None),
                    },
                )

            return payload

        try:
            return AdminDashboardCacheService.get_or_set(
                key=cache_key,
                producer=producer,
                timeout=None,
            )

        except Exception as exc:
            raise AdminDashboardOperationalAlertsUnavailableException() from exc