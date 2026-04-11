from django.core.cache import cache

from ech.admin_dashboard.constants.cache import (
    ADMIN_DASHBOARD_CACHE_DEFAULT_VERSION,
    ADMIN_DASHBOARD_CACHE_TIMEOUT_DEFAULT,
)

from ech.admin_dashboard.utils.cache_keys import (
    dashboard_version_key,
    operational_metrics_version_key,
    activity_feed_version_key,
    alerts_version_key,
    management_version_key,
)


class AdminDashboardCacheService:
    """
    Service responsible for admin dashboard cache operations
    and cache invalidation.
    """

    @staticmethod
    def get(*, key, default=None):
        return cache.get(key, default)

    @staticmethod
    def set(*, key, value, timeout=ADMIN_DASHBOARD_CACHE_TIMEOUT_DEFAULT):
        cache.set(key, value, timeout)

    @staticmethod
    def delete(*, key):
        cache.delete(key)

    @classmethod
    def get_or_set(
        cls,
        *,
        key,
        producer,
        timeout=ADMIN_DASHBOARD_CACHE_TIMEOUT_DEFAULT,
    ):
        cached_value = cls.get(key=key)

        if cached_value is not None:
            return cached_value

        value = producer()

        cls.set(
            key=key,
            value=value,
            timeout=timeout,
        )

        return value

    @classmethod
    def get_dashboard_version(cls):
        key = dashboard_version_key()
        return cls.get(key=key, default=ADMIN_DASHBOARD_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_operational_metrics_version(cls):
        key = operational_metrics_version_key()
        return cls.get(key=key, default=ADMIN_DASHBOARD_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_activity_feed_version(cls):
        key = activity_feed_version_key()
        return cls.get(key=key, default=ADMIN_DASHBOARD_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_alerts_version(cls):
        key = alerts_version_key()
        return cls.get(key=key, default=ADMIN_DASHBOARD_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_management_version(cls):
        key = management_version_key()
        return cls.get(key=key, default=ADMIN_DASHBOARD_CACHE_DEFAULT_VERSION)

    @classmethod
    def bump_dashboard_version(cls):
        key = dashboard_version_key()
        current = cls.get(key=key, default=ADMIN_DASHBOARD_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_operational_metrics_version(cls):
        key = operational_metrics_version_key()
        current = cls.get(key=key, default=ADMIN_DASHBOARD_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_activity_feed_version(cls):
        key = activity_feed_version_key()
        current = cls.get(key=key, default=ADMIN_DASHBOARD_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_alerts_version(cls):
        key = alerts_version_key()
        current = cls.get(key=key, default=ADMIN_DASHBOARD_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_management_version(cls):
        key = management_version_key()
        current = cls.get(key=key, default=ADMIN_DASHBOARD_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def invalidate_dashboard_cache(cls):
        """
        Invalidate dashboard summary cache.
        """
        cls.bump_dashboard_version()
        cls.bump_management_version()

    @classmethod
    def invalidate_operational_metrics_cache(cls):
        """
        Invalidate operational metrics cache.
        """
        cls.bump_operational_metrics_version()
        cls.bump_management_version()

    @classmethod
    def invalidate_activity_feed_cache(cls):
        """
        Invalidate recent activity cache.
        """
        cls.bump_activity_feed_version()
        cls.bump_management_version()

    @classmethod
    def invalidate_alerts_cache(cls):
        """
        Invalidate alerts cache.
        """
        cls.bump_alerts_version()
        cls.bump_management_version()

    @classmethod
    def invalidate_all_dashboard_views(cls):
        """
        Invalidate all admin dashboard cache namespaces.
        """

        cls.bump_dashboard_version()
        cls.bump_operational_metrics_version()
        cls.bump_activity_feed_version()
        cls.bump_alerts_version()
        cls.bump_management_version()