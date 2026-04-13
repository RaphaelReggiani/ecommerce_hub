import uuid
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import patch, call

from django.test import SimpleTestCase

from ech.admin_dashboard.exceptions import (
    AdminDashboardNotificationRetryException,
)
from ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service import (
    AdminDashboardBulkNotificationRetryService,
)


class AdminDashboardBulkNotificationRetryServiceTestCase(SimpleTestCase):
    def _build_notification(self, *, notification_id=None, status="failed"):
        """Build a lightweight notification-like object for testing."""
        return SimpleNamespace(
            id=notification_id or uuid.uuid4(),
            status=status,
        )

    def _build_user(self, user_id=None):
        """Build a lightweight user-like object for testing."""
        return SimpleNamespace(id=user_id or 10)

    def test_retry_notifications_raises_for_empty_notification_ids(self):
        """Raise exception when notification id list is empty."""
        with self.assertRaises(AdminDashboardNotificationRetryException) as context:
            AdminDashboardBulkNotificationRetryService.retry_notifications(
                notification_ids=[],
                performed_by=None,
            )

        self.assertEqual(
            str(context.exception),
            "Notification ID list cannot be empty",
        )

    def test_retry_notifications_raises_when_batch_exceeds_maximum(self):
        """Raise exception when retry batch exceeds maximum allowed size."""
        too_many_ids = [uuid.uuid4() for _ in range(
            AdminDashboardBulkNotificationRetryService.MAX_RETRY_BATCH + 1
        )]

        with self.assertRaises(AdminDashboardNotificationRetryException) as context:
            AdminDashboardBulkNotificationRetryService.retry_notifications(
                notification_ids=too_many_ids,
                performed_by=None,
            )

        self.assertEqual(
            str(context.exception),
            "Retry batch exceeds maximum allowed size",
        )

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.transaction.atomic",
        return_value=nullcontext(),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.Notification.objects"
    )
    def test_retry_notifications_raises_when_no_notifications_are_found(
        self,
        notification_objects_mock,
        atomic_mock,
    ):
        """Raise wrapped retry exception when no matching notifications are found."""
        notification_objects_mock.select_for_update.return_value.filter.return_value = []

        with self.assertRaises(AdminDashboardNotificationRetryException) as context:
            AdminDashboardBulkNotificationRetryService.retry_notifications(
                notification_ids=[uuid.uuid4()],
                performed_by=None,
            )

        self.assertEqual(
            str(context.exception),
            "Notification retry failed.",
        )

        notification_objects_mock.select_for_update.assert_called_once_with()
        notification_objects_mock.select_for_update.return_value.filter.assert_called_once()

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.transaction.atomic",
        return_value=nullcontext(),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.AdminDashboardCacheService.invalidate_activity_feed_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.AdminDashboardCacheService.invalidate_operational_metrics_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.AdminDashboardCacheService.invalidate_dashboard_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.AdminDashboardLogService.log_notification_retry"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.NotificationDeliveryService.deliver_notification",
        create=True,
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.Notification.objects"
    )
    def test_retry_notifications_retries_failed_notifications_successfully(
        self,
        notification_objects_mock,
        deliver_mock,
        log_mock,
        invalidate_dashboard_mock,
        invalidate_operational_mock,
        invalidate_activity_mock,
        atomic_mock,
    ):
        """Retry failed notifications successfully and invalidate related caches."""
        performed_by = self._build_user()
        notification_1 = self._build_notification(status="failed")
        notification_2 = self._build_notification(status="failed")
        notification_ids = [notification_1.id, notification_2.id]

        notification_objects_mock.select_for_update.return_value.filter.return_value = [
            notification_1,
            notification_2,
        ]

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.Notification.STATUS_FAILED",
            "failed",
        ):
            result = AdminDashboardBulkNotificationRetryService.retry_notifications(
                notification_ids=notification_ids,
                performed_by=performed_by,
            )

        self.assertEqual(
            result,
            {
                "retried_notifications": [notification_1.id, notification_2.id],
                "total_retried": 2,
            },
        )

        notification_objects_mock.select_for_update.assert_called_once_with()
        notification_objects_mock.select_for_update.return_value.filter.assert_called_once_with(
            id__in=notification_ids
        )

        deliver_mock.assert_has_calls(
            [
                call(
                    notification=notification_1,
                    performed_by=performed_by,
                ),
                call(
                    notification=notification_2,
                    performed_by=performed_by,
                ),
            ]
        )
        self.assertEqual(deliver_mock.call_count, 2)

        log_mock.assert_called_once_with(
            notification_ids=[notification_1.id, notification_2.id],
            performed_by=performed_by,
        )

        invalidate_dashboard_mock.assert_called_once_with()
        invalidate_operational_mock.assert_called_once_with()
        invalidate_activity_mock.assert_called_once_with()

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.transaction.atomic",
        return_value=nullcontext(),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.AdminDashboardCacheService.invalidate_activity_feed_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.AdminDashboardCacheService.invalidate_operational_metrics_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.AdminDashboardCacheService.invalidate_dashboard_cache"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.AdminDashboardLogService.log_notification_retry"
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.NotificationDeliveryService.deliver_notification",
        create=True,
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.Notification.objects"
    )
    def test_retry_notifications_skips_non_failed_notifications(
        self,
        notification_objects_mock,
        deliver_mock,
        log_mock,
        invalidate_dashboard_mock,
        invalidate_operational_mock,
        invalidate_activity_mock,
        atomic_mock,
    ):
        """Skip notifications that are not in failed status."""
        failed_notification = self._build_notification(status="failed")
        unread_notification = self._build_notification(status="unread")
        notification_ids = [failed_notification.id, unread_notification.id]

        notification_objects_mock.select_for_update.return_value.filter.return_value = [
            failed_notification,
            unread_notification,
        ]

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.Notification.STATUS_FAILED",
            "failed",
        ):
            result = AdminDashboardBulkNotificationRetryService.retry_notifications(
                notification_ids=notification_ids,
                performed_by=None,
            )

        self.assertEqual(
            result,
            {
                "retried_notifications": [failed_notification.id],
                "total_retried": 1,
            },
        )

        deliver_mock.assert_called_once_with(
            notification=failed_notification,
            performed_by=None,
        )

        log_mock.assert_called_once_with(
            notification_ids=[failed_notification.id],
            performed_by=None,
        )

        invalidate_dashboard_mock.assert_called_once_with()
        invalidate_operational_mock.assert_called_once_with()
        invalidate_activity_mock.assert_called_once_with()

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.transaction.atomic",
        return_value=nullcontext(),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.NotificationDeliveryService.deliver_notification",
        side_effect=Exception("delivery failure"),
        create=True,
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.Notification.objects"
    )
    def test_retry_notifications_wraps_delivery_errors(
        self,
        notification_objects_mock,
        deliver_mock,
        atomic_mock,
    ):
        """Wrap internal delivery errors with the default retry exception."""
        notification = self._build_notification(status="failed")

        notification_objects_mock.select_for_update.return_value.filter.return_value = [
            notification,
        ]

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.Notification.STATUS_FAILED",
            "failed",
        ):
            with self.assertRaises(AdminDashboardNotificationRetryException) as context:
                AdminDashboardBulkNotificationRetryService.retry_notifications(
                    notification_ids=[notification.id],
                    performed_by=None,
                )

        self.assertEqual(
            str(context.exception),
            "Notification retry failed.",
        )

        deliver_mock.assert_called_once_with(
            notification=notification,
            performed_by=None,
        )

    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.transaction.atomic",
        return_value=nullcontext(),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.AdminDashboardLogService.log_notification_retry",
        side_effect=Exception("log failure"),
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.NotificationDeliveryService.deliver_notification",
        create=True,
    )
    @patch(
        "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.Notification.objects"
    )
    def test_retry_notifications_wraps_log_errors(
        self,
        notification_objects_mock,
        deliver_mock,
        log_mock,
        atomic_mock,
    ):
        """Wrap logging errors with the default retry exception."""
        notification = self._build_notification(status="failed")

        notification_objects_mock.select_for_update.return_value.filter.return_value = [
            notification,
        ]

        with patch(
            "ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service.Notification.STATUS_FAILED",
            "failed",
        ):
            with self.assertRaises(AdminDashboardNotificationRetryException) as context:
                AdminDashboardBulkNotificationRetryService.retry_notifications(
                    notification_ids=[notification.id],
                    performed_by=None,
                )

        self.assertEqual(
            str(context.exception),
            "Notification retry failed.",
        )

        deliver_mock.assert_called_once_with(
            notification=notification,
            performed_by=None,
        )