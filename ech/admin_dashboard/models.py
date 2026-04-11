import uuid

from django.conf import settings
from django.db import models

from ech.admin_dashboard.constants.constants import (
    LABEL_EVENT_TYPE_DASHBOARD_VIEWED,
    LABEL_EVENT_TYPE_DASHBOARD_SUMMARY_FETCHED,
    LABEL_EVENT_TYPE_DASHBOARD_OPERATIONAL_METRICS_FETCHED,
    LABEL_EVENT_TYPE_DASHBOARD_RECENT_ACTIVITY_FETCHED,
    LABEL_EVENT_TYPE_ORDER_BULK_ACTION_EXECUTED,
    LABEL_EVENT_TYPE_REVIEW_BULK_MODERATION_EXECUTED,
    LABEL_EVENT_TYPE_NOTIFICATION_RETRY_EXECUTED,
    LABEL_EVENT_TYPE_OPERATIONAL_ALERT_TRIGGERED,
)


class AdminDashboardLog(models.Model):
    """
    Stores administrative actions performed through the Admin Dashboard.

    This model acts as the audit log for operational activities executed
    through the dashboard such as bulk operations, dashboard access,
    and system monitoring queries.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    action_type = models.CharField(
        max_length=120,
        db_index=True,
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="admin_dashboard_logs",
    )

    target_object_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    target_module = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
    )

    metadata = models.JSONField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["action_type"],
                name="adminlog_action_type_idx",
            ),
            models.Index(
                fields=["performed_by"],
                name="adminlog_performed_by_idx",
            ),
            models.Index(
                fields=["target_module"],
                name="adminlog_target_module_idx",
            ),
            models.Index(
                fields=["created_at"],
                name="adminlog_created_idx",
            ),
        ]

    def __str__(self):
        return f"{self.action_type} - {self.created_at}"


class AdminDashboardLifecycle(models.Model):
    """
    Tracks lifecycle timestamps of dashboard-related administrative processes.

    Useful for tracing long-running operations such as bulk actions
    and system monitoring tasks.
    """

    log = models.OneToOneField(
        AdminDashboardLog,
        on_delete=models.CASCADE,
        related_name="lifecycle",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    failed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Lifecycle for Admin Log {self.log_id}"


class AdminDashboardEvent(models.Model):
    """
    Stores dashboard-related system events.

    These events power the Admin Dashboard "Recent Activity"
    and provide traceability for monitoring operations.
    """

    TYPE_DASHBOARD_VIEWED = "dashboard_viewed"
    TYPE_DASHBOARD_SUMMARY_FETCHED = "dashboard_summary_fetched"
    TYPE_DASHBOARD_OPERATIONAL_METRICS_FETCHED = "dashboard_operational_metrics_fetched"
    TYPE_DASHBOARD_RECENT_ACTIVITY_FETCHED = "dashboard_recent_activity_fetched"

    TYPE_ORDER_BULK_ACTION_EXECUTED = "order_bulk_action_executed"
    TYPE_REVIEW_BULK_MODERATION_EXECUTED = "review_bulk_moderation_executed"
    TYPE_NOTIFICATION_RETRY_EXECUTED = "notification_retry_executed"

    TYPE_OPERATIONAL_ALERT_TRIGGERED = "operational_alert_triggered"

    EVENT_TYPE_CHOICES = [
        (TYPE_DASHBOARD_VIEWED, LABEL_EVENT_TYPE_DASHBOARD_VIEWED),
        (
            TYPE_DASHBOARD_SUMMARY_FETCHED,
            LABEL_EVENT_TYPE_DASHBOARD_SUMMARY_FETCHED,
        ),
        (
            TYPE_DASHBOARD_OPERATIONAL_METRICS_FETCHED,
            LABEL_EVENT_TYPE_DASHBOARD_OPERATIONAL_METRICS_FETCHED,
        ),
        (
            TYPE_DASHBOARD_RECENT_ACTIVITY_FETCHED,
            LABEL_EVENT_TYPE_DASHBOARD_RECENT_ACTIVITY_FETCHED,
        ),
        (
            TYPE_ORDER_BULK_ACTION_EXECUTED,
            LABEL_EVENT_TYPE_ORDER_BULK_ACTION_EXECUTED,
        ),
        (
            TYPE_REVIEW_BULK_MODERATION_EXECUTED,
            LABEL_EVENT_TYPE_REVIEW_BULK_MODERATION_EXECUTED,
        ),
        (
            TYPE_NOTIFICATION_RETRY_EXECUTED,
            LABEL_EVENT_TYPE_NOTIFICATION_RETRY_EXECUTED,
        ),
        (
            TYPE_OPERATIONAL_ALERT_TRIGGERED,
            LABEL_EVENT_TYPE_OPERATIONAL_ALERT_TRIGGERED,
        ),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    event_type = models.CharField(
        max_length=120,
        choices=EVENT_TYPE_CHOICES,
        db_index=True,
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="admin_dashboard_events",
    )

    related_log = models.ForeignKey(
        AdminDashboardLog,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
    )

    metadata = models.JSONField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["event_type"],
                name="admindash_event_type_idx",
            ),
            models.Index(
                fields=["created_at"],
                name="admindash_event_created_idx",
            ),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.created_at}"