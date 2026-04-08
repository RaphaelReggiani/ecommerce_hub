import django_filters

from ech.analytics.models import AnalyticsSnapshot


class AnalyticsSnapshotFilter(django_filters.FilterSet):
    """
    Customer-facing analytics snapshot filters.
    """

    period_type = django_filters.CharFilter(
        field_name="period_type",
        lookup_expr="exact",
    )

    generated_by = django_filters.NumberFilter(
        field_name="generated_by__id",
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

    total_revenue_min = django_filters.NumberFilter(
        field_name="total_revenue",
        lookup_expr="gte",
    )

    total_revenue_max = django_filters.NumberFilter(
        field_name="total_revenue",
        lookup_expr="lte",
    )

    total_orders_min = django_filters.NumberFilter(
        field_name="total_orders",
        lookup_expr="gte",
    )

    total_orders_max = django_filters.NumberFilter(
        field_name="total_orders",
        lookup_expr="lte",
    )

    average_rating_min = django_filters.NumberFilter(
        field_name="average_rating",
        lookup_expr="gte",
    )

    average_rating_max = django_filters.NumberFilter(
        field_name="average_rating",
        lookup_expr="lte",
    )

    class Meta:
        model = AnalyticsSnapshot
        fields = [
            "period_type",
            "generated_by",
        ]


class AnalyticsSnapshotManagementFilter(django_filters.FilterSet):
    """
    Management analytics snapshot filters.
    """

    period_type = django_filters.CharFilter(
        field_name="period_type",
        lookup_expr="exact",
    )

    generated_by = django_filters.NumberFilter(
        field_name="generated_by__id",
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

    total_revenue_min = django_filters.NumberFilter(
        field_name="total_revenue",
        lookup_expr="gte",
    )

    total_revenue_max = django_filters.NumberFilter(
        field_name="total_revenue",
        lookup_expr="lte",
    )

    total_orders_min = django_filters.NumberFilter(
        field_name="total_orders",
        lookup_expr="gte",
    )

    total_orders_max = django_filters.NumberFilter(
        field_name="total_orders",
        lookup_expr="lte",
    )

    average_rating_min = django_filters.NumberFilter(
        field_name="average_rating",
        lookup_expr="gte",
    )

    average_rating_max = django_filters.NumberFilter(
        field_name="average_rating",
        lookup_expr="lte",
    )

    active_customers_min = django_filters.NumberFilter(
        field_name="active_customers",
        lookup_expr="gte",
    )

    active_customers_max = django_filters.NumberFilter(
        field_name="active_customers",
        lookup_expr="lte",
    )

    total_registered_users_min = django_filters.NumberFilter(
        field_name="total_registered_users",
        lookup_expr="gte",
    )

    total_registered_users_max = django_filters.NumberFilter(
        field_name="total_registered_users",
        lookup_expr="lte",
    )

    total_reviews_min = django_filters.NumberFilter(
        field_name="total_reviews",
        lookup_expr="gte",
    )

    total_reviews_max = django_filters.NumberFilter(
        field_name="total_reviews",
        lookup_expr="lte",
    )

    metadata = django_filters.CharFilter(
        field_name="metadata",
        lookup_expr="icontains",
    )

    class Meta:
        model = AnalyticsSnapshot
        fields = [
            "period_type",
            "generated_by",
            "metadata",
        ]