from django.contrib import admin

from ech.reviews.models import (
    Review, 
    ReviewLifecycle, 
    ReviewEvent,
)


class ReviewLifecycleInline(admin.StackedInline):
    model = ReviewLifecycle
    extra = 0
    can_delete = False
    readonly_fields = (
        "approved_at",
        "rejected_at",
        "hidden_at",
        "cancelled_at",
        "created_at",
        "updated_at",
    )


class ReviewEventInline(admin.TabularInline):
    model = ReviewEvent
    extra = 0
    can_delete = False
    readonly_fields = (
        "event_type",
        "performed_by",
        "metadata",
        "created_at",
    )
    ordering = ("-created_at",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "customer",
        "rating",
        "status",
        "is_verified_purchase",
        "moderated_by",
        "created_at",
    )
    list_filter = (
        "status",
        "rating",
        "is_verified_purchase",
        "created_at",
    )
    search_fields = (
        "id",
        "title",
        "comment",
        "product__name",
        "customer__email",
        "customer__user_name",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "moderated_at",
    )
    autocomplete_fields = (
        "customer",
        "product",
        "moderated_by",
    )
    inlines = [ReviewLifecycleInline, ReviewEventInline]


@admin.register(ReviewLifecycle)
class ReviewLifecycleAdmin(admin.ModelAdmin):
    list_display = (
        "review",
        "approved_at",
        "rejected_at",
        "hidden_at",
        "cancelled_at",
        "created_at",
        "updated_at",
    )
    search_fields = ("review__id",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("review",)


@admin.register(ReviewEvent)
class ReviewEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "review",
        "event_type",
        "performed_by",
        "created_at",
    )
    list_filter = (
        "event_type",
        "created_at",
    )
    search_fields = (
        "id",
        "review__id",
        "performed_by__email",
        "performed_by__user_name",
    )
    readonly_fields = (
        "id",
        "created_at",
    )
    autocomplete_fields = (
        "review",
        "performed_by",
    )