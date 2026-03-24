import uuid

from django.conf import settings
from django.db import models

from ech.orders.models import Order

from ech.shipping.constants.messages import (
    SHIPMENT_NOTE_HELP_TEXT,
)

from ech.shipping.constants.constants import (
    LABEL_SHIPMENT_STATUS_PENDING,
    LABEL_SHIPMENT_STATUS_PREPARING,
    LABEL_SHIPMENT_STATUS_READY_TO_SHIP,
    LABEL_SHIPMENT_STATUS_SHIPPED,
    LABEL_SHIPMENT_STATUS_IN_TRANSIT,
    LABEL_SHIPMENT_STATUS_OUT_FOR_DELIVERY,
    LABEL_SHIPMENT_STATUS_DELIVERED,
    LABEL_SHIPMENT_STATUS_FAILED,
    LABEL_SHIPMENT_STATUS_RETURNED,
    LABEL_SHIPMENT_STATUS_CANCELLED,
    LABEL_SHIPPING_METHOD_STANDARD,
    LABEL_SHIPPING_METHOD_EXPRESS,
    LABEL_SHIPPING_METHOD_SAME_DAY,
    LABEL_SHIPPING_METHOD_PICKUP_POINT,
    LABEL_EVENT_TYPE_CREATED,
    LABEL_EVENT_TYPE_UPDATED,
    LABEL_EVENT_TYPE_STATUS_CHANGED,
    LABEL_EVENT_TYPE_PREPARING_STARTED,
    LABEL_EVENT_TYPE_READY_TO_SHIP,
    LABEL_EVENT_TYPE_SHIPPED,
    LABEL_EVENT_TYPE_IN_TRANSIT,
    LABEL_EVENT_TYPE_OUT_FOR_DELIVERY,
    LABEL_EVENT_TYPE_DELIVERED,
    LABEL_EVENT_TYPE_FAILED,
    LABEL_EVENT_TYPE_RETURNED,
    LABEL_EVENT_TYPE_CANCELLED,
    LABEL_EVENT_TYPE_TRACKING_UPDATED,
)


class Shipment(models.Model):
    """
    Main Shipment model (Aggregate Root).

    Represents the shipping process associated with an order.
    Centralizes operational shipping data such as carrier,
    tracking reference, delivery estimate, and current status.
    """

    """
    Shipment status choices.
    """

    STATUS_PENDING = "pending"
    STATUS_PREPARING = "preparing"
    STATUS_READY_TO_SHIP = "ready_to_ship"
    STATUS_SHIPPED = "shipped"
    STATUS_IN_TRANSIT = "in_transit"
    STATUS_OUT_FOR_DELIVERY = "out_for_delivery"
    STATUS_DELIVERED = "delivered"
    STATUS_FAILED = "failed"
    STATUS_RETURNED = "returned"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, LABEL_SHIPMENT_STATUS_PENDING),
        (STATUS_PREPARING, LABEL_SHIPMENT_STATUS_PREPARING),
        (STATUS_READY_TO_SHIP, LABEL_SHIPMENT_STATUS_READY_TO_SHIP),
        (STATUS_SHIPPED, LABEL_SHIPMENT_STATUS_SHIPPED),
        (STATUS_IN_TRANSIT, LABEL_SHIPMENT_STATUS_IN_TRANSIT),
        (STATUS_OUT_FOR_DELIVERY, LABEL_SHIPMENT_STATUS_OUT_FOR_DELIVERY),
        (STATUS_DELIVERED, LABEL_SHIPMENT_STATUS_DELIVERED),
        (STATUS_FAILED, LABEL_SHIPMENT_STATUS_FAILED),
        (STATUS_RETURNED, LABEL_SHIPMENT_STATUS_RETURNED),
        (STATUS_CANCELLED, LABEL_SHIPMENT_STATUS_CANCELLED),
    ]

    """
    Shipping method choices.
    """

    METHOD_STANDARD = "standard"
    METHOD_EXPRESS = "express"
    METHOD_SAME_DAY = "same_day"
    METHOD_PICKUP_POINT = "pickup_point"

    METHOD_CHOICES = [
        (METHOD_STANDARD, LABEL_SHIPPING_METHOD_STANDARD),
        (METHOD_EXPRESS, LABEL_SHIPPING_METHOD_EXPRESS),
        (METHOD_SAME_DAY, LABEL_SHIPPING_METHOD_SAME_DAY),
        (METHOD_PICKUP_POINT, LABEL_SHIPPING_METHOD_PICKUP_POINT),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="shipment",
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="shipments",
    )

    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        db_index=True,
    )

    shipping_method = models.CharField(
        max_length=32,
        choices=METHOD_CHOICES,
        default=METHOD_STANDARD,
        db_index=True,
    )

    carrier_name = models.CharField(
        max_length=120,
        blank=True,
    )

    tracking_code = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
    )

    external_reference = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        db_index=True,
        help_text= "Reference used by external carrier or shipping gateway.",
    )

    idempotency_key = models.UUIDField(
        null=True,
        blank=True,
        unique=True,
        db_index=True,
    )

    shipping_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    currency = models.CharField(
        max_length=10,
        default="USD",
    )

    estimated_delivery_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
    )

    delivered_to_name = models.CharField(
        max_length=255,
        blank=True,
        help_text= "Optional recipient confirmation name for delivery.",
    )

    is_return_to_sender = models.BooleanField(
        default=False,
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
                fields=["customer", "created_at"],
                name="ship_cust_created_idx",
            ),
            models.Index(
                fields=["status"],
                name="ship_status_idx",
            ),
            models.Index(
                fields=["tracking_code"],
                name="ship_track_idx",
            ),
            models.Index(
                fields=["estimated_delivery_date"],
                name="ship_est_deliv_idx",
            ),
        ]

    def __str__(self):
        return f"Shipment {self.id}"


class ShipmentAddress(models.Model):
    """
    Snapshot of the delivery address used for the shipment.

    This is intentionally separated from the order address so the
    shipment can preserve its own historical delivery destination,
    even if operational adjustments happen later.
    """

    shipment = models.OneToOneField(
        Shipment,
        on_delete=models.CASCADE,
        related_name="address",
    )

    full_name = models.CharField(
        max_length=255,
    )

    address_line = models.CharField(
        max_length=255,
    )

    city = models.CharField(
        max_length=120,
    )

    state = models.CharField(
        max_length=120,
    )

    country = models.CharField(
        max_length=120,
    )

    postal_code = models.CharField(
        max_length=20,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    delivery_instructions = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.full_name} - {self.city}"


class ShipmentLifecycle(models.Model):
    """
    Tracks lifecycle timestamps of a shipment.
    """

    shipment = models.OneToOneField(
        Shipment,
        on_delete=models.CASCADE,
        related_name= "lifecycle",
    )

    preparing_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    ready_to_ship_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    shipped_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    in_transit_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    out_for_delivery_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    failed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    returned_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    cancelled_at = models.DateTimeField(
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
        return f"Lifecycle for Shipment {self.shipment_id}"


class ShipmentEvent(models.Model):
    """
    Stores audit events related to a shipment.

    Useful for operational monitoring, debugging, and
    business-level traceability.
    """

    TYPE_CREATED = "shipment_created"
    TYPE_UPDATED = "shipment_updated"
    TYPE_STATUS_CHANGED = "shipment_status_changed"
    TYPE_PREPARING_STARTED = "shipment_preparing_started"
    TYPE_READY_TO_SHIP = "shipment_ready_to_ship"
    TYPE_SHIPPED = "shipment_shipped"
    TYPE_IN_TRANSIT = "shipment_in_transit"
    TYPE_OUT_FOR_DELIVERY = "shipment_out_for_delivery"
    TYPE_DELIVERED = "shipment_delivered"
    TYPE_FAILED = "shipment_failed"
    TYPE_RETURNED = "shipment_returned"
    TYPE_CANCELLED = "shipment_cancelled"
    TYPE_TRACKING_UPDATED = "shipment_tracking_updated"

    SHIPMENT_EVENT_TYPE_CHOICES = [
        (TYPE_CREATED, LABEL_EVENT_TYPE_CREATED),
        (TYPE_UPDATED, LABEL_EVENT_TYPE_UPDATED),
        (TYPE_STATUS_CHANGED, LABEL_EVENT_TYPE_STATUS_CHANGED),
        (TYPE_PREPARING_STARTED, LABEL_EVENT_TYPE_PREPARING_STARTED),
        (TYPE_READY_TO_SHIP, LABEL_EVENT_TYPE_READY_TO_SHIP),
        (TYPE_SHIPPED, LABEL_EVENT_TYPE_SHIPPED),
        (TYPE_IN_TRANSIT, LABEL_EVENT_TYPE_IN_TRANSIT),
        (TYPE_OUT_FOR_DELIVERY, LABEL_EVENT_TYPE_OUT_FOR_DELIVERY),
        (TYPE_DELIVERED, LABEL_EVENT_TYPE_DELIVERED),
        (TYPE_FAILED, LABEL_EVENT_TYPE_FAILED),
        (TYPE_RETURNED, LABEL_EVENT_TYPE_RETURNED),
        (TYPE_CANCELLED, LABEL_EVENT_TYPE_CANCELLED),
        (TYPE_TRACKING_UPDATED, LABEL_EVENT_TYPE_TRACKING_UPDATED),
    ]


    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name= "events",
    )

    event_type = models.CharField(
        max_length=100,
        db_index=True,
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
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
                fields=["shipment", "created_at"],
                name="shipevent_ship_created",
            ),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.shipment.id}"


class ShipmentTrackingUpdate(models.Model):
    """
    Stores chronological tracking updates for a shipment.

    These records may come from internal operations or from
    an external carrier integration.
    """

    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name= "tracking_updates",
    )

    status = models.CharField(
        max_length=32,
        choices=Shipment.STATUS_CHOICES,
        blank=True,
    )

    location = models.CharField(
        max_length=255,
        blank=True,
    )

    description = models.CharField(
        max_length=255,
    )

    raw_payload = models.JSONField(
        null=True,
        blank=True,
        help_text= "Optional original payload from carrier integration.",
    )

    event_at = models.DateTimeField(
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-event_at", "-created_at"]
        indexes = [
            models.Index(
                fields=["shipment", "event_at"],
                name="shiptrack_ship_event_idx",
            ),
        ]

    def __str__(self):
        return f"Tracking update for {self.shipment_id}"


class ShipmentNote(models.Model):
    """
    Communication log related to a shipment.

    Can be used for customer-facing or internal operational notes.
    """

    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name="notes",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )

    message = models.TextField()

    is_internal = models.BooleanField(
        default=False,
        help_text=SHIPMENT_NOTE_HELP_TEXT,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=["shipment", "created_at"],
                name="shipnote_ship_created",
            ),
        ]

    def __str__(self):
        return f"Note on {self.shipment_id}"