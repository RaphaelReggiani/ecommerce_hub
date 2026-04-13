import uuid
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import patch, call

from django.test import SimpleTestCase

from ech.admin_dashboard.exceptions import (
    AdminDashboardBulkOrderActionException,
)
from ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service import (
    AdminDashboardBulkOrderActionsService,
)


class AdminDashboardBulkOrderActionsServiceTestCase(SimpleTestCase):
    def _build_order(self, order_id=None):
        """Build a lightweight order-like object for testing."""
        return SimpleNamespace(id=order_id or uuid.uuid4())

    def _build_user(self, user_id=None):
        """Build a lightweight user-like object for testing."""
        return SimpleNamespace(id=user_id or 10)

    def test_execute_bulk_action_raises_for_invalid_action(self):
        """Raise exception when bulk order action is invalid."""
        with self.assertRaises(AdminDashboardBulkOrderActionException) as context:
            AdminDashboardBulkOrderActionsService.execute_bulk_action(
                action_type="invalid_action",
                order_ids=[uuid.uuid4()],
                performed_by=None,
            )

        self.assertEqual(
            str(context.exception),
            "Invalid bulk order action: invalid_action",
        )

    def test_execute_bulk_action_raises_for_empty_order_ids(self):
        """Raise exception when order id list is empty."""
        with self.assertRaises(AdminDashboardBulkOrderActionException) as context:
            AdminDashboardBulkOrderActionsService.execute_bulk_action(
                action_type="cancel_orders",
                order_ids=[],
                performed_by=None,
            )

        self.assertEqual(
            str(context.exception),
            "Order ID list cannot be empty",
        )

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.transaction.atomic",
        return_value=nullcontext(),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.Order.objects"
    )
    def test_execute_bulk_action_raises_when_no_orders_found(
        self,
        order_objects_mock,
        atomic_mock,
    ):
        """Raise wrapped bulk order operation exception when no matching orders are found."""
        order_objects_mock.select_for_update.return_value.filter.return_value = []

        with self.assertRaises(AdminDashboardBulkOrderActionException) as context:
            AdminDashboardBulkOrderActionsService.execute_bulk_action(
                action_type="cancel_orders",
                order_ids=[uuid.uuid4()],
                performed_by=None,
            )

        self.assertEqual(
            str(context.exception),
            "Bulk order operation failed.",
        )

        order_objects_mock.select_for_update.assert_called_once_with()
        order_objects_mock.select_for_update.return_value.filter.assert_called_once()

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.transaction.atomic",
        return_value=nullcontext(),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.AdminDashboardCacheService.invalidate_activity_feed_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.AdminDashboardCacheService.invalidate_operational_metrics_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.AdminDashboardCacheService.invalidate_dashboard_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.AdminDashboardLogService.log_bulk_order_action"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.CancelOrderService.cancel_order",
        create=True,
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.Order.objects"
    )
    def test_execute_bulk_action_cancels_orders_successfully(
        self,
        order_objects_mock,
        cancel_order_mock,
        log_mock,
        invalidate_dashboard_mock,
        invalidate_operational_mock,
        invalidate_activity_mock,
        atomic_mock,
    ):
        """Cancel all returned orders successfully and invalidate related caches."""
        performed_by = self._build_user()
        order_1 = self._build_order()
        order_2 = self._build_order()
        order_ids = [order_1.id, order_2.id]

        order_objects_mock.select_for_update.return_value.filter.return_value = [
            order_1,
            order_2,
        ]

        result = AdminDashboardBulkOrderActionsService.execute_bulk_action(
            action_type="cancel_orders",
            order_ids=order_ids,
            performed_by=performed_by,
        )

        self.assertEqual(
            result,
            {
                "action": "cancel_orders",
                "processed_orders": [order_1.id, order_2.id],
                "total_processed": 2,
            },
        )

        cancel_order_mock.assert_has_calls(
            [
                call(
                    order=order_1,
                    performed_by=performed_by,
                ),
                call(
                    order=order_2,
                    performed_by=performed_by,
                ),
            ]
        )
        self.assertEqual(cancel_order_mock.call_count, 2)

        log_mock.assert_called_once_with(
            action_type="cancel_orders",
            order_ids=[order_1.id, order_2.id],
            performed_by=performed_by,
        )

        invalidate_dashboard_mock.assert_called_once_with()
        invalidate_operational_mock.assert_called_once_with()
        invalidate_activity_mock.assert_called_once_with()

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.transaction.atomic",
        return_value=nullcontext(),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.AdminDashboardCacheService.invalidate_activity_feed_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.AdminDashboardCacheService.invalidate_operational_metrics_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.AdminDashboardCacheService.invalidate_dashboard_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.AdminDashboardLogService.log_bulk_order_action"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.OrderStatusService.update_order_status",
        create=True,
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.Order.objects"
    )
    def test_execute_bulk_action_marks_orders_processing_successfully(
        self,
        order_objects_mock,
        update_status_mock,
        log_mock,
        invalidate_dashboard_mock,
        invalidate_operational_mock,
        invalidate_activity_mock,
        atomic_mock,
    ):
        """Mark all returned orders as processing successfully."""
        performed_by = self._build_user()
        order_1 = self._build_order()
        order_2 = self._build_order()
        order_ids = [order_1.id, order_2.id]

        order_objects_mock.select_for_update.return_value.filter.return_value = [
            order_1,
            order_2,
        ]

        with patch.object(
            AdminDashboardBulkOrderActionsService.__module__ and __import__(
                "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service",
                fromlist=["Order"],
            ).Order,
            "ORDER_STATUS_PROCESSING",
            "processing",
            create=True,
        ):
            result = AdminDashboardBulkOrderActionsService.execute_bulk_action(
                action_type="mark_processing",
                order_ids=order_ids,
                performed_by=performed_by,
            )

        self.assertEqual(
            result,
            {
                "action": "mark_processing",
                "processed_orders": [order_1.id, order_2.id],
                "total_processed": 2,
            },
        )

        update_status_mock.assert_has_calls(
            [
                call(
                    order=order_1,
                    new_status="processing",
                    performed_by=performed_by,
                ),
                call(
                    order=order_2,
                    new_status="processing",
                    performed_by=performed_by,
                ),
            ]
        )
        self.assertEqual(update_status_mock.call_count, 2)

        log_mock.assert_called_once_with(
            action_type="mark_processing",
            order_ids=[order_1.id, order_2.id],
            performed_by=performed_by,
        )

        invalidate_dashboard_mock.assert_called_once_with()
        invalidate_operational_mock.assert_called_once_with()
        invalidate_activity_mock.assert_called_once_with()

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.transaction.atomic",
        return_value=nullcontext(),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.OrderStatusService.update_order_status",
        side_effect=Exception("status error"),
        create=True,
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.Order.objects"
    )
    def test_execute_bulk_action_wraps_status_errors(
        self,
        order_objects_mock,
        update_status_mock,
        atomic_mock,
    ):
        """Wrap internal order status errors with the default bulk operation exception."""
        order = self._build_order()

        order_objects_mock.select_for_update.return_value.filter.return_value = [
            order,
        ]

        with patch.object(
            __import__(
                "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service",
                fromlist=["Order"],
            ).Order,
            "ORDER_STATUS_SHIPPED",
            "shipped",
            create=True,
        ):
            with self.assertRaises(AdminDashboardBulkOrderActionException) as context:
                AdminDashboardBulkOrderActionsService.execute_bulk_action(
                    action_type="mark_shipped",
                    order_ids=[order.id],
                    performed_by=None,
                )

        self.assertEqual(
            str(context.exception),
            "Bulk order operation failed.",
        )

        update_status_mock.assert_called_once_with(
            order=order,
            new_status="shipped",
            performed_by=None,
        )

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.transaction.atomic",
        return_value=nullcontext(),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.AdminDashboardLogService.log_bulk_order_action",
        side_effect=Exception("log failure"),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.CancelOrderService.cancel_order",
        create=True,
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service.Order.objects"
    )
    def test_execute_bulk_action_wraps_log_errors(
        self,
        order_objects_mock,
        cancel_order_mock,
        log_mock,
        atomic_mock,
    ):
        """Wrap logging errors with the default bulk order operation exception."""
        order = self._build_order()

        order_objects_mock.select_for_update.return_value.filter.return_value = [
            order,
        ]

        with self.assertRaises(AdminDashboardBulkOrderActionException) as context:
            AdminDashboardBulkOrderActionsService.execute_bulk_action(
                action_type="cancel_orders",
                order_ids=[order.id],
                performed_by=None,
            )

        self.assertEqual(
            str(context.exception),
            "Bulk order operation failed.",
        )

        cancel_order_mock.assert_called_once_with(
            order=order,
            performed_by=None,
        )