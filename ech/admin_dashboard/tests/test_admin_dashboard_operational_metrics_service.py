from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase

from ech.admin_dashboard.exceptions import (
    AdminDashboardOperationalMetricsUnavailableException,
)
from ech.admin_dashboard.services.admin_dashboard_operational_metrics_service import (
    AdminDashboardOperationalMetricsService,
)


class AdminDashboardOperationalMetricsServiceTestCase(TestCase):
    def setUp(self):
        cache.clear()

    def _build_operational_payload(self):
        return {
            "orders": {
                "pending_orders": 4,
                "processing_orders": 2,
                "cancelled_orders": 1,
            },
            "payments": {
                "failed_payments": 2,
                "processing_payments": 3,
                "refunded_payments": 1,
            },
            "shipping": {
                "delayed_shipments": 1,
                "failed_shipments": 2,
                "in_transit_shipments": 4,
            },
            "reviews": {
                "pending_moderation": 3,
                "flagged_reviews": 2,
                "hidden_reviews": 1,
            },
            "notifications": {
                "failed_notifications": 5,
                "pending_notifications": 4,
                "unread_notifications": 8,
            },
            "products": {
                "low_stock_products": 3,
                "out_of_stock_products": 2,
                "products_without_images": 1,
            },
        }

    def test_get_operational_metrics_returns_expected_payload(self):
        """Return the expected aggregated operational metrics payload."""
        expected_payload = self._build_operational_payload()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "AdminDashboardCacheService.get_operational_metrics_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_order_operational_metrics",
            return_value=expected_payload["orders"],
        ) as orders_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_payment_operational_metrics",
            return_value=expected_payload["payments"],
        ) as payments_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_shipping_operational_metrics",
            return_value=expected_payload["shipping"],
        ) as shipping_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_review_operational_metrics",
            return_value=expected_payload["reviews"],
        ) as reviews_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_notification_operational_metrics",
            return_value=expected_payload["notifications"],
        ) as notifications_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_product_operational_metrics",
            return_value=expected_payload["products"],
        ) as products_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "build_operational_metrics_payload",
            return_value=expected_payload,
        ) as builder_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "AdminDashboardLogService.log_dashboard_access",
        ) as log_mock:
            payload = AdminDashboardOperationalMetricsService.get_operational_metrics(
                performed_by=None,
            )

        self.assertEqual(payload, expected_payload)

        orders_mock.assert_called_once_with()
        payments_mock.assert_called_once_with()
        shipping_mock.assert_called_once_with()
        reviews_mock.assert_called_once_with()
        notifications_mock.assert_called_once_with()
        products_mock.assert_called_once_with()

        builder_mock.assert_called_once_with(
            order_metrics=expected_payload["orders"],
            payment_metrics=expected_payload["payments"],
            shipping_metrics=expected_payload["shipping"],
            review_metrics=expected_payload["reviews"],
            notification_metrics=expected_payload["notifications"],
            product_metrics=expected_payload["products"],
        )
        log_mock.assert_called_once_with(user=None)

    def test_get_operational_metrics_uses_cache_for_identical_requests(self):
        """Reuse cached operational metrics payload for identical requests."""
        expected_payload = self._build_operational_payload()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "AdminDashboardCacheService.get_operational_metrics_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_order_operational_metrics",
            return_value=expected_payload["orders"],
        ) as orders_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_payment_operational_metrics",
            return_value=expected_payload["payments"],
        ) as payments_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_shipping_operational_metrics",
            return_value=expected_payload["shipping"],
        ) as shipping_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_review_operational_metrics",
            return_value=expected_payload["reviews"],
        ) as reviews_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_notification_operational_metrics",
            return_value=expected_payload["notifications"],
        ) as notifications_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_product_operational_metrics",
            return_value=expected_payload["products"],
        ) as products_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "build_operational_metrics_payload",
            return_value=expected_payload,
        ) as builder_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "AdminDashboardLogService.log_dashboard_access",
        ) as log_mock:
            result_1 = AdminDashboardOperationalMetricsService.get_operational_metrics(
                performed_by=None,
            )
            result_2 = AdminDashboardOperationalMetricsService.get_operational_metrics(
                performed_by=None,
            )

        self.assertEqual(result_1, result_2)

        orders_mock.assert_called_once()
        payments_mock.assert_called_once()
        shipping_mock.assert_called_once()
        reviews_mock.assert_called_once()
        notifications_mock.assert_called_once()
        products_mock.assert_called_once()
        builder_mock.assert_called_once()
        log_mock.assert_called_once()

    def test_get_operational_metrics_rebuilds_after_cache_clear(self):
        """Rebuild operational metrics payload after cache is cleared."""
        expected_payload = self._build_operational_payload()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "AdminDashboardCacheService.get_operational_metrics_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_order_operational_metrics",
            return_value=expected_payload["orders"],
        ) as orders_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_payment_operational_metrics",
            return_value=expected_payload["payments"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_shipping_operational_metrics",
            return_value=expected_payload["shipping"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_review_operational_metrics",
            return_value=expected_payload["reviews"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_notification_operational_metrics",
            return_value=expected_payload["notifications"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_product_operational_metrics",
            return_value=expected_payload["products"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "build_operational_metrics_payload",
            return_value=expected_payload,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "AdminDashboardLogService.log_dashboard_access",
        ):
            AdminDashboardOperationalMetricsService.get_operational_metrics(
                performed_by=None,
            )

            cache.clear()

            AdminDashboardOperationalMetricsService.get_operational_metrics(
                performed_by=None,
            )

        self.assertEqual(orders_mock.call_count, 2)

    def test_get_operational_metrics_returns_empty_structure(self):
        """Return an empty operational metrics structure when selectors return empty dictionaries."""
        expected_payload = {
            "orders": {},
            "payments": {},
            "shipping": {},
            "reviews": {},
            "notifications": {},
            "products": {},
        }

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "AdminDashboardCacheService.get_operational_metrics_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_order_operational_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_payment_operational_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_shipping_operational_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_review_operational_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_notification_operational_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_product_operational_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "build_operational_metrics_payload",
            return_value=expected_payload,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "AdminDashboardLogService.log_dashboard_access",
        ):
            payload = AdminDashboardOperationalMetricsService.get_operational_metrics(
                performed_by=None,
            )

        self.assertEqual(payload, expected_payload)

    def test_get_operational_metrics_logs_dashboard_access_with_performer(self):
        """Log dashboard access using the provided performer."""
        expected_payload = self._build_operational_payload()
        performed_by = object()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "AdminDashboardCacheService.get_operational_metrics_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_order_operational_metrics",
            return_value=expected_payload["orders"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_payment_operational_metrics",
            return_value=expected_payload["payments"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_shipping_operational_metrics",
            return_value=expected_payload["shipping"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_review_operational_metrics",
            return_value=expected_payload["reviews"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_notification_operational_metrics",
            return_value=expected_payload["notifications"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "get_product_operational_metrics",
            return_value=expected_payload["products"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "build_operational_metrics_payload",
            return_value=expected_payload,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "AdminDashboardLogService.log_dashboard_access",
        ) as log_mock:
            AdminDashboardOperationalMetricsService.get_operational_metrics(
                performed_by=performed_by,
            )

        log_mock.assert_called_once_with(user=performed_by)

    def test_get_operational_metrics_raises_unavailable_when_cache_layer_fails(self):
        """Raise operational metrics unavailable exception when cache orchestration fails."""
        with patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "AdminDashboardCacheService.get_operational_metrics_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_operational_metrics_service."
            "AdminDashboardCacheService.get_or_set",
            side_effect=Exception("cache failure"),
        ):
            with self.assertRaises(AdminDashboardOperationalMetricsUnavailableException):
                AdminDashboardOperationalMetricsService.get_operational_metrics(
                    performed_by=None,
                )