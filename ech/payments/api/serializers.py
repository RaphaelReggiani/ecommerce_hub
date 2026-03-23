from rest_framework import serializers

from ech.orders.models import Order
from ech.payments.exceptions import PaymentError
from ech.payments.models import (
    Payment,
    PaymentEvent,
    PaymentLifecycle,
    PaymentRefund,
    PaymentTransaction,
)
from ech.payments.services.payment_creation_service import PaymentCreationService
from ech.payments.services.payment_processing_service import PaymentProcessingService
from ech.payments.services.payment_refund_service import PaymentRefundService


class CreatePaymentSerializer(serializers.Serializer):
    """
    Serializer responsible for validating payment creation payload
    and delegating business logic to PaymentCreationService.
    """

    order_id = serializers.UUIDField()
    method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    payment_reference = serializers.CharField(required=False, allow_blank=False)
    idempotency_key = serializers.UUIDField(required=False)
    gateway_name = serializers.CharField(required=False, allow_blank=True, max_length=120)
    gateway_payment_id = serializers.CharField(required=False, allow_blank=True, max_length=255)
    gateway_customer_id = serializers.CharField(required=False, allow_blank=True, max_length=255)
    metadata = serializers.JSONField(required=False)

    def validate_order_id(self, value):
        """
        Validates if the related order exists.
        """
        if not Order.objects.filter(id=value).exists():
            raise serializers.ValidationError("Order not found.")

        return value

    def create(self, validated_data):
        """
        Creates a new payment using the service layer.
        """
        request = self.context["request"]
        order = Order.objects.select_related("totals", "customer").get(
            id=validated_data["order_id"]
        )

        try:
            return PaymentCreationService.create_payment(
                order=order,
                method=validated_data["method"],
                created_by=request.user,
                payment_reference=validated_data.get("payment_reference"),
                idempotency_key=validated_data.get("idempotency_key"),
                gateway_name=validated_data.get("gateway_name", ""),
                gateway_payment_id=validated_data.get("gateway_payment_id", ""),
                gateway_customer_id=validated_data.get("gateway_customer_id", ""),
                metadata=validated_data.get("metadata"),
            )
        except PaymentError as exc:
            raise serializers.ValidationError({"detail": str(exc)})


class PaymentTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for payment transactions.
    """

    performed_by_name = serializers.CharField(
        source="performed_by.user_name",
        read_only=True,
    )
    performed_by_email = serializers.CharField(
        source="performed_by.user_email",
        read_only=True,
    )

    class Meta:
        model = PaymentTransaction
        fields = [
            "id",
            "transaction_type",
            "status",
            "amount",
            "currency",
            "gateway_transaction_id",
            "gateway_response_code",
            "gateway_response_message",
            "metadata",
            "performed_by",
            "performed_by_name",
            "performed_by_email",
            "processed_at",
            "created_at",
        ]


class PaymentRefundSerializer(serializers.ModelSerializer):
    """
    Serializer for payment refunds.
    """

    requested_by_name = serializers.CharField(
        source="requested_by.user_name",
        read_only=True,
    )
    requested_by_email = serializers.CharField(
        source="requested_by.user_email",
        read_only=True,
    )
    processed_by_name = serializers.CharField(
        source="processed_by.user_name",
        read_only=True,
    )
    processed_by_email = serializers.CharField(
        source="processed_by.user_email",
        read_only=True,
    )

    class Meta:
        model = PaymentRefund
        fields = [
            "id",
            "payment",
            "amount",
            "reason",
            "status",
            "gateway_refund_id",
            "metadata",
            "requested_by",
            "requested_by_name",
            "requested_by_email",
            "processed_by",
            "processed_by_name",
            "processed_by_email",
            "processed_at",
            "created_at",
            "updated_at",
        ]


class PaymentEventSerializer(serializers.ModelSerializer):
    """
    Serializer for payment events.
    """

    performed_by_name = serializers.CharField(
        source="performed_by.user_name",
        read_only=True,
    )
    performed_by_email = serializers.CharField(
        source="performed_by.user_email",
        read_only=True,
    )

    class Meta:
        model = PaymentEvent
        fields = [
            "id",
            "event_type",
            "performed_by",
            "performed_by_name",
            "performed_by_email",
            "metadata",
            "created_at",
        ]


class PaymentLifecycleSerializer(serializers.ModelSerializer):
    """
    Serializer for payment lifecycle timestamps.
    """

    class Meta:
        model = PaymentLifecycle
        fields = [
            "processing_started_at",
            "authorized_at",
            "captured_at",
            "failed_at",
            "cancelled_at",
            "refunded_at",
            "updated_at",
        ]


class PaymentListSerializer(serializers.ModelSerializer):
    """
    Serializer used for payment list endpoints.
    Lightweight and suitable for customer dashboards.
    """

    customer_name = serializers.CharField(
        source="customer.user_name",
        read_only=True,
    )
    customer_email = serializers.CharField(
        source="customer.user_email",
        read_only=True,
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "customer",
            "customer_name",
            "customer_email",
            "payment_reference",
            "method",
            "status",
            "amount",
            "refunded_amount",
            "currency",
            "gateway_name",
            "created_at",
            "updated_at",
        ]


class PaymentDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for payment detail endpoints.
    """

    customer_name = serializers.CharField(
        source="customer.user_name",
        read_only=True,
    )
    customer_email = serializers.CharField(
        source="customer.user_email",
        read_only=True,
    )

    transactions = PaymentTransactionSerializer(many=True, read_only=True)
    refunds = PaymentRefundSerializer(many=True, read_only=True)
    lifecycle = PaymentLifecycleSerializer(read_only=True)
    events = PaymentEventSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "customer",
            "customer_name",
            "customer_email",
            "payment_reference",
            "method",
            "status",
            "amount",
            "refunded_amount",
            "currency",
            "gateway_name",
            "gateway_payment_id",
            "gateway_customer_id",
            "failure_code",
            "failure_message",
            "metadata",
            "transactions",
            "refunds",
            "lifecycle",
            "events",
            "created_at",
            "updated_at",
        ]


class PaymentManagementDetailSerializer(serializers.ModelSerializer):
    """
    Serializer used for staff management payment detail endpoints.
    Optimized for operational dashboards.
    """

    customer_name = serializers.CharField(
        source="customer.user_name",
        read_only=True,
    )
    customer_email = serializers.CharField(
        source="customer.user_email",
        read_only=True,
    )

    transactions = PaymentTransactionSerializer(many=True, read_only=True)
    refunds = PaymentRefundSerializer(many=True, read_only=True)
    lifecycle = PaymentLifecycleSerializer(read_only=True)
    events = PaymentEventSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "customer",
            "customer_name",
            "customer_email",
            "payment_reference",
            "method",
            "status",
            "amount",
            "refunded_amount",
            "currency",
            "gateway_name",
            "gateway_payment_id",
            "gateway_customer_id",
            "failure_code",
            "failure_message",
            "idempotency_key",
            "metadata",
            "transactions",
            "refunds",
            "lifecycle",
            "events",
            "created_at",
            "updated_at",
        ]


class PaymentStartProcessingSerializer(serializers.Serializer):
    """
    Serializer responsible for starting payment processing.
    """

    metadata = serializers.JSONField(required=False)

    def save(self, **kwargs):
        payment = self.context["payment"]
        request = self.context["request"]

        try:
            return PaymentProcessingService.start_processing(
                payment=payment,
                performed_by=request.user,
                metadata=self.validated_data.get("metadata"),
            )
        except PaymentError as exc:
            raise serializers.ValidationError({"detail": str(exc)})


class PaymentAuthorizeSerializer(serializers.Serializer):
    """
    Serializer responsible for authorizing a payment.
    """

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
    )
    gateway_transaction_id = serializers.CharField(required=False, allow_blank=True, max_length=255)
    gateway_response_code = serializers.CharField(required=False, allow_blank=True, max_length=120)
    gateway_response_message = serializers.CharField(required=False, allow_blank=True, max_length=255)
    metadata = serializers.JSONField(required=False)

    def save(self, **kwargs):
        payment = self.context["payment"]
        request = self.context["request"]

        try:
            return PaymentProcessingService.authorize_payment(
                payment=payment,
                performed_by=request.user,
                amount=self.validated_data.get("amount"),
                gateway_transaction_id=self.validated_data.get("gateway_transaction_id", ""),
                gateway_response_code=self.validated_data.get("gateway_response_code", ""),
                gateway_response_message=self.validated_data.get("gateway_response_message", ""),
                metadata=self.validated_data.get("metadata"),
            )
        except PaymentError as exc:
            raise serializers.ValidationError({"detail": str(exc)})


class PaymentCaptureSerializer(serializers.Serializer):
    """
    Serializer responsible for capturing a payment.
    """

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
    )
    gateway_transaction_id = serializers.CharField(required=False, allow_blank=True, max_length=255)
    gateway_response_code = serializers.CharField(required=False, allow_blank=True, max_length=120)
    gateway_response_message = serializers.CharField(required=False, allow_blank=True, max_length=255)
    metadata = serializers.JSONField(required=False)

    def save(self, **kwargs):
        payment = self.context["payment"]
        request = self.context["request"]

        try:
            return PaymentProcessingService.capture_payment(
                payment=payment,
                performed_by=request.user,
                amount=self.validated_data.get("amount"),
                gateway_transaction_id=self.validated_data.get("gateway_transaction_id", ""),
                gateway_response_code=self.validated_data.get("gateway_response_code", ""),
                gateway_response_message=self.validated_data.get("gateway_response_message", ""),
                metadata=self.validated_data.get("metadata"),
            )
        except PaymentError as exc:
            raise serializers.ValidationError({"detail": str(exc)})


class PaymentChargeSerializer(serializers.Serializer):
    """
    Serializer responsible for charging a payment directly.
    """

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
    )
    gateway_transaction_id = serializers.CharField(required=False, allow_blank=True, max_length=255)
    gateway_response_code = serializers.CharField(required=False, allow_blank=True, max_length=120)
    gateway_response_message = serializers.CharField(required=False, allow_blank=True, max_length=255)
    metadata = serializers.JSONField(required=False)

    def save(self, **kwargs):
        payment = self.context["payment"]
        request = self.context["request"]

        try:
            return PaymentProcessingService.charge_payment(
                payment=payment,
                performed_by=request.user,
                amount=self.validated_data.get("amount"),
                gateway_transaction_id=self.validated_data.get("gateway_transaction_id", ""),
                gateway_response_code=self.validated_data.get("gateway_response_code", ""),
                gateway_response_message=self.validated_data.get("gateway_response_message", ""),
                metadata=self.validated_data.get("metadata"),
            )
        except PaymentError as exc:
            raise serializers.ValidationError({"detail": str(exc)})


class PaymentFailSerializer(serializers.Serializer):
    """
    Serializer responsible for marking a payment as failed.
    """

    failure_code = serializers.CharField(required=False, allow_blank=True, max_length=120)
    failure_message = serializers.CharField(required=False, allow_blank=True, max_length=255)
    gateway_transaction_id = serializers.CharField(required=False, allow_blank=True, max_length=255)
    gateway_response_code = serializers.CharField(required=False, allow_blank=True, max_length=120)
    gateway_response_message = serializers.CharField(required=False, allow_blank=True, max_length=255)
    metadata = serializers.JSONField(required=False)

    def save(self, **kwargs):
        payment = self.context["payment"]
        request = self.context["request"]

        try:
            return PaymentProcessingService.fail_payment(
                payment=payment,
                performed_by=request.user,
                failure_code=self.validated_data.get("failure_code", ""),
                failure_message=self.validated_data.get("failure_message", ""),
                gateway_transaction_id=self.validated_data.get("gateway_transaction_id", ""),
                gateway_response_code=self.validated_data.get("gateway_response_code", ""),
                gateway_response_message=self.validated_data.get("gateway_response_message", ""),
                metadata=self.validated_data.get("metadata"),
            )
        except PaymentError as exc:
            raise serializers.ValidationError({"detail": str(exc)})


class PaymentCancelSerializer(serializers.Serializer):
    """
    Serializer responsible for cancelling a payment.
    """

    gateway_transaction_id = serializers.CharField(required=False, allow_blank=True, max_length=255)
    gateway_response_code = serializers.CharField(required=False, allow_blank=True, max_length=120)
    gateway_response_message = serializers.CharField(required=False, allow_blank=True, max_length=255)
    metadata = serializers.JSONField(required=False)

    def save(self, **kwargs):
        payment = self.context["payment"]
        request = self.context["request"]

        try:
            return PaymentProcessingService.cancel_payment(
                payment=payment,
                performed_by=request.user,
                gateway_transaction_id=self.validated_data.get("gateway_transaction_id", ""),
                gateway_response_code=self.validated_data.get("gateway_response_code", ""),
                gateway_response_message=self.validated_data.get("gateway_response_message", ""),
                metadata=self.validated_data.get("metadata"),
            )
        except PaymentError as exc:
            raise serializers.ValidationError({"detail": str(exc)})


class PaymentRefundRequestSerializer(serializers.Serializer):
    """
    Serializer responsible for creating a refund request.
    """

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    reason = serializers.CharField(max_length=255)
    gateway_refund_id = serializers.CharField(required=False, allow_blank=True, max_length=255)
    metadata = serializers.JSONField(required=False)

    def save(self, **kwargs):
        payment = self.context["payment"]
        request = self.context["request"]

        try:
            return PaymentRefundService.request_refund(
                payment=payment,
                amount=self.validated_data["amount"],
                reason=self.validated_data["reason"],
                performed_by=request.user,
                gateway_refund_id=self.validated_data.get("gateway_refund_id", ""),
                metadata=self.validated_data.get("metadata"),
            )
        except PaymentError as exc:
            raise serializers.ValidationError({"detail": str(exc)})


class PaymentRefundProcessSerializer(serializers.Serializer):
    """
    Serializer responsible for processing a pending refund.
    """

    gateway_transaction_id = serializers.CharField(required=False, allow_blank=True, max_length=255)
    metadata = serializers.JSONField(required=False)

    def save(self, **kwargs):
        refund = self.context["refund"]
        request = self.context["request"]

        try:
            return PaymentRefundService.process_refund(
                refund=refund,
                performed_by=request.user,
                gateway_transaction_id=self.validated_data.get("gateway_transaction_id", ""),
                metadata=self.validated_data.get("metadata"),
            )
        except PaymentError as exc:
            raise serializers.ValidationError({"detail": str(exc)})


class PaymentRefundFailSerializer(serializers.Serializer):
    """
    Serializer responsible for marking a pending refund as failed.
    """

    metadata = serializers.JSONField(required=False)

    def save(self, **kwargs):
        refund = self.context["refund"]
        request = self.context["request"]

        try:
            return PaymentRefundService.fail_refund(
                refund=refund,
                performed_by=request.user,
                metadata=self.validated_data.get("metadata"),
            )
        except PaymentError as exc:
            raise serializers.ValidationError({"detail": str(exc)})


class PaymentRefundCancelSerializer(serializers.Serializer):
    """
    Serializer responsible for cancelling a pending refund.
    """

    metadata = serializers.JSONField(required=False)

    def save(self, **kwargs):
        refund = self.context["refund"]
        request = self.context["request"]

        try:
            return PaymentRefundService.cancel_refund(
                refund=refund,
                performed_by=request.user,
                metadata=self.validated_data.get("metadata"),
            )
        except PaymentError as exc:
            raise serializers.ValidationError({"detail": str(exc)})