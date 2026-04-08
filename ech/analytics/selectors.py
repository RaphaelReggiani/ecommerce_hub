from django.db.models import Q

from ech.analytics.constants.cache import (
    ANALYTIC_CACHE_TIMEOUT_DEFAULT,
    ANALYTIC_CACHE_TIMEOUT_LONG,
)
from ech.analytics.exceptions import (
    AnalyticsSnapshotNotFoundException,
)
from ech.analytics.models import AnalyticsSnapshot
from ech.analytics.services.cache_service import AnalyticsCacheService
from ech.analytics.utils.cache_keys import (
    analytics_snapshot_detail_cache_key,
    analytics_snapshot_list_cache_key,
    analytics_snapshot_period_list_cache_key,
    analytics_snapshot_period_range_cache_key,
    latest_analytics_snapshot_cache_key,
)
from ech.notifications.models import Notification
from ech.orders.models import Order
from ech.payments.models import Payment
from ech.products.models import Product
from ech.reviews.models import Review
from ech.shipping.models import Shipment
from ech.users.models import CustomUser


def analytics_snapshot_base_queryset():
    """
    Return the base analytics snapshot queryset
    with optimized related loading.
    """
    return AnalyticsSnapshot.objects.select_related(
        "generated_by",
        "lifecycle",
    ).prefetch_related(
        "events",
    )


def _rebuild_snapshot_queryset_from_ids(*, snapshot_ids):
    """
    Rebuild analytics snapshot queryset from cached IDs.
    """
    return analytics_snapshot_base_queryset().filter(id__in=snapshot_ids)


def get_analytics_snapshot_by_id(*, snapshot_id):
    """
    Retrieve an analytics snapshot by ID with related objects.
    """
    snapshot_version = AnalyticsCacheService.get_snapshot_version(
        snapshot_id=snapshot_id,
    )
    cache_key = analytics_snapshot_detail_cache_key(
        snapshot_id=snapshot_id,
        snapshot_version=snapshot_version,
    )

    def producer():
        try:
            return analytics_snapshot_base_queryset().get(id=snapshot_id)
        except AnalyticsSnapshot.DoesNotExist as exc:
            raise AnalyticsSnapshotNotFoundException() from exc

    return AnalyticsCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=ANALYTIC_CACHE_TIMEOUT_DEFAULT,
    )


def get_analytics_snapshot_with_related(*, snapshot_id):
    """
    Retrieve an analytics snapshot by ID with related objects.
    Kept for compatibility with a conventional selector API.
    """
    return get_analytics_snapshot_by_id(snapshot_id=snapshot_id)


def get_latest_analytics_snapshot_by_period_type(*, period_type):
    """
    Retrieve the latest analytics snapshot for a given period type.
    """
    period_version = AnalyticsCacheService.get_snapshot_period_version(
        period_type=period_type,
    )
    cache_key = latest_analytics_snapshot_cache_key(
        period_type=period_type,
        period_version=period_version,
    )

    def producer():
        try:
            return (
                analytics_snapshot_base_queryset()
                .filter(period_type=period_type)
                .latest("period_end")
            )
        except AnalyticsSnapshot.DoesNotExist as exc:
            raise AnalyticsSnapshotNotFoundException() from exc

    return AnalyticsCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=ANALYTIC_CACHE_TIMEOUT_DEFAULT,
    )


def list_analytics_snapshots():
    """
    List analytics snapshots for management dashboards.
    """
    management_version = AnalyticsCacheService.get_management_version()
    cache_key = analytics_snapshot_list_cache_key(
        management_version=management_version,
    )

    def producer():
        return list(
            analytics_snapshot_base_queryset()
            .values_list("id", flat=True)
        )

    snapshot_ids = AnalyticsCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=ANALYTIC_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_snapshot_queryset_from_ids(
        snapshot_ids=snapshot_ids,
    )


def list_analytics_snapshots_by_period_type(*, period_type):
    """
    List analytics snapshots filtered by period type.
    """
    period_version = AnalyticsCacheService.get_snapshot_period_version(
        period_type=period_type,
    )
    cache_key = analytics_snapshot_period_list_cache_key(
        period_type=period_type,
        period_version=period_version,
    )

    def producer():
        return list(
            analytics_snapshot_base_queryset()
            .filter(period_type=period_type)
            .values_list("id", flat=True)
        )

    snapshot_ids = AnalyticsCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=ANALYTIC_CACHE_TIMEOUT_LONG,
    )

    return _rebuild_snapshot_queryset_from_ids(
        snapshot_ids=snapshot_ids,
    ).filter(period_type=period_type)


def list_analytics_snapshots_by_period_range(
    *,
    period_start,
    period_end,
    period_type=None,
):
    """
    List analytics snapshots filtered by period range,
    optionally restricted to a specific period type.
    """
    management_version = AnalyticsCacheService.get_management_version()
    cache_key = analytics_snapshot_period_range_cache_key(
        period_start=period_start,
        period_end=period_end,
        period_type=period_type,
        management_version=management_version,
    )

    def producer():
        queryset = analytics_snapshot_base_queryset().filter(
            period_start__gte=period_start,
            period_end__lte=period_end,
        )

        if period_type:
            queryset = queryset.filter(period_type=period_type)

        return list(queryset.values_list("id", flat=True))

    snapshot_ids = AnalyticsCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=ANALYTIC_CACHE_TIMEOUT_LONG,
    )

    queryset = _rebuild_snapshot_queryset_from_ids(
        snapshot_ids=snapshot_ids,
    ).filter(
        period_start__gte=period_start,
        period_end__lte=period_end,
    )

    if period_type:
        queryset = queryset.filter(period_type=period_type)

    return queryset


def list_recent_analytics_snapshots():
    """
    List recent analytics snapshots.
    Kept compatible with the original selector style
    used across the project.
    """
    return analytics_snapshot_base_queryset().order_by("-created_at")


def order_analytics_base_queryset():
    """
    Return the base order queryset used by analytics services.
    """
    return Order.objects.select_related(
        "customer",
        "totals",
        "lifecycle",
        "address",
    ).prefetch_related(
        "items",
        "events",
    )


def list_orders_for_analytics(*, period_start, period_end):
    """
    List orders created within the given analytics period.
    """
    return order_analytics_base_queryset().filter(
        created_at__gte=period_start,
        created_at__lt=period_end,
    )


def payment_analytics_base_queryset():
    """
    Return the base payment queryset used by analytics services.
    """
    return Payment.objects.select_related(
        "order",
        "customer",
        "lifecycle",
    ).prefetch_related(
        "transactions",
        "refunds",
        "events",
    )


def list_payments_for_analytics(*, period_start, period_end):
    """
    List payments created within the given analytics period.
    """
    return payment_analytics_base_queryset().filter(
        created_at__gte=period_start,
        created_at__lt=period_end,
    )


def shipment_analytics_base_queryset():
    """
    Return the base shipment queryset used by analytics services.
    """
    return Shipment.objects.select_related(
        "order",
        "customer",
        "address",
        "lifecycle",
    ).prefetch_related(
        "events",
        "tracking_updates",
        "notes",
    )


def list_shipments_for_analytics(*, period_start, period_end):
    """
    List shipments created within the given analytics period.
    """
    return shipment_analytics_base_queryset().filter(
        created_at__gte=period_start,
        created_at__lt=period_end,
    )


def product_analytics_base_queryset():
    """
    Return the base product queryset used by analytics services.
    """
    return Product.objects.select_related(
        "sold_by",
        "inventory_record",
    ).prefetch_related(
        "images",
        "reviews",
        "event_logs",
    )


def list_products_for_analytics():
    """
    List products used by analytics services.
    """
    return product_analytics_base_queryset()


def customer_analytics_base_queryset():
    """
    Return the base customer queryset used by analytics services.
    """
    return CustomUser.objects.filter(
        user_role=CustomUser.ROLE_CUSTOMER_USER,
    )


def list_customers_for_analytics(*, period_start=None, period_end=None):
    """
    List customer users for analytics, optionally filtered by join date.
    """
    queryset = customer_analytics_base_queryset()

    if period_start is not None:
        queryset = queryset.filter(date_joined__gte=period_start)

    if period_end is not None:
        queryset = queryset.filter(date_joined__lt=period_end)

    return queryset


def user_analytics_base_queryset():
    """
    Return the base user queryset used by analytics services.
    """
    return CustomUser.objects.all()


def list_users_for_analytics(*, period_end=None):
    """
    List users for analytics, optionally restricted to registrations
    created up to a specific datetime.
    """
    queryset = user_analytics_base_queryset()

    if period_end is not None:
        queryset = queryset.filter(date_joined__lt=period_end)

    return queryset


def review_analytics_base_queryset():
    """
    Return the base review queryset used by analytics services.
    """
    return Review.objects.select_related(
        "customer",
        "product",
        "moderated_by",
        "lifecycle",
    ).prefetch_related(
        "events",
    )


def list_reviews_for_analytics(*, period_start, period_end):
    """
    List reviews created within the given analytics period.
    """
    return review_analytics_base_queryset().filter(
        created_at__gte=period_start,
        created_at__lt=period_end,
    )


def notification_analytics_base_queryset():
    """
    Return the base notification queryset used by analytics services.
    """
    return Notification.objects.select_related(
        "recipient",
        "created_by",
        "lifecycle",
    ).prefetch_related(
        "deliveries",
        "events",
    )


def list_notifications_for_analytics(*, period_start, period_end):
    """
    List notifications created within the given analytics period.
    """
    return notification_analytics_base_queryset().filter(
        created_at__gte=period_start,
        created_at__lt=period_end,
    )


def search_analytics_snapshots(*, query):
    """
    Search analytics snapshots by period type or metadata content.
    """
    management_version = AnalyticsCacheService.get_management_version()
    cache_key = analytics_snapshot_period_range_cache_key(
        period_start="search",
        period_end=query,
        period_type="all",
        management_version=management_version,
    )

    def producer():
        return list(
            analytics_snapshot_base_queryset()
            .filter(
                Q(period_type__icontains=query)
                | Q(metadata__icontains=query)
            )
            .values_list("id", flat=True)
        )

    snapshot_ids = AnalyticsCacheService.get_or_set(
        key=cache_key,
        producer=producer,
        timeout=ANALYTIC_CACHE_TIMEOUT_DEFAULT,
    )

    return _rebuild_snapshot_queryset_from_ids(
        snapshot_ids=snapshot_ids,
    ).filter(
        Q(period_type__icontains=query)
        | Q(metadata__icontains=query)
    )