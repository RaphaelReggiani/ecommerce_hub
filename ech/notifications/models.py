import uuid

from django.conf import settings
from django.db import models

from ech.notifications.constants.constants import (
    LABEL_NOTIFICATION_STATUS_PENDING,
    LABEL_NOTIFICATION_STATUS_UNREAD,
    LABEL_NOTIFICATION_STATUS_READ,
    LABEL_NOTIFICATION_STATUS_ARCHIVED,
    LABEL_NOTIFICATION_STATUS_CANCELLED,
    LABEL_NOTIFICATION_STATUS_FAILED,
    LABEL_NOTIFICATION_CHANNEL_IN_APP,
    LABEL_NOTIFICATION_CHANNEL_EMAIL,
    LABEL_NOTIFICATION_CHANNEL_BOTH,
    LABEL_NOTIFICATION_PRIORITY_LOW,
    LABEL_NOTIFICATION_PRIORITY_NORMAL,
    LABEL_NOTIFICATION_PRIORITY_HIGH,
    LABEL_NOTIFICATION_PRIORITY_CRITICAL,
    LABEL_DELIVERY_STATUS_PENDING,
    LABEL_DELIVERY_STATUS_SENT,
    LABEL_DELIVERY_STATUS_DELIVERED,
    LABEL_DELIVERY_STATUS_FAILED,
    LABEL_DELIVERY_STATUS_CANCELLED,
    LABEL_DELIVERY_CHANNEL_IN_APP,
    LABEL_DELIVERY_CHANNEL_EMAIL,
    LABEL_EVENT_TYPE_CREATED,
    LABEL_EVENT_TYPE_STATUS_CHANGED,
    LABEL_EVENT_TYPE_DISPATCHED,
    LABEL_EVENT_TYPE_READ,
    LABEL_EVENT_TYPE_ARCHIVED,
    LABEL_EVENT_TYPE_CANCELLED,
    LABEL_EVENT_TYPE_FAILED,
    LABEL_EVENT_TYPE_DELIVERY_SENT,
    LABEL_EVENT_TYPE_DELIVERY_FAILED,
)


class Notification(models.Model):
    """
    Main Notification model (Aggregate Root).

    Represents a user-facing notification that can be delivered
    through one or more channels such as in-app or email.

    The aggregate stores the canonical notification content,
    recipient, current notification state, source reference,
    operational metadata, and idempotency information.
    """

    STATUS_PENDING = "pending"
    STATUS_UNREAD = "unread"
    STATUS_READ = "read"
    STATUS_ARCHIVED = "archived"
    STATUS_CANCELLED = "cancelled"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, LABEL_NOTIFICATION_STATUS_PENDING),
        (STATUS_UNREAD, LABEL_NOTIFICATION_STATUS_UNREAD),
        (STATUS_READ, LABEL_NOTIFICATION_STATUS_READ),
        (STATUS_ARCHIVED, LABEL_NOTIFICATION_STATUS_ARCHIVED),
        (STATUS_CANCELLED, LABEL_NOTIFICATION_STATUS_CANCELLED),
        (STATUS_FAILED, LABEL_NOTIFICATION_STATUS_FAILED),
    ]

    CHANNEL_IN_APP = "in_app"
    CHANNEL_EMAIL = "email"
    CHANNEL_BOTH = "both"

    CHANNEL_CHOICES = [
        (CHANNEL_IN_APP, LABEL_NOTIFICATION_CHANNEL_IN_APP),
        (CHANNEL_EMAIL, LABEL_NOTIFICATION_CHANNEL_EMAIL),
        (CHANNEL_BOTH, LABEL_NOTIFICATION_CHANNEL_BOTH),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_NORMAL = "normal"
    PRIORITY_HIGH = "high"
    PRIORITY_CRITICAL = "critical"

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, LABEL_NOTIFICATION_PRIORITY_LOW),
        (PRIORITY_NORMAL, LABEL_NOTIFICATION_PRIORITY_NORMAL),
        (PRIORITY_HIGH, LABEL_NOTIFICATION_PRIORITY_HIGH),
        (PRIORITY_CRITICAL, LABEL_NOTIFICATION_PRIORITY_CRITICAL),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="notifications",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_notifications",
    )

    notification_type = models.CharField(
        max_length=100,
        db_index=True,
        help_text=(
            "Business-level notification type "
            "(example: order_shipped, payment_captured)."
        ),
    )

    title = models.CharField(
        max_length=255,
    )

    message = models.TextField()

    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )

    channel = models.CharField(
        max_length=32,
        choices=CHANNEL_CHOICES,
        default=CHANNEL_IN_APP,
        db_index=True,
    )

    priority = models.CharField(
        max_length=16,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_NORMAL,
        db_index=True,
    )

    source_module = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text=(
            "Origin module of the notification "
            "(example: orders, payments, shipping)."
        ),
    )

    source_event = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Origin event name that triggered the notification.",
    )

    source_object_id = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text=(
            "Identifier of the related source object. "
            "Stored as text for flexibility."
        ),
    )

    scheduled_for = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Optional future datetime for deferred dispatch.",
    )

    idempotency_key = models.UUIDField(
        null=True,
        blank=True,
        unique=True,
        db_index=True,
    )

    failure_code = models.CharField(
        max_length=64,
        blank=True,
    )

    failure_message = models.TextField(
        blank=True,
    )

    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text=(
            "Flexible context payload used for rendering, auditing, "
            "or integrations."
        ),
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
        indexes = [
            models.Index(
                fields=["recipient", "created_at"],
                name="not_rec_created_idx",
            ),
            models.Index(
                fields=["status"],
                name="not_status_idx",
            ),
            models.Index(
                fields=["channel"],
                name="not_chan_idx",
            ),
            models.Index(
                fields=["scheduled_for"],
                name="not_sched_idx",
            ),
            models.Index(
                fields=["source_module", "source_object_id"],
                name="not_src_ref_idx",
            ),
        ]

    def __str__(self):
        return f"Notification {self.id} - {self.recipient_id}"


class NotificationLifecycle(models.Model):
    """
    Tracks lifecycle timestamps of a notification.
    """

    notification = models.OneToOneField(
        Notification,
        on_delete=models.CASCADE,
        related_name="lifecycle",
    )

    dispatched_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    archived_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    cancelled_at = models.DateTimeField(
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
        return f"Lifecycle for Notification {self.notification_id}"


class NotificationDelivery(models.Model):
    """
    Stores per-channel delivery attempts for a notification.
    """

    CHANNEL_IN_APP = "in_app"
    CHANNEL_EMAIL = "email"

    CHANNEL_CHOICES = [
        (CHANNEL_IN_APP, LABEL_DELIVERY_CHANNEL_IN_APP),
        (CHANNEL_EMAIL, LABEL_DELIVERY_CHANNEL_EMAIL),
    ]

    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"
    STATUS_DELIVERED = "delivered"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, LABEL_DELIVERY_STATUS_PENDING),
        (STATUS_SENT, LABEL_DELIVERY_STATUS_SENT),
        (STATUS_DELIVERED, LABEL_DELIVERY_STATUS_DELIVERED),
        (STATUS_FAILED, LABEL_DELIVERY_STATUS_FAILED),
        (STATUS_CANCELLED, LABEL_DELIVERY_STATUS_CANCELLED),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )

    channel = models.CharField(
        max_length=32,
        choices=CHANNEL_CHOICES,
        db_index=True,
    )

    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )

    provider_name = models.CharField(
        max_length=50,
        blank=True,
        help_text=(
            "Logical provider used for the delivery attempt "
            "(example: email_provider, in_app_provider)."
        ),
    )

    recipient_address = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Resolved delivery destination such as email address "
            "when applicable."
        ),
    )

    external_message_id = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        help_text="Optional external provider message identifier.",
    )

    failure_code = models.CharField(
        max_length=64,
        blank=True,
    )

    failure_message = models.TextField(
        blank=True,
    )

    metadata = models.JSONField(
        null=True,
        blank=True,
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="performed_notification_deliveries",
    )

    processed_at = models.DateTimeField(
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
                fields=["notification", "created_at"],
                name="notdel_not_cre_idx",
            ),
            models.Index(
                fields=["channel", "status"],
                name="notdel_ch_st_idx",
            ),
        ]

    def __str__(self):
        return f"{self.channel} delivery - {self.notification_id}"


class NotificationEvent(models.Model):
    """
    Stores audit events related to a notification.
    """

    TYPE_CREATED = "notification_created"
    TYPE_STATUS_CHANGED = "notification_status_changed"
    TYPE_DISPATCHED = "notification_dispatched"
    TYPE_READ = "notification_read"
    TYPE_ARCHIVED = "notification_archived"
    TYPE_CANCELLED = "notification_cancelled"
    TYPE_FAILED = "notification_failed"
    TYPE_DELIVERY_SENT = "notification_delivery_sent"
    TYPE_DELIVERY_FAILED = "notification_delivery_failed"

    EVENT_TYPE_CHOICES = [
        (TYPE_CREATED, LABEL_EVENT_TYPE_CREATED),
        (TYPE_STATUS_CHANGED, LABEL_EVENT_TYPE_STATUS_CHANGED),
        (TYPE_DISPATCHED, LABEL_EVENT_TYPE_DISPATCHED),
        (TYPE_READ, LABEL_EVENT_TYPE_READ),
        (TYPE_ARCHIVED, LABEL_EVENT_TYPE_ARCHIVED),
        (TYPE_CANCELLED, LABEL_EVENT_TYPE_CANCELLED),
        (TYPE_FAILED, LABEL_EVENT_TYPE_FAILED),
        (TYPE_DELIVERY_SENT, LABEL_EVENT_TYPE_DELIVERY_SENT),
        (TYPE_DELIVERY_FAILED, LABEL_EVENT_TYPE_DELIVERY_FAILED),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    notification = models.ForeignKey(
        Notification,
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
        related_name="performed_notification_events",
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
                fields=["notification", "created_at"],
                name="notevt_not_cre_idx",
            ),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.notification_id}"