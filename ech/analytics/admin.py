from django.contrib import admin

from ech.analytics.models import (
    AnalyticsSnapshot,
    AnalyticsSnapshotLifecycle,
    AnalyticsEvent,
)


class AnalyticsSnapshotLifecycleInline(admin.StackedInline):
    model = AnalyticsSnapshotLifecycle
    extra = 0

    readonly_fields = (
        "generation_started_at",
        "generation_completed_at",
        "refreshed_at",
        "failed_at",
        "created_at",
        "updated_at",
    )

    can_delete = False


class AnalyticsEventInline(admin.TabularInline):
    model = AnalyticsEvent
    extra = 0

    readonly_fields = (
        "event_type",
        "performed_by",
        "metadata",
        "created_at",
    )

    can_delete = False


@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "period_type",
        "period_start",
        "period_end",
        "total_orders",
        "total_revenue",
        "net_revenue",
        "active_customers",
        "generated_by",
        "created_at",
    )

    list_filter = (
        "period_type",
        "created_at",
        "period_start",
        "period_end",
    )

    search_fields = (
        "id",
        "period_type",
        "generated_by__user_email",
        "generated_by__user_name",
        "top_product_id",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    inlines = [
        AnalyticsSnapshotLifecycleInline,
        AnalyticsEventInline,
    ]


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):

    list_display = (
        "snapshot",
        "event_type",
        "performed_by",
        "created_at",
    )

    list_filter = (
        "event_type",
        "created_at",
    )

    search_fields = (
        "snapshot__id",
        "performed_by__user_email",
        "performed_by__user_name",
    )

    readonly_fields = (
        "id",
        "snapshot",
        "event_type",
        "performed_by",
        "metadata",
        "created_at",
    )

    ordering = ("-created_at",)