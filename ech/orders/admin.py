from django.contrib import admin

from ech.orders.models import (
    Order,
    OrderItem,
    OrderTotals,
    OrderAddress,
    OrderLifecycle,
    OrderEvent,
    OrderNote,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    readonly_fields = (
        "product",
        "product_name_snapshot",
        "brand_snapshot",
        "product_type_snapshot",
        "quantity",
        "unit_price",
        "discount_price",
        "total_price",
        "created_at",
    )

    can_delete = False


class OrderEventInline(admin.TabularInline):
    model = OrderEvent
    extra = 0

    readonly_fields = (
        "event_type",
        "performed_by",
        "metadata",
        "created_at",
    )

    can_delete = False


class OrderNoteInline(admin.TabularInline):
    model = OrderNote
    extra = 0

    readonly_fields = (
        "author",
        "message",
        "is_internal",
        "created_at",
    )


class OrderTotalsInline(admin.StackedInline):
    model = OrderTotals
    extra = 0

    readonly_fields = (
        "subtotal",
        "discount_total",
        "tax_total",
        "shipping_total",
        "grand_total",
        "updated_at",
    )

    can_delete = False


class OrderAddressInline(admin.StackedInline):
    model = OrderAddress
    extra = 0

    readonly_fields = (
        "full_name",
        "address_line",
        "city",
        "state",
        "country",
        "postal_code",
        "phone",
        "created_at",
    )

    can_delete = False


class OrderLifecycleInline(admin.StackedInline):
    model = OrderLifecycle
    extra = 0

    readonly_fields = (
        "confirmed_at",
        "processing_at",
        "shipped_at",
        "delivered_at",
        "cancelled_at",
        "refunded_at",
    )

    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer",
        "status",
        "payment_status",
        "shipping_status",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_status",
        "shipping_status",
        "created_at",
    )

    search_fields = (
        "id",
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
        OrderItemInline,
        OrderTotalsInline,
        OrderAddressInline,
        OrderLifecycleInline,
        OrderEventInline,
        OrderNoteInline,
    ]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "product_name_snapshot",
        "quantity",
        "unit_price",
        "total_price",
    )

    search_fields = (
        "product_name_snapshot",
        "order__id",
    )


@admin.register(OrderEvent)
class OrderEventAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "event_type",
        "performed_by",
        "created_at",
    )

    list_filter = (
        "event_type",
        "created_at",
    )

    search_fields = (
        "order__id",
    )


@admin.register(OrderNote)
class OrderNoteAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "author",
        "is_internal",
        "created_at",
    )

    list_filter = (
        "is_internal",
    )

    search_fields = (
        "order__id",
        "author__user_email",
    )
