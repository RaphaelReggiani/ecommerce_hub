import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.admin_dashboard.filters import (
    AdminDashboardEventFilter,
    AdminDashboardLogFilter,
)
from ech.admin_dashboard.models import (
    AdminDashboardEvent,
    AdminDashboardLog,
)

User = get_user_model()


class BaseAdminDashboardFilterFactoryMixin:
    def create_user(self, **kwargs):
        suffix = uuid.uuid4().hex[:8]

        data = {
            "email": f"user_{suffix}@test.com",
            "password": "StrongPassword123",
            "user_name": f"User {suffix}",
            "role": User.ROLE_ADMIN,
            "is_active": True,
            "email_confirmed": True,
        }
        data.update(kwargs)
        return User.objects.create_user(**data)

    def create_admin_log(self, **kwargs):
        performed_by = kwargs.pop("performed_by", None) or self.create_user()

        data = {
            "action_type": "bulk_review_moderation",
            "performed_by": performed_by,
            "target_module": "reviews",
            "metadata": {"source": "unit-test"},
        }
        data.update(kwargs)

        return AdminDashboardLog.objects.create(**data)

    def create_admin_event(self, **kwargs):
        performed_by = kwargs.pop("performed_by", None) or self.create_user()
        related_log = kwargs.pop("related_log", None)

        data = {
            "event_type": AdminDashboardEvent.TYPE_DASHBOARD_VIEWED,
            "performed_by": performed_by,
            "related_log": related_log,
            "metadata": {"source": "unit-test"},
        }
        data.update(kwargs)

        return AdminDashboardEvent.objects.create(**data)


class AdminDashboardLogFilterTestCase(
    BaseAdminDashboardFilterFactoryMixin,
    TestCase,
):
    def setUp(self):
        self.admin_1 = self.create_user(email="admin1@company.com")
        self.admin_2 = self.create_user(email="admin2@company.com")

        self.log_1 = self.create_admin_log(
            performed_by=self.admin_1,
            action_type="bulk_review_moderation",
            target_module="reviews",
        )

        self.log_2 = self.create_admin_log(
            performed_by=self.admin_2,
            action_type="bulk_order_action",
            target_module="orders",
        )

        AdminDashboardLog.objects.filter(id=self.log_1.id).update(
            created_at=timezone.now() - timedelta(days=1)
        )
        AdminDashboardLog.objects.filter(id=self.log_2.id).update(
            created_at=timezone.now()
        )

        self.log_1.refresh_from_db()
        self.log_2.refresh_from_db()

    def test_filter_by_action_type(self):
        """Filter admin logs by action type."""
        queryset = AdminDashboardLog.objects.all()

        filtered = AdminDashboardLogFilter(
            {"action_type": "bulk_order_action"},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.log_2)

    def test_filter_by_target_module(self):
        """Filter admin logs by target module."""
        queryset = AdminDashboardLog.objects.all()

        filtered = AdminDashboardLogFilter(
            {"target_module": "reviews"},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.log_1)

    def test_filter_by_performed_by(self):
        """Filter admin logs by performing user."""
        queryset = AdminDashboardLog.objects.all()

        filtered = AdminDashboardLogFilter(
            {"performed_by": self.admin_1.id},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.log_1)

    def test_filter_by_created_after(self):
        """Filter logs created after a timestamp."""
        queryset = AdminDashboardLog.objects.all()

        filtered = AdminDashboardLogFilter(
            {"created_after": self.log_1.created_at + timedelta(hours=1)},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.log_2)

    def test_filter_by_created_before(self):
        """Filter logs created before a timestamp."""
        queryset = AdminDashboardLog.objects.all()

        filtered = AdminDashboardLogFilter(
            {"created_before": self.log_2.created_at - timedelta(hours=1)},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.log_1)

    def test_filter_by_metadata(self):
        """Filter logs using metadata search."""
        queryset = AdminDashboardLog.objects.all()

        filtered = AdminDashboardLogFilter(
            {"metadata": "unit"},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 2)


class AdminDashboardEventFilterTestCase(
    BaseAdminDashboardFilterFactoryMixin,
    TestCase,
):
    def setUp(self):
        self.admin_1 = self.create_user(email="staff1@company.com")
        self.admin_2 = self.create_user(email="staff2@company.com")

        self.log = self.create_admin_log(performed_by=self.admin_1)

        self.event_1 = self.create_admin_event(
            performed_by=self.admin_1,
            related_log=self.log,
            event_type=AdminDashboardEvent.TYPE_DASHBOARD_VIEWED,
        )

        self.event_2 = self.create_admin_event(
            performed_by=self.admin_2,
            event_type=AdminDashboardEvent.TYPE_ORDER_BULK_ACTION_EXECUTED,
        )

        AdminDashboardEvent.objects.filter(id=self.event_1.id).update(
            created_at=timezone.now() - timedelta(days=1)
        )
        AdminDashboardEvent.objects.filter(id=self.event_2.id).update(
            created_at=timezone.now()
        )

        self.event_1.refresh_from_db()
        self.event_2.refresh_from_db()

    def test_filter_by_event_type(self):
        """Filter events by event type."""
        queryset = AdminDashboardEvent.objects.all()

        filtered = AdminDashboardEventFilter(
            {"event_type": AdminDashboardEvent.TYPE_DASHBOARD_VIEWED},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.event_1)

    def test_filter_by_performed_by(self):
        """Filter events by performing user."""
        queryset = AdminDashboardEvent.objects.all()

        filtered = AdminDashboardEventFilter(
            {"performed_by": self.admin_1.id},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.event_1)

    def test_filter_by_created_after(self):
        """Filter events created after timestamp."""
        queryset = AdminDashboardEvent.objects.all()

        filtered = AdminDashboardEventFilter(
            {"created_after": self.event_1.created_at + timedelta(hours=1)},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.event_2)

    def test_filter_by_created_before(self):
        """Filter events created before timestamp."""
        queryset = AdminDashboardEvent.objects.all()

        filtered = AdminDashboardEventFilter(
            {"created_before": self.event_2.created_at - timedelta(hours=1)},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.event_1)