from ech.admin_dashboard.constants.cache import (
    ADMIN_DASHBOARD_CACHE_MANAGEMENT_PREFIX,
    ADMIN_DASHBOARD_CACHE_SEARCH_PREFIX,
    ADMIN_DASHBOARD_CACHE_VERSION_PREFIX,
)


def _normalize_text(value):
    """
    Normalize text values for cache keys.
    """

    if value is None:
        return "none"

    return str(value).strip().lower().replace(" ", "_")


def dashboard_version_key():
    return f"{ADMIN_DASHBOARD_CACHE_VERSION_PREFIX}:dashboard"


def operational_metrics_version_key():
    return f"{ADMIN_DASHBOARD_CACHE_VERSION_PREFIX}:operational-metrics"


def activity_feed_version_key():
    return f"{ADMIN_DASHBOARD_CACHE_VERSION_PREFIX}:activity-feed"


def alerts_version_key():
    return f"{ADMIN_DASHBOARD_CACHE_VERSION_PREFIX}:alerts"


def management_version_key():
    return f"{ADMIN_DASHBOARD_CACHE_VERSION_PREFIX}:management"

def admin_dashboard_summary_cache_key(*, dashboard_version):
    return (
        f"{ADMIN_DASHBOARD_CACHE_MANAGEMENT_PREFIX}:dashboard-summary:"
        f"v{dashboard_version}"
    )


def admin_dashboard_operational_metrics_cache_key(*, operational_version):
    return (
        f"{ADMIN_DASHBOARD_CACHE_MANAGEMENT_PREFIX}:operational-metrics:"
        f"v{operational_version}"
    )


def admin_dashboard_recent_activity_cache_key(
    *,
    activity_version,
    limit,
):
    return (
        f"{ADMIN_DASHBOARD_CACHE_MANAGEMENT_PREFIX}:activity-feed:"
        f"{_normalize_text(limit)}:"
        f"v{activity_version}"
    )


def admin_dashboard_alerts_cache_key(*, alerts_version):
    return (
        f"{ADMIN_DASHBOARD_CACHE_MANAGEMENT_PREFIX}:alerts:"
        f"v{alerts_version}"
    )


def admin_dashboard_search_cache_key(*, query, management_version):
    return (
        f"{ADMIN_DASHBOARD_CACHE_SEARCH_PREFIX}:"
        f"{_normalize_text(query)}:"
        f"v{management_version}"
    )