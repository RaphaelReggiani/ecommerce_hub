import django_filters

from ech.shipping.models import Shipment


class ShipmentFilter(django_filters.FilterSet):
    """
    Customer-facing shipment filters.
    """

    status = django_filters.CharFilter(
        field_name="status",
        lookup_expr="exact",
    )

    shipping_method = django_filters.CharFilter(
        field_name="shipping_method",
        lookup_expr="exact",
    )

    carrier_name = django_filters.CharFilter(
        field_name="carrier_name",
        lookup_expr="icontains",
    )

    tracking_code = django_filters.CharFilter(
        field_name="tracking_code",
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

    estimated_delivery_after = django_filters.DateFilter(
        field_name="estimated_delivery_date",
        lookup_expr="gte",
    )

    estimated_delivery_before = django_filters.DateFilter(
        field_name="estimated_delivery_date",
        lookup_expr="lte",
    )

    class Meta:
        model = Shipment
        fields = [
            "status",
            "shipping_method",
            "carrier_name",
            "tracking_code",
        ]


class ShipmentManagementFilter(django_filters.FilterSet):
    """
    Management and operations shipment filters.

    Provides more extensive filtering for staff dashboards
    and operational tooling.
    """

    status = django_filters.CharFilter(
        field_name="status",
        lookup_expr="exact",
    )

    shipping_method = django_filters.CharFilter(
        field_name="shipping_method",
        lookup_expr="exact",
    )

    carrier_name = django_filters.CharFilter(
        field_name="carrier_name",
        lookup_expr="icontains",
    )

    tracking_code = django_filters.CharFilter(
        field_name="tracking_code",
        lookup_expr="icontains",
    )

    external_reference = django_filters.CharFilter(
        field_name="external_reference",
        lookup_expr="icontains",
    )

    customer_id = django_filters.NumberFilter(
        field_name="customer__id",
        lookup_expr="exact",
    )

    order_id = django_filters.UUIDFilter(
        field_name="order__id",
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

    estimated_delivery_after = django_filters.DateFilter(
        field_name="estimated_delivery_date",
        lookup_expr="gte",
    )

    estimated_delivery_before = django_filters.DateFilter(
        field_name="estimated_delivery_date",
        lookup_expr="lte",
    )

    class Meta:
        model = Shipment
        fields = [
            "status",
            "shipping_method",
            "carrier_name",
            "tracking_code",
            "external_reference",
            "customer_id",
            "order_id",
        ]