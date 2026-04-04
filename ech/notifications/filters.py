import django_filters

from ech.notifications.models import Notification


class NotificationFilter(django_filters.FilterSet):
    """
    Recipient-facing notification filters.
    """

    status = django_filters.CharFilter(
        field_name="status",
        lookup_expr="exact",
    )

    channel = django_filters.CharFilter(
        field_name="channel",
        lookup_expr="exact",
    )

    priority = django_filters.CharFilter(
        field_name="priority",
        lookup_expr="exact",
    )

    notification_type = django_filters.CharFilter(
        field_name="notification_type",
        lookup_expr="icontains",
    )

    source_module = django_filters.CharFilter(
        field_name="source_module",
        lookup_expr="icontains",
    )

    created_after = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )

    created_before = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )

    scheduled_after = django_filters.DateTimeFilter(
        field_name="scheduled_for",
        lookup_expr="gte",
    )

    scheduled_before = django_filters.DateTimeFilter(
        field_name="scheduled_for",
        lookup_expr="lte",
    )

    class Meta:
        model = Notification
        fields = [
            "status",
            "channel",
            "priority",
            "notification_type",
            "source_module",
        ]


class NotificationManagementFilter(django_filters.FilterSet):
    """
    Management and operations notification filters.

    Provides more extensive filtering for staff dashboards
    and operational tooling.
    """

    status = django_filters.CharFilter(
        field_name="status",
        lookup_expr="exact",
    )

    channel = django_filters.CharFilter(
        field_name="channel",
        lookup_expr="exact",
    )

    priority = django_filters.CharFilter(
        field_name="priority",
        lookup_expr="exact",
    )

    notification_type = django_filters.CharFilter(
        field_name="notification_type",
        lookup_expr="icontains",
    )

    source_module = django_filters.CharFilter(
        field_name="source_module",
        lookup_expr="icontains",
    )

    source_event = django_filters.CharFilter(
        field_name="source_event",
        lookup_expr="icontains",
    )

    source_object_id = django_filters.CharFilter(
        field_name="source_object_id",
        lookup_expr="icontains",
    )

    recipient_id = django_filters.NumberFilter(
        field_name="recipient__id",
        lookup_expr="exact",
    )

    created_by_id = django_filters.NumberFilter(
        field_name="created_by__id",
        lookup_expr="exact",
    )

    created_after = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )

    created_before = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )

    scheduled_after = django_filters.DateTimeFilter(
        field_name="scheduled_for",
        lookup_expr="gte",
    )

    scheduled_before = django_filters.DateTimeFilter(
        field_name="scheduled_for",
        lookup_expr="lte",
    )

    class Meta:
        model = Notification
        fields = [
            "status",
            "channel",
            "priority",
            "notification_type",
            "source_module",
            "source_event",
            "source_object_id",
            "recipient_id",
            "created_by_id",
        ]