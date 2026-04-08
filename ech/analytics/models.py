import uuid

from django.conf import settings
from django.db import models

from ech.analytics.constants.constants import (
    LABEL_SNAPSHOT_PERIOD_DAILY,
    LABEL_SNAPSHOT_PERIOD_WEEKLY,
    LABEL_SNAPSHOT_PERIOD_MONTHLY,
    LABEL_EVENT_TYPE_SNAPSHOT_CREATED,
    LABEL_EVENT_TYPE_SNAPSHOT_GENERATION_STARTED,
    LABEL_EVENT_TYPE_SNAPSHOT_GENERATION_COMPLETED,
    LABEL_EVENT_TYPE_SNAPSHOT_REFRESHED,
    LABEL_EVENT_TYPE_SNAPSHOT_FAILED,
)


class AnalyticsSnapshot(models.Model):
    """
    Main Analytics Snapshot model (Aggregate Root).

    Represents a materialized analytics snapshot for a specific period.
    Snapshots store aggregated business metrics to support fast dashboard
    queries and avoid repeated heavy aggregations across operational tables.
    """

    PERIOD_DAILY = "daily"
    PERIOD_WEEKLY = "weekly"
    PERIOD_MONTHLY = "monthly"

    PERIOD_TYPE_CHOICES = [
        (PERIOD_DAILY, LABEL_SNAPSHOT_PERIOD_DAILY),
        (PERIOD_WEEKLY, LABEL_SNAPSHOT_PERIOD_WEEKLY),
        (PERIOD_MONTHLY, LABEL_SNAPSHOT_PERIOD_MONTHLY),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    period_type = models.CharField(
        max_length=16,
        choices=PERIOD_TYPE_CHOICES,
        db_index=True,
    )

    period_start = models.DateTimeField(
        db_index=True,
    )

    period_end = models.DateTimeField(
        db_index=True,
    )

    total_orders = models.PositiveIntegerField(
        default=0,
    )

    orders_pending = models.PositiveIntegerField(
        default=0,
    )

    orders_processing = models.PositiveIntegerField(
        default=0,
    )

    orders_shipped = models.PositiveIntegerField(
        default=0,
    )

    orders_delivered = models.PositiveIntegerField(
        default=0,
    )

    orders_cancelled = models.PositiveIntegerField(
        default=0,
    )

    total_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    total_refunds = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    net_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    payments_captured = models.PositiveIntegerField(
        default=0,
    )

    payments_failed = models.PositiveIntegerField(
        default=0,
    )

    payments_refunded = models.PositiveIntegerField(
        default=0,
    )

    shipments_in_transit = models.PositiveIntegerField(
        default=0,
    )

    shipments_delivered = models.PositiveIntegerField(
        default=0,
    )

    shipments_failed = models.PositiveIntegerField(
        default=0,
    )

    products_sold = models.PositiveIntegerField(
        default=0,
    )

    top_product_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    active_customers = models.PositiveIntegerField(
        default=0,
    )

    new_customers = models.PositiveIntegerField(
        default=0,
    )

    total_registered_users = models.PositiveIntegerField(
        default=0,
    )

    active_users = models.PositiveIntegerField(
        default=0,
    )

    inactive_users = models.PositiveIntegerField(
        default=0,
    )

    confirmed_users = models.PositiveIntegerField(
        default=0,
    )

    unconfirmed_users = models.PositiveIntegerField(
        default=0,
    )

    staff_users = models.PositiveIntegerField(
        default=0,
    )

    customer_users = models.PositiveIntegerField(
        default=0,
    )

    total_reviews = models.PositiveIntegerField(
        default=0,
    )

    approved_reviews = models.PositiveIntegerField(
        default=0,
    )

    rejected_reviews = models.PositiveIntegerField(
        default=0,
    )

    hidden_reviews = models.PositiveIntegerField(
        default=0,
    )

    cancelled_reviews = models.PositiveIntegerField(
        default=0,
    )

    verified_purchase_reviews = models.PositiveIntegerField(
        default=0,
    )

    average_rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0,
    )

    low_rated_products_count = models.PositiveIntegerField(
        default=0,
    )

    high_rated_products_count = models.PositiveIntegerField(
        default=0,
    )

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="generated_analytics_snapshots",
    )

    idempotency_key = models.UUIDField(
        null=True,
        blank=True,
        unique=True,
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

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["period_type", "period_start", "period_end"],
                name="unique_analytics_snapshot_period",
            ),
        ]

        indexes = [
            models.Index(
                fields=["period_type", "period_start"],
                name="analytic_period_start_idx",
            ),
            models.Index(
                fields=["period_type", "period_end"],
                name="analytic_period_end_idx",
            ),
            models.Index(
                fields=["period_start", "period_end"],
                name="analytic_period_range_idx",
            ),
            models.Index(
                fields=["generated_by"],
                name="analytic_generated_by_idx",
            ),
            models.Index(
                fields=["idempotency_key"],
                name="analytic_idempotency_idx",
            ),
            models.Index(
                fields=["top_product_id"],
                name="analytic_top_product_idx",
            ),
        ]

    def __str__(self):
        return f"{self.period_type} snapshot - {self.period_start}"


class AnalyticsSnapshotLifecycle(models.Model):
    """
    Tracks lifecycle timestamps of an analytics snapshot.
    """

    snapshot = models.OneToOneField(
        AnalyticsSnapshot,
        on_delete=models.CASCADE,
        related_name="lifecycle",
    )

    generation_started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    generation_completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    refreshed_at = models.DateTimeField(
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
        return f"Lifecycle for Snapshot {self.snapshot_id}"


class AnalyticsEvent(models.Model):
    """
    Stores audit events related to analytics operations.

    Useful for operational monitoring, traceability, debugging,
    snapshot lifecycle auditing, and future observability integrations.
    """

    TYPE_SNAPSHOT_CREATED = "snapshot_created"
    TYPE_SNAPSHOT_GENERATION_STARTED = "snapshot_generation_started"
    TYPE_SNAPSHOT_GENERATION_COMPLETED = "snapshot_generation_completed"
    TYPE_SNAPSHOT_REFRESHED = "snapshot_refreshed"
    TYPE_SNAPSHOT_FAILED = "snapshot_failed"

    EVENT_TYPE_CHOICES = [
        (TYPE_SNAPSHOT_CREATED, LABEL_EVENT_TYPE_SNAPSHOT_CREATED),
        (
            TYPE_SNAPSHOT_GENERATION_STARTED,
            LABEL_EVENT_TYPE_SNAPSHOT_GENERATION_STARTED,
        ),
        (
            TYPE_SNAPSHOT_GENERATION_COMPLETED,
            LABEL_EVENT_TYPE_SNAPSHOT_GENERATION_COMPLETED,
        ),
        (TYPE_SNAPSHOT_REFRESHED, LABEL_EVENT_TYPE_SNAPSHOT_REFRESHED),
        (TYPE_SNAPSHOT_FAILED, LABEL_EVENT_TYPE_SNAPSHOT_FAILED),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    snapshot = models.ForeignKey(
        AnalyticsSnapshot,
        on_delete=models.CASCADE,
        related_name="events",
    )

    event_type = models.CharField(
        max_length=100,
        choices=EVENT_TYPE_CHOICES,
        db_index=True,
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="analytics_events",
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
                fields=["snapshot", "created_at"],
                name="analyticevent_ss_created_idx",
            ),
            models.Index(
                fields=["event_type"],
                name="analyticevent_type_idx",
            ),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.snapshot_id}"