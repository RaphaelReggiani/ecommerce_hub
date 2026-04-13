import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.admin_dashboard.models import (
    AdminDashboardLog,
    AdminDashboardLifecycle,
    AdminDashboardEvent,
)


User = get_user_model()


class BaseAdminDashboardModelFactoryMixin:

    def create_user(self, **kwargs):
        unique_suffix = uuid.uuid4().hex[:8]

        data = {
            "email": f"admin_{unique_suffix}@company.com",
            "password": "StrongPassword123",
            "user_name": f"Admin User {unique_suffix}",
            "role": User.ROLE_ADMIN,
            "is_active": True,
            "email_confirmed": True,
        }

        data.update(kwargs)

        return User.objects.create_user(**data)

    def create_log(self, **kwargs):

        performed_by = kwargs.pop("performed_by", None) or self.create_user()

        data = {
            "action_type": "test_action",
            "target_module": "orders",
            "performed_by": performed_by,
            "metadata": {"source": "unit-test"},
        }

        data.update(kwargs)

        return AdminDashboardLog.objects.create(**data)


class AdminDashboardLogModelTestCase(BaseAdminDashboardModelFactoryMixin, TestCase):

    def test_admin_dashboard_log_creation_success(self):
        """Create admin dashboard log successfully."""

        log = self.create_log()

        self.assertIsInstance(log.id, uuid.UUID)
        self.assertEqual(log.action_type, "test_action")
        self.assertEqual(log.target_module, "orders")
        self.assertEqual(log.metadata, {"source": "unit-test"})
        self.assertIsNotNone(log.created_at)

    def test_admin_dashboard_log_string_representation(self):
        """Return action type and timestamp in string representation."""

        log = self.create_log()

        self.assertEqual(
            str(log),
            f"{log.action_type} - {log.created_at}",
        )

    def test_admin_dashboard_log_related_name_works_correctly(self):
        """Expose logs through performed_by related name."""

        log = self.create_log()

        self.assertIn(
            log,
            log.performed_by.admin_dashboard_logs.all(),
        )

    def test_admin_dashboard_log_ordering_by_created_at_desc(self):
        """Order admin logs by newest created_at first."""

        first = self.create_log()
        second = self.create_log(action_type="second_action")

        logs = list(AdminDashboardLog.objects.all())

        self.assertEqual(logs[0], second)
        self.assertEqual(logs[1], first)

    def test_admin_dashboard_log_meta_ordering_is_configured(self):
        """Configure log ordering by created_at descending."""

        self.assertEqual(AdminDashboardLog._meta.ordering, ["-created_at"])

    def test_admin_dashboard_log_meta_indexes_are_configured(self):
        """Configure indexes used for dashboard queries."""

        index_names = {index.name for index in AdminDashboardLog._meta.indexes}

        self.assertIn("adminlog_action_type_idx", index_names)
        self.assertIn("adminlog_performed_by_idx", index_names)
        self.assertIn("adminlog_target_module_idx", index_names)
        self.assertIn("adminlog_created_idx", index_names)

    def test_admin_dashboard_log_optional_fields_configuration(self):
        """Configure optional log fields correctly."""

        performed_by_field = AdminDashboardLog._meta.get_field("performed_by")
        metadata_field = AdminDashboardLog._meta.get_field("metadata")

        self.assertTrue(performed_by_field.null)
        self.assertTrue(performed_by_field.blank)
        self.assertTrue(metadata_field.null)
        self.assertTrue(metadata_field.blank)


class AdminDashboardLifecycleModelTestCase(BaseAdminDashboardModelFactoryMixin, TestCase):

    def test_admin_dashboard_lifecycle_creation_success(self):
        """Create lifecycle record successfully."""

        log = self.create_log()
        now = timezone.now()

        lifecycle = AdminDashboardLifecycle.objects.create(
            log=log,
            started_at=now,
            completed_at=now,
        )

        self.assertEqual(lifecycle.log, log)
        self.assertEqual(lifecycle.started_at, now)
        self.assertEqual(lifecycle.completed_at, now)
        self.assertIsNone(lifecycle.failed_at)
        self.assertIsNotNone(lifecycle.created_at)
        self.assertIsNotNone(lifecycle.updated_at)

    def test_admin_dashboard_lifecycle_string_representation(self):
        """Return log identifier in lifecycle string representation."""

        log = self.create_log()
        lifecycle = AdminDashboardLifecycle.objects.create(log=log)

        self.assertEqual(
            str(lifecycle),
            f"Lifecycle for Admin Log {log.id}",
        )

    def test_admin_dashboard_lifecycle_related_name_works_correctly(self):
        """Expose lifecycle through log one-to-one related name."""

        log = self.create_log()
        lifecycle = AdminDashboardLifecycle.objects.create(log=log)

        self.assertEqual(log.lifecycle, lifecycle)


class AdminDashboardEventModelTestCase(BaseAdminDashboardModelFactoryMixin, TestCase):

    def test_admin_dashboard_event_creation_success(self):
        """Create dashboard event successfully."""

        user = self.create_user()

        event = AdminDashboardEvent.objects.create(
            event_type=AdminDashboardEvent.TYPE_DASHBOARD_VIEWED,
            performed_by=user,
            metadata={"source": "unit-test"},
        )

        self.assertIsInstance(event.id, uuid.UUID)
        self.assertEqual(
            event.event_type,
            AdminDashboardEvent.TYPE_DASHBOARD_VIEWED,
        )
        self.assertEqual(event.performed_by, user)
        self.assertEqual(event.metadata, {"source": "unit-test"})
        self.assertIsNotNone(event.created_at)

    def test_admin_dashboard_event_string_representation(self):
        """Return event type and timestamp in string representation."""

        event = AdminDashboardEvent.objects.create(
            event_type=AdminDashboardEvent.TYPE_DASHBOARD_VIEWED,
        )

        self.assertEqual(
            str(event),
            f"{event.event_type} - {event.created_at}",
        )

    def test_admin_dashboard_event_ordering_by_created_at_desc(self):
        """Order events by newest created_at first."""

        first = AdminDashboardEvent.objects.create(
            event_type=AdminDashboardEvent.TYPE_DASHBOARD_VIEWED,
        )

        second = AdminDashboardEvent.objects.create(
            event_type=AdminDashboardEvent.TYPE_DASHBOARD_SUMMARY_FETCHED,
        )

        events = list(AdminDashboardEvent.objects.all())

        self.assertEqual(events[0], second)
        self.assertEqual(events[1], first)

    def test_admin_dashboard_event_meta_configuration(self):
        """Configure event ordering and indexes correctly."""

        self.assertEqual(AdminDashboardEvent._meta.ordering, ["-created_at"])

        index_names = {index.name for index in AdminDashboardEvent._meta.indexes}

        self.assertIn("admindash_event_type_idx", index_names)
        self.assertIn("admindash_event_created_idx", index_names)

    def test_admin_dashboard_event_choices_include_expected_values(self):
        """Expose all supported admin dashboard event types."""

        choices = dict(AdminDashboardEvent.EVENT_TYPE_CHOICES)

        self.assertIn(AdminDashboardEvent.TYPE_DASHBOARD_VIEWED, choices)
        self.assertIn(
            AdminDashboardEvent.TYPE_DASHBOARD_SUMMARY_FETCHED,
            choices,
        )
        self.assertIn(
            AdminDashboardEvent.TYPE_DASHBOARD_OPERATIONAL_METRICS_FETCHED,
            choices,
        )
        self.assertIn(
            AdminDashboardEvent.TYPE_DASHBOARD_RECENT_ACTIVITY_FETCHED,
            choices,
        )
        self.assertIn(
            AdminDashboardEvent.TYPE_ORDER_BULK_ACTION_EXECUTED,
            choices,
        )
        self.assertIn(
            AdminDashboardEvent.TYPE_REVIEW_BULK_MODERATION_EXECUTED,
            choices,
        )
        self.assertIn(
            AdminDashboardEvent.TYPE_NOTIFICATION_RETRY_EXECUTED,
            choices,
        )
        self.assertIn(
            AdminDashboardEvent.TYPE_OPERATIONAL_ALERT_TRIGGERED,
            choices,
        )

    def test_admin_dashboard_event_related_name_works_correctly(self):
        """Expose dashboard events through user related name."""

        user = self.create_user()

        event = AdminDashboardEvent.objects.create(
            event_type=AdminDashboardEvent.TYPE_DASHBOARD_VIEWED,
            performed_by=user,
        )

        self.assertIn(
            event,
            user.admin_dashboard_events.all(),
        )