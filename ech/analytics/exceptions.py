from ech.analytics.constants.messages import (
    ANALYTICS_SNAPSHOT_NOT_FOUND,
    ANALYTICS_SNAPSHOT_ACCESS_DENIED,
    ANALYTICS_SNAPSHOT_ALREADY_EXISTS,
    ANALYTICS_SNAPSHOT_CREATION_FAILED,
    ANALYTICS_SNAPSHOT_REFRESH_FAILED,
    ANALYTICS_SNAPSHOT_REFRESH_NOT_ALLOWED,
    ANALYTICS_DASHBOARD_DATA_UNAVAILABLE,
    ANALYTICS_SALES_DATA_UNAVAILABLE,
    ANALYTICS_ORDER_ANALYTICS_UNAVAILABLE,
    ANALYTICS_PAYMENT_ANALYTICS_UNAVAILABLE,
    ANALYTICS_SHIPPING_ANALYTICS_UNAVAILABLE,
    ANALYTICS_PRODUCT_ANALYTICS_UNAVAILABLE,
    ANALYTICS_CUSTOMER_ANALYTICS_UNAVAILABLE,
    ANALYTICS_IDEMPOTENCY_KEY_CONFLICT,
)


class AnalyticsException(Exception):
    """
    Base exception for the analytics domain.
    """
    pass


class AnalyticsSnapshotNotFoundException(AnalyticsException):
    """
    Raised when an analytics snapshot cannot be found.
    """

    def __init__(self, message=ANALYTICS_SNAPSHOT_NOT_FOUND):
        super().__init__(message)


class AnalyticsSnapshotAccessDeniedException(AnalyticsException):
    """
    Raised when a user attempts to access a snapshot without permission.
    """

    def __init__(self, message=ANALYTICS_SNAPSHOT_ACCESS_DENIED):
        super().__init__(message)


class AnalyticsSnapshotAlreadyExistsException(AnalyticsException):
    """
    Raised when attempting to generate a snapshot that already exists
    for the same period.
    """

    def __init__(self, message=ANALYTICS_SNAPSHOT_ALREADY_EXISTS):
        super().__init__(message)


class AnalyticsSnapshotCreationException(AnalyticsException):
    """
    Raised when snapshot generation fails.
    """

    def __init__(self, message=ANALYTICS_SNAPSHOT_CREATION_FAILED):
        super().__init__(message)


class AnalyticsSnapshotRefreshException(AnalyticsException):
    """
    Raised when snapshot refresh fails.
    """

    def __init__(self, message=ANALYTICS_SNAPSHOT_REFRESH_FAILED):
        super().__init__(message)


class AnalyticsSnapshotRefreshNotAllowedException(AnalyticsException):
    """
    Raised when a snapshot refresh is not allowed in the current state.
    """

    def __init__(self, message=ANALYTICS_SNAPSHOT_REFRESH_NOT_ALLOWED):
        super().__init__(message)


class AnalyticsDashboardUnavailableException(AnalyticsException):
    """
    Raised when dashboard analytics data is unavailable.
    """

    def __init__(self, message=ANALYTICS_DASHBOARD_DATA_UNAVAILABLE):
        super().__init__(message)


class AnalyticsSalesUnavailableException(AnalyticsException):
    """
    Raised when sales analytics data is unavailable.
    """

    def __init__(self, message=ANALYTICS_SALES_DATA_UNAVAILABLE):
        super().__init__(message)


class AnalyticsOrderUnavailableException(AnalyticsException):
    """
    Raised when order funnel analytics data is unavailable.
    """

    def __init__(self, message=ANALYTICS_ORDER_ANALYTICS_UNAVAILABLE):
        super().__init__(message)


class AnalyticsPaymentUnavailableException(AnalyticsException):
    """
    Raised when payment analytics data is unavailable.
    """

    def __init__(self, message=ANALYTICS_PAYMENT_ANALYTICS_UNAVAILABLE):
        super().__init__(message)


class AnalyticsShippingUnavailableException(AnalyticsException):
    """
    Raised when shipping analytics data is unavailable.
    """

    def __init__(self, message=ANALYTICS_SHIPPING_ANALYTICS_UNAVAILABLE):
        super().__init__(message)


class AnalyticsProductUnavailableException(AnalyticsException):
    """
    Raised when product analytics data is unavailable.
    """

    def __init__(self, message=ANALYTICS_PRODUCT_ANALYTICS_UNAVAILABLE):
        super().__init__(message)


class AnalyticsCustomerUnavailableException(AnalyticsException):
    """
    Raised when customer analytics data is unavailable.
    """

    def __init__(self, message=ANALYTICS_CUSTOMER_ANALYTICS_UNAVAILABLE):
        super().__init__(message)


class IdempotencyConflictException(AnalyticsException):
    """
    Raised when an idempotency key is reused with a different payload.
    """

    def __init__(self, message=ANALYTICS_IDEMPOTENCY_KEY_CONFLICT):
        super().__init__(message)