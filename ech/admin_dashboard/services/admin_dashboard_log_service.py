import logging

from ech.admin_dashboard.models import (
    AdminDashboardLog,
    AdminDashboardEvent,
)

from ech.admin_dashboard.domain_events.dispatcher import DomainEventDispatcher
from ech.admin_dashboard.domain_events.events import (
    AdminDashboardAccessedEvent,
)

from ech.admin_dashboard.constants.constants import (
    LABEL_EVENT_TYPE_DASHBOARD_VIEWED,
    LABEL_EVENT_TYPE_ORDER_BULK_ACTION_EXECUTED,
    LABEL_EVENT_TYPE_REVIEW_BULK_MODERATION_EXECUTED,
    LABEL_EVENT_TYPE_NOTIFICATION_RETRY_EXECUTED,
    LABEL_EVENT_TYPE_OPERATIONAL_ALERT_TRIGGERED,
)

logger = logging.getLogger(__name__)


class AdminDashboardLogService:
    """
    Service responsible for structured admin dashboard logs
    and domain event dispatching.
    """

    @staticmethod
    def _create_log(
        *,
        action_type,
        target_module,
        performed_by=None,
        metadata=None,
    ):
        """
        Persist an admin dashboard log entry.
        """

        return AdminDashboardLog.objects.create(
            action_type=action_type,
            target_module=target_module,
            performed_by=performed_by,
            metadata=metadata or {},
        )

    @staticmethod
    def _create_event(
        *,
        event_type,
        performed_by=None,
        metadata=None,
    ):
        """
        Persist an admin dashboard event entry.
        """

        return AdminDashboardEvent.objects.create(
            event_type=event_type,
            performed_by=performed_by,
            metadata=metadata or {},
        )

    @classmethod
    def log_dashboard_access(cls, *, user):
        """
        Log dashboard access.
        """

        logger.info(
            "Admin dashboard accessed.",
            extra={
                "user_id": getattr(user, "id", None),
            },
        )

        cls._create_event(
            event_type=LABEL_EVENT_TYPE_DASHBOARD_VIEWED,
            performed_by=user,
            metadata={},
        )

        DomainEventDispatcher.dispatch(
            AdminDashboardAccessedEvent(
                user_id=getattr(user, "id", None),
            )
        )

    @classmethod
    def log_bulk_order_action(
        cls,
        *,
        action_type,
        order_ids,
        performed_by=None,
    ):
        """
        Log bulk order administrative operation.
        """

        metadata = {
            "order_ids": order_ids,
        }

        logger.info(
            "Admin bulk order action executed.",
            extra={
                "action_type": action_type,
                "order_ids": order_ids,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

        cls._create_log(
            action_type=action_type,
            target_module="orders",
            performed_by=performed_by,
            metadata=metadata,
        )

        cls._create_event(
            event_type=LABEL_EVENT_TYPE_ORDER_BULK_ACTION_EXECUTED,
            performed_by=performed_by,
            metadata=metadata,
        )

    @classmethod
    def log_bulk_review_moderation(
        cls,
        *,
        moderation_action,
        review_ids,
        performed_by=None,
    ):
        """
        Log bulk review moderation action.
        """

        metadata = {
            "review_ids": review_ids,
            "moderation_action": moderation_action,
        }

        logger.info(
            "Admin bulk review moderation executed.",
            extra={
                "moderation_action": moderation_action,
                "review_ids": review_ids,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

        cls._create_log(
            action_type="bulk_review_moderation",
            target_module="reviews",
            performed_by=performed_by,
            metadata=metadata,
        )

        cls._create_event(
            event_type=LABEL_EVENT_TYPE_REVIEW_BULK_MODERATION_EXECUTED,
            performed_by=performed_by,
            metadata=metadata,
        )

    @classmethod
    def log_notification_retry(
        cls,
        *,
        notification_ids,
        performed_by=None,
    ):
        """
        Log notification retry administrative operation.
        """

        metadata = {
            "notification_ids": notification_ids,
        }

        logger.info(
            "Admin notification retry executed.",
            extra={
                "notification_ids": notification_ids,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

        cls._create_log(
            action_type="notification_retry",
            target_module="notifications",
            performed_by=performed_by,
            metadata=metadata,
        )

        cls._create_event(
            event_type=LABEL_EVENT_TYPE_NOTIFICATION_RETRY_EXECUTED,
            performed_by=performed_by,
            metadata=metadata,
        )

    @classmethod
    def log_dashboard_alert(
        cls,
        *,
        alert_type,
        alert_message,
        metadata=None,
    ):
        """
        Log a dashboard alert.
        """

        logger.warning(
            "Admin dashboard alert generated.",
            extra={
                "alert_type": alert_type,
                "alert_message": alert_message,
                "metadata": metadata or {},
            },
        )

        cls._create_event(
            event_type=LABEL_EVENT_TYPE_OPERATIONAL_ALERT_TRIGGERED,
            metadata={
                "alert_type": alert_type,
                "alert_message": alert_message,
                **(metadata or {}),
            },
        )