import django_filters

from ech.analytics.models import AnalyticsSnapshot


class AnalyticsSnapshotFilter(django_filters.FilterSet):
    """
    Customer-facing analytics filters.

    Allows filtering analytics snapshots by
    period type and period range.
    """

    period_type = django_filters.CharFilter(
        field_name="period_type",
        lookup_expr="exact",
    )

    period_start_after = django_filters.DateTimeFilter(
        field_name="period_start",
        lookup_expr="gte",
    )

    period_start_before = django_filters.DateTimeFilter(
        field_name="period_start",
        lookup_expr="lte",
    )

    period_end_after = django_filters.DateTimeFilter(
        field_name="period_end",
        lookup_expr="gte",
    )

    period_end_before = django_filters.DateTimeFilter(
        field_name="period_end",
        lookup_expr="lte",
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
        model = AnalyticsSnapshot
        fields = [
            "period_type",
        ]


class AnalyticsSnapshotManagementFilter(django_filters.FilterSet):
    """
    Management analytics filters.

    Provides extended filtering capabilities for
    analytics operations dashboards and staff tooling.
    """

    period_type = django_filters.CharFilter(
        field_name="period_type",
        lookup_expr="exact",
    )

    generated_by = django_filters.NumberFilter(
        field_name="generated_by__id",
        lookup_expr="exact",
    )

    top_product_id = django_filters.UUIDFilter(
        field_name="top_product_id",
        lookup_expr="exact",
    )

    period_start_after = django_filters.DateTimeFilter(
        field_name="period_start",
        lookup_expr="gte",
    )

    period_start_before = django_filters.DateTimeFilter(
        field_name="period_start",
        lookup_expr="lte",
    )

    period_end_after = django_filters.DateTimeFilter(
        field_name="period_end",
        lookup_expr="gte",
    )

    period_end_before = django_filters.DateTimeFilter(
        field_name="period_end",
        lookup_expr="lte",
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
        model = AnalyticsSnapshot
        fields = [
            "period_type",
            "generated_by",
            "top_product_id",
        ]