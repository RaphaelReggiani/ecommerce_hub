import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from ech.products.models import Product

from ech.orders.constants.messages import (
    ORDER_NOTE_HELP_TEXT,
)

from ech.orders.constants.constants import (
    LABEL_ORDER_STATUS_PENDING,
    LABEL_ORDER_STATUS_CONFIRMED,
    LABEL_ORDER_STATUS_PROCESSING,
    LABEL_ORDER_STATUS_SHIPPED,
    LABEL_ORDER_STATUS_DELIVERED,
    LABEL_ORDER_STATUS_CANCELLED,
    LABEL_ORDER_STATUS_REFUNDED,
    LABEL_PAYMENT_PENDING,
    LABEL_PAYMENT_AUTHORIZED,
    LABEL_PAYMENT_CAPTURED,
    LABEL_PAYMENT_FAILED,
    LABEL_PAYMENT_REFUNDED,
    LABEL_SHIPPING_PENDING,
    LABEL_SHIPPING_PREPARING,
    LABEL_SHIPPING_SHIPPED,
    LABEL_SHIPPING_IN_TRANSIT,
    LABEL_SHIPPING_DELIVERED,
)


class Order(models.Model):
    """
    Main Order model (Aggregate Root).

    Represents a customer's order.
    All related entities (items, totals, lifecycle, etc.)
    belong to this aggregate.
    
    """

    """
    Order status choices.
    """

    ORDER_STATUS_PENDING = "pending"
    ORDER_STATUS_CONFIRMED = "confirmed"
    ORDER_STATUS_PROCESSING = "processing"
    ORDER_STATUS_SHIPPED = "shipped"
    ORDER_STATUS_DELIVERED = "delivered"
    ORDER_STATUS_CANCELLED = "cancelled"
    ORDER_STATUS_REFUNDED = "refunded"


    ORDER_STATUS_CHOICES = [
        (ORDER_STATUS_PENDING, LABEL_ORDER_STATUS_PENDING),
        (ORDER_STATUS_CONFIRMED, LABEL_ORDER_STATUS_CONFIRMED),
        (ORDER_STATUS_PROCESSING, LABEL_ORDER_STATUS_PROCESSING),
        (ORDER_STATUS_SHIPPED, LABEL_ORDER_STATUS_SHIPPED),
        (ORDER_STATUS_DELIVERED, LABEL_ORDER_STATUS_DELIVERED),
        (ORDER_STATUS_CANCELLED, LABEL_ORDER_STATUS_CANCELLED),
        (ORDER_STATUS_REFUNDED, LABEL_ORDER_STATUS_REFUNDED),
    ]

    """
    Payment status choices.
    """

    PAYMENT_STATUS_PENDING = "pending"
    PAYMENT_STATUS_AUTHORIZED = "authorized"
    PAYMENT_STATUS_CAPTURED = "captured"
    PAYMENT_STATUS_FAILED = "failed"
    PAYMENT_STATUS_REFUNDED = "refunded"


    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, LABEL_PAYMENT_PENDING),
        (PAYMENT_STATUS_AUTHORIZED, LABEL_PAYMENT_AUTHORIZED),
        (PAYMENT_STATUS_CAPTURED, LABEL_PAYMENT_CAPTURED),
        (PAYMENT_STATUS_FAILED, LABEL_PAYMENT_FAILED),
        (PAYMENT_STATUS_REFUNDED, LABEL_PAYMENT_REFUNDED),
    ]

    """
    Shipping status choices.
    """

    SHIPPING_STATUS_PENDING = "pending"
    SHIPPING_STATUS_PREPARING = "preparing"
    SHIPPING_STATUS_SHIPPED = "shipped"
    SHIPPING_STATUS_IN_TRANSIT = "in_transit"
    SHIPPING_STATUS_DELIVERED = "delivered"


    SHIPPING_STATUS_CHOICES = [
        (SHIPPING_STATUS_PENDING, LABEL_SHIPPING_PENDING),
        (SHIPPING_STATUS_PREPARING, LABEL_SHIPPING_PREPARING),
        (SHIPPING_STATUS_SHIPPED, LABEL_SHIPPING_SHIPPED),
        (SHIPPING_STATUS_IN_TRANSIT, LABEL_SHIPPING_IN_TRANSIT),
        (SHIPPING_STATUS_DELIVERED, LABEL_SHIPPING_DELIVERED),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders"
    )

    status = models.CharField(
        max_length=32,
        choices=ORDER_STATUS_CHOICES,
        db_index=True
    )

    payment_status = models.CharField(
        max_length=32,
        choices=PAYMENT_STATUS_CHOICES,
        db_index=True
    )

    shipping_status = models.CharField(
        max_length=32,
        choices=SHIPPING_STATUS_CHOICES,
        db_index=True
    )

    idempotency_key = models.UUIDField(
        null=True,
        blank=True,
        unique=True,
        db_index=True
    )

    currency = models.CharField(
        max_length=10,
        default="USD"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["customer", "created_at"],
                name="order_customer_created_idx"
            ),
            models.Index(
                fields=["status"],
                name="order_status_idx"
            ),
        ]

    def __str__(self):
        return f"Order {self.id}"


class OrderItem(models.Model):
    """
    Represents a product purchased within an order.

    Product information is stored as a snapshot
    to preserve historical accuracy.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    product_name_snapshot = models.CharField(
        max_length=255
    )

    product_type_snapshot = models.CharField(
        max_length=50
    )

    brand_snapshot = models.CharField(
        max_length=120
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["order"],
                name="orderitem_order_idx"
            ),
        ]

    def __str__(self):
        return f"{self.product_name_snapshot} x{self.quantity}"


class OrderTotals(models.Model):
    """
    Stores calculated financial totals for an order.

    Separated to allow recalculation and audit tracking.
    """

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="totals"
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    discount_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    tax_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    shipping_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    grand_total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Totals for Order {self.order_id}"


class OrderAddress(models.Model):
    """
    Snapshot of the shipping address used in the order.
    """

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="address"
    )

    full_name = models.CharField(max_length=255)

    address_line = models.CharField(max_length=255)

    city = models.CharField(max_length=120)

    state = models.CharField(max_length=120)

    country = models.CharField(max_length=120)

    postal_code = models.CharField(max_length=20)

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.full_name} - {self.city}"


class OrderLifecycle(models.Model):
    """
    Tracks lifecycle timestamps of an order.
    """

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="lifecycle"
    )

    confirmed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    processing_at = models.DateTimeField(
        null=True,
        blank=True
    )

    shipped_at = models.DateTimeField(
        null=True,
        blank=True
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True
    )

    refunded_at = models.DateTimeField(
        null=True,
        blank=True
    )


class OrderEvent(models.Model):
    """
    Stores audit events related to an order.
    Useful for operational monitoring and debugging.
    """

    TYPE_CREATED = "order_created"
    TYPE_CONFIRMED = "order_confirmed"
    TYPE_PROCESSING_STARTED = "order_processing_started"
    TYPE_SHIPPED = "order_shipped"
    TYPE_DELIVERED = "order_delivered"
    TYPE_CANCELLED = "order_cancelled"
    TYPE_REFUNDED = "order_refunded"


    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="events"
    )

    event_type = models.CharField(
        max_length=100,
        db_index=True
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    metadata = models.JSONField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type} - {self.order_id}"


class OrderNote(models.Model):
    """
    Communication log between customer and staff
    regarding an order.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="notes"
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    message = models.TextField()

    is_internal = models.BooleanField(
        default=False,
        help_text=ORDER_NOTE_HELP_TEXT
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Note on {self.order_id}"
