from django.contrib import admin

from ech.shipping.models import (
    Shipment,
    ShipmentAddress,
    ShipmentLifecycle,
    ShipmentEvent,
    ShipmentTrackingUpdate,
    ShipmentNote,
)


class ShipmentAddressInline(admin.StackedInline):
    model = ShipmentAddress
    extra = 0

    readonly_fields = (
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
    )

    can_delete = False


class ShipmentLifecycleInline(admin.StackedInline):
    model = ShipmentLifecycle
    extra = 0

    readonly_fields = (
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
    )

    can_delete = False


class ShipmentEventInline(admin.TabularInline):
    model = ShipmentEvent
    extra = 0

    readonly_fields = (
        "event_type",
        "performed_by",
        "metadata",
        "created_at",
    )

    can_delete = False


class ShipmentTrackingUpdateInline(admin.TabularInline):
    model = ShipmentTrackingUpdate
    extra = 0

    readonly_fields = (
        "status",
        "location",
        "description",
        "raw_payload",
        "event_at",
        "created_at",
    )

    can_delete = False


class ShipmentNoteInline(admin.TabularInline):
    model = ShipmentNote
    extra = 0

    readonly_fields = (
        "author",
        "message",
        "is_internal",
        "created_at",
    )


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "customer",
        "status",
        "shipping_method",
        "carrier_name",
        "tracking_code",
        "estimated_delivery_date",
        "created_at",
    )

    list_filter = (
        "status",
        "shipping_method",
        "carrier_name",
        "is_return_to_sender",
        "created_at",
        "estimated_delivery_date",
    )

    search_fields = (
        "id",
        "tracking_code",
        "external_reference",
        "carrier_name",
        "order__id",
        "customer__user_email",
        "customer__user_name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    inlines = [
        ShipmentAddressInline,
        ShipmentLifecycleInline,
        ShipmentEventInline,
        ShipmentTrackingUpdateInline,
        ShipmentNoteInline,
    ]


@admin.register(ShipmentEvent)
class ShipmentEventAdmin(admin.ModelAdmin):

    list_display = (
        "shipment",
        "event_type",
        "performed_by",
        "created_at",
    )

    list_filter = (
        "event_type",
        "created_at",
    )

    search_fields = (
        "shipment__id",
        "shipment__tracking_code",
        "shipment__external_reference",
    )

    readonly_fields = (
        "id",
        "shipment",
        "event_type",
        "performed_by",
        "metadata",
        "created_at",
    )

    ordering = ("-created_at",)


@admin.register(ShipmentTrackingUpdate)
class ShipmentTrackingUpdateAdmin(admin.ModelAdmin):

    list_display = (
        "shipment",
        "status",
        "location",
        "event_at",
        "created_at",
    )

    list_filter = (
        "status",
        "event_at",
        "created_at",
    )

    search_fields = (
        "shipment__id",
        "shipment__tracking_code",
        "location",
        "description",
    )

    readonly_fields = (
        "shipment",
        "status",
        "location",
        "description",
        "raw_payload",
        "event_at",
        "created_at",
    )

    ordering = ("-event_at", "-created_at")


@admin.register(ShipmentNote)
class ShipmentNoteAdmin(admin.ModelAdmin):

    list_display = (
        "shipment",
        "author",
        "is_internal",
        "created_at",
    )

    list_filter = (
        "is_internal",
        "created_at",
    )

    search_fields = (
        "shipment__id",
        "author__user_email",
        "author__user_name",
    )

    readonly_fields = (
        "shipment",
        "author",
        "message",
        "is_internal",
        "created_at",
    )

    ordering = ("-created_at",)