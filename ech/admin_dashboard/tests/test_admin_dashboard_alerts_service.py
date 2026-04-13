from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase

from ech.admin_dashboard.exceptions import (
    AdminDashboardOperationalAlertsUnavailableException,
)
from ech.admin_dashboard.services.admin_dashboard_alerts_service import (
    AdminDashboardAlertsService,
)


class AdminDashboardAlertsServiceTestCase(TestCase):
    def setUp(self):
        """Clear cache before each test execution."""
        cache.clear()

    def _build_alerts_payload(self):
        """Build a representative alerts payload."""
        return {
            "alerts": [
                {
                    "type": "pending_orders",
                    "message": "There are pending orders requiring attention.",
                    "severity": "warning",
                },
                {
                    "type": "failed_notifications",
                    "message": "Notification delivery failures detected.",
                    "severity": "critical",
                },
            ],
            "total_alerts": 2,
        }

    def test_get_alerts_returns_expected_payload(self):
        """Return the expected aggregated alerts payload."""
        expected_payload = self._build_alerts_payload()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "AdminDashboardCacheService.get_alerts_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_order_operational_metrics",
            return_value={"pending_orders": 3},
        ) as order_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_payment_operational_metrics",
            return_value={"failed_payments": 0},
        ) as payment_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_shipping_operational_metrics",
            return_value={"failed_shipments": 0},
        ) as shipping_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_review_operational_metrics",
            return_value={"flagged_reviews": 0},
        ) as review_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_notification_operational_metrics",
            return_value={"failed_notifications": 5},
        ) as notification_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_product_operational_metrics",
            return_value={"products_without_images": 1},
        ) as product_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "build_admin_dashboard_alerts_payload",
            return_value=expected_payload,
        ) as builder_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "AdminDashboardLogService.log_dashboard_alert",
        ) as log_mock:
            payload = AdminDashboardAlertsService.get_alerts(
                performed_by=None,
            )

        self.assertEqual(payload, expected_payload)

        order_mock.assert_called_once_with()
        payment_mock.assert_called_once_with()
        shipping_mock.assert_called_once_with()
        review_mock.assert_called_once_with()
        notification_mock.assert_called_once_with()
        product_mock.assert_called_once_with()

        builder_mock.assert_called_once_with(
            order_metrics={"pending_orders": 3},
            payment_metrics={"failed_payments": 0},
            shipping_metrics={"failed_shipments": 0},
            review_metrics={"flagged_reviews": 0},
            notification_metrics={"failed_notifications": 5},
            product_metrics={"products_without_images": 1},
        )

        log_mock.assert_called_once_with(
            alert_type="operational_alerts_generated",
            alert_message="Operational alerts detected in admin dashboard",
            metadata={
                "alerts_count": 2,
                "performed_by_id": None,
            },
        )

    def test_get_alerts_does_not_log_when_no_alerts_are_generated(self):
        """Do not create alert log entries when the payload contains no alerts."""
        expected_payload = {
            "alerts": [],
            "total_alerts": 0,
        }

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "AdminDashboardCacheService.get_alerts_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_order_operational_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_payment_operational_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_shipping_operational_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_review_operational_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_notification_operational_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_product_operational_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "build_admin_dashboard_alerts_payload",
            return_value=expected_payload,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "AdminDashboardLogService.log_dashboard_alert",
        ) as log_mock:
            payload = AdminDashboardAlertsService.get_alerts(
                performed_by=None,
            )

        self.assertEqual(payload, expected_payload)
        log_mock.assert_not_called()

    def test_get_alerts_uses_cache_for_identical_requests(self):
        """Reuse cached alerts payload for identical requests."""
        expected_payload = self._build_alerts_payload()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "AdminDashboardCacheService.get_alerts_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_order_operational_metrics",
            return_value={"pending_orders": 3},
        ) as order_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_payment_operational_metrics",
            return_value={"failed_payments": 0},
        ) as payment_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_shipping_operational_metrics",
            return_value={"failed_shipments": 0},
        ) as shipping_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_review_operational_metrics",
            return_value={"flagged_reviews": 0},
        ) as review_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_notification_operational_metrics",
            return_value={"failed_notifications": 5},
        ) as notification_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_product_operational_metrics",
            return_value={"products_without_images": 1},
        ) as product_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "build_admin_dashboard_alerts_payload",
            return_value=expected_payload,
        ) as builder_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "AdminDashboardLogService.log_dashboard_alert",
        ) as log_mock:
            result_1 = AdminDashboardAlertsService.get_alerts(
                performed_by=None,
            )
            result_2 = AdminDashboardAlertsService.get_alerts(
                performed_by=None,
            )

        self.assertEqual(result_1, result_2)

        order_mock.assert_called_once()
        payment_mock.assert_called_once()
        shipping_mock.assert_called_once()
        review_mock.assert_called_once()
        notification_mock.assert_called_once()
        product_mock.assert_called_once()
        builder_mock.assert_called_once()
        log_mock.assert_called_once()

    def test_get_alerts_rebuilds_after_cache_clear(self):
        """Rebuild alerts payload after cache is cleared."""
        expected_payload = self._build_alerts_payload()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "AdminDashboardCacheService.get_alerts_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_order_operational_metrics",
            return_value={"pending_orders": 3},
        ) as order_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_payment_operational_metrics",
            return_value={"failed_payments": 0},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_shipping_operational_metrics",
            return_value={"failed_shipments": 0},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_review_operational_metrics",
            return_value={"flagged_reviews": 0},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_notification_operational_metrics",
            return_value={"failed_notifications": 5},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_product_operational_metrics",
            return_value={"products_without_images": 1},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "build_admin_dashboard_alerts_payload",
            return_value=expected_payload,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "AdminDashboardLogService.log_dashboard_alert",
        ):
            AdminDashboardAlertsService.get_alerts(
                performed_by=None,
            )

            cache.clear()

            AdminDashboardAlertsService.get_alerts(
                performed_by=None,
            )

        self.assertEqual(order_mock.call_count, 2)

    def test_get_alerts_logs_performer_id_when_performer_is_provided(self):
        """Include performer id in alert log metadata when performer is provided."""
        expected_payload = self._build_alerts_payload()
        performed_by = type("User", (), {"id": 42})()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "AdminDashboardCacheService.get_alerts_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_order_operational_metrics",
            return_value={"pending_orders": 3},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_payment_operational_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_shipping_operational_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_review_operational_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_notification_operational_metrics",
            return_value={"failed_notifications": 5},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "get_product_operational_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "build_admin_dashboard_alerts_payload",
            return_value=expected_payload,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "AdminDashboardLogService.log_dashboard_alert",
        ) as log_mock:
            AdminDashboardAlertsService.get_alerts(
                performed_by=performed_by,
            )

        log_mock.assert_called_once_with(
            alert_type="operational_alerts_generated",
            alert_message="Operational alerts detected in admin dashboard",
            metadata={
                "alerts_count": 2,
                "performed_by_id": 42,
            },
        )

    def test_get_alerts_raises_unavailable_when_cache_layer_fails(self):
        """Raise operational alerts unavailable exception when cache orchestration fails."""
        with patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "AdminDashboardCacheService.get_alerts_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_alerts_service."
            "AdminDashboardCacheService.get_or_set",
            side_effect=Exception("cache failure"),
        ):
            with self.assertRaises(AdminDashboardOperationalAlertsUnavailableException):
                AdminDashboardAlertsService.get_alerts(
                    performed_by=None,
                )