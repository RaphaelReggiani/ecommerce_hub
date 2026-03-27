from django.contrib.auth import get_user_model

from rest_framework import serializers

from ech.orders.models import Order
from ech.shipping.models import (
    Shipment,
    ShipmentAddress,
    ShipmentLifecycle,
    ShipmentEvent,
    ShipmentTrackingUpdate,
    ShipmentNote,
)
from ech.shipping.services.shipping_creation_service import (
    ShippingCreationService,
)
from ech.shipping.services.shipping_update_service import (
    ShippingUpdateService,
)
from ech.shipping.services.shipping_status_service import (
    ShippingStatusService,
)
from ech.shipping.services.shipping_cancellation_service import (
    ShippingCancellationService,
)
from ech.shipping.services.shipping_tracking_service import (
    ShippingTrackingService,
)


User = get_user_model()


class ShipmentAddressInputSerializer(serializers.Serializer):
    """
    Input serializer for shipment address snapshot during shipment creation
    and address updates.
    """

    full_name = serializers.CharField(max_length=255)
    address_line = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=120)
    state = serializers.CharField(max_length=120)
    country = serializers.CharField(max_length=120)
    postal_code = serializers.CharField(max_length=20)
    phone = serializers.CharField(
        max_length=30,
        required=False,
        allow_blank=True,
    )
    delivery_instructions = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class CreateShipmentSerializer(serializers.Serializer):
    """
    Serializer responsible for validating shipment creation payload
    and delegating business logic to ShippingCreationService.
    """

    order_id = serializers.UUIDField()
    shipping_method = serializers.ChoiceField(
        choices=Shipment._meta.get_field("shipping_method").choices,
    )
    address_data = ShipmentAddressInputSerializer()
    shipping_cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        default=0,
    )
    currency = serializers.CharField(
        max_length=10,
        required=False,
        default="USD",
    )
    carrier_name = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=True,
    )
    tracking_code = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    external_reference = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    estimated_delivery_date = serializers.DateField(
        required=False,
        allow_null=True,
    )
    idempotency_key = serializers.UUIDField(required=False)

    def validate_order_id(self, value):
        """
        Validate that the referenced order exists.
        """
        if not Order.objects.filter(id=value).exists():
            raise serializers.ValidationError("Order not found.")
        return value

    def validate(self, attrs):
        """
        Validate cross-field constraints for shipment creation.
        """
        order = Order.objects.select_related("customer").filter(
            id=attrs["order_id"]
        ).first()

        if order is None:
            raise serializers.ValidationError(
                {"order_id": "Order not found."}
            )

        attrs["order"] = order
        attrs["customer"] = order.customer

        return attrs

    def create(self, validated_data):
        """
        Create a new shipment using the service layer.
        """
        request = self.context["request"]

        return ShippingCreationService.create_shipment(
            order=validated_data["order"],
            customer=validated_data["customer"],
            shipping_method=validated_data["shipping_method"],
            address_data=validated_data["address_data"],
            shipping_cost=validated_data.get("shipping_cost", 0),
            currency=validated_data.get("currency", "USD"),
            carrier_name=validated_data.get("carrier_name", ""),
            tracking_code=validated_data.get("tracking_code"),
            external_reference=validated_data.get("external_reference"),
            estimated_delivery_date=validated_data.get(
                "estimated_delivery_date"
            ),
            idempotency_key=validated_data.get("idempotency_key"),
            performed_by=request.user,
        )


class ShipmentAddressSerializer(serializers.ModelSerializer):
    """
    Serializer for shipment address snapshot.
    """

    class Meta:
        model = ShipmentAddress
        fields = [
            "full_name",
            "address_line",
            "city",
            "state",
            "country",
            "postal_code",
            "phone",
            "delivery_instructions",
            "created_at",
            "updated_at",
        ]


class ShipmentLifecycleSerializer(serializers.ModelSerializer):
    """
    Serializer for shipment lifecycle timestamps.
    """

    class Meta:
        model = ShipmentLifecycle
        fields = [
            "preparing_at",
            "ready_to_ship_at",
            "shipped_at",
            "in_transit_at",
            "out_for_delivery_at",
            "delivered_at",
            "failed_at",
            "returned_at",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]


class ShipmentEventSerializer(serializers.ModelSerializer):
    """
    Serializer for shipment events.
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
        model = ShipmentEvent
        fields = [
            "id",
            "event_type",
            "performed_by",
            "performed_by_name",
            "performed_by_email",
            "metadata",
            "created_at",
        ]


class ShipmentTrackingUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for shipment tracking updates.
    """

    class Meta:
        model = ShipmentTrackingUpdate
        fields = [
            "id",
            "status",
            "description",
            "location",
            "raw_payload",
            "event_at",
            "created_at",
        ]


class ShipmentNoteSerializer(serializers.ModelSerializer):
    """
    Serializer for shipment notes.
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
        model = ShipmentNote
        fields = [
            "id",
            "author",
            "author_name",
            "author_email",
            "message",
            "is_internal",
            "created_at",
        ]


class ShipmentListSerializer(serializers.ModelSerializer):
    """
    Serializer used for customer shipment list endpoints.
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
        model = Shipment
        fields = [
            "id",
            "order",
            "customer",
            "customer_name",
            "customer_email",
            "status",
            "shipping_method",
            "carrier_name",
            "tracking_code",
            "external_reference",
            "shipping_cost",
            "currency",
            "estimated_delivery_date",
            "created_at",
            "updated_at",
        ]


class ShipmentDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for customer shipment detail endpoints.
    """

    customer_name = serializers.CharField(
        source="customer.user_name",
        read_only=True,
    )
    customer_email = serializers.CharField(
        source="customer.user_email",
        read_only=True,
    )

    address = ShipmentAddressSerializer(read_only=True)
    lifecycle = ShipmentLifecycleSerializer(read_only=True)
    events = ShipmentEventSerializer(many=True, read_only=True)
    tracking_updates = ShipmentTrackingUpdateSerializer(
        many=True,
        read_only=True,
    )
    visible_notes = serializers.SerializerMethodField()

    class Meta:
        model = Shipment
        fields = [
            "id",
            "order",
            "customer",
            "customer_name",
            "customer_email",
            "status",
            "shipping_method",
            "carrier_name",
            "tracking_code",
            "external_reference",
            "shipping_cost",
            "currency",
            "estimated_delivery_date",
            "delivered_to_name",
            "is_return_to_sender",
            "address",
            "lifecycle",
            "events",
            "tracking_updates",
            "visible_notes",
            "created_at",
            "updated_at",
        ]

    def get_visible_notes(self, obj):
        """
        Return only notes that are visible to customers.
        """
        notes = obj.notes.filter(is_internal=False)
        return ShipmentNoteSerializer(notes, many=True).data


class ShipmentManagementListSerializer(serializers.ModelSerializer):
    """
    Serializer used for staff shipment management list endpoints.
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

    class Meta:
        model = Shipment
        fields = [
            "id",
            "order",
            "customer",
            "customer_name",
            "customer_email",
            "status",
            "shipping_method",
            "carrier_name",
            "tracking_code",
            "external_reference",
            "shipping_cost",
            "currency",
            "estimated_delivery_date",
            "created_at",
            "updated_at",
        ]


class ShipmentManagementDetailSerializer(serializers.ModelSerializer):
    """
    Serializer used for staff shipment detail endpoints.
    """

    customer_name = serializers.CharField(
        source="customer.user_name",
        read_only=True,
    )
    customer_email = serializers.CharField(
        source="customer.user_email",
        read_only=True,
    )

    address = ShipmentAddressSerializer(read_only=True)
    lifecycle = ShipmentLifecycleSerializer(read_only=True)
    events = ShipmentEventSerializer(many=True, read_only=True)
    tracking_updates = ShipmentTrackingUpdateSerializer(
        many=True,
        read_only=True,
    )
    notes = ShipmentNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Shipment
        fields = [
            "id",
            "order",
            "customer",
            "customer_name",
            "customer_email",
            "status",
            "shipping_method",
            "carrier_name",
            "tracking_code",
            "external_reference",
            "shipping_cost",
            "currency",
            "estimated_delivery_date",
            "delivered_to_name",
            "is_return_to_sender",
            "address",
            "lifecycle",
            "events",
            "tracking_updates",
            "notes",
            "created_at",
            "updated_at",
        ]


class ShipmentUpdateDataSerializer(serializers.Serializer):
    """
    Serializer for shipment operational fields that can be updated.
    """

    shipping_method = serializers.ChoiceField(
        choices=Shipment._meta.get_field("shipping_method").choices,
        required=False,
    )
    carrier_name = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=True,
    )
    tracking_code = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    external_reference = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    shipping_cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
    )
    currency = serializers.CharField(
        max_length=10,
        required=False,
    )
    estimated_delivery_date = serializers.DateField(
        required=False,
        allow_null=True,
    )
    delivered_to_name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )
    is_return_to_sender = serializers.BooleanField(
        required=False,
    )


class ShipmentUpdateSerializer(serializers.Serializer):
    """
    Serializer responsible for validating shipment update payload
    and delegating business logic to ShippingUpdateService.
    """

    shipment_data = ShipmentUpdateDataSerializer(required=False)
    address_data = ShipmentAddressInputSerializer(required=False)

    def validate(self, attrs):
        """
        Ensure at least one update block is provided.
        """
        if not attrs.get("shipment_data") and not attrs.get("address_data"):
            raise serializers.ValidationError(
                "At least one of 'shipment_data' or 'address_data' must be provided."
            )
        return attrs

    def create(self, validated_data):
        """
        Update shipment data through the service layer.
        """
        shipment = validated_data["shipment"]
        performed_by = validated_data.get("performed_by")

        return ShippingUpdateService.update_shipment(
            shipment=shipment,
            shipment_data=validated_data.get("shipment_data"),
            address_data=validated_data.get("address_data"),
            performed_by=performed_by,
        )


class ShipmentProcessSerializer(serializers.Serializer):
    """
    Serializer responsible for validating shipment status transitions
    and delegating business logic to ShippingStatusService.
    """

    new_status = serializers.ChoiceField(
        choices=Shipment._meta.get_field("status").choices,
    )
    metadata = serializers.JSONField(required=False)

    def create(self, validated_data):
        """
        Process a shipment status transition through the service layer.
        """
        shipment = validated_data["shipment"]
        performed_by = validated_data.get("performed_by")

        return ShippingStatusService.update_status(
            shipment=shipment,
            new_status=validated_data["new_status"],
            performed_by=performed_by,
            metadata=validated_data.get("metadata"),
        )


class ShipmentCancelSerializer(serializers.Serializer):
    """
    Serializer responsible for validating shipment cancellation payload
    and delegating business logic to ShippingCancellationService.
    """

    metadata = serializers.JSONField(required=False)

    def create(self, validated_data):
        """
        Cancel a shipment through the service layer.
        """
        shipment = validated_data["shipment"]
        performed_by = validated_data.get("performed_by")

        return ShippingCancellationService.cancel_shipment(
            shipment=shipment,
            performed_by=performed_by,
            metadata=validated_data.get("metadata"),
        )


class ShipmentTrackingSerializer(serializers.Serializer):
    """
    Serializer responsible for validating shipment tracking update payload
    and delegating business logic to ShippingTrackingService.
    """

    status = serializers.CharField(required=False, allow_blank=False)
    description = serializers.CharField()
    location = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    raw_payload = serializers.JSONField(required=False)
    event_at = serializers.DateTimeField()
    tracking_code = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    carrier_name = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    external_reference = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def create(self, validated_data):
        """
        Register a shipment tracking update through the service layer.
        """
        shipment = validated_data["shipment"]
        performed_by = validated_data.get("performed_by")

        return ShippingTrackingService.register_tracking_update(
            shipment=shipment,
            status=validated_data.get("status"),
            description=validated_data["description"],
            location=validated_data.get("location", ""),
            raw_payload=validated_data.get("raw_payload"),
            event_at=validated_data["event_at"],
            tracking_code=validated_data.get("tracking_code"),
            carrier_name=validated_data.get("carrier_name"),
            external_reference=validated_data.get("external_reference"),
            performed_by=performed_by,
        )
    