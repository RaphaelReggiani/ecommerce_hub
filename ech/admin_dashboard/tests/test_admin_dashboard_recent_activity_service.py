from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase

from ech.admin_dashboard.exceptions import (
    AdminDashboardRecentActivityUnavailableException,
)
from ech.admin_dashboard.services.admin_dashboard_recent_activity_service import (
    AdminDashboardRecentActivityService,
)


class AdminDashboardRecentActivityServiceTestCase(TestCase):
    def setUp(self):
        cache.clear()

    def _build_activity_payload(self):
        return {
            "activities": [
                {
                    "source": "orders",
                    "type": "order",
                    "entity_id": "order-1",
                    "status": "pending",
                    "created_at": "2026-04-13T10:00:00Z",
                },
                {
                    "source": "payments",
                    "type": "payment",
                    "entity_id": "payment-1",
                    "status": "captured",
                    "created_at": "2026-04-13T09:50:00Z",
                },
                {
                    "source": "admin_dashboard",
                    "type": "admin_action",
                    "entity_id": "log-1",
                    "action_type": "bulk_review_moderation",
                    "target_module": "reviews",
                    "created_at": "2026-04-13T09:40:00Z",
                },
            ],
            "total": 3,
            "limit": 50,
        }

    def test_get_recent_activity_returns_expected_payload(self):
        """Return the expected aggregated recent activity payload."""
        expected_payload = self._build_activity_payload()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "AdminDashboardCacheService.get_activity_feed_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_order_activity",
            return_value=[expected_payload["activities"][0]],
        ) as order_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_payment_activity",
            return_value=[expected_payload["activities"][1]],
        ) as payment_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_shipping_activity",
            return_value=[],
        ) as shipping_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_review_activity",
            return_value=[],
        ) as review_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_notification_activity",
            return_value=[],
        ) as notification_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_admin_activity",
            return_value=[expected_payload["activities"][2]],
        ) as admin_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_product_activity",
            return_value=[],
        ) as product_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "build_recent_activity_payload",
            return_value=expected_payload,
        ) as builder_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "AdminDashboardLogService.log_dashboard_access",
        ) as log_mock:
            payload = AdminDashboardRecentActivityService.get_recent_activity(
                performed_by=None,
            )

        self.assertEqual(payload, expected_payload)

        order_mock.assert_called_once_with(limit=50)
        payment_mock.assert_called_once_with(limit=50)
        shipping_mock.assert_called_once_with(limit=50)
        review_mock.assert_called_once_with(limit=50)
        notification_mock.assert_called_once_with(limit=50)
        admin_mock.assert_called_once_with(limit=50)
        product_mock.assert_called_once_with(limit=50)

        builder_mock.assert_called_once_with(
            order_activity=[expected_payload["activities"][0]],
            payment_activity=[expected_payload["activities"][1]],
            shipping_activity=[],
            review_activity=[],
            notification_activity=[],
            admin_activity=[expected_payload["activities"][2]],
            product_activity=[],
            limit=50,
        )
        log_mock.assert_called_once_with(user=None)

    def test_get_recent_activity_uses_default_limit_when_omitted(self):
        """Use the default activity limit when no limit is provided."""
        expected_payload = self._build_activity_payload()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "AdminDashboardCacheService.get_activity_feed_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_order_activity",
            return_value=[],
        ) as order_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_payment_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_shipping_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_review_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_notification_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_admin_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_product_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "build_recent_activity_payload",
            return_value=expected_payload,
        ) as builder_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "AdminDashboardLogService.log_dashboard_access",
        ):
            AdminDashboardRecentActivityService.get_recent_activity(
                performed_by=None,
            )

        default_limit = AdminDashboardRecentActivityService.DEFAULT_ACTIVITY_LIMIT
        order_mock.assert_called_once_with(limit=default_limit)
        builder_mock.assert_called_once()
        self.assertEqual(builder_mock.call_args.kwargs["limit"], default_limit)

    def test_get_recent_activity_uses_cache_for_identical_requests(self):
        """Reuse cached recent activity payload for identical requests."""
        expected_payload = self._build_activity_payload()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "AdminDashboardCacheService.get_activity_feed_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_order_activity",
            return_value=[],
        ) as order_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_payment_activity",
            return_value=[],
        ) as payment_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_shipping_activity",
            return_value=[],
        ) as shipping_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_review_activity",
            return_value=[],
        ) as review_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_notification_activity",
            return_value=[],
        ) as notification_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_admin_activity",
            return_value=[],
        ) as admin_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_product_activity",
            return_value=[],
        ) as product_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "build_recent_activity_payload",
            return_value=expected_payload,
        ) as builder_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "AdminDashboardLogService.log_dashboard_access",
        ) as log_mock:
            result_1 = AdminDashboardRecentActivityService.get_recent_activity(
                limit=25,
                performed_by=None,
            )
            result_2 = AdminDashboardRecentActivityService.get_recent_activity(
                limit=25,
                performed_by=None,
            )

        self.assertEqual(result_1, result_2)

        order_mock.assert_called_once()
        payment_mock.assert_called_once()
        shipping_mock.assert_called_once()
        review_mock.assert_called_once()
        notification_mock.assert_called_once()
        admin_mock.assert_called_once()
        product_mock.assert_called_once()
        builder_mock.assert_called_once()
        log_mock.assert_called_once()

    def test_get_recent_activity_rebuilds_after_cache_clear(self):
        """Rebuild recent activity payload after cache clear."""
        expected_payload = self._build_activity_payload()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "AdminDashboardCacheService.get_activity_feed_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_order_activity",
            return_value=[],
        ) as order_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_payment_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_shipping_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_review_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_notification_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_admin_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_product_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "build_recent_activity_payload",
            return_value=expected_payload,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "AdminDashboardLogService.log_dashboard_access",
        ):
            AdminDashboardRecentActivityService.get_recent_activity(
                limit=10,
                performed_by=None,
            )

            cache.clear()

            AdminDashboardRecentActivityService.get_recent_activity(
                limit=10,
                performed_by=None,
            )

        self.assertEqual(order_mock.call_count, 2)

    def test_get_recent_activity_uses_distinct_cache_for_different_limits(self):
        """Use distinct cache entries for different requested limits."""
        payload_limit_10 = {
            "activities": [{"entity_id": "a"}],
            "total": 1,
            "limit": 10,
        }
        payload_limit_20 = {
            "activities": [{"entity_id": "b"}],
            "total": 1,
            "limit": 20,
        }

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "AdminDashboardCacheService.get_activity_feed_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_order_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_payment_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_shipping_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_review_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_notification_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_admin_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_product_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "build_recent_activity_payload",
            side_effect=[payload_limit_10, payload_limit_20],
        ) as builder_mock, patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "AdminDashboardLogService.log_dashboard_access",
        ):
            result_10 = AdminDashboardRecentActivityService.get_recent_activity(
                limit=10,
                performed_by=None,
            )
            result_20 = AdminDashboardRecentActivityService.get_recent_activity(
                limit=20,
                performed_by=None,
            )

        self.assertEqual(result_10, payload_limit_10)
        self.assertEqual(result_20, payload_limit_20)
        self.assertEqual(builder_mock.call_count, 2)

    def test_get_recent_activity_returns_empty_payload_structure(self):
        """Return an empty recent activity structure when builder returns empty payload."""
        expected_payload = {
            "activities": [],
            "total": 0,
            "limit": 50,
        }

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "AdminDashboardCacheService.get_activity_feed_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_order_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_payment_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_shipping_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_review_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_notification_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_admin_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_product_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "build_recent_activity_payload",
            return_value=expected_payload,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "AdminDashboardLogService.log_dashboard_access",
        ):
            payload = AdminDashboardRecentActivityService.get_recent_activity(
                performed_by=None,
            )

        self.assertEqual(payload, expected_payload)
        self.assertEqual(payload["activities"], [])
        self.assertEqual(payload["total"], 0)

    def test_get_recent_activity_logs_dashboard_access_with_performer(self):
        """Log dashboard access using the provided performer."""
        expected_payload = self._build_activity_payload()
        performed_by = object()

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "AdminDashboardCacheService.get_activity_feed_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_order_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_payment_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_shipping_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_review_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_notification_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_admin_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "get_recent_product_activity",
            return_value=[],
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "build_recent_activity_payload",
            return_value=expected_payload,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "AdminDashboardLogService.log_dashboard_access",
        ) as log_mock:
            AdminDashboardRecentActivityService.get_recent_activity(
                limit=15,
                performed_by=performed_by,
            )

        log_mock.assert_called_once_with(user=performed_by)

    def test_get_recent_activity_raises_unavailable_when_cache_layer_fails(self):
        """Raise recent activity unavailable exception when cache orchestration fails."""
        with patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "AdminDashboardCacheService.get_activity_feed_version",
            return_value=1,
        ), patch(
            "ech.admin_dashboard.services.admin_dashboard_recent_activity_service."
            "AdminDashboardCacheService.get_or_set",
            side_effect=Exception("cache failure"),
        ):
            with self.assertRaises(AdminDashboardRecentActivityUnavailableException):
                AdminDashboardRecentActivityService.get_recent_activity(
                    performed_by=None,
                )