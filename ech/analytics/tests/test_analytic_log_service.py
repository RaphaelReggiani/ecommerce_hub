import uuid
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase
from django.utils import timezone

from ech.analytics.services.analytic_log_service import AnalyticsLogService


class BaseAnalyticsLogFactoryMixin:
    @staticmethod
    def build_snapshot():
        now = timezone.now()

        return SimpleNamespace(
            id=uuid.uuid4(),
            period_type="daily",
            period_start=now.replace(hour=0, minute=0, second=0, microsecond=0),
            period_end=now.replace(hour=0, minute=0, second=0, microsecond=0),
        )

    @staticmethod
    def build_user(user_id=None):
        return SimpleNamespace(id=user_id if user_id is not None else 99)


class AnalyticsSnapshotLogServiceTestCase(
    BaseAnalyticsLogFactoryMixin,
    SimpleTestCase,
):
    @patch("ech.analytics.services.analytic_log_service.logger.info")
    def test_log_snapshot_created_logs_expected_payload(self, logger_info_mock):
        """Log analytics snapshot creation with structured payload."""
        snapshot = self.build_snapshot()
        performed_by = self.build_user(user_id=10)

        AnalyticsLogService.log_snapshot_created(
            snapshot=snapshot,
            performed_by=performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Analytics snapshot created.",
            extra={
                "snapshot_id": str(snapshot.id),
                "period_type": snapshot.period_type,
                "period_start": snapshot.period_start.isoformat(),
                "period_end": snapshot.period_end.isoformat(),
                "performed_by_id": 10,
            },
        )

    @patch("ech.analytics.services.analytic_log_service.logger.info")
    def test_log_snapshot_created_allows_null_performed_by(self, logger_info_mock):
        """Log snapshot creation with null performer when omitted."""
        snapshot = self.build_snapshot()

        AnalyticsLogService.log_snapshot_created(
            snapshot=snapshot,
            performed_by=None,
        )

        logger_info_mock.assert_called_once_with(
            "Analytics snapshot created.",
            extra={
                "snapshot_id": str(snapshot.id),
                "period_type": snapshot.period_type,
                "period_start": snapshot.period_start.isoformat(),
                "period_end": snapshot.period_end.isoformat(),
                "performed_by_id": None,
            },
        )

    @patch("ech.analytics.services.analytic_log_service.logger.info")
    def test_log_snapshot_refreshed_logs_expected_payload(self, logger_info_mock):
        """Log analytics snapshot refresh with structured payload."""
        snapshot = self.build_snapshot()
        performed_by = self.build_user(user_id=20)

        AnalyticsLogService.log_snapshot_refreshed(
            snapshot=snapshot,
            performed_by=performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Analytics snapshot refreshed.",
            extra={
                "snapshot_id": str(snapshot.id),
                "period_type": snapshot.period_type,
                "period_start": snapshot.period_start.isoformat(),
                "period_end": snapshot.period_end.isoformat(),
                "performed_by_id": 20,
            },
        )

    @patch("ech.analytics.services.analytic_log_service.logger.info")
    def test_log_snapshot_metrics_updated_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log updated snapshot metric fields with performer metadata."""
        snapshot = self.build_snapshot()
        performed_by = self.build_user(user_id=30)
        updated_fields = [
            "total_orders",
            "total_revenue",
            "net_revenue",
        ]

        AnalyticsLogService.log_snapshot_metrics_updated(
            snapshot=snapshot,
            updated_fields=updated_fields,
            performed_by=performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Analytics snapshot metrics updated.",
            extra={
                "snapshot_id": str(snapshot.id),
                "period_type": snapshot.period_type,
                "updated_fields": updated_fields,
                "performed_by_id": 30,
            },
        )

    @patch("ech.analytics.services.analytic_log_service.logger.info")
    def test_log_snapshot_metrics_updated_defaults_to_empty_field_list(
        self,
        logger_info_mock,
    ):
        """Default updated_fields to an empty list when not provided."""
        snapshot = self.build_snapshot()

        AnalyticsLogService.log_snapshot_metrics_updated(
            snapshot=snapshot,
            updated_fields=None,
            performed_by=None,
        )

        logger_info_mock.assert_called_once_with(
            "Analytics snapshot metrics updated.",
            extra={
                "snapshot_id": str(snapshot.id),
                "period_type": snapshot.period_type,
                "updated_fields": [],
                "performed_by_id": None,
            },
        )


class AnalyticsAggregateLogServiceTestCase(SimpleTestCase):
    def setUp(self):
        self.period_start = timezone.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        self.period_end = self.period_start + timezone.timedelta(days=1)
        self.performed_by = SimpleNamespace(id=50)

    @patch("ech.analytics.services.analytic_log_service.logger.info")
    def test_log_dashboard_generated_logs_expected_payload(self, logger_info_mock):
        """Log dashboard generation with resolved period metadata."""
        AnalyticsLogService.log_dashboard_generated(
            period_type="daily",
            period_start=self.period_start,
            period_end=self.period_end,
            performed_by=self.performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Analytics dashboard generated.",
            extra={
                "period_type": "daily",
                "period_start": self.period_start.isoformat(),
                "period_end": self.period_end.isoformat(),
                "performed_by_id": 50,
            },
        )

    @patch("ech.analytics.services.analytic_log_service.logger.info")
    def test_log_sales_metrics_calculated_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log sales analytics calculation with totals."""
        AnalyticsLogService.log_sales_metrics_calculated(
            period_start=self.period_start,
            period_end=self.period_end,
            total_orders=12,
            total_revenue=Decimal("1999.90"),
            performed_by=self.performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Sales analytics calculated.",
            extra={
                "period_start": self.period_start.isoformat(),
                "period_end": self.period_end.isoformat(),
                "total_orders": 12,
                "total_revenue": "1999.90",
                "performed_by_id": 50,
            },
        )

    @patch("ech.analytics.services.analytic_log_service.logger.info")
    def test_log_payment_metrics_calculated_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log payment analytics calculation with operational counts."""
        AnalyticsLogService.log_payment_metrics_calculated(
            period_start=self.period_start,
            period_end=self.period_end,
            captured_payments=7,
            failed_payments=2,
            refunded_payments=1,
            performed_by=self.performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Payment analytics calculated.",
            extra={
                "period_start": self.period_start.isoformat(),
                "period_end": self.period_end.isoformat(),
                "captured_payments": 7,
                "failed_payments": 2,
                "refunded_payments": 1,
                "performed_by_id": 50,
            },
        )

    @patch("ech.analytics.services.analytic_log_service.logger.info")
    def test_log_shipping_metrics_calculated_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log shipping analytics calculation with status counts."""
        AnalyticsLogService.log_shipping_metrics_calculated(
            period_start=self.period_start,
            period_end=self.period_end,
            shipments_delivered=9,
            shipments_failed=1,
            shipments_in_transit=3,
            performed_by=self.performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Shipping analytics calculated.",
            extra={
                "period_start": self.period_start.isoformat(),
                "period_end": self.period_end.isoformat(),
                "shipments_delivered": 9,
                "shipments_failed": 1,
                "shipments_in_transit": 3,
                "performed_by_id": 50,
            },
        )

    @patch("ech.analytics.services.analytic_log_service.logger.info")
    def test_log_product_metrics_calculated_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log product analytics calculation with top product identifier."""
        top_product_id = uuid.uuid4()

        AnalyticsLogService.log_product_metrics_calculated(
            period_start=self.period_start,
            period_end=self.period_end,
            products_sold=25,
            top_product_id=top_product_id,
            performed_by=self.performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Product analytics calculated.",
            extra={
                "period_start": self.period_start.isoformat(),
                "period_end": self.period_end.isoformat(),
                "products_sold": 25,
                "top_product_id": str(top_product_id),
                "performed_by_id": 50,
            },
        )

    @patch("ech.analytics.services.analytic_log_service.logger.info")
    def test_log_product_metrics_calculated_allows_null_top_product_id(
        self,
        logger_info_mock,
    ):
        """Log product analytics calculation with null top product id."""
        AnalyticsLogService.log_product_metrics_calculated(
            period_start=self.period_start,
            period_end=self.period_end,
            products_sold=0,
            top_product_id=None,
            performed_by=None,
        )

        logger_info_mock.assert_called_once_with(
            "Product analytics calculated.",
            extra={
                "period_start": self.period_start.isoformat(),
                "period_end": self.period_end.isoformat(),
                "products_sold": 0,
                "top_product_id": None,
                "performed_by_id": None,
            },
        )

    @patch("ech.analytics.services.analytic_log_service.logger.info")
    def test_log_customer_metrics_calculated_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log customer analytics calculation with customer metrics."""
        AnalyticsLogService.log_customer_metrics_calculated(
            period_start=self.period_start,
            period_end=self.period_end,
            active_customers=11,
            new_customers=4,
            performed_by=self.performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Customer analytics calculated.",
            extra={
                "period_start": self.period_start.isoformat(),
                "period_end": self.period_end.isoformat(),
                "active_customers": 11,
                "new_customers": 4,
                "performed_by_id": 50,
            },
        )

    @patch("ech.analytics.services.analytic_log_service.logger.info")
    def test_log_user_metrics_calculated_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log user analytics calculation with user counts."""
        AnalyticsLogService.log_user_metrics_calculated(
            period_start=self.period_start,
            period_end=self.period_end,
            total_registered_users=100,
            active_users=94,
            performed_by=self.performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "User analytics calculated.",
            extra={
                "period_start": self.period_start.isoformat(),
                "period_end": self.period_end.isoformat(),
                "total_registered_users": 100,
                "active_users": 94,
                "performed_by_id": 50,
            },
        )

    @patch("ech.analytics.services.analytic_log_service.logger.info")
    def test_log_review_metrics_calculated_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log review analytics calculation with summary metrics."""
        AnalyticsLogService.log_review_metrics_calculated(
            period_start=self.period_start,
            period_end=self.period_end,
            total_reviews=18,
            average_rating=Decimal("4.44"),
            performed_by=self.performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Review analytics calculated.",
            extra={
                "period_start": self.period_start.isoformat(),
                "period_end": self.period_end.isoformat(),
                "total_reviews": 18,
                "average_rating": "4.44",
                "performed_by_id": 50,
            },
        )

    @patch("ech.analytics.services.analytic_log_service.logger.info")
    def test_log_analytics_cache_invalidated_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log analytics cache invalidation with reason metadata."""
        AnalyticsLogService.log_analytics_cache_invalidated(
            reason="snapshot_refresh",
            performed_by=self.performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Analytics cache invalidated.",
            extra={
                "reason": "snapshot_refresh",
                "performed_by_id": 50,
            },
        )