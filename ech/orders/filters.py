import django_filters

from ech.orders.models import Order


class OrderFilter(django_filters.FilterSet):
    """
    Filters for operational order management endpoints.
    """

    status = django_filters.CharFilter(
        field_name="status",
        lookup_expr="iexact",
    )

    payment_status = django_filters.CharFilter(
        field_name="payment_status",
        lookup_expr="iexact",
    )

    shipping_status = django_filters.CharFilter(
        field_name="shipping_status",
        lookup_expr="iexact",
    )

    customer_email = django_filters.CharFilter(
        field_name="customer__user_email",
        lookup_expr="icontains",
    )

    customer_name = django_filters.CharFilter(
        field_name="customer__user_name",
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

    class Meta:
        model = Order
        fields = [
            "status",
            "payment_status",
            "shipping_status",
            "customer_email",
            "customer_name",
            "created_after",
            "created_before",
        ]
