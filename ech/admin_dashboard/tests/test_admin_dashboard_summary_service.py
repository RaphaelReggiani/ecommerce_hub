from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase

from ech.admin_dashboard.exceptions import (
    AdminDashboardSummaryUnavailableException,
)
from ech.admin_dashboard.services.admin_dashboard_summary_service import (
    AdminDashboardSummaryService,
)


class AdminDashboardSummaryServiceTestCase(TestCase):
    def setUp(self):
        cache.clear()

    def _build_summary_payload(self):
        return {
            "orders": {
                "total_orders": 10,
                "pending_orders": 2,
                "processing_orders": 3,
                "shipped_orders": 1,
                "delivered_orders": 3,
                "cancelled_orders": 1,
            },
            "payments": {
                "total_payments": 8,
                "captured_payments": 5,
                "failed_payments": 2,
                "refunded_payments": 1,
                "partially_refunded_payments": 0,
            },
            "shipping": {
                "total_shipments": 7,
                "pending_shipments": 1,
                "in_transit_shipments": 2,
                "delivered_shipments": 3,
                "failed_shipments": 1,
                "returned_shipments": 0,
            },
            "users": {
                "total_users": 20,
                "active_users": 18,
                "inactive_users": 2,
                "staff_users": 4,
                "customer_users": 16,
                "confirmed_users": 17,
                "unconfirmed_users": 3,
            },
            "reviews": {
                "total_reviews": 12,
                "pending_reviews": 2,
                "approved_reviews": 8,
                "rejected_reviews": 1,
                "hidden_reviews": 1,
                "cancelled_reviews": 0,
            },
            "products": {
                "total_products": 15,
                "active_products": 12,
                "inactive_products": 3,
            },
        }

    def test_get_summary_returns_expected_payload(self):
        """Return the expected aggregated summary payload."""
        expected_payload = self._build_summary_payload()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "AdminDashboardCacheService.get_dashboard_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_orders_summary_metrics",
            return_value=expected_payload["orders"],
        ) as orders_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_payments_summary_metrics",
            return_value=expected_payload["payments"],
        ) as payments_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_shipping_summary_metrics",
            return_value=expected_payload["shipping"],
        ) as shipping_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_users_summary_metrics",
            return_value=expected_payload["users"],
        ) as users_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_reviews_summary_metrics",
            return_value=expected_payload["reviews"],
        ) as reviews_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_products_summary_metrics",
            return_value=expected_payload["products"],
        ) as products_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "AdminDashboardLogService.log_dashboard_access",
        ) as log_mock:
            summary = AdminDashboardSummaryService.get_summary(
                performed_by=None,
            )

        self.assertEqual(summary, expected_payload)

        orders_mock.assert_called_once_with()
        payments_mock.assert_called_once_with()
        shipping_mock.assert_called_once_with()
        users_mock.assert_called_once_with()
        reviews_mock.assert_called_once_with()
        products_mock.assert_called_once_with()
        log_mock.assert_called_once_with(user=None)

    def test_get_summary_uses_cache_for_identical_requests(self):
        """Reuse cached payload for identical summary requests."""
        expected_payload = self._build_summary_payload()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "AdminDashboardCacheService.get_dashboard_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_orders_summary_metrics",
            return_value=expected_payload["orders"],
        ) as orders_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_payments_summary_metrics",
            return_value=expected_payload["payments"],
        ) as payments_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_shipping_summary_metrics",
            return_value=expected_payload["shipping"],
        ) as shipping_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_users_summary_metrics",
            return_value=expected_payload["users"],
        ) as users_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_reviews_summary_metrics",
            return_value=expected_payload["reviews"],
        ) as reviews_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_products_summary_metrics",
            return_value=expected_payload["products"],
        ) as products_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "AdminDashboardLogService.log_dashboard_access",
        ) as log_mock:
            result_1 = AdminDashboardSummaryService.get_summary(
                performed_by=None,
            )
            result_2 = AdminDashboardSummaryService.get_summary(
                performed_by=None,
            )

        self.assertEqual(result_1, result_2)

        orders_mock.assert_called_once()
        payments_mock.assert_called_once()
        shipping_mock.assert_called_once()
        users_mock.assert_called_once()
        reviews_mock.assert_called_once()
        products_mock.assert_called_once()
        log_mock.assert_called_once()

    def test_get_summary_rebuilds_after_cache_clear(self):
        """Rebuild summary payload after cache is cleared."""
        expected_payload = self._build_summary_payload()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "AdminDashboardCacheService.get_dashboard_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_orders_summary_metrics",
            return_value=expected_payload["orders"],
        ) as orders_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_payments_summary_metrics",
            return_value=expected_payload["payments"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_shipping_summary_metrics",
            return_value=expected_payload["shipping"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_users_summary_metrics",
            return_value=expected_payload["users"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_reviews_summary_metrics",
            return_value=expected_payload["reviews"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_products_summary_metrics",
            return_value=expected_payload["products"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "AdminDashboardLogService.log_dashboard_access",
        ):
            AdminDashboardSummaryService.get_summary(
                performed_by=None,
            )

            cache.clear()

            AdminDashboardSummaryService.get_summary(
                performed_by=None,
            )

        self.assertEqual(orders_mock.call_count, 2)

    def test_get_summary_returns_empty_metrics_structure(self):
        """Return an empty summary structure when all selectors return empty dictionaries."""
        expected_payload = {
            "orders": {},
            "payments": {},
            "shipping": {},
            "users": {},
            "reviews": {},
            "products": {},
        }

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "AdminDashboardCacheService.get_dashboard_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_orders_summary_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_payments_summary_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_shipping_summary_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_users_summary_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_reviews_summary_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_products_summary_metrics",
            return_value={},
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "AdminDashboardLogService.log_dashboard_access",
        ):
            summary = AdminDashboardSummaryService.get_summary(
                performed_by=None,
            )

        self.assertEqual(summary, expected_payload)
        self.assertEqual(summary["orders"], {})
        self.assertEqual(summary["payments"], {})
        self.assertEqual(summary["shipping"], {})
        self.assertEqual(summary["users"], {})
        self.assertEqual(summary["reviews"], {})
        self.assertEqual(summary["products"], {})

    def test_get_summary_logs_dashboard_access_with_performer(self):
        """Log dashboard access using the provided performer."""
        expected_payload = self._build_summary_payload()
        performed_by = object()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "AdminDashboardCacheService.get_dashboard_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_orders_summary_metrics",
            return_value=expected_payload["orders"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_payments_summary_metrics",
            return_value=expected_payload["payments"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_shipping_summary_metrics",
            return_value=expected_payload["shipping"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_users_summary_metrics",
            return_value=expected_payload["users"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_reviews_summary_metrics",
            return_value=expected_payload["reviews"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "get_products_summary_metrics",
            return_value=expected_payload["products"],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "AdminDashboardLogService.log_dashboard_access",
        ) as log_mock:
            AdminDashboardSummaryService.get_summary(
                performed_by=performed_by,
            )

        log_mock.assert_called_once_with(user=performed_by)

    def test_get_summary_raises_summary_unavailable_when_cache_layer_fails(self):
        """Raise summary unavailable exception when cache orchestration fails."""
        with patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "AdminDashboardCacheService.get_dashboard_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_summary_service."
            "AdminDashboardCacheService.get_or_set",
            side_effect=Exception("cache failure"),
        ):
            with self.assertRaises(AdminDashboardSummaryUnavailableException):
                AdminDashboardSummaryService.get_summary(
                    performed_by=None,
                )