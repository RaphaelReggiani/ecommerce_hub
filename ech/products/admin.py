from django.contrib import admin
from ech.products.models import Product, ProductImage, ProductInventory


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "product_type", "price", "is_active", "created_at")
    list_filter = ("product_type", "is_active")
    search_fields = ("name", "brand")


admin.site.register(ProductImage)
admin.site.register(ProductInventory)