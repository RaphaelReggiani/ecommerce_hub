import django_filters

from ech.reviews.models import Review
from ech.reviews.constants.constants import (
    REVIEW_ALLOWED_ORDERING,
    REVIEW_ORDERING_NEWEST,
    REVIEW_ORDERING_OLDEST,
    REVIEW_ORDERING_RATING_HIGH,
    REVIEW_ORDERING_RATING_LOW,
)


class ReviewFilter(django_filters.FilterSet):
    """
    Filter set for review listing endpoints.

    Supports customer review listings, management dashboards,
    and public product review listings.
    """

    status = django_filters.CharFilter(
        field_name="status",
        lookup_expr="iexact",
    )

    rating = django_filters.NumberFilter(
        field_name="rating",
    )

    rating_min = django_filters.NumberFilter(
        field_name="rating",
        lookup_expr="gte",
    )

    rating_max = django_filters.NumberFilter(
        field_name="rating",
        lookup_expr="lte",
    )

    product_id = django_filters.UUIDFilter(
        field_name="product_id",
    )

    customer_id = django_filters.NumberFilter(
        field_name="customer_id",
    )

    is_verified_purchase = django_filters.BooleanFilter(
        field_name="is_verified_purchase",
    )

    moderated_by_id = django_filters.NumberFilter(
        field_name="moderated_by_id",
    )

    created_after = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )

    created_before = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )

    ordering = django_filters.CharFilter(
        method="filter_ordering",
    )

    class Meta:
        model = Review
        fields = [
            "status",
            "rating",
            "rating_min",
            "rating_max",
            "product_id",
            "customer_id",
            "is_verified_purchase",
            "moderated_by_id",
            "created_after",
            "created_before",
        ]

    def filter_ordering(self, queryset, name, value):
        """
        Apply supported ordering strategies for review listings.
        Invalid ordering values return the queryset unchanged.
        """
        if value not in REVIEW_ALLOWED_ORDERING:
            return queryset

        if value == REVIEW_ORDERING_NEWEST:
            return queryset.order_by("-created_at")

        if value == REVIEW_ORDERING_OLDEST:
            return queryset.order_by("created_at")

        if value == REVIEW_ORDERING_RATING_HIGH:
            return queryset.order_by("-rating", "-created_at")

        if value == REVIEW_ORDERING_RATING_LOW:
            return queryset.order_by("rating", "-created_at")

        return queryset