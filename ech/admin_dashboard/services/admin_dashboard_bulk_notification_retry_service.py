from django.db import transaction

from ech.admin_dashboard.exceptions import (
    AdminDashboardNotificationRetryException,
)

from ech.admin_dashboard.services.admin_dashboard_log_service import (
    AdminDashboardLogService,
)

from ech.admin_dashboard.services.cache_service import (
    AdminDashboardCacheService,
)

from ech.notifications.models import Notification
from ech.notifications.services.notification_delivery_service import (
    NotificationDeliveryService,
)


class AdminDashboardBulkNotificationRetryService:
    """
    Service responsible for retrying failed notifications
    from the admin dashboard.
    """

    MAX_RETRY_BATCH = 100

    @classmethod
    def retry_notifications(
        cls,
        *,
        notification_ids,
        performed_by=None,
    ):

        if not notification_ids:
            raise AdminDashboardNotificationRetryException(
                "Notification ID list cannot be empty"
            )

        if len(notification_ids) > cls.MAX_RETRY_BATCH:
            raise AdminDashboardNotificationRetryException(
                "Retry batch exceeds maximum allowed size"
            )

        try:

            with transaction.atomic():

                notifications = list(
                    Notification.objects.select_for_update().filter(
                        id__in=notification_ids
                    )
                )

                if not notifications:
                    raise AdminDashboardNotificationRetryException(
                        "No valid notifications found for retry"
                    )

                retried_notifications = []

                for notification in notifications:

                    if notification.status != Notification.STATUS_FAILED:
                        continue

                    NotificationDeliveryService.deliver_notification(
                        notification=notification,
                        performed_by=performed_by,
                    )

                    retried_notifications.append(notification.id)

                AdminDashboardLogService.log_notification_retry(
                    notification_ids=retried_notifications,
                    performed_by=performed_by,
                )

                AdminDashboardCacheService.invalidate_dashboard_cache()
                AdminDashboardCacheService.invalidate_operational_metrics_cache()
                AdminDashboardCacheService.invalidate_activity_feed_cache()

                return {
                    "retried_notifications": retried_notifications,
                    "total_retried": len(retried_notifications),
                }

        except Exception as exc:
            raise AdminDashboardNotificationRetryException() from exc