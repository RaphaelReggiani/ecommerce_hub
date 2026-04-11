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


class AdminDashboardException(Exception):
    """
    Base exception for the admin dashboard domain.
    """
    pass


class AdminDashboardAccessDeniedException(AdminDashboardException):
    """
    Raised when a user attempts to access the admin dashboard
    without proper permissions.
    """

    def __init__(self, message=ADMIN_DASHBOARD_ACCESS_DENIED):
        super().__init__(message)


class AdminDashboardUnavailableException(AdminDashboardException):
    """
    Raised when dashboard data cannot be retrieved.
    """

    def __init__(self, message=ADMIN_DASHBOARD_DATA_UNAVAILABLE):
        super().__init__(message)


class AdminDashboardSummaryUnavailableException(AdminDashboardException):
    """
    Raised when dashboard summary metrics cannot be retrieved.
    """

    def __init__(self, message=ADMIN_DASHBOARD_SUMMARY_UNAVAILABLE):
        super().__init__(message)


class AdminDashboardOperationalMetricsUnavailableException(AdminDashboardException):
    """
    Raised when operational metrics cannot be retrieved.
    """

    def __init__(self, message=ADMIN_OPERATIONAL_METRICS_UNAVAILABLE):
        super().__init__(message)


class AdminDashboardRecentActivityUnavailableException(AdminDashboardException):
    """
    Raised when recent activity feed cannot be retrieved.
    """

    def __init__(self, message=ADMIN_RECENT_ACTIVITY_UNAVAILABLE):
        super().__init__(message)


class AdminDashboardOperationalAlertsUnavailableException(AdminDashboardException):
    """
    Raised when operational alerts cannot be retrieved.
    """

    def __init__(self, message=ADMIN_OPERATIONAL_ALERTS_UNAVAILABLE):
        super().__init__(message)


class AdminDashboardBulkOrderActionPermissionDeniedException(AdminDashboardException):
    """
    Raised when a user attempts to execute bulk order actions
    without sufficient permissions.
    """

    def __init__(self, message=ADMIN_ORDER_BULK_ACTION_PERMISSION_DENIED):
        super().__init__(message)


class AdminDashboardBulkOrderActionException(AdminDashboardException):
    """
    Raised when a bulk order operation fails.
    """

    def __init__(self, message=ADMIN_ORDER_BULK_ACTION_FAILED):
        super().__init__(message)


class AdminDashboardBulkOrderLimitExceededException(AdminDashboardException):
    """
    Raised when a bulk order operation exceeds the allowed limit.
    """

    def __init__(self, message=ADMIN_ORDER_BULK_LIMIT_EXCEEDED):
        super().__init__(message)


class AdminDashboardBulkReviewModerationPermissionDeniedException(AdminDashboardException):
    """
    Raised when a user attempts to moderate reviews
    without proper permissions.
    """

    def __init__(self, message=ADMIN_REVIEW_BULK_MODERATION_PERMISSION_DENIED):
        super().__init__(message)


class AdminDashboardReviewBulkModerationException(AdminDashboardException):
    """
    Raised when a bulk review moderation operation fails.
    """

    def __init__(self, message=ADMIN_REVIEW_BULK_MODERATION_FAILED):
        super().__init__(message)


class AdminDashboardBulkReviewLimitExceededException(AdminDashboardException):
    """
    Raised when a review moderation operation exceeds
    the allowed limit.
    """

    def __init__(self, message=ADMIN_REVIEW_BULK_LIMIT_EXCEEDED):
        super().__init__(message)


class AdminDashboardNotificationRetryPermissionDeniedException(AdminDashboardException):
    """
    Raised when a user attempts to retry notifications
    without proper permissions.
    """

    def __init__(self, message=ADMIN_NOTIFICATION_RETRY_PERMISSION_DENIED):
        super().__init__(message)


class AdminDashboardNotificationRetryException(AdminDashboardException):
    """
    Raised when retrying notifications fails.
    """

    def __init__(self, message=ADMIN_NOTIFICATION_RETRY_FAILED):
        super().__init__(message)


class AdminDashboardNotificationRetryLimitExceededException(AdminDashboardException):
    """
    Raised when a notification retry operation exceeds
    the allowed retry batch size.
    """

    def __init__(self, message=ADMIN_NOTIFICATION_RETRY_LIMIT_EXCEEDED):
        super().__init__(message)


class IdempotencyConflictException(AdminDashboardException):
    """
    Raised when an idempotency key is reused with a
    different payload.
    """

    def __init__(self, message=ADMIN_IDEMPOTENCY_KEY_CONFLICT):
        super().__init__(message)