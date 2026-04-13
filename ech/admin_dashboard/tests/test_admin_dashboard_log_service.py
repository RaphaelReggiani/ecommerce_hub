import uuid
from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase, SimpleTestCase

from ech.admin_dashboard.models import (
    AdminDashboardEvent,
    AdminDashboardLog,
)
from ech.admin_dashboard.services.admin_dashboard_log_service import (
    AdminDashboardLogService,
)
from ech.users.models import CustomUser


class BaseAdminDashboardLogFactoryMixin:
    @staticmethod
    def build_user(user_id=None):
        return SimpleNamespace(id=user_id if user_id is not None else 99)


class AdminDashboardLogServiceLoggingTestCase(
    BaseAdminDashboardLogFactoryMixin,
    SimpleTestCase,
):
    @patch("ech.admin_dashboard.services.admin_dashboard_log_service.DomainEventDispatcher.dispatch")
    @patch("ech.admin_dashboard.services.admin_dashboard_log_service.logger.info")
    def test_log_dashboard_access_logs_expected_payload(
        self,
        logger_info_mock,
        dispatch_mock,
    ):
        """Log dashboard access with structured payload."""
        user = self.build_user(user_id=10)

        with patch.object(
            AdminDashboardLogService,
            "_create_event",
            return_value=SimpleNamespace(id=uuid.uuid4()),
        ) as create_event_mock:
            AdminDashboardLogService.log_dashboard_access(user=user)

        logger_info_mock.assert_called_once_with(
            "Admin dashboard accessed.",
            extra={
                "user_id": 10,
            },
        )

        create_event_mock.assert_called_once_with(
            event_type="admin_dashboard_accessed",
            performed_by=user,
            metadata={},
        )

        dispatched_event = dispatch_mock.call_args[0][0]
        self.assertEqual(dispatched_event.event_name, "admin_dashboard_accessed")
        self.assertEqual(dispatched_event.user_id, 10)

    @patch("ech.admin_dashboard.services.admin_dashboard_log_service.logger.info")
    def test_log_bulk_order_action_logs_expected_payload(self, logger_info_mock):
        """Log bulk order action with structured payload."""
        performed_by = self.build_user(user_id=20)
        order_ids = [uuid.uuid4(), uuid.uuid4()]

        with patch.object(
            AdminDashboardLogService,
            "_create_log",
            return_value=SimpleNamespace(id=uuid.uuid4()),
        ) as create_log_mock:
            AdminDashboardLogService.log_bulk_order_action(
                action_type="mark_processing",
                order_ids=order_ids,
                performed_by=performed_by,
            )

        logger_info_mock.assert_called_once_with(
            "Admin bulk order action executed.",
            extra={
                "action_type": "mark_processing",
                "order_ids": order_ids,
                "performed_by_id": 20,
            },
        )

        create_log_mock.assert_called_once_with(
            action_type="mark_processing",
            target_module="orders",
            performed_by=performed_by,
            metadata={
                "order_ids": order_ids,
            },
        )

    @patch("ech.admin_dashboard.services.admin_dashboard_log_service.logger.info")
    def test_log_bulk_review_moderation_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log bulk review moderation with structured payload."""
        performed_by = self.build_user(user_id=30)
        review_ids = [uuid.uuid4(), uuid.uuid4()]

        with patch.object(
            AdminDashboardLogService,
            "_create_log",
            return_value=SimpleNamespace(id=uuid.uuid4()),
        ) as create_log_mock:
            AdminDashboardLogService.log_bulk_review_moderation(
                moderation_action="approve",
                review_ids=review_ids,
                performed_by=performed_by,
            )

        logger_info_mock.assert_called_once_with(
            "Admin bulk review moderation executed.",
            extra={
                "moderation_action": "approve",
                "review_ids": review_ids,
                "performed_by_id": 30,
            },
        )

        create_log_mock.assert_called_once_with(
            action_type="bulk_review_moderation",
            target_module="reviews",
            performed_by=performed_by,
            metadata={
                "review_ids": review_ids,
                "moderation_action": "approve",
            },
        )

    @patch("ech.admin_dashboard.services.admin_dashboard_log_service.logger.info")
    def test_log_notification_retry_logs_expected_payload(self, logger_info_mock):
        """Log notification retry with structured payload."""
        performed_by = self.build_user(user_id=40)
        notification_ids = [uuid.uuid4(), uuid.uuid4()]

        with patch.object(
            AdminDashboardLogService,
            "_create_log",
            return_value=SimpleNamespace(id=uuid.uuid4()),
        ) as create_log_mock:
            AdminDashboardLogService.log_notification_retry(
                notification_ids=notification_ids,
                performed_by=performed_by,
            )

        logger_info_mock.assert_called_once_with(
            "Admin notification retry executed.",
            extra={
                "notification_ids": notification_ids,
                "performed_by_id": 40,
            },
        )

        create_log_mock.assert_called_once_with(
            action_type="notification_retry",
            target_module="notifications",
            performed_by=performed_by,
            metadata={
                "notification_ids": notification_ids,
            },
        )

    @patch("ech.admin_dashboard.services.admin_dashboard_log_service.logger.warning")
    def test_log_dashboard_alert_logs_expected_payload(self, logger_warning_mock):
        """Log dashboard alert with structured payload."""
        metadata = {
            "alerts_count": 3,
            "performed_by_id": 50,
        }

        with patch.object(
            AdminDashboardLogService,
            "_create_event",
            return_value=SimpleNamespace(id=uuid.uuid4()),
        ) as create_event_mock:
            AdminDashboardLogService.log_dashboard_alert(
                alert_type="operational_alerts_generated",
                alert_message="Operational alerts detected in admin dashboard",
                metadata=metadata,
            )

        logger_warning_mock.assert_called_once_with(
            "Admin dashboard alert generated.",
            extra={
                "alert_type": "operational_alerts_generated",
                "alert_message": "Operational alerts detected in admin dashboard",
                "metadata": metadata,
            },
        )

        create_event_mock.assert_called_once_with(
            event_type="admin_dashboard_alert_generated",
            metadata={
                "alert_type": "operational_alerts_generated",
                "alert_message": "Operational alerts detected in admin dashboard",
                "alerts_count": 3,
                "performed_by_id": 50,
            },
        )

    @patch("ech.admin_dashboard.services.admin_dashboard_log_service.logger.info")
    def test_log_bulk_order_action_allows_null_performed_by(self, logger_info_mock):
        """Log bulk order action with null performer when omitted."""
        order_ids = [uuid.uuid4()]

        with patch.object(
            AdminDashboardLogService,
            "_create_log",
            return_value=SimpleNamespace(id=uuid.uuid4()),
        ) as create_log_mock:
            AdminDashboardLogService.log_bulk_order_action(
                action_type="mark_shipped",
                order_ids=order_ids,
                performed_by=None,
            )

        logger_info_mock.assert_called_once_with(
            "Admin bulk order action executed.",
            extra={
                "action_type": "mark_shipped",
                "order_ids": order_ids,
                "performed_by_id": None,
            },
        )

        create_log_mock.assert_called_once_with(
            action_type="mark_shipped",
            target_module="orders",
            performed_by=None,
            metadata={
                "order_ids": order_ids,
            },
        )


class AdminDashboardLogServicePersistenceTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = CustomUser.objects.create_user(
            email="admin.log@company.com",
            password="StrongPassword123",
            user_name="Admin Log User",
            role=CustomUser.ROLE_ADMIN,
            is_active=True,
            email_confirmed=True,
        )

    def test_create_log_persists_admin_dashboard_log(self):
        """Persist admin dashboard log through _create_log helper."""
        log = AdminDashboardLogService._create_log(
            action_type="notification_retry",
            target_module="notifications",
            performed_by=None,
            metadata={"notification_ids": [str(uuid.uuid4())]},
        )

        self.assertEqual(AdminDashboardLog.objects.count(), 1)
        self.assertEqual(log.action_type, "notification_retry")
        self.assertEqual(log.target_module, "notifications")
        self.assertIsNone(log.performed_by)
        self.assertEqual(
            log.metadata,
            {"notification_ids": [log.metadata["notification_ids"][0]]},
        )

    def test_create_event_persists_admin_dashboard_event(self):
        """Persist admin dashboard event through _create_event helper."""
        event = AdminDashboardLogService._create_event(
            event_type="admin_dashboard_alert_generated",
            performed_by=None,
            metadata={"alert_type": "pending_orders"},
        )

        self.assertEqual(AdminDashboardEvent.objects.count(), 1)
        self.assertEqual(event.event_type, "admin_dashboard_alert_generated")
        self.assertIsNone(event.performed_by)
        self.assertEqual(
            event.metadata,
            {"alert_type": "pending_orders"},
        )

    @patch("ech.admin_dashboard.services.admin_dashboard_log_service.DomainEventDispatcher.dispatch")
    def test_log_dashboard_access_persists_event(self, dispatch_mock):
        """Persist dashboard access event through log_dashboard_access."""
        AdminDashboardLogService.log_dashboard_access(user=self.admin)

        self.assertEqual(AdminDashboardEvent.objects.count(), 1)

        event = AdminDashboardEvent.objects.first()
        self.assertEqual(event.event_type, "admin_dashboard_accessed")
        self.assertEqual(event.performed_by, self.admin)
        self.assertEqual(event.metadata, {})

        dispatched_event = dispatch_mock.call_args[0][0]
        self.assertEqual(dispatched_event.user_id, self.admin.id)

    def test_log_bulk_order_action_persists_log(self):
        """Persist bulk order action log."""
        order_ids = [str(uuid.uuid4()), str(uuid.uuid4())]

        AdminDashboardLogService.log_bulk_order_action(
            action_type="cancel_orders",
            order_ids=order_ids,
            performed_by=None,
        )

        self.assertEqual(AdminDashboardLog.objects.count(), 1)

        log = AdminDashboardLog.objects.first()
        self.assertEqual(log.action_type, "cancel_orders")
        self.assertEqual(log.target_module, "orders")
        self.assertEqual(log.metadata, {"order_ids": order_ids})

    def test_log_bulk_review_moderation_persists_log(self):
        """Persist bulk review moderation log."""
        review_ids = [str(uuid.uuid4())]

        AdminDashboardLogService.log_bulk_review_moderation(
            moderation_action="reject",
            review_ids=review_ids,
            performed_by=None,
        )

        self.assertEqual(AdminDashboardLog.objects.count(), 1)

        log = AdminDashboardLog.objects.first()
        self.assertEqual(log.action_type, "bulk_review_moderation")
        self.assertEqual(log.target_module, "reviews")
        self.assertEqual(
            log.metadata,
            {
                "review_ids": review_ids,
                "moderation_action": "reject",
            },
        )

    def test_log_notification_retry_persists_log(self):
        """Persist notification retry log."""
        notification_ids = [str(uuid.uuid4())]

        AdminDashboardLogService.log_notification_retry(
            notification_ids=notification_ids,
            performed_by=None,
        )

        self.assertEqual(AdminDashboardLog.objects.count(), 1)

        log = AdminDashboardLog.objects.first()
        self.assertEqual(log.action_type, "notification_retry")
        self.assertEqual(log.target_module, "notifications")
        self.assertEqual(
            log.metadata,
            {"notification_ids": notification_ids},
        )

    def test_log_dashboard_alert_persists_event(self):
        """Persist dashboard alert event."""
        AdminDashboardLogService.log_dashboard_alert(
            alert_type="failed_payments",
            alert_message="Failed payments detected.",
            metadata={"alerts_count": 2},
        )

        self.assertEqual(AdminDashboardEvent.objects.count(), 1)

        event = AdminDashboardEvent.objects.first()
        self.assertEqual(event.event_type, "admin_dashboard_alert_generated")
        self.assertEqual(
            event.metadata,
            {
                "alert_type": "failed_payments",
                "alert_message": "Failed payments detected.",
                "alerts_count": 2,
            },
        )