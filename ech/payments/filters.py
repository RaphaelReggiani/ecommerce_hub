import django_filters
from django.db import models
from django.db.models import QuerySet

from ech.payments.models import Payment


class PaymentFilter(django_filters.FilterSet):
    """
    Filter class for Payment list endpoints.

    Supports filtering by:
        - status
        - method
        - customer
        - order
        - payment_reference
        - gateway_payment_id
        - amount range
        - refunded amount range
        - created_at range
    """

    status = django_filters.CharFilter(field_name="status")
    method = django_filters.CharFilter(field_name="method")

    customer_id = django_filters.UUIDFilter(field_name="customer_id")
    order_id = django_filters.UUIDFilter(field_name="order_id")

    payment_reference = django_filters.CharFilter(
        field_name="payment_reference",
        lookup_expr="icontains",
    )

    gateway_payment_id = django_filters.CharFilter(
        field_name="gateway_payment_id",
        lookup_expr="icontains",
    )

    min_amount = django_filters.NumberFilter(
        field_name="amount",
        lookup_expr="gte",
    )

    max_amount = django_filters.NumberFilter(
        field_name="amount",
        lookup_expr="lte",
    )

    min_refunded_amount = django_filters.NumberFilter(
        field_name="refunded_amount",
        lookup_expr="gte",
    )

    max_refunded_amount = django_filters.NumberFilter(
        field_name="refunded_amount",
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

    is_refunded = django_filters.BooleanFilter(method="filter_is_refunded")
    is_partially_refunded = django_filters.BooleanFilter(method="filter_is_partially_refunded")

    class Meta:
        model = Payment
        fields = []

    def filter_is_refunded(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """
        Filter fully refunded payments.
        """

        if value:
            return queryset.filter(refunded_amount__gte=models.F("amount"))
        return queryset.exclude(refunded_amount__gte=models.F("amount"))

    def filter_is_partially_refunded(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """
        Filter partially refunded payments.
        """

        if value:
            return queryset.filter(
                refunded_amount__gt=0,
                refunded_amount__lt=models.F("amount"),
            )

        return queryset.exclude(
            refunded_amount__gt=0,
            refunded_amount__lt=models.F("amount"),
        )