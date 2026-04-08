from ech.analytics.constants.cache import (
    ANALYTIC_CACHE_DETAIL_PREFIX,
    ANALYTIC_CACHE_MANAGEMENT_PREFIX,
    ANALYTIC_CACHE_SEARCH_PREFIX,
    ANALYTIC_CACHE_VERSION_PREFIX,
)


def _normalize_text(value):
    """
    Normalize text values for cache keys.
    """
    if value is None:
        return "none"

    return str(value).strip().lower().replace(" ", "_")


def snapshot_version_key(*, snapshot_id):
    return f"{ANALYTIC_CACHE_VERSION_PREFIX}:snapshot:{snapshot_id}"


def snapshot_period_version_key(*, period_type):
    return (
        f"{ANALYTIC_CACHE_VERSION_PREFIX}:snapshot-period:"
        f"{_normalize_text(period_type)}"
    )


def dashboard_version_key():
    return f"{ANALYTIC_CACHE_VERSION_PREFIX}:dashboard"


def sales_version_key():
    return f"{ANALYTIC_CACHE_VERSION_PREFIX}:sales"


def order_funnel_version_key():
    return f"{ANALYTIC_CACHE_VERSION_PREFIX}:order_funnel"


def payment_version_key():
    return f"{ANALYTIC_CACHE_VERSION_PREFIX}:payment"


def shipping_version_key():
    return f"{ANALYTIC_CACHE_VERSION_PREFIX}:shipping"


def product_version_key():
    return f"{ANALYTIC_CACHE_VERSION_PREFIX}:product"


def customer_version_key():
    return f"{ANALYTIC_CACHE_VERSION_PREFIX}:customer"


def user_version_key():
    return f"{ANALYTIC_CACHE_VERSION_PREFIX}:user"


def review_version_key():
    return f"{ANALYTIC_CACHE_VERSION_PREFIX}:review"


def management_version_key():
    return f"{ANALYTIC_CACHE_VERSION_PREFIX}:management"


def analytics_snapshot_detail_cache_key(*, snapshot_id, snapshot_version):
    return (
        f"{ANALYTIC_CACHE_DETAIL_PREFIX}:snapshot:{snapshot_id}:"
        f"v{snapshot_version}"
    )


def analytics_snapshot_list_cache_key(*, management_version):
    return (
        f"{ANALYTIC_CACHE_MANAGEMENT_PREFIX}:snapshot-list:"
        f"v{management_version}"
    )


def analytics_snapshot_period_list_cache_key(
    *,
    period_type,
    period_version,
):
    return (
        f"{ANALYTIC_CACHE_MANAGEMENT_PREFIX}:snapshot-period:"
        f"{_normalize_text(period_type)}:"
        f"v{period_version}"
    )


def analytics_snapshot_period_range_cache_key(
    *,
    period_start,
    period_end,
    period_type,
    management_version,
):
    return (
        f"{ANALYTIC_CACHE_MANAGEMENT_PREFIX}:snapshot-range:"
        f"{_normalize_text(period_start)}:"
        f"{_normalize_text(period_end)}:"
        f"{_normalize_text(period_type)}:"
        f"v{management_version}"
    )


def latest_analytics_snapshot_cache_key(
    *,
    period_type,
    period_version,
):
    return (
        f"{ANALYTIC_CACHE_DETAIL_PREFIX}:snapshot-latest:"
        f"{_normalize_text(period_type)}:"
        f"v{period_version}"
    )


def dashboard_summary_cache_key(
    *,
    period_start,
    period_end,
    dashboard_version,
):
    return (
        f"{ANALYTIC_CACHE_MANAGEMENT_PREFIX}:dashboard-summary:"
        f"{_normalize_text(period_start)}:"
        f"{_normalize_text(period_end)}:"
        f"v{dashboard_version}"
    )


def sales_overview_cache_key(
    *,
    period_start,
    period_end,
    sales_version,
):
    return (
        f"{ANALYTIC_CACHE_MANAGEMENT_PREFIX}:sales-overview:"
        f"{_normalize_text(period_start)}:"
        f"{_normalize_text(period_end)}:"
        f"v{sales_version}"
    )


def order_funnel_cache_key(
    *,
    period_start,
    period_end,
    funnel_version,
):
    return (
        f"{ANALYTIC_CACHE_MANAGEMENT_PREFIX}:order-funnel:"
        f"{_normalize_text(period_start)}:"
        f"{_normalize_text(period_end)}:"
        f"v{funnel_version}"
    )


def payment_overview_cache_key(
    *,
    period_start,
    period_end,
    payment_version,
):
    return (
        f"{ANALYTIC_CACHE_MANAGEMENT_PREFIX}:payment-overview:"
        f"{_normalize_text(period_start)}:"
        f"{_normalize_text(period_end)}:"
        f"v{payment_version}"
    )


def shipping_overview_cache_key(
    *,
    period_start,
    period_end,
    shipping_version,
):
    return (
        f"{ANALYTIC_CACHE_MANAGEMENT_PREFIX}:shipping-overview:"
        f"{_normalize_text(period_start)}:"
        f"{_normalize_text(period_end)}:"
        f"v{shipping_version}"
    )


def product_performance_cache_key(
    *,
    period_start,
    period_end,
    product_version,
):
    return (
        f"{ANALYTIC_CACHE_MANAGEMENT_PREFIX}:product-performance:"
        f"{_normalize_text(period_start)}:"
        f"{_normalize_text(period_end)}:"
        f"v{product_version}"
    )


def customer_summary_cache_key(
    *,
    period_start,
    period_end,
    customer_version,
):
    return (
        f"{ANALYTIC_CACHE_MANAGEMENT_PREFIX}:customer-summary:"
        f"{_normalize_text(period_start)}:"
        f"{_normalize_text(period_end)}:"
        f"v{customer_version}"
    )


def user_overview_cache_key(
    *,
    period_start,
    period_end,
    user_version,
):
    return (
        f"{ANALYTIC_CACHE_MANAGEMENT_PREFIX}:user-overview:"
        f"{_normalize_text(period_start)}:"
        f"{_normalize_text(period_end)}:"
        f"v{user_version}"
    )


def review_overview_cache_key(
    *,
    period_start,
    period_end,
    review_version,
):
    return (
        f"{ANALYTIC_CACHE_MANAGEMENT_PREFIX}:review-overview:"
        f"{_normalize_text(period_start)}:"
        f"{_normalize_text(period_end)}:"
        f"v{review_version}"
    )


def analytics_snapshot_search_cache_key(*, query, management_version):
    return (
        f"{ANALYTIC_CACHE_SEARCH_PREFIX}:"
        f"{_normalize_text(query)}:"
        f"v{management_version}"
    )