from django.contrib import admin

from ech.notifications.models import (
    Notification,
    NotificationLifecycle,
    NotificationDelivery,
    NotificationEvent,
)


class NotificationLifecycleInline(admin.StackedInline):
    model = NotificationLifecycle
    extra = 0

    readonly_fields = (
        "dispatched_at",
        "read_at",
        "archived_at",
        "cancelled_at",
        "failed_at",
        "created_at",
        "updated_at",
    )

    can_delete = False


class NotificationDeliveryInline(admin.TabularInline):
    model = NotificationDelivery
    extra = 0

    readonly_fields = (
        "id",
        "channel",
        "status",
        "provider_name",
        "recipient_address",
        "external_message_id",
        "failure_code",
        "failure_message",
        "metadata",
        "performed_by",
        "processed_at",
        "created_at",
    )

    can_delete = False


class NotificationEventInline(admin.TabularInline):
    model = NotificationEvent
    extra = 0

    readonly_fields = (
        "id",
        "event_type",
        "performed_by",
        "metadata",
        "created_at",
    )

    can_delete = False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "recipient",
        "notification_type",
        "status",
        "channel",
        "priority",
        "source_module",
        "scheduled_for",
        "created_at",
    )

    list_filter = (
        "status",
        "channel",
        "priority",
        "source_module",
        "created_at",
        "scheduled_for",
    )

    search_fields = (
        "id",
        "title",
        "message",
        "notification_type",
        "source_module",
        "source_event",
        "source_object_id",
        "recipient__user_email",
        "recipient__user_name",
        "created_by__user_email",
        "created_by__user_name",
    )

    readonly_fields = (
        "id",
        "failure_code",
        "failure_message",
        "metadata",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    inlines = [
        NotificationLifecycleInline,
        NotificationDeliveryInline,
        NotificationEventInline,
    ]


@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "notification",
        "channel",
        "status",
        "provider_name",
        "recipient_address",
        "processed_at",
        "created_at",
    )

    list_filter = (
        "channel",
        "status",
        "provider_name",
        "processed_at",
        "created_at",
    )

    search_fields = (
        "id",
        "notification__id",
        "notification__notification_type",
        "notification__recipient__user_email",
        "notification__recipient__user_name",
        "recipient_address",
        "external_message_id",
        "failure_code",
    )

    readonly_fields = (
        "id",
        "notification",
        "channel",
        "status",
        "provider_name",
        "recipient_address",
        "external_message_id",
        "failure_code",
        "failure_message",
        "metadata",
        "performed_by",
        "processed_at",
        "created_at",
    )

    ordering = ("-created_at",)


@admin.register(NotificationEvent)
class NotificationEventAdmin(admin.ModelAdmin):

    list_display = (
        "notification",
        "event_type",
        "performed_by",
        "created_at",
    )

    list_filter = (
        "event_type",
        "created_at",
    )

    search_fields = (
        "notification__id",
        "notification__notification_type",
        "notification__recipient__user_email",
        "notification__recipient__user_name",
    )

    readonly_fields = (
        "id",
        "notification",
        "event_type",
        "performed_by",
        "metadata",
        "created_at",
    )

    ordering = ("-created_at",)