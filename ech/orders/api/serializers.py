from rest_framework import serializers

from ech.orders.models import (
    Order,
    OrderItem,
    OrderTotals,
    OrderAddress,
    OrderEvent,
    OrderNote,
    OrderLifecycle,
)
from ech.products.selectors import get_active_product_by_id
from ech.orders.services.create_order_service import (
    CreateOrderService,
)

from ech.orders.constants.messages import (
    MSG_VALIDATION_ERROR_PRODUCT_NOT_AVAILABLE,
    MSG_VALIDATION_ERROR_MINIMUM_ITEM_PROVIDE,
)


class OrderItemInputSerializer(serializers.Serializer):
    """
    Input serializer for order items during order creation.
    """

    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        """
        Validates if the product exists and is active.
        """
        product = get_active_product_by_id(value)

        if not product:
            raise serializers.ValidationError(MSG_VALIDATION_ERROR_PRODUCT_NOT_AVAILABLE)

        return value


class OrderAddressInputSerializer(serializers.Serializer):
    """
    Input serializer for order address during order creation.
    """

    full_name = serializers.CharField(max_length=255)
    address_line = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=120)
    state = serializers.CharField(max_length=120)
    country = serializers.CharField(max_length=120)
    postal_code = serializers.CharField(max_length=20)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True)


class CreateOrderSerializer(serializers.Serializer):
    """
    Serializer responsible for validating order creation payload
    and delegating business logic to CreateOrderService.
    """

    items = OrderItemInputSerializer(many=True)
    address = OrderAddressInputSerializer()
    idempotency_key = serializers.UUIDField(required=False)

    def validate_items(self, value):
        """
        Validates that at least one item was provided.
        """
        if not value:
            raise serializers.ValidationError(MSG_VALIDATION_ERROR_MINIMUM_ITEM_PROVIDE)

        return value

    def create(self, validated_data):
        """
        Creates a new order using the service layer.
        """
        request = self.context["request"]

        service = CreateOrderService(
            customer=request.user,
            items=validated_data["items"],
            address=validated_data["address"],
            idempotency_key=validated_data.get("idempotency_key"),
        )

        return service.execute()


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for order items.
    """

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name_snapshot",
            "product_type_snapshot",
            "brand_snapshot",
            "quantity",
            "unit_price",
            "discount_price",
            "total_price",
            "created_at",
        ]


class OrderTotalsSerializer(serializers.ModelSerializer):
    """
    Serializer for order totals.
    """

    class Meta:
        model = OrderTotals
        fields = [
            "subtotal",
            "discount_total",
            "tax_total",
            "shipping_total",
            "grand_total",
            "updated_at",
        ]


class OrderAddressSerializer(serializers.ModelSerializer):
    """
    Serializer for order address snapshot.
    """

    class Meta:
        model = OrderAddress
        fields = [
            "full_name",
            "address_line",
            "city",
            "state",
            "country",
            "postal_code",
            "phone",
            "created_at",
        ]


class OrderEventSerializer(serializers.ModelSerializer):
    """
    Serializer for order events.
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
        model = OrderEvent
        fields = [
            "id",
            "event_type",
            "performed_by",
            "performed_by_name",
            "performed_by_email",
            "metadata",
            "created_at",
        ]


class OrderNoteSerializer(serializers.ModelSerializer):
    """
    Serializer for order notes / chat messages.
    """

    author_name = serializers.CharField(
        source="author.user_name",
        read_only=True,
    )
    author_email = serializers.CharField(
        source="author.user_email",
        read_only=True,
    )

    class Meta:
        model = OrderNote
        fields = [
            "id",
            "author",
            "author_name",
            "author_email",
            "message",
            "is_internal",
            "created_at",
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """
    Serializer used for order list endpoints.
    Lightweight and suitable for dashboards.
    """

    customer_name = serializers.CharField(
        source="customer.user_name",
        read_only=True,
    )
    customer_email = serializers.CharField(
        source="customer.user_email",
        read_only=True,
    )
    totals = OrderTotalsSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "customer_name",
            "customer_email",
            "status",
            "payment_status",
            "shipping_status",
            "currency",
            "totals",
            "created_at",
            "updated_at",
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for order detail endpoints.
    """

    customer_name = serializers.CharField(
        source="customer.user_name",
        read_only=True,
    )
    customer_email = serializers.CharField(
        source="customer.user_email",
        read_only=True,
    )

    items = OrderItemSerializer(many=True, read_only=True)
    totals = OrderTotalsSerializer(read_only=True)
    address = OrderAddressSerializer(read_only=True)
    events = OrderEventSerializer(many=True, read_only=True)
    notes = OrderNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "customer_name",
            "customer_email",
            "status",
            "payment_status",
            "shipping_status",
            "currency",
            "items",
            "totals",
            "address",
            "events",
            "notes",
            "created_at",
            "updated_at",
        ]

class OrderLifecycleSerializer(serializers.Serializer):
    """
    Serializer for order lifecycle timestamps.
    """

    confirmed_at = serializers.DateTimeField(read_only=True)
    processing_at = serializers.DateTimeField(read_only=True)
    shipped_at = serializers.DateTimeField(read_only=True)
    delivered_at = serializers.DateTimeField(read_only=True)
    cancelled_at = serializers.DateTimeField(read_only=True)
    refunded_at = serializers.DateTimeField(read_only=True)


class OrderManagementListSerializer(serializers.ModelSerializer):
    """
    Serializer used for staff management order list endpoints.
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
    totals = OrderTotalsSerializer(read_only=True)

    class Meta:
        model = OrderLifecycle
        fields = [
            "confirmed_at",
            "processing_at",
            "shipped_at",
            "delivered_at",
            "cancelled_at",
            "refunded_at",
            "created_at",
            "updated_at",
        ]


class OrderManagementDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for staff management order detail endpoints.
    Includes operational and audit information.
    """

    customer_name = serializers.CharField(
        source="customer.user_name",
        read_only=True,
    )
    customer_email = serializers.CharField(
        source="customer.user_email",
        read_only=True,
    )

    items = OrderItemSerializer(many=True, read_only=True)
    totals = OrderTotalsSerializer(read_only=True)
    address = OrderAddressSerializer(read_only=True)
    lifecycle = OrderLifecycleSerializer(read_only=True)
    events = OrderEventSerializer(many=True, read_only=True)
    notes = OrderNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "customer_name",
            "customer_email",
            "status",
            "payment_status",
            "shipping_status",
            "currency",
            "items",
            "totals",
            "address",
            "lifecycle",
            "events",
            "notes",
            "created_at",
            "updated_at",
        ]
