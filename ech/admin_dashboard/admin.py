from django.contrib import admin

from ech.admin_dashboard.models import (
    AdminDashboardEvent,
    AdminDashboardLog,
)


@admin.register(AdminDashboardEvent)
class AdminDashboardEventAdmin(admin.ModelAdmin):
    """
    Admin interface for admin dashboard domain events.
    """

    list_display = (
        "event_type",
        "performed_by",
        "created_at",
    )

    list_filter = (
        "event_type",
        "created_at",
    )

    search_fields = (
        "performed_by__user_email",
        "performed_by__user_name",
        "event_type",
    )

    readonly_fields = (
        "id",
        "event_type",
        "performed_by",
        "metadata",
        "created_at",
    )

    ordering = ("-created_at",)


@admin.register(AdminDashboardLog)
class AdminDashboardLogAdmin(admin.ModelAdmin):
    """
    Admin interface for administrative operation logs.
    """

    list_display = (
        "action_type",
        "target_module",
        "performed_by",
        "created_at",
    )

    list_filter = (
        "action_type",
        "target_module",
        "created_at",
    )

    search_fields = (
        "performed_by__user_email",
        "performed_by__user_name",
        "target_module",
    )

    readonly_fields = (
        "id",
        "action_type",
        "target_module",
        "performed_by",
        "metadata",
        "created_at",
    )

    ordering = ("-created_at",)