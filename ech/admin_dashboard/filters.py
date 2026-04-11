import django_filters

from ech.admin_dashboard.models import (
    AdminDashboardEvent,
    AdminDashboardLog,
)


class AdminDashboardEventFilter(django_filters.FilterSet):
    """
    Filters for dashboard activity events.
    """

    event_type = django_filters.CharFilter(
        field_name="event_type",
        lookup_expr="exact",
    )

    performed_by = django_filters.NumberFilter(
        field_name="performed_by__id",
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

    class Meta:
        model = AdminDashboardEvent
        fields = [
            "event_type",
            "performed_by",
        ]


class AdminDashboardLogFilter(django_filters.FilterSet):
    """
    Filters for administrative dashboard logs.
    """

    action_type = django_filters.CharFilter(
        field_name="action_type",
        lookup_expr="exact",
    )

    performed_by = django_filters.NumberFilter(
        field_name="performed_by__id",
        lookup_expr="exact",
    )

    target_module = django_filters.CharFilter(
        field_name="target_module",
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

    metadata = django_filters.CharFilter(
        field_name="metadata",
        lookup_expr="icontains",
    )

    class Meta:
        model = AdminDashboardLog
        fields = [
            "action_type",
            "performed_by",
            "target_module",
            "metadata",
        ]