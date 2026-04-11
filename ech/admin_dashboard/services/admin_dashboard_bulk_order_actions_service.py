from django.db import transaction

from ech.admin_dashboard.exceptions import (
    AdminDashboardBulkOrderActionException,
)

from ech.admin_dashboard.services.admin_dashboard_log_service import (
    AdminDashboardLogService,
)

from ech.admin_dashboard.services.cache_service import (
    AdminDashboardCacheService,
)

from ech.orders.models import Order
from ech.orders.services.order_status_service import (
    OrderStatusService,
)
from ech.orders.services.order_cancel_service import (
    CancelOrderService,
)


class AdminDashboardBulkOrderActionsService:
    """
    Service responsible for executing administrative bulk
    operations on orders.
    """

    ALLOWED_ACTIONS = {
        "cancel_orders",
        "mark_processing",
        "mark_shipped",
    }

    @classmethod
    def execute_bulk_action(
        cls,
        *,
        action_type,
        order_ids,
        performed_by=None,
    ):

        if action_type not in cls.ALLOWED_ACTIONS:
            raise AdminDashboardBulkOrderActionException(
                f"Invalid bulk order action: {action_type}"
            )

        if not order_ids:
            raise AdminDashboardBulkOrderActionException(
                "Order ID list cannot be empty"
            )

        try:

            with transaction.atomic():

                orders = list(
                    Order.objects.select_for_update().filter(
                        id__in=order_ids
                    )
                )

                if not orders:
                    raise AdminDashboardBulkOrderActionException(
                        "No valid orders found for bulk operation"
                    )

                results = []

                for order in orders:

                    if action_type == "cancel_orders":

                        CancelOrderService.cancel_order(
                            order=order,
                            performed_by=performed_by,
                        )

                    elif action_type == "mark_processing":

                        OrderStatusService.update_order_status(
                            order=order,
                            new_status=Order.ORDER_STATUS_PROCESSING,
                            performed_by=performed_by,
                        )

                    elif action_type == "mark_shipped":

                        OrderStatusService.update_order_status(
                            order=order,
                            new_status=Order.ORDER_STATUS_SHIPPED,
                            performed_by=performed_by,
                        )

                    results.append(order.id)

                AdminDashboardLogService.log_bulk_order_action(
                    action_type=action_type,
                    order_ids=results,
                    performed_by=performed_by,
                )

                AdminDashboardCacheService.invalidate_dashboard_cache()
                AdminDashboardCacheService.invalidate_operational_metrics_cache()
                AdminDashboardCacheService.invalidate_activity_feed_cache()

                return {
                    "action": action_type,
                    "processed_orders": results,
                    "total_processed": len(results),
                }

        except Exception as exc:
            raise AdminDashboardBulkOrderActionException() from exc