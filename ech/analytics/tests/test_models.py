from datetime import timedelta
from decimal import Decimal
import uuid

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from ech.analytics.models import (
    AnalyticsEvent,
    AnalyticsSnapshot,
    AnalyticsSnapshotLifecycle,
)


User = get_user_model()


class BaseAnalyticsModelFactoryMixin:
    def create_user(self, **kwargs):
        unique_suffix = uuid.uuid4().hex[:8]

        data = {
            "email": f"customer_{unique_suffix}@test.com",
            "password": "StrongPassword123",
            "user_name": f"Analytics User {unique_suffix}",
            "role": User.ROLE_CUSTOMER_USER,
            "is_active": True,
            "email_confirmed": True,
        }
        data.update(kwargs)
        return User.objects.create_user(**data)

    def create_staff_user(self, **kwargs):
        unique_suffix = uuid.uuid4().hex[:8]

        data = {
            "email": f"staff_{unique_suffix}@company.com",
            "password": "StrongPassword123",
            "user_name": f"Staff User {unique_suffix}",
            "role": User.ROLE_ADMIN,
            "is_active": True,
            "email_confirmed": True,
        }
        data.update(kwargs)
        return User.objects.create_user(**data)

    def create_snapshot(self, **kwargs):
        generated_by = kwargs.pop("generated_by", None) or self.create_user()

        now = timezone.now()
        period_start = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        period_end = period_start + timedelta(days=1)

        data = {
            "period_type": AnalyticsSnapshot.PERIOD_DAILY,
            "period_start": period_start,
            "period_end": period_end,
            "generated_by": generated_by,
            "total_orders": 10,
            "orders_pending": 2,
            "orders_processing": 2,
            "orders_shipped": 2,
            "orders_delivered": 3,
            "orders_cancelled": 1,
            "total_revenue": Decimal("1000.00"),
            "total_refunds": Decimal("100.00"),
            "net_revenue": Decimal("900.00"),
            "payments_captured": 8,
            "payments_failed": 1,
            "payments_refunded": 1,
            "shipments_in_transit": 2,
            "shipments_delivered": 5,
            "shipments_failed": 1,
            "products_sold": 20,
            "top_product_id": uuid.uuid4(),
            "active_customers": 7,
            "new_customers": 3,
            "total_registered_users": 50,
            "active_users": 45,
            "inactive_users": 5,
            "confirmed_users": 40,
            "unconfirmed_users": 10,
            "staff_users": 5,
            "customer_users": 45,
            "total_reviews": 12,
            "approved_reviews": 8,
            "rejected_reviews": 1,
            "hidden_reviews": 1,
            "cancelled_reviews": 2,
            "verified_purchase_reviews": 6,
            "average_rating": Decimal("4.25"),
            "low_rated_products_count": 1,
            "high_rated_products_count": 3,
            "metadata": {"source": "unit-test"},
        }
        data.update(kwargs)
        return AnalyticsSnapshot.objects.create(**data)


class AnalyticsSnapshotModelTestCase(BaseAnalyticsModelFactoryMixin, TestCase):
    def test_analytics_snapshot_creation_success(self):
        """Create analytics snapshot successfully with all metric groups."""
        snapshot = self.create_snapshot()

        self.assertIsInstance(snapshot.id, uuid.UUID)
        self.assertEqual(snapshot.period_type, AnalyticsSnapshot.PERIOD_DAILY)
        self.assertEqual(snapshot.total_orders, 10)
        self.assertEqual(snapshot.total_revenue, Decimal("1000.00"))
        self.assertEqual(snapshot.total_refunds, Decimal("100.00"))
        self.assertEqual(snapshot.net_revenue, Decimal("900.00"))
        self.assertEqual(snapshot.products_sold, 20)
        self.assertEqual(snapshot.active_customers, 7)
        self.assertEqual(snapshot.total_registered_users, 50)
        self.assertEqual(snapshot.total_reviews, 12)
        self.assertEqual(snapshot.average_rating, Decimal("4.25"))
        self.assertEqual(snapshot.metadata, {"source": "unit-test"})
        self.assertIsNotNone(snapshot.created_at)
        self.assertIsNotNone(snapshot.updated_at)

    def test_analytics_snapshot_defaults_are_applied(self):
        """Apply snapshot defaults when optional metrics are omitted."""
        now = timezone.now()
        snapshot = AnalyticsSnapshot.objects.create(
            period_type=AnalyticsSnapshot.PERIOD_WEEKLY,
            period_start=now,
            period_end=now + timedelta(days=7),
        )

        self.assertEqual(snapshot.total_orders, 0)
        self.assertEqual(snapshot.total_revenue, Decimal("0"))
        self.assertEqual(snapshot.total_refunds, Decimal("0"))
        self.assertEqual(snapshot.net_revenue, Decimal("0"))
        self.assertEqual(snapshot.payments_captured, 0)
        self.assertEqual(snapshot.shipments_delivered, 0)
        self.assertEqual(snapshot.products_sold, 0)
        self.assertIsNone(snapshot.top_product_id)
        self.assertEqual(snapshot.active_customers, 0)
        self.assertEqual(snapshot.new_customers, 0)
        self.assertEqual(snapshot.total_registered_users, 0)
        self.assertEqual(snapshot.active_users, 0)
        self.assertEqual(snapshot.inactive_users, 0)
        self.assertEqual(snapshot.confirmed_users, 0)
        self.assertEqual(snapshot.unconfirmed_users, 0)
        self.assertEqual(snapshot.staff_users, 0)
        self.assertEqual(snapshot.customer_users, 0)
        self.assertEqual(snapshot.total_reviews, 0)
        self.assertEqual(snapshot.approved_reviews, 0)
        self.assertEqual(snapshot.average_rating, Decimal("0"))
        self.assertEqual(snapshot.low_rated_products_count, 0)
        self.assertEqual(snapshot.high_rated_products_count, 0)
        self.assertIsNone(snapshot.generated_by)
        self.assertIsNone(snapshot.idempotency_key)
        self.assertIsNone(snapshot.metadata)

    def test_analytics_snapshot_string_representation(self):
        """Return period type and period start in string representation."""
        snapshot = self.create_snapshot()
        self.assertEqual(
            str(snapshot),
            f"{snapshot.period_type} snapshot - {snapshot.period_start}",
        )

    def test_analytics_snapshot_related_name_works_correctly(self):
        """Expose analytics snapshots through generated_by related name."""
        snapshot = self.create_snapshot()

        self.assertIn(
            snapshot,
            snapshot.generated_by.generated_analytics_snapshots.all(),
        )

    def test_analytics_snapshot_ordering_by_created_at_desc(self):
        """Order analytics snapshots by newest created_at first."""
        first = self.create_snapshot()
        second = self.create_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_WEEKLY,
            period_start=first.period_end,
            period_end=first.period_end + timedelta(days=7),
        )

        snapshots = list(AnalyticsSnapshot.objects.all())

        self.assertEqual(snapshots[0], second)
        self.assertEqual(snapshots[1], first)

    def test_analytics_snapshot_idempotency_key_must_be_unique(self):
        """Prevent duplicate idempotency keys across snapshots."""
        idempotency_key = uuid.uuid4()
        self.create_snapshot(idempotency_key=idempotency_key)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_snapshot(
                    period_type=AnalyticsSnapshot.PERIOD_WEEKLY,
                    idempotency_key=idempotency_key,
                )

    def test_analytics_snapshot_unique_period_constraint(self):
        """Prevent duplicate snapshots for the same period."""
        now = timezone.now()
        period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = period_start + timedelta(days=1)

        self.create_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=period_start,
            period_end=period_end,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_snapshot(
                    period_type=AnalyticsSnapshot.PERIOD_DAILY,
                    period_start=period_start,
                    period_end=period_end,
                )

    def test_analytics_snapshot_meta_ordering_is_configured(self):
        """Configure snapshot default ordering by created_at descending."""
        self.assertEqual(AnalyticsSnapshot._meta.ordering, ["-created_at"])

    def test_analytics_snapshot_meta_indexes_are_configured(self):
        """Configure snapshot indexes for analytics queries."""
        index_names = {index.name for index in AnalyticsSnapshot._meta.indexes}

        self.assertIn("analytic_period_start_idx", index_names)
        self.assertIn("analytic_period_end_idx", index_names)
        self.assertIn("analytic_period_range_idx", index_names)
        self.assertIn("analytic_generated_by_idx", index_names)
        self.assertIn("analytic_idempotency_idx", index_names)
        self.assertIn("analytic_top_product_idx", index_names)

    def test_analytics_snapshot_period_choices_include_expected_values(self):
        """Expose all supported snapshot period types."""
        choices = dict(AnalyticsSnapshot.PERIOD_TYPE_CHOICES)

        self.assertIn(AnalyticsSnapshot.PERIOD_DAILY, choices)
        self.assertIn(AnalyticsSnapshot.PERIOD_WEEKLY, choices)
        self.assertIn(AnalyticsSnapshot.PERIOD_MONTHLY, choices)

    def test_analytics_snapshot_field_metadata_is_configured(self):
        """Configure optional snapshot field metadata correctly."""
        top_product_id_field = AnalyticsSnapshot._meta.get_field("top_product_id")
        generated_by_field = AnalyticsSnapshot._meta.get_field("generated_by")
        metadata_field = AnalyticsSnapshot._meta.get_field("metadata")

        self.assertTrue(top_product_id_field.null)
        self.assertTrue(top_product_id_field.blank)
        self.assertTrue(generated_by_field.null)
        self.assertTrue(generated_by_field.blank)
        self.assertTrue(metadata_field.null)
        self.assertTrue(metadata_field.blank)


class AnalyticsSnapshotLifecycleModelTestCase(BaseAnalyticsModelFactoryMixin, TestCase):
    def test_analytics_snapshot_lifecycle_creation_success(self):
        """Create analytics snapshot lifecycle successfully."""
        snapshot = self.create_snapshot()
        now = timezone.now()

        lifecycle = AnalyticsSnapshotLifecycle.objects.create(
            snapshot=snapshot,
            generation_started_at=now,
            generation_completed_at=now,
        )

        self.assertEqual(lifecycle.snapshot, snapshot)
        self.assertEqual(lifecycle.generation_started_at, now)
        self.assertEqual(lifecycle.generation_completed_at, now)
        self.assertIsNone(lifecycle.refreshed_at)
        self.assertIsNone(lifecycle.failed_at)
        self.assertIsNotNone(lifecycle.created_at)
        self.assertIsNotNone(lifecycle.updated_at)

    def test_analytics_snapshot_lifecycle_string_representation(self):
        """Return snapshot identifier in lifecycle string representation."""
        snapshot = self.create_snapshot()
        lifecycle = AnalyticsSnapshotLifecycle.objects.create(snapshot=snapshot)

        self.assertEqual(
            str(lifecycle),
            f"Lifecycle for Snapshot {snapshot.id}",
        )

    def test_analytics_snapshot_lifecycle_related_name_works_correctly(self):
        """Expose lifecycle through snapshot one-to-one related name."""
        snapshot = self.create_snapshot()
        lifecycle = AnalyticsSnapshotLifecycle.objects.create(snapshot=snapshot)

        self.assertEqual(snapshot.lifecycle, lifecycle)


class AnalyticsEventModelTestCase(BaseAnalyticsModelFactoryMixin, TestCase):
    def test_analytics_event_creation_success(self):
        """Create an analytics audit event successfully."""
        snapshot = self.create_snapshot()
        operator = self.create_staff_user(
            email="analytics_operator@company.com",
            role=User.ROLE_ANALYTICS_STAFF,
        )

        event = AnalyticsEvent.objects.create(
            snapshot=snapshot,
            event_type=AnalyticsEvent.TYPE_SNAPSHOT_CREATED,
            performed_by=operator,
            metadata={"source": "unit-test"},
        )

        self.assertEqual(event.snapshot, snapshot)
        self.assertEqual(event.event_type, AnalyticsEvent.TYPE_SNAPSHOT_CREATED)
        self.assertEqual(event.performed_by, operator)
        self.assertEqual(event.metadata, {"source": "unit-test"})
        self.assertIsNotNone(event.created_at)

    def test_analytics_event_string_representation(self):
        """Return event type and snapshot identifier in string representation."""
        snapshot = self.create_snapshot()
        event = AnalyticsEvent.objects.create(
            snapshot=snapshot,
            event_type=AnalyticsEvent.TYPE_SNAPSHOT_REFRESHED,
        )

        self.assertEqual(
            str(event),
            f"{AnalyticsEvent.TYPE_SNAPSHOT_REFRESHED} - {snapshot.id}",
        )

    def test_analytics_event_ordering_by_created_at_desc(self):
        """Order analytics events by newest created_at first."""
        snapshot = self.create_snapshot()
        first = AnalyticsEvent.objects.create(
            snapshot=snapshot,
            event_type=AnalyticsEvent.TYPE_SNAPSHOT_CREATED,
        )
        second = AnalyticsEvent.objects.create(
            snapshot=snapshot,
            event_type=AnalyticsEvent.TYPE_SNAPSHOT_REFRESHED,
        )

        events = list(AnalyticsEvent.objects.all())

        self.assertEqual(events[0], second)
        self.assertEqual(events[1], first)

    def test_analytics_event_meta_is_configured(self):
        """Configure analytics event ordering and indexes correctly."""
        self.assertEqual(AnalyticsEvent._meta.ordering, ["-created_at"])

        index_names = {index.name for index in AnalyticsEvent._meta.indexes}
        self.assertIn("analyticevent_ss_created_idx", index_names)
        self.assertIn("analyticevent_type_idx", index_names)

    def test_analytics_event_choices_include_expected_values(self):
        """Expose all supported analytics event types."""
        choices = dict(AnalyticsEvent.EVENT_TYPE_CHOICES)

        self.assertIn(AnalyticsEvent.TYPE_SNAPSHOT_CREATED, choices)
        self.assertIn(AnalyticsEvent.TYPE_SNAPSHOT_GENERATION_STARTED, choices)
        self.assertIn(AnalyticsEvent.TYPE_SNAPSHOT_GENERATION_COMPLETED, choices)
        self.assertIn(AnalyticsEvent.TYPE_SNAPSHOT_REFRESHED, choices)
        self.assertIn(AnalyticsEvent.TYPE_SNAPSHOT_FAILED, choices)

    def test_analytics_event_related_name_works_correctly(self):
        """Expose analytics events through snapshot related name."""
        snapshot = self.create_snapshot()
        event = AnalyticsEvent.objects.create(
            snapshot=snapshot,
            event_type=AnalyticsEvent.TYPE_SNAPSHOT_CREATED,
        )

        self.assertIn(event, snapshot.events.all())