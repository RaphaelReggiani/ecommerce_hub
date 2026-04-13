from django.test import SimpleTestCase

from ech.admin_dashboard.constants.messages import (
    ADMIN_DASHBOARD_ACCESS_DENIED,
    ADMIN_DASHBOARD_DATA_UNAVAILABLE,
    ADMIN_DASHBOARD_SUMMARY_UNAVAILABLE,
    ADMIN_OPERATIONAL_METRICS_UNAVAILABLE,
    ADMIN_RECENT_ACTIVITY_UNAVAILABLE,
    ADMIN_OPERATIONAL_ALERTS_UNAVAILABLE,
    ADMIN_ORDER_BULK_ACTION_FAILED,
    ADMIN_ORDER_BULK_ACTION_PERMISSION_DENIED,
    ADMIN_ORDER_BULK_LIMIT_EXCEEDED,
    ADMIN_REVIEW_BULK_MODERATION_FAILED,
    ADMIN_REVIEW_BULK_MODERATION_PERMISSION_DENIED,
    ADMIN_REVIEW_BULK_LIMIT_EXCEEDED,
    ADMIN_NOTIFICATION_RETRY_FAILED,
    ADMIN_NOTIFICATION_RETRY_PERMISSION_DENIED,
    ADMIN_NOTIFICATION_RETRY_LIMIT_EXCEEDED,
    ADMIN_IDEMPOTENCY_KEY_CONFLICT,
)
from ech.admin_dashboard.exceptions import (
    AdminDashboardException,
    AdminDashboardAccessDeniedException,
    AdminDashboardUnavailableException,
    AdminDashboardSummaryUnavailableException,
    AdminDashboardOperationalMetricsUnavailableException,
    AdminDashboardRecentActivityUnavailableException,
    AdminDashboardOperationalAlertsUnavailableException,
    AdminDashboardBulkOrderActionPermissionDeniedException,
    AdminDashboardBulkOrderActionException,
    AdminDashboardBulkOrderLimitExceededException,
    AdminDashboardBulkReviewModerationPermissionDeniedException,
    AdminDashboardReviewBulkModerationException,
    AdminDashboardBulkReviewLimitExceededException,
    AdminDashboardNotificationRetryPermissionDeniedException,
    AdminDashboardNotificationRetryException,
    AdminDashboardNotificationRetryLimitExceededException,
    IdempotencyConflictException,
)


class AdminDashboardExceptionTestCase(SimpleTestCase):
    def test_admin_dashboard_exception_inherits_from_exception(self):
        """Inherit the base admin dashboard exception from Python Exception."""
        self.assertTrue(issubclass(AdminDashboardException, Exception))

    def test_admin_dashboard_exception_accepts_custom_message(self):
        """Store a custom message in the base admin dashboard exception."""
        exception = AdminDashboardException("Custom admin dashboard error")

        self.assertEqual(str(exception), "Custom admin dashboard error")


class AdminDashboardAccessDeniedExceptionTestCase(SimpleTestCase):
    def test_access_denied_exception_inherits_from_admin_dashboard_exception(self):
        """Inherit access denied exception from AdminDashboardException."""
        self.assertTrue(
            issubclass(
                AdminDashboardAccessDeniedException,
                AdminDashboardException,
            )
        )

    def test_access_denied_exception_uses_default_message(self):
        """Use the default access denied message."""
        exception = AdminDashboardAccessDeniedException()

        self.assertEqual(str(exception), ADMIN_DASHBOARD_ACCESS_DENIED)

    def test_access_denied_exception_accepts_custom_message(self):
        """Allow a custom message for access denied exception."""
        exception = AdminDashboardAccessDeniedException(
            "Custom access denied"
        )

        self.assertEqual(str(exception), "Custom access denied")


class AdminDashboardUnavailableExceptionTestCase(SimpleTestCase):
    def test_unavailable_exception_inherits_from_admin_dashboard_exception(self):
        """Inherit unavailable exception from AdminDashboardException."""
        self.assertTrue(
            issubclass(
                AdminDashboardUnavailableException,
                AdminDashboardException,
            )
        )

    def test_unavailable_exception_uses_default_message(self):
        """Use the default dashboard unavailable message."""
        exception = AdminDashboardUnavailableException()

        self.assertEqual(str(exception), ADMIN_DASHBOARD_DATA_UNAVAILABLE)

    def test_unavailable_exception_accepts_custom_message(self):
        """Allow a custom message for unavailable exception."""
        exception = AdminDashboardUnavailableException(
            "Custom dashboard unavailable"
        )

        self.assertEqual(str(exception), "Custom dashboard unavailable")


class AdminDashboardSummaryUnavailableExceptionTestCase(SimpleTestCase):
    def test_summary_unavailable_exception_inherits_from_admin_dashboard_exception(
        self,
    ):
        """Inherit summary unavailable exception from AdminDashboardException."""
        self.assertTrue(
            issubclass(
                AdminDashboardSummaryUnavailableException,
                AdminDashboardException,
            )
        )

    def test_summary_unavailable_exception_uses_default_message(self):
        """Use the default summary unavailable message."""
        exception = AdminDashboardSummaryUnavailableException()

        self.assertEqual(str(exception), ADMIN_DASHBOARD_SUMMARY_UNAVAILABLE)

    def test_summary_unavailable_exception_accepts_custom_message(self):
        """Allow a custom message for summary unavailable exception."""
        exception = AdminDashboardSummaryUnavailableException(
            "Custom summary unavailable"
        )

        self.assertEqual(str(exception), "Custom summary unavailable")


class AdminDashboardOperationalMetricsUnavailableExceptionTestCase(SimpleTestCase):
    def test_operational_metrics_unavailable_exception_inherits_from_admin_dashboard_exception(
        self,
    ):
        """Inherit operational metrics unavailable exception from AdminDashboardException."""
        self.assertTrue(
            issubclass(
                AdminDashboardOperationalMetricsUnavailableException,
                AdminDashboardException,
            )
        )

    def test_operational_metrics_unavailable_exception_uses_default_message(
        self,
    ):
        """Use the default operational metrics unavailable message."""
        exception = AdminDashboardOperationalMetricsUnavailableException()

        self.assertEqual(str(exception), ADMIN_OPERATIONAL_METRICS_UNAVAILABLE)

    def test_operational_metrics_unavailable_exception_accepts_custom_message(
        self,
    ):
        """Allow a custom message for operational metrics unavailable exception."""
        exception = AdminDashboardOperationalMetricsUnavailableException(
            "Custom operational metrics unavailable"
        )

        self.assertEqual(str(exception), "Custom operational metrics unavailable")


class AdminDashboardRecentActivityUnavailableExceptionTestCase(SimpleTestCase):
    def test_recent_activity_unavailable_exception_inherits_from_admin_dashboard_exception(
        self,
    ):
        """Inherit recent activity unavailable exception from AdminDashboardException."""
        self.assertTrue(
            issubclass(
                AdminDashboardRecentActivityUnavailableException,
                AdminDashboardException,
            )
        )

    def test_recent_activity_unavailable_exception_uses_default_message(
        self,
    ):
        """Use the default recent activity unavailable message."""
        exception = AdminDashboardRecentActivityUnavailableException()

        self.assertEqual(str(exception), ADMIN_RECENT_ACTIVITY_UNAVAILABLE)

    def test_recent_activity_unavailable_exception_accepts_custom_message(
        self,
    ):
        """Allow a custom message for recent activity unavailable exception."""
        exception = AdminDashboardRecentActivityUnavailableException(
            "Custom recent activity unavailable"
        )

        self.assertEqual(str(exception), "Custom recent activity unavailable")


class AdminDashboardOperationalAlertsUnavailableExceptionTestCase(SimpleTestCase):
    def test_operational_alerts_unavailable_exception_inherits_from_admin_dashboard_exception(
        self,
    ):
        """Inherit operational alerts unavailable exception from AdminDashboardException."""
        self.assertTrue(
            issubclass(
                AdminDashboardOperationalAlertsUnavailableException,
                AdminDashboardException,
            )
        )

    def test_operational_alerts_unavailable_exception_uses_default_message(
        self,
    ):
        """Use the default operational alerts unavailable message."""
        exception = AdminDashboardOperationalAlertsUnavailableException()

        self.assertEqual(str(exception), ADMIN_OPERATIONAL_ALERTS_UNAVAILABLE)

    def test_operational_alerts_unavailable_exception_accepts_custom_message(
        self,
    ):
        """Allow a custom message for operational alerts unavailable exception."""
        exception = AdminDashboardOperationalAlertsUnavailableException(
            "Custom operational alerts unavailable"
        )

        self.assertEqual(str(exception), "Custom operational alerts unavailable")


class AdminDashboardBulkOrderActionPermissionDeniedExceptionTestCase(SimpleTestCase):
    def test_bulk_order_permission_denied_exception_inherits_from_admin_dashboard_exception(
        self,
    ):
        """Inherit bulk order permission denied exception from AdminDashboardException."""
        self.assertTrue(
            issubclass(
                AdminDashboardBulkOrderActionPermissionDeniedException,
                AdminDashboardException,
            )
        )

    def test_bulk_order_permission_denied_exception_uses_default_message(
        self,
    ):
        """Use the default bulk order permission denied message."""
        exception = AdminDashboardBulkOrderActionPermissionDeniedException()

        self.assertEqual(
            str(exception),
            ADMIN_ORDER_BULK_ACTION_PERMISSION_DENIED,
        )

    def test_bulk_order_permission_denied_exception_accepts_custom_message(
        self,
    ):
        """Allow a custom message for bulk order permission denied exception."""
        exception = AdminDashboardBulkOrderActionPermissionDeniedException(
            "Custom bulk order permission denied"
        )

        self.assertEqual(
            str(exception),
            "Custom bulk order permission denied",
        )


class AdminDashboardBulkOrderActionExceptionTestCase(SimpleTestCase):
    def test_bulk_order_action_exception_inherits_from_admin_dashboard_exception(
        self,
    ):
        """Inherit bulk order action exception from AdminDashboardException."""
        self.assertTrue(
            issubclass(
                AdminDashboardBulkOrderActionException,
                AdminDashboardException,
            )
        )

    def test_bulk_order_action_exception_uses_default_message(self):
        """Use the default bulk order action failed message."""
        exception = AdminDashboardBulkOrderActionException()

        self.assertEqual(str(exception), ADMIN_ORDER_BULK_ACTION_FAILED)

    def test_bulk_order_action_exception_accepts_custom_message(self):
        """Allow a custom message for bulk order action exception."""
        exception = AdminDashboardBulkOrderActionException(
            "Custom bulk order action failed"
        )

        self.assertEqual(str(exception), "Custom bulk order action failed")


class AdminDashboardBulkOrderLimitExceededExceptionTestCase(SimpleTestCase):
    def test_bulk_order_limit_exceeded_exception_inherits_from_admin_dashboard_exception(
        self,
    ):
        """Inherit bulk order limit exceeded exception from AdminDashboardException."""
        self.assertTrue(
            issubclass(
                AdminDashboardBulkOrderLimitExceededException,
                AdminDashboardException,
            )
        )

    def test_bulk_order_limit_exceeded_exception_uses_default_message(self):
        """Use the default bulk order limit exceeded message."""
        exception = AdminDashboardBulkOrderLimitExceededException()

        self.assertEqual(str(exception), ADMIN_ORDER_BULK_LIMIT_EXCEEDED)

    def test_bulk_order_limit_exceeded_exception_accepts_custom_message(self):
        """Allow a custom message for bulk order limit exceeded exception."""
        exception = AdminDashboardBulkOrderLimitExceededException(
            "Custom bulk order limit exceeded"
        )

        self.assertEqual(str(exception), "Custom bulk order limit exceeded")


class AdminDashboardBulkReviewModerationPermissionDeniedExceptionTestCase(
    SimpleTestCase
):
    def test_bulk_review_permission_denied_exception_inherits_from_admin_dashboard_exception(
        self,
    ):
        """Inherit bulk review moderation permission denied exception from AdminDashboardException."""
        self.assertTrue(
            issubclass(
                AdminDashboardBulkReviewModerationPermissionDeniedException,
                AdminDashboardException,
            )
        )

    def test_bulk_review_permission_denied_exception_uses_default_message(
        self,
    ):
        """Use the default bulk review moderation permission denied message."""
        exception = (
            AdminDashboardBulkReviewModerationPermissionDeniedException()
        )

        self.assertEqual(
            str(exception),
            ADMIN_REVIEW_BULK_MODERATION_PERMISSION_DENIED,
        )

    def test_bulk_review_permission_denied_exception_accepts_custom_message(
        self,
    ):
        """Allow a custom message for bulk review moderation permission denied exception."""
        exception = (
            AdminDashboardBulkReviewModerationPermissionDeniedException(
                "Custom bulk review moderation permission denied"
            )
        )

        self.assertEqual(
            str(exception),
            "Custom bulk review moderation permission denied",
        )


class AdminDashboardReviewBulkModerationExceptionTestCase(SimpleTestCase):
    def test_review_bulk_moderation_exception_inherits_from_admin_dashboard_exception(
        self,
    ):
        """Inherit review bulk moderation exception from AdminDashboardException."""
        self.assertTrue(
            issubclass(
                AdminDashboardReviewBulkModerationException,
                AdminDashboardException,
            )
        )

    def test_review_bulk_moderation_exception_uses_default_message(self):
        """Use the default review bulk moderation failed message."""
        exception = AdminDashboardReviewBulkModerationException()

        self.assertEqual(str(exception), ADMIN_REVIEW_BULK_MODERATION_FAILED)

    def test_review_bulk_moderation_exception_accepts_custom_message(self):
        """Allow a custom message for review bulk moderation exception."""
        exception = AdminDashboardReviewBulkModerationException(
            "Custom review bulk moderation failed"
        )

        self.assertEqual(
            str(exception),
            "Custom review bulk moderation failed",
        )


class AdminDashboardBulkReviewLimitExceededExceptionTestCase(SimpleTestCase):
    def test_bulk_review_limit_exceeded_exception_inherits_from_admin_dashboard_exception(
        self,
    ):
        """Inherit bulk review limit exceeded exception from AdminDashboardException."""
        self.assertTrue(
            issubclass(
                AdminDashboardBulkReviewLimitExceededException,
                AdminDashboardException,
            )
        )

    def test_bulk_review_limit_exceeded_exception_uses_default_message(
        self,
    ):
        """Use the default bulk review limit exceeded message."""
        exception = AdminDashboardBulkReviewLimitExceededException()

        self.assertEqual(str(exception), ADMIN_REVIEW_BULK_LIMIT_EXCEEDED)

    def test_bulk_review_limit_exceeded_exception_accepts_custom_message(
        self,
    ):
        """Allow a custom message for bulk review limit exceeded exception."""
        exception = AdminDashboardBulkReviewLimitExceededException(
            "Custom bulk review limit exceeded"
        )

        self.assertEqual(str(exception), "Custom bulk review limit exceeded")


class AdminDashboardNotificationRetryPermissionDeniedExceptionTestCase(
    SimpleTestCase
):
    def test_notification_retry_permission_denied_exception_inherits_from_admin_dashboard_exception(
        self,
    ):
        """Inherit notification retry permission denied exception from AdminDashboardException."""
        self.assertTrue(
            issubclass(
                AdminDashboardNotificationRetryPermissionDeniedException,
                AdminDashboardException,
            )
        )

    def test_notification_retry_permission_denied_exception_uses_default_message(
        self,
    ):
        """Use the default notification retry permission denied message."""
        exception = AdminDashboardNotificationRetryPermissionDeniedException()

        self.assertEqual(
            str(exception),
            ADMIN_NOTIFICATION_RETRY_PERMISSION_DENIED,
        )

    def test_notification_retry_permission_denied_exception_accepts_custom_message(
        self,
    ):
        """Allow a custom message for notification retry permission denied exception."""
        exception = AdminDashboardNotificationRetryPermissionDeniedException(
            "Custom notification retry permission denied"
        )

        self.assertEqual(
            str(exception),
            "Custom notification retry permission denied",
        )


class AdminDashboardNotificationRetryExceptionTestCase(SimpleTestCase):
    def test_notification_retry_exception_inherits_from_admin_dashboard_exception(
        self,
    ):
        """Inherit notification retry exception from AdminDashboardException."""
        self.assertTrue(
            issubclass(
                AdminDashboardNotificationRetryException,
                AdminDashboardException,
            )
        )

    def test_notification_retry_exception_uses_default_message(self):
        """Use the default notification retry failed message."""
        exception = AdminDashboardNotificationRetryException()

        self.assertEqual(str(exception), ADMIN_NOTIFICATION_RETRY_FAILED)

    def test_notification_retry_exception_accepts_custom_message(self):
        """Allow a custom message for notification retry exception."""
        exception = AdminDashboardNotificationRetryException(
            "Custom notification retry failed"
        )

        self.assertEqual(str(exception), "Custom notification retry failed")


class AdminDashboardNotificationRetryLimitExceededExceptionTestCase(
    SimpleTestCase
):
    def test_notification_retry_limit_exceeded_exception_inherits_from_admin_dashboard_exception(
        self,
    ):
        """Inherit notification retry limit exceeded exception from AdminDashboardException."""
        self.assertTrue(
            issubclass(
                AdminDashboardNotificationRetryLimitExceededException,
                AdminDashboardException,
            )
        )

    def test_notification_retry_limit_exceeded_exception_uses_default_message(
        self,
    ):
        """Use the default notification retry limit exceeded message."""
        exception = AdminDashboardNotificationRetryLimitExceededException()

        self.assertEqual(
            str(exception),
            ADMIN_NOTIFICATION_RETRY_LIMIT_EXCEEDED,
        )

    def test_notification_retry_limit_exceeded_exception_accepts_custom_message(
        self,
    ):
        """Allow a custom message for notification retry limit exceeded exception."""
        exception = AdminDashboardNotificationRetryLimitExceededException(
            "Custom notification retry limit exceeded"
        )

        self.assertEqual(
            str(exception),
            "Custom notification retry limit exceeded",
        )


class IdempotencyConflictExceptionTestCase(SimpleTestCase):
    def test_idempotency_conflict_exception_inherits_from_admin_dashboard_exception(
        self,
    ):
        """Inherit idempotency conflict exception from AdminDashboardException."""
        self.assertTrue(
            issubclass(
                IdempotencyConflictException,
                AdminDashboardException,
            )
        )

    def test_idempotency_conflict_exception_uses_default_message(self):
        """Use the default idempotency conflict message."""
        exception = IdempotencyConflictException()

        self.assertEqual(str(exception), ADMIN_IDEMPOTENCY_KEY_CONFLICT)

    def test_idempotency_conflict_exception_accepts_custom_message(self):
        """Allow a custom message for idempotency conflict exception."""
        exception = IdempotencyConflictException(
            "Custom idempotency conflict"
        )

        self.assertEqual(str(exception), "Custom idempotency conflict")