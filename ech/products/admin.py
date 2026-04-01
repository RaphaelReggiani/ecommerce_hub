from django.contrib import admin

from ech.products.models import (
    Product,
    ProductInventory,
    ProductImage,
    ProductEventLog,
)


class ProductInventoryInline(admin.StackedInline):
    model = ProductInventory
    extra = 0
    max_num = 1
    can_delete = False
    fields = ("quantity", "updated_at")
    readonly_fields = ("updated_at",)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ("image", "order", "created_at")
    readonly_fields = ("created_at",)
    ordering = ("order",)


class ProductEventLogInline(admin.TabularInline):
    model = ProductEventLog
    extra = 0
    fields = ("event_type", "performed_by", "created_at")
    readonly_fields = ("event_type", "performed_by", "created_at")
    ordering = ("-created_at",)
    can_delete = False
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "brand",
        "product_type",
        "price",
        "discount_price",
        "has_discount",
        "inventory_quantity",
        "is_active",
        "sold_by",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "product_type",
        "is_active",
        "brand",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "brand",
        "description",
        "technical_information",
        "sold_by__email",
        "sold_by__user_name",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "has_discount",
        "main_image_preview",
    )
    ordering = ("-created_at",)
    list_select_related = ("sold_by",)
    inlines = (
        ProductInventoryInline,
        ProductImageInline,
        ProductEventLogInline,
    )

    fieldsets = (
        (
            "Product Information",
            {
                "fields": (
                    "id",
                    "name",
                    "product_type",
                    "brand",
                    "sold_by",
                    "is_active",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "description",
                    "technical_information",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "price",
                    "discount_price",
                    "has_discount",
                )
            },
        ),
        (
            "Media",
            {
                "fields": (
                    "main_image_preview",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(description="Inventory")
    def inventory_quantity(self, obj):
        if hasattr(obj, "inventory_record"):
            return obj.inventory_record.quantity
        return 0

    @admin.display(description="Main image")
    def main_image_preview(self, obj):
        return obj.main_image or "-"


@admin.register(ProductInventory)
class ProductInventoryAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "quantity",
        "updated_at",
    )
    search_fields = (
        "product__name",
        "product__brand",
        "product__id",
    )
    readonly_fields = ("updated_at",)
    list_select_related = ("product",)
    ordering = ("product__name",)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "order",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "product__name",
        "product__brand",
        "product__id",
    )
    readonly_fields = ("created_at",)
    list_select_related = ("product",)
    ordering = ("product", "order")


@admin.register(ProductEventLog)
class ProductEventLogAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "event_type",
        "performed_by",
        "created_at",
    )
    list_filter = (
        "event_type",
        "created_at",
    )
    search_fields = (
        "product__name",
        "product__brand",
        "product__id",
        "performed_by__email",
        "performed_by__user_name",
    )
    readonly_fields = (
        "id",
        "product",
        "event_type",
        "performed_by",
        "metadata",
        "created_at",
    )
    list_select_related = (
        "product",
        "performed_by",
    )
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False