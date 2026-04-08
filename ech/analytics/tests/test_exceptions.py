from django.test import SimpleTestCase

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
    ANALYTICS_USER_ANALYTICS_UNAVAILABLE,
    ANALYTICS_REVIEW_ANALYTICS_UNAVAILABLE,
    ANALYTICS_IDEMPOTENCY_KEY_CONFLICT,
)
from ech.analytics.exceptions import (
    AnalyticsException,
    AnalyticsSnapshotNotFoundException,
    AnalyticsSnapshotAccessDeniedException,
    AnalyticsSnapshotAlreadyExistsException,
    AnalyticsSnapshotCreationException,
    AnalyticsSnapshotRefreshException,
    AnalyticsSnapshotRefreshNotAllowedException,
    AnalyticsDashboardUnavailableException,
    AnalyticsSalesUnavailableException,
    AnalyticsOrderUnavailableException,
    AnalyticsPaymentUnavailableException,
    AnalyticsShippingUnavailableException,
    AnalyticsProductUnavailableException,
    AnalyticsCustomerUnavailableException,
    AnalyticsUserUnavailableException,
    AnalyticsReviewUnavailableException,
    IdempotencyConflictException,
)


class AnalyticsExceptionTestCase(SimpleTestCase):
    def test_analytics_exception_inherits_from_exception(self):
        """Inherit the base analytics exception from Python Exception."""
        self.assertTrue(issubclass(AnalyticsException, Exception))

    def test_analytics_exception_accepts_custom_message(self):
        """Store a custom message in the base analytics exception."""
        exception = AnalyticsException("Custom analytics error")

        self.assertEqual(str(exception), "Custom analytics error")


class AnalyticsSnapshotNotFoundExceptionTestCase(SimpleTestCase):
    def test_snapshot_not_found_exception_inherits_from_analytics_exception(self):
        """Inherit snapshot not found exception from AnalyticsException."""
        self.assertTrue(
            issubclass(AnalyticsSnapshotNotFoundException, AnalyticsException)
        )

    def test_snapshot_not_found_exception_uses_default_message(self):
        """Use the default snapshot not found message."""
        exception = AnalyticsSnapshotNotFoundException()

        self.assertEqual(str(exception), ANALYTICS_SNAPSHOT_NOT_FOUND)

    def test_snapshot_not_found_exception_accepts_custom_message(self):
        """Allow a custom message for snapshot not found exception."""
        exception = AnalyticsSnapshotNotFoundException("Custom snapshot not found")

        self.assertEqual(str(exception), "Custom snapshot not found")


class AnalyticsSnapshotAccessDeniedExceptionTestCase(SimpleTestCase):
    def test_snapshot_access_denied_exception_inherits_from_analytics_exception(self):
        """Inherit snapshot access denied exception from AnalyticsException."""
        self.assertTrue(
            issubclass(AnalyticsSnapshotAccessDeniedException, AnalyticsException)
        )

    def test_snapshot_access_denied_exception_uses_default_message(self):
        """Use the default snapshot access denied message."""
        exception = AnalyticsSnapshotAccessDeniedException()

        self.assertEqual(str(exception), ANALYTICS_SNAPSHOT_ACCESS_DENIED)

    def test_snapshot_access_denied_exception_accepts_custom_message(self):
        """Allow a custom message for snapshot access denied exception."""
        exception = AnalyticsSnapshotAccessDeniedException(
            "Custom snapshot access denied"
        )

        self.assertEqual(str(exception), "Custom snapshot access denied")


class AnalyticsSnapshotAlreadyExistsExceptionTestCase(SimpleTestCase):
    def test_snapshot_already_exists_exception_inherits_from_analytics_exception(self):
        """Inherit snapshot already exists exception from AnalyticsException."""
        self.assertTrue(
            issubclass(AnalyticsSnapshotAlreadyExistsException, AnalyticsException)
        )

    def test_snapshot_already_exists_exception_uses_default_message(self):
        """Use the default snapshot already exists message."""
        exception = AnalyticsSnapshotAlreadyExistsException()

        self.assertEqual(str(exception), ANALYTICS_SNAPSHOT_ALREADY_EXISTS)

    def test_snapshot_already_exists_exception_accepts_custom_message(self):
        """Allow a custom message for snapshot already exists exception."""
        exception = AnalyticsSnapshotAlreadyExistsException(
            "Custom snapshot already exists"
        )

        self.assertEqual(str(exception), "Custom snapshot already exists")


class AnalyticsSnapshotCreationExceptionTestCase(SimpleTestCase):
    def test_snapshot_creation_exception_inherits_from_analytics_exception(self):
        """Inherit snapshot creation exception from AnalyticsException."""
        self.assertTrue(
            issubclass(AnalyticsSnapshotCreationException, AnalyticsException)
        )

    def test_snapshot_creation_exception_uses_default_message(self):
        """Use the default snapshot creation failed message."""
        exception = AnalyticsSnapshotCreationException()

        self.assertEqual(str(exception), ANALYTICS_SNAPSHOT_CREATION_FAILED)

    def test_snapshot_creation_exception_accepts_custom_message(self):
        """Allow a custom message for snapshot creation exception."""
        exception = AnalyticsSnapshotCreationException(
            "Custom snapshot creation failed"
        )

        self.assertEqual(str(exception), "Custom snapshot creation failed")


class AnalyticsSnapshotRefreshExceptionTestCase(SimpleTestCase):
    def test_snapshot_refresh_exception_inherits_from_analytics_exception(self):
        """Inherit snapshot refresh exception from AnalyticsException."""
        self.assertTrue(
            issubclass(AnalyticsSnapshotRefreshException, AnalyticsException)
        )

    def test_snapshot_refresh_exception_uses_default_message(self):
        """Use the default snapshot refresh failed message."""
        exception = AnalyticsSnapshotRefreshException()

        self.assertEqual(str(exception), ANALYTICS_SNAPSHOT_REFRESH_FAILED)

    def test_snapshot_refresh_exception_accepts_custom_message(self):
        """Allow a custom message for snapshot refresh exception."""
        exception = AnalyticsSnapshotRefreshException(
            "Custom snapshot refresh failed"
        )

        self.assertEqual(str(exception), "Custom snapshot refresh failed")


class AnalyticsSnapshotRefreshNotAllowedExceptionTestCase(SimpleTestCase):
    def test_snapshot_refresh_not_allowed_exception_inherits_from_analytics_exception(
        self,
    ):
        """Inherit snapshot refresh not allowed exception from AnalyticsException."""
        self.assertTrue(
            issubclass(
                AnalyticsSnapshotRefreshNotAllowedException,
                AnalyticsException,
            )
        )

    def test_snapshot_refresh_not_allowed_exception_uses_default_message(self):
        """Use the default snapshot refresh not allowed message."""
        exception = AnalyticsSnapshotRefreshNotAllowedException()

        self.assertEqual(str(exception), ANALYTICS_SNAPSHOT_REFRESH_NOT_ALLOWED)

    def test_snapshot_refresh_not_allowed_exception_accepts_custom_message(self):
        """Allow a custom message for snapshot refresh not allowed exception."""
        exception = AnalyticsSnapshotRefreshNotAllowedException(
            "Custom snapshot refresh not allowed"
        )

        self.assertEqual(str(exception), "Custom snapshot refresh not allowed")


class AnalyticsDashboardUnavailableExceptionTestCase(SimpleTestCase):
    def test_dashboard_unavailable_exception_inherits_from_analytics_exception(self):
        """Inherit dashboard unavailable exception from AnalyticsException."""
        self.assertTrue(
            issubclass(AnalyticsDashboardUnavailableException, AnalyticsException)
        )

    def test_dashboard_unavailable_exception_uses_default_message(self):
        """Use the default dashboard unavailable message."""
        exception = AnalyticsDashboardUnavailableException()

        self.assertEqual(str(exception), ANALYTICS_DASHBOARD_DATA_UNAVAILABLE)

    def test_dashboard_unavailable_exception_accepts_custom_message(self):
        """Allow a custom message for dashboard unavailable exception."""
        exception = AnalyticsDashboardUnavailableException(
            "Custom dashboard unavailable"
        )

        self.assertEqual(str(exception), "Custom dashboard unavailable")


class AnalyticsSalesUnavailableExceptionTestCase(SimpleTestCase):
    def test_sales_unavailable_exception_inherits_from_analytics_exception(self):
        """Inherit sales unavailable exception from AnalyticsException."""
        self.assertTrue(
            issubclass(AnalyticsSalesUnavailableException, AnalyticsException)
        )

    def test_sales_unavailable_exception_uses_default_message(self):
        """Use the default sales unavailable message."""
        exception = AnalyticsSalesUnavailableException()

        self.assertEqual(str(exception), ANALYTICS_SALES_DATA_UNAVAILABLE)

    def test_sales_unavailable_exception_accepts_custom_message(self):
        """Allow a custom message for sales unavailable exception."""
        exception = AnalyticsSalesUnavailableException("Custom sales unavailable")

        self.assertEqual(str(exception), "Custom sales unavailable")


class AnalyticsOrderUnavailableExceptionTestCase(SimpleTestCase):
    def test_order_unavailable_exception_inherits_from_analytics_exception(self):
        """Inherit order unavailable exception from AnalyticsException."""
        self.assertTrue(
            issubclass(AnalyticsOrderUnavailableException, AnalyticsException)
        )

    def test_order_unavailable_exception_uses_default_message(self):
        """Use the default order unavailable message."""
        exception = AnalyticsOrderUnavailableException()

        self.assertEqual(str(exception), ANALYTICS_ORDER_ANALYTICS_UNAVAILABLE)

    def test_order_unavailable_exception_accepts_custom_message(self):
        """Allow a custom message for order unavailable exception."""
        exception = AnalyticsOrderUnavailableException("Custom order unavailable")

        self.assertEqual(str(exception), "Custom order unavailable")


class AnalyticsPaymentUnavailableExceptionTestCase(SimpleTestCase):
    def test_payment_unavailable_exception_inherits_from_analytics_exception(self):
        """Inherit payment unavailable exception from AnalyticsException."""
        self.assertTrue(
            issubclass(AnalyticsPaymentUnavailableException, AnalyticsException)
        )

    def test_payment_unavailable_exception_uses_default_message(self):
        """Use the default payment unavailable message."""
        exception = AnalyticsPaymentUnavailableException()

        self.assertEqual(str(exception), ANALYTICS_PAYMENT_ANALYTICS_UNAVAILABLE)

    def test_payment_unavailable_exception_accepts_custom_message(self):
        """Allow a custom message for payment unavailable exception."""
        exception = AnalyticsPaymentUnavailableException(
            "Custom payment unavailable"
        )

        self.assertEqual(str(exception), "Custom payment unavailable")


class AnalyticsShippingUnavailableExceptionTestCase(SimpleTestCase):
    def test_shipping_unavailable_exception_inherits_from_analytics_exception(self):
        """Inherit shipping unavailable exception from AnalyticsException."""
        self.assertTrue(
            issubclass(AnalyticsShippingUnavailableException, AnalyticsException)
        )

    def test_shipping_unavailable_exception_uses_default_message(self):
        """Use the default shipping unavailable message."""
        exception = AnalyticsShippingUnavailableException()

        self.assertEqual(str(exception), ANALYTICS_SHIPPING_ANALYTICS_UNAVAILABLE)

    def test_shipping_unavailable_exception_accepts_custom_message(self):
        """Allow a custom message for shipping unavailable exception."""
        exception = AnalyticsShippingUnavailableException(
            "Custom shipping unavailable"
        )

        self.assertEqual(str(exception), "Custom shipping unavailable")


class AnalyticsProductUnavailableExceptionTestCase(SimpleTestCase):
    def test_product_unavailable_exception_inherits_from_analytics_exception(self):
        """Inherit product unavailable exception from AnalyticsException."""
        self.assertTrue(
            issubclass(AnalyticsProductUnavailableException, AnalyticsException)
        )

    def test_product_unavailable_exception_uses_default_message(self):
        """Use the default product unavailable message."""
        exception = AnalyticsProductUnavailableException()

        self.assertEqual(str(exception), ANALYTICS_PRODUCT_ANALYTICS_UNAVAILABLE)

    def test_product_unavailable_exception_accepts_custom_message(self):
        """Allow a custom message for product unavailable exception."""
        exception = AnalyticsProductUnavailableException(
            "Custom product unavailable"
        )

        self.assertEqual(str(exception), "Custom product unavailable")


class AnalyticsCustomerUnavailableExceptionTestCase(SimpleTestCase):
    def test_customer_unavailable_exception_inherits_from_analytics_exception(self):
        """Inherit customer unavailable exception from AnalyticsException."""
        self.assertTrue(
            issubclass(AnalyticsCustomerUnavailableException, AnalyticsException)
        )

    def test_customer_unavailable_exception_uses_default_message(self):
        """Use the default customer unavailable message."""
        exception = AnalyticsCustomerUnavailableException()

        self.assertEqual(str(exception), ANALYTICS_CUSTOMER_ANALYTICS_UNAVAILABLE)

    def test_customer_unavailable_exception_accepts_custom_message(self):
        """Allow a custom message for customer unavailable exception."""
        exception = AnalyticsCustomerUnavailableException(
            "Custom customer unavailable"
        )

        self.assertEqual(str(exception), "Custom customer unavailable")


class AnalyticsUserUnavailableExceptionTestCase(SimpleTestCase):
    def test_user_unavailable_exception_inherits_from_analytics_exception(self):
        """Inherit user unavailable exception from AnalyticsException."""
        self.assertTrue(
            issubclass(AnalyticsUserUnavailableException, AnalyticsException)
        )

    def test_user_unavailable_exception_uses_default_message(self):
        """Use the default user unavailable message."""
        exception = AnalyticsUserUnavailableException()

        self.assertEqual(str(exception), ANALYTICS_USER_ANALYTICS_UNAVAILABLE)

    def test_user_unavailable_exception_accepts_custom_message(self):
        """Allow a custom message for user unavailable exception."""
        exception = AnalyticsUserUnavailableException("Custom user unavailable")

        self.assertEqual(str(exception), "Custom user unavailable")


class AnalyticsReviewUnavailableExceptionTestCase(SimpleTestCase):
    def test_review_unavailable_exception_inherits_from_analytics_exception(self):
        """Inherit review unavailable exception from AnalyticsException."""
        self.assertTrue(
            issubclass(AnalyticsReviewUnavailableException, AnalyticsException)
        )

    def test_review_unavailable_exception_uses_default_message(self):
        """Use the default review unavailable message."""
        exception = AnalyticsReviewUnavailableException()

        self.assertEqual(str(exception), ANALYTICS_REVIEW_ANALYTICS_UNAVAILABLE)

    def test_review_unavailable_exception_accepts_custom_message(self):
        """Allow a custom message for review unavailable exception."""
        exception = AnalyticsReviewUnavailableException(
            "Custom review unavailable"
        )

        self.assertEqual(str(exception), "Custom review unavailable")


class IdempotencyConflictExceptionTestCase(SimpleTestCase):
    def test_idempotency_conflict_exception_inherits_from_analytics_exception(self):
        """Inherit idempotency conflict exception from AnalyticsException."""
        self.assertTrue(
            issubclass(IdempotencyConflictException, AnalyticsException)
        )

    def test_idempotency_conflict_exception_uses_default_message(self):
        """Use the default idempotency conflict message."""
        exception = IdempotencyConflictException()

        self.assertEqual(str(exception), ANALYTICS_IDEMPOTENCY_KEY_CONFLICT)

    def test_idempotency_conflict_exception_accepts_custom_message(self):
        """Allow a custom message for idempotency conflict exception."""
        exception = IdempotencyConflictException(
            "Custom idempotency conflict"
        )

        self.assertEqual(str(exception), "Custom idempotency conflict")