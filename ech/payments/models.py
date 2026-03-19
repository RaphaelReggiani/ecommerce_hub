import uuid

from django.conf import settings
from django.db import models

from ech.orders.models import Order

from django.core.exceptions import ValidationError

from ech.payments.constants.constants import (
    LABEL_PAYMENT_STATUS_PENDING,
    LABEL_PAYMENT_STATUS_PROCESSING,
    LABEL_PAYMENT_STATUS_AUTHORIZED,
    LABEL_PAYMENT_STATUS_CAPTURED,
    LABEL_PAYMENT_STATUS_FAILED,
    LABEL_PAYMENT_STATUS_CANCELLED,
    LABEL_PAYMENT_STATUS_PARTIALLY_REFUNDED,
    LABEL_PAYMENT_STATUS_REFUNDED,
    LABEL_PAYMENT_METHOD_CREDIT_CARD,
    LABEL_PAYMENT_METHOD_DEBIT_CARD,
    LABEL_PAYMENT_METHOD_PIX,
    LABEL_PAYMENT_METHOD_BANK_SLIP,
    LABEL_PAYMENT_METHOD_WALLET,
    LABEL_TRANSACTION_TYPE_AUTHORIZATION,
    LABEL_TRANSACTION_TYPE_CAPTURE,
    LABEL_TRANSACTION_TYPE_CHARGE,
    LABEL_TRANSACTION_TYPE_REFUND,
    LABEL_TRANSACTION_TYPE_PARTIAL_REFUND,
    LABEL_TRANSACTION_TYPE_CANCELLATION,
    LABEL_TRANSACTION_TYPE_FAILURE,
    LABEL_TRANSACTION_STATUS_PENDING,
    LABEL_TRANSACTION_STATUS_SUCCESS,
    LABEL_TRANSACTION_STATUS_FAILED,
    LABEL_TRANSACTION_STATUS_CANCELLED,
    LABEL_REFUND_STATUS_PENDING,
    LABEL_REFUND_STATUS_PROCESSED,
    LABEL_REFUND_STATUS_FAILED,
    LABEL_REFUND_STATUS_CANCELLED,
)


class Payment(models.Model):
    """
    Main Payment model (Aggregate Root).

    Represents the financial record associated with an order.
    Stores the current payment state, gateway references,
    failure information, and timestamps for the payment lifecycle.
    """

    """
    Payment status choices.
    """

    PAYMENT_STATUS_PENDING = "pending"
    PAYMENT_STATUS_PROCESSING = "processing"
    PAYMENT_STATUS_AUTHORIZED = "authorized"
    PAYMENT_STATUS_CAPTURED = "captured"
    PAYMENT_STATUS_FAILED = "failed"
    PAYMENT_STATUS_CANCELLED = "cancelled"
    PAYMENT_STATUS_PARTIALLY_REFUNDED = "partially_refunded"
    PAYMENT_STATUS_REFUNDED = "refunded"

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, LABEL_PAYMENT_STATUS_PENDING),
        (PAYMENT_STATUS_PROCESSING, LABEL_PAYMENT_STATUS_PROCESSING),
        (PAYMENT_STATUS_AUTHORIZED, LABEL_PAYMENT_STATUS_AUTHORIZED),
        (PAYMENT_STATUS_CAPTURED, LABEL_PAYMENT_STATUS_CAPTURED),
        (PAYMENT_STATUS_FAILED, LABEL_PAYMENT_STATUS_FAILED),
        (PAYMENT_STATUS_CANCELLED, LABEL_PAYMENT_STATUS_CANCELLED),
        (PAYMENT_STATUS_PARTIALLY_REFUNDED, LABEL_PAYMENT_STATUS_PARTIALLY_REFUNDED),
        (PAYMENT_STATUS_REFUNDED, LABEL_PAYMENT_STATUS_REFUNDED),
    ]

    """
    Payment method choices.
    """

    PAYMENT_METHOD_CREDIT_CARD = "credit_card"
    PAYMENT_METHOD_DEBIT_CARD = "debit_card"
    PAYMENT_METHOD_PIX = "pix"
    PAYMENT_METHOD_BANK_SLIP = "bank_slip"
    PAYMENT_METHOD_WALLET = "wallet"

    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_CREDIT_CARD, LABEL_PAYMENT_METHOD_CREDIT_CARD),
        (PAYMENT_METHOD_DEBIT_CARD, LABEL_PAYMENT_METHOD_DEBIT_CARD),
        (PAYMENT_METHOD_PIX, LABEL_PAYMENT_METHOD_PIX),
        (PAYMENT_METHOD_BANK_SLIP, LABEL_PAYMENT_METHOD_BANK_SLIP),
        (PAYMENT_METHOD_WALLET, LABEL_PAYMENT_METHOD_WALLET),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payment"
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    payment_reference = models.CharField(
        max_length=64,
        unique=True,
        db_index=True
    )

    method = models.CharField(
        max_length=32,
        choices=PAYMENT_METHOD_CHOICES,
        db_index=True
    )

    status = models.CharField(
        max_length=32,
        choices=PAYMENT_STATUS_CHOICES,
        db_index=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    refunded_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    currency = models.CharField(
        max_length=10,
        default="USD"
    )

    gateway_name = models.CharField(
        max_length=50,
        blank=True
    )

    gateway_payment_id = models.CharField(
        max_length=120,
        blank=True,
        db_index=True
    )

    gateway_customer_id = models.CharField(
        max_length=120,
        blank=True
    )

    idempotency_key = models.UUIDField(
        null=True,
        blank=True,
        unique=True,
        db_index=True
    )

    failure_code = models.CharField(
        max_length=64,
        blank=True
    )

    failure_message = models.TextField(
        blank=True
    )

    metadata = models.JSONField(
        null=True,
        blank=True
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
                name="payment_customer_created_idx"
            ),
            models.Index(
                fields=["status"],
                name="payment_status_idx"
            ),
            models.Index(
                fields=["method"],
                name="payment_method_idx"
            ),
        ]

    def __str__(self):
        return f"Payment {self.payment_reference}"


class PaymentTransaction(models.Model):
    """
    Stores every financial operation attempt related to a payment.

    This model preserves the operational history of the payment,
    including successful and failed actions such as authorization,
    capture, refund, and cancellation.
    """

    """
    Transaction type choices.
    """

    TRANSACTION_TYPE_AUTHORIZATION = "authorization"
    TRANSACTION_TYPE_CAPTURE = "capture"
    TRANSACTION_TYPE_CHARGE = "charge"
    TRANSACTION_TYPE_REFUND = "refund"
    TRANSACTION_TYPE_PARTIAL_REFUND = "partial_refund"
    TRANSACTION_TYPE_CANCELLATION = "cancellation"
    TRANSACTION_TYPE_FAILURE = "failure"

    TRANSACTION_TYPE_CHOICES = [
        (TRANSACTION_TYPE_AUTHORIZATION, LABEL_TRANSACTION_TYPE_AUTHORIZATION),
        (TRANSACTION_TYPE_CAPTURE, LABEL_TRANSACTION_TYPE_CAPTURE),
        (TRANSACTION_TYPE_CHARGE, LABEL_TRANSACTION_TYPE_CHARGE),
        (TRANSACTION_TYPE_REFUND, LABEL_TRANSACTION_TYPE_REFUND),
        (TRANSACTION_TYPE_PARTIAL_REFUND, LABEL_TRANSACTION_TYPE_PARTIAL_REFUND),
        (TRANSACTION_TYPE_CANCELLATION, LABEL_TRANSACTION_TYPE_CANCELLATION),
        (TRANSACTION_TYPE_FAILURE, LABEL_TRANSACTION_TYPE_FAILURE),
    ]

    """
    Transaction status choices.
    """

    TRANSACTION_STATUS_PENDING = "pending"
    TRANSACTION_STATUS_SUCCESS = "success"
    TRANSACTION_STATUS_FAILED = "failed"
    TRANSACTION_STATUS_CANCELLED = "cancelled"

    TRANSACTION_STATUS_CHOICES = [
        (TRANSACTION_STATUS_PENDING, LABEL_TRANSACTION_STATUS_PENDING),
        (TRANSACTION_STATUS_SUCCESS, LABEL_TRANSACTION_STATUS_SUCCESS),
        (TRANSACTION_STATUS_FAILED, LABEL_TRANSACTION_STATUS_FAILED),
        (TRANSACTION_STATUS_CANCELLED, LABEL_TRANSACTION_STATUS_CANCELLED),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    transaction_type = models.CharField(
        max_length=32,
        choices=TRANSACTION_TYPE_CHOICES,
        db_index=True
    )

    status = models.CharField(
        max_length=32,
        choices=TRANSACTION_STATUS_CHOICES,
        db_index=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    currency = models.CharField(
        max_length=10,
        default="USD"
    )

    gateway_transaction_id = models.CharField(
        max_length=120,
        blank=True,
        db_index=True
    )

    gateway_response_code = models.CharField(
        max_length=64,
        blank=True
    )

    gateway_response_message = models.TextField(
        blank=True
    )

    idempotency_key = models.UUIDField(
        null=True,
        blank=True,
        unique=True,
        db_index=True
    )

    metadata = models.JSONField(
        null=True,
        blank=True
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="payment_transactions"
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["payment", "created_at"],
                name="paymenttx_payment_created_idx"
            ),
            models.Index(
                fields=["transaction_type", "status"],
                name="paymenttx_type_status_idx"
            ),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.payment.payment_reference}"


class PaymentRefund(models.Model):
    """
    Stores refund requests and outcomes for a payment.

    Supports full and partial refunds while keeping a dedicated
    refund history separate from generic payment transactions.
    """

    """
    Refund status choices.
    """

    REFUND_STATUS_PENDING = "pending"
    REFUND_STATUS_PROCESSED = "processed"
    REFUND_STATUS_FAILED = "failed"
    REFUND_STATUS_CANCELLED = "cancelled"

    REFUND_STATUS_CHOICES = [
        (REFUND_STATUS_PENDING, LABEL_REFUND_STATUS_PENDING),
        (REFUND_STATUS_PROCESSED, LABEL_REFUND_STATUS_PROCESSED),
        (REFUND_STATUS_FAILED, LABEL_REFUND_STATUS_FAILED),
        (REFUND_STATUS_CANCELLED, LABEL_REFUND_STATUS_CANCELLED),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="refunds"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    reason = models.CharField(
        max_length=255
    )

    status = models.CharField(
        max_length=32,
        choices=REFUND_STATUS_CHOICES,
        db_index=True
    )

    gateway_refund_id = models.CharField(
        max_length=120,
        blank=True,
        db_index=True
    )

    metadata = models.JSONField(
        null=True,
        blank=True
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="requested_payment_refunds"
    )

    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="processed_payment_refunds"
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True
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
                fields=["payment", "created_at"],
                name="payrf_pay_created_idx"
            ),
            models.Index(
                fields=["status"],
                name="payrf_status_idx"
            ),
        ]

    def __str__(self):
        return f"Refund {self.id} - {self.payment.payment_reference}"


class PaymentLifecycle(models.Model):
    """
    Tracks lifecycle timestamps of a payment.
    """

    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name="lifecycle"
    )

    processing_started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    authorized_at = models.DateTimeField(
        null=True,
        blank=True
    )

    captured_at = models.DateTimeField(
        null=True,
        blank=True
    )

    failed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True
    )

    partially_refunded_at = models.DateTimeField(
        null=True,
        blank=True
    )

    refunded_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Lifecycle for Payment {self.payment_id}"


class PaymentEvent(models.Model):
    """
    Stores audit events related to a payment.
    Useful for operational monitoring, traceability, and debugging.
    """

    TYPE_CREATED = "payment_created"
    TYPE_PROCESSING_STARTED = "payment_processing_started"
    TYPE_AUTHORIZED = "payment_authorized"
    TYPE_CAPTURED = "payment_captured"
    TYPE_FAILED = "payment_failed"
    TYPE_CANCELLED = "payment_cancelled"
    TYPE_REFUND_REQUESTED = "payment_refund_requested"
    TYPE_PARTIALLY_REFUNDED = "payment_partially_refunded"
    TYPE_REFUNDED = "payment_refunded"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    payment = models.ForeignKey(
        Payment,
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
        return f"{self.event_type} - {self.payment.payment_reference}"