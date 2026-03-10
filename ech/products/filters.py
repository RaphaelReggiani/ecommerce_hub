import django_filters

from ech.products.models import Product


class ProductFilter(django_filters.FilterSet):

    price_min = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte"
    )

    price_max = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte"
    )

    brand = django_filters.CharFilter(
        field_name="brand",
        lookup_expr="iexact"
    )

    class Meta:
        model = Product
        fields = [
            "brand",
            "product_type",
        ]