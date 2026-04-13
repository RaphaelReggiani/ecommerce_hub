import uuid
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.analytics.domain_events.events import (
    AnalyticsSnapshotFailedEvent,
    AnalyticsSnapshotRefreshedEvent,
)
from ech.analytics.exceptions import (
    AnalyticsSnapshotRefreshException,
    AnalyticsSnapshotRefreshNotAllowedException,
)
from ech.analytics.models import (
    AnalyticsEvent,
    AnalyticsSnapshot,
    AnalyticsSnapshotLifecycle,
)
from ech.analytics.services.analytic_snapshot_refresh_service import (
    AnalyticsSnapshotRefreshService,
)
from ech.orders.models import Order

User = get_user_model()


class BaseAnalyticsSnapshotRefreshFactoryMixin:
    @staticmethod
    def unique_suffix():
        return uuid.uuid4().hex[:8]

    @classmethod
    def create_user(cls, **kwargs):
        suffix = cls.unique_suffix()
        data = {
            "email": f"user_{suffix}@test.com",
            "password": "StrongPassword123",
            "user_name": f"User {suffix}",
            "role": User.ROLE_CUSTOMER_USER,
            "is_active": True,
            "email_confirmed": True,
        }
        data.update(kwargs)
        return User.objects.create_user(**data)

    @classmethod
    def create_staff_user(cls, **kwargs):
        suffix = cls.unique_suffix()
        data = {
            "email": f"staff_{suffix}@company.com",
            "password": "StrongPassword123",
            "user_name": f"Staff {suffix}",
            "role": User.ROLE_ANALYTICS_STAFF,
            "is_active": True,
            "email_confirmed": True,
        }
        data.update(kwargs)
        return User.objects.create_user(**data)

    @classmethod
    def create_snapshot(cls, **kwargs):
        generated_by = kwargs.pop("generated_by", None) or cls.create_staff_user()
        now = timezone.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        data = {
            "period_type": AnalyticsSnapshot.PERIOD_DAILY,
            "period_start": now,
            "period_end": now + timedelta(days=1),
            "generated_by": generated_by,
            "total_orders": 0,
            "orders_pending": 0,
            "orders_processing": 0,
            "orders_shipped": 0,
            "orders_delivered": 0,
            "orders_cancelled": 0,
            "total_revenue": Decimal("0.00"),
            "total_refunds": Decimal("0.00"),
            "net_revenue": Decimal("0.00"),
            "payments_captured": 0,
            "payments_failed": 0,
            "payments_refunded": 0,
            "shipments_in_transit": 0,
            "shipments_delivered": 0,
            "shipments_failed": 0,
            "products_sold": 0,
            "top_product_id": None,
            "active_customers": 0,
            "new_customers": 0,
            "total_registered_users": 0,
            "active_users": 0,
            "inactive_users": 0,
            "confirmed_users": 0,
            "unconfirmed_users": 0,
            "staff_users": 0,
            "customer_users": 0,
            "total_reviews": 0,
            "approved_reviews": 0,
            "rejected_reviews": 0,
            "hidden_reviews": 0,
            "cancelled_reviews": 0,
            "verified_purchase_reviews": 0,
            "average_rating": Decimal("0.00"),
            "low_rated_products_count": 0,
            "high_rated_products_count": 0,
            "metadata": {"source": "refresh-test"},
        }
        data.update(kwargs)
        return AnalyticsSnapshot.objects.create(**data)

    @classmethod
    def create_snapshot_with_lifecycle(cls, **kwargs):
        snapshot = cls.create_snapshot(**kwargs)

        lifecycle = AnalyticsSnapshotLifecycle.objects.create(
            snapshot=snapshot,
            generation_started_at=timezone.now() - timedelta(minutes=5),
            generation_completed_at=timezone.now() - timedelta(minutes=4),
        )

        return snapshot, lifecycle

    @classmethod
    def create_order(cls, **kwargs):
        customer = kwargs.pop("customer", None) or cls.create_user()
        created_at = kwargs.pop("created_at", None)

        data = {
            "customer": customer,
            "status": Order.ORDER_STATUS_PENDING,
            "payment_status": Order.PAYMENT_STATUS_PENDING,
            "shipping_status": Order.SHIPPING_STATUS_PENDING,
            "currency": "USD",
        }
        data.update(kwargs)
        order = Order.objects.create(**data)

        if created_at is not None:
            Order.objects.filter(id=order.id).update(created_at=created_at)
            order.refresh_from_db()

        return order


class AnalyticsSnapshotRefreshServiceTestCase(
    BaseAnalyticsSnapshotRefreshFactoryMixin,
    TestCase,
):
    @classmethod
    def setUpTestData(cls):
        cls.analytics_staff = cls.create_staff_user(
            email="analytics.refresh@company.com",
        )
        cls.customer = cls.create_user(
            email="customer.refresh@test.com",
        )

    def setUp(self):
        AnalyticsSnapshot.objects.all().delete()

    def test_refresh_snapshot_rebuilds_metrics_and_updates_lifecycle(self):
        """Ensure refreshing a snapshot rebuilds metrics, updates lifecycle state, emits events, and invalidates cache."""
        snapshot, lifecycle = self.create_snapshot_with_lifecycle(
            generated_by=self.analytics_staff,
            total_orders=0,
            orders_pending=0,
        )

        rebuilt_metrics = {
            "total_orders": 3,
            "orders_pending": 1,
            "orders_processing": 1,
            "orders_shipped": 0,
            "orders_delivered": 1,
            "orders_cancelled": 0,
            "total_revenue": Decimal("150.00"),
            "total_refunds": Decimal("10.00"),
            "net_revenue": Decimal("140.00"),
            "payments_captured": 2,
            "payments_failed": 1,
            "payments_refunded": 1,
            "shipments_in_transit": 1,
            "shipments_delivered": 1,
            "shipments_failed": 0,
            "products_sold": 5,
            "top_product_id": uuid.uuid4(),
            "active_customers": 2,
            "new_customers": 1,
            "total_registered_users": 8,
            "active_users": 7,
            "inactive_users": 1,
            "confirmed_users": 7,
            "unconfirmed_users": 1,
            "staff_users": 1,
            "customer_users": 7,
            "total_reviews": 4,
            "approved_reviews": 3,
            "rejected_reviews": 1,
            "hidden_reviews": 0,
            "cancelled_reviews": 0,
            "verified_purchase_reviews": 2,
            "average_rating": Decimal("4.50"),
            "low_rated_products_count": 0,
            "high_rated_products_count": 2,
        }

        with patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "AnalyticsSnapshotGenerationService._build_snapshot_metrics",
            return_value=rebuilt_metrics,
        ) as build_metrics_mock, patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "AnalyticsLogService.log_snapshot_refreshed"
        ) as log_refreshed_mock, patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "AnalyticsLogService.log_snapshot_metrics_updated"
        ) as log_metrics_mock, patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "DomainEventDispatcher.dispatch"
        ) as dispatch_mock, patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "AnalyticsCacheService.invalidate_after_snapshot_mutation"
        ) as invalidate_mock:
            with self.captureOnCommitCallbacks(execute=True) as callbacks:
                refreshed_snapshot = AnalyticsSnapshotRefreshService.refresh_snapshot(
                    snapshot=snapshot,
                    performed_by=self.analytics_staff,
                    metadata={"source": "manual-refresh"},
                )

        refreshed_snapshot.refresh_from_db()
        lifecycle.refresh_from_db()

        self.assertEqual(refreshed_snapshot.id, snapshot.id)
        self.assertEqual(refreshed_snapshot.total_orders, 3)
        self.assertEqual(refreshed_snapshot.orders_pending, 1)
        self.assertEqual(refreshed_snapshot.orders_processing, 1)
        self.assertEqual(refreshed_snapshot.orders_delivered, 1)
        self.assertEqual(refreshed_snapshot.total_revenue, Decimal("150.00"))
        self.assertEqual(refreshed_snapshot.total_refunds, Decimal("10.00"))
        self.assertEqual(refreshed_snapshot.net_revenue, Decimal("140.00"))
        self.assertEqual(refreshed_snapshot.payments_captured, 2)
        self.assertEqual(refreshed_snapshot.shipments_in_transit, 1)
        self.assertEqual(refreshed_snapshot.products_sold, 5)
        self.assertEqual(refreshed_snapshot.active_customers, 2)
        self.assertEqual(refreshed_snapshot.total_registered_users, 8)
        self.assertEqual(refreshed_snapshot.total_reviews, 4)
        self.assertEqual(refreshed_snapshot.average_rating, Decimal("4.50"))
        self.assertIsNotNone(lifecycle.refreshed_at)
        self.assertIsNone(lifecycle.failed_at)

        event_types = list(
            snapshot.events.order_by("created_at").values_list("event_type", flat=True)
        )
        self.assertEqual(
            event_types,
            [
                AnalyticsEvent.TYPE_SNAPSHOT_GENERATION_STARTED,
                AnalyticsEvent.TYPE_SNAPSHOT_REFRESHED,
            ],
        )

        build_metrics_mock.assert_called_once_with(
            period_start=snapshot.period_start,
            period_end=snapshot.period_end,
        )
        log_refreshed_mock.assert_called_once_with(
            snapshot=snapshot,
            performed_by=self.analytics_staff,
        )
        log_metrics_mock.assert_called_once_with(
            snapshot=snapshot,
            updated_fields=list(rebuilt_metrics.keys()),
            performed_by=self.analytics_staff,
        )
        self.assertEqual(dispatch_mock.call_count, 1)

        dispatched_event = dispatch_mock.call_args.args[0]
        self.assertIsInstance(dispatched_event, AnalyticsSnapshotRefreshedEvent)
        self.assertEqual(dispatched_event.snapshot_id, snapshot.id)
        self.assertEqual(dispatched_event.refreshed_by_id, self.analytics_staff.id)

        self.assertEqual(len(callbacks), 1)
        invalidate_mock.assert_called_once_with(
            snapshot_id=snapshot.id,
            period_type=snapshot.period_type,
        )

    def test_refresh_snapshot_creates_expected_refresh_events_metadata(self):
        """Ensure refresh operations persist the expected event metadata for start and completion events."""
        snapshot, _ = self.create_snapshot_with_lifecycle(
            generated_by=self.analytics_staff,
        )

        rebuilt_metrics = {
            "total_orders": 1,
            "orders_pending": 1,
            "orders_processing": 0,
            "orders_shipped": 0,
            "orders_delivered": 0,
            "orders_cancelled": 0,
            "total_revenue": Decimal("0.00"),
            "total_refunds": Decimal("0.00"),
            "net_revenue": Decimal("0.00"),
            "payments_captured": 0,
            "payments_failed": 0,
            "payments_refunded": 0,
            "shipments_in_transit": 0,
            "shipments_delivered": 0,
            "shipments_failed": 0,
            "products_sold": 0,
            "top_product_id": None,
            "active_customers": 0,
            "new_customers": 0,
            "total_registered_users": 0,
            "active_users": 0,
            "inactive_users": 0,
            "confirmed_users": 0,
            "unconfirmed_users": 0,
            "staff_users": 0,
            "customer_users": 0,
            "total_reviews": 0,
            "approved_reviews": 0,
            "rejected_reviews": 0,
            "hidden_reviews": 0,
            "cancelled_reviews": 0,
            "verified_purchase_reviews": 0,
            "average_rating": Decimal("0.00"),
            "low_rated_products_count": 0,
            "high_rated_products_count": 0,
        }

        with patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "AnalyticsSnapshotGenerationService._build_snapshot_metrics",
            return_value=rebuilt_metrics,
        ), patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "AnalyticsLogService.log_snapshot_refreshed"
        ), patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "AnalyticsLogService.log_snapshot_metrics_updated"
        ), patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "DomainEventDispatcher.dispatch"
        ), patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "AnalyticsCacheService.invalidate_after_snapshot_mutation"
        ):
            with self.captureOnCommitCallbacks(execute=True):
                AnalyticsSnapshotRefreshService.refresh_snapshot(
                    snapshot=snapshot,
                    performed_by=self.analytics_staff,
                    metadata={"source": "scheduled-job"},
                )

        events = list(snapshot.events.order_by("created_at"))
        self.assertEqual(len(events), 2)

        self.assertEqual(events[0].event_type, AnalyticsEvent.TYPE_SNAPSHOT_GENERATION_STARTED)
        self.assertEqual(
            events[0].metadata,
            {
                "operation": "refresh",
                "source": "scheduled-job",
            },
        )

        self.assertEqual(events[1].event_type, AnalyticsEvent.TYPE_SNAPSHOT_REFRESHED)
        self.assertEqual(
            events[1].metadata,
            {"source": "scheduled-job"},
        )

    def test_refresh_snapshot_raises_not_allowed_when_snapshot_is_none(self):
        """Ensure refreshing is rejected when no snapshot instance is provided."""
        with self.assertRaises(AnalyticsSnapshotRefreshNotAllowedException):
            AnalyticsSnapshotRefreshService.refresh_snapshot(
                snapshot=None,
                performed_by=self.analytics_staff,
            )

    def test_refresh_snapshot_raises_not_allowed_when_lifecycle_is_missing(self):
        """Ensure refreshing is rejected when the snapshot lifecycle record does not exist."""
        snapshot = self.create_snapshot(
            generated_by=self.analytics_staff,
        )

        with self.assertRaises(AnalyticsSnapshotRefreshNotAllowedException):
            AnalyticsSnapshotRefreshService.refresh_snapshot(
                snapshot=snapshot,
                performed_by=self.analytics_staff,
            )

    def test_refresh_snapshot_marks_failure_and_dispatches_failed_event(self):
        """Ensure refresh failures raise a domain exception, mark failure handling, and dispatch a failed event."""
        snapshot, lifecycle = self.create_snapshot_with_lifecycle(
            generated_by=self.analytics_staff,
        )

        with patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "AnalyticsSnapshotGenerationService._build_snapshot_metrics",
            side_effect=Exception("refresh boom"),
        ), patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "DomainEventDispatcher.dispatch"
        ) as dispatch_mock, patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "AnalyticsSnapshotRefreshService._mark_refresh_failure"
        ) as mark_failure_mock:
            with self.assertRaises(AnalyticsSnapshotRefreshException):
                AnalyticsSnapshotRefreshService.refresh_snapshot(
                    snapshot=snapshot,
                    performed_by=self.analytics_staff,
                    metadata={"source": "refresh-failure"},
                )

        lifecycle.refresh_from_db()

        self.assertIsNone(lifecycle.failed_at)
        self.assertIsNone(lifecycle.refreshed_at)

        mark_failure_mock.assert_called_once_with(snapshot=snapshot)

        self.assertEqual(dispatch_mock.call_count, 1)
        dispatched_event = dispatch_mock.call_args.args[0]
        self.assertIsInstance(dispatched_event, AnalyticsSnapshotFailedEvent)
        self.assertEqual(dispatched_event.snapshot_id, snapshot.id)
        self.assertEqual(dispatched_event.period_type, snapshot.period_type)
        self.assertEqual(dispatched_event.error_message, "refresh boom")
        self.assertEqual(dispatched_event.performed_by_id, self.analytics_staff.id)

    def test_mark_refresh_failure_is_noop_when_lifecycle_is_missing(self):
        """Ensure marking refresh failure does nothing when the snapshot has no lifecycle record."""
        snapshot = self.create_snapshot(
            generated_by=self.analytics_staff,
        )

        AnalyticsSnapshotRefreshService._mark_refresh_failure(snapshot=snapshot)

        self.assertFalse(
            AnalyticsSnapshotLifecycle.objects.filter(snapshot=snapshot).exists()
        )

    def test_create_event_persists_snapshot_event(self):
        """Ensure creating a refresh event persists the expected snapshot event record and metadata."""
        snapshot, _ = self.create_snapshot_with_lifecycle(
            generated_by=self.analytics_staff,
        )

        AnalyticsSnapshotRefreshService._create_event(
            snapshot=snapshot,
            event_type=AnalyticsEvent.TYPE_SNAPSHOT_REFRESHED,
            performed_by=self.analytics_staff,
            metadata={"source": "unit-test"},
        )

        event = snapshot.events.get(event_type=AnalyticsEvent.TYPE_SNAPSHOT_REFRESHED)
        self.assertEqual(event.snapshot, snapshot)
        self.assertEqual(event.performed_by, self.analytics_staff)
        self.assertEqual(event.metadata, {"source": "unit-test"})

    def test_validate_refresh_allowed_accepts_snapshot_with_lifecycle(self):
        """Ensure refresh validation passes when the snapshot has an associated lifecycle record."""
        snapshot, _ = self.create_snapshot_with_lifecycle(
            generated_by=self.analytics_staff,
        )

        AnalyticsSnapshotRefreshService._validate_refresh_allowed(snapshot=snapshot)

    def test_refresh_snapshot_allows_empty_metadata(self):
        """Ensure refreshing a snapshot succeeds and persists default event metadata when metadata is omitted."""
        snapshot, lifecycle = self.create_snapshot_with_lifecycle(
            generated_by=self.analytics_staff,
        )

        rebuilt_metrics = {
            "total_orders": 0,
            "orders_pending": 0,
            "orders_processing": 0,
            "orders_shipped": 0,
            "orders_delivered": 0,
            "orders_cancelled": 0,
            "total_revenue": Decimal("0.00"),
            "total_refunds": Decimal("0.00"),
            "net_revenue": Decimal("0.00"),
            "payments_captured": 0,
            "payments_failed": 0,
            "payments_refunded": 0,
            "shipments_in_transit": 0,
            "shipments_delivered": 0,
            "shipments_failed": 0,
            "products_sold": 0,
            "top_product_id": None,
            "active_customers": 0,
            "new_customers": 0,
            "total_registered_users": 0,
            "active_users": 0,
            "inactive_users": 0,
            "confirmed_users": 0,
            "unconfirmed_users": 0,
            "staff_users": 0,
            "customer_users": 0,
            "total_reviews": 0,
            "approved_reviews": 0,
            "rejected_reviews": 0,
            "hidden_reviews": 0,
            "cancelled_reviews": 0,
            "verified_purchase_reviews": 0,
            "average_rating": Decimal("0.00"),
            "low_rated_products_count": 0,
            "high_rated_products_count": 0,
        }

        with patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "AnalyticsSnapshotGenerationService._build_snapshot_metrics",
            return_value=rebuilt_metrics,
        ), patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "AnalyticsLogService.log_snapshot_refreshed"
        ), patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "AnalyticsLogService.log_snapshot_metrics_updated"
        ), patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "DomainEventDispatcher.dispatch"
        ), patch(
            "ech.analytics.services.analytic_snapshot_refresh_service."
            "AnalyticsCacheService.invalidate_after_snapshot_mutation"
        ):
            with self.captureOnCommitCallbacks(execute=True):
                AnalyticsSnapshotRefreshService.refresh_snapshot(
                    snapshot=snapshot,
                    performed_by=self.analytics_staff,
                    metadata=None,
                )

        lifecycle.refresh_from_db()
        self.assertIsNotNone(lifecycle.refreshed_at)

        events = list(snapshot.events.order_by("created_at"))
        self.assertEqual(events[0].metadata, {"operation": "refresh"})
        self.assertEqual(events[1].metadata, {})