from django.core.cache import cache

from ech.analytics.constants.cache import (
    ANALYTIC_CACHE_DEFAULT_VERSION,
    ANALYTIC_CACHE_TIMEOUT_DEFAULT,
)
from ech.analytics.utils.cache_keys import (
    customer_version_key,
    dashboard_version_key,
    management_version_key,
    order_funnel_version_key,
    payment_version_key,
    product_version_key,
    review_version_key,
    sales_version_key,
    shipping_version_key,
    snapshot_period_version_key,
    snapshot_version_key,
    user_version_key,
)


class AnalyticsCacheService:
    """
    Service responsible for analytics cache operations and cache invalidation.
    """

    @staticmethod
    def get(*, key, default=None):
        return cache.get(key, default)

    @staticmethod
    def set(*, key, value, timeout=ANALYTIC_CACHE_TIMEOUT_DEFAULT):
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
        timeout=ANALYTIC_CACHE_TIMEOUT_DEFAULT,
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
    def get_snapshot_version(cls, *, snapshot_id):
        key = snapshot_version_key(snapshot_id=snapshot_id)
        return cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_snapshot_period_version(cls, *, period_type):
        key = snapshot_period_version_key(period_type=period_type)
        return cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_dashboard_version(cls):
        key = dashboard_version_key()
        return cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_sales_version(cls):
        key = sales_version_key()
        return cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_order_funnel_version(cls):
        key = order_funnel_version_key()
        return cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_payment_version(cls):
        key = payment_version_key()
        return cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_shipping_version(cls):
        key = shipping_version_key()
        return cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_product_version(cls):
        key = product_version_key()
        return cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_customer_version(cls):
        key = customer_version_key()
        return cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_user_version(cls):
        key = user_version_key()
        return cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_review_version(cls):
        key = review_version_key()
        return cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)

    @classmethod
    def get_management_version(cls):
        key = management_version_key()
        return cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)

    @classmethod
    def bump_snapshot_version(cls, *, snapshot_id):
        key = snapshot_version_key(snapshot_id=snapshot_id)
        current = cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_snapshot_period_version(cls, *, period_type):
        key = snapshot_period_version_key(period_type=period_type)
        current = cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_dashboard_version(cls):
        key = dashboard_version_key()
        current = cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_sales_version(cls):
        key = sales_version_key()
        current = cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_order_funnel_version(cls):
        key = order_funnel_version_key()
        current = cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_payment_version(cls):
        key = payment_version_key()
        current = cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_shipping_version(cls):
        key = shipping_version_key()
        current = cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_product_version(cls):
        key = product_version_key()
        current = cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_customer_version(cls):
        key = customer_version_key()
        current = cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_user_version(cls):
        key = user_version_key()
        current = cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_review_version(cls):
        key = review_version_key()
        current = cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def bump_management_version(cls):
        key = management_version_key()
        current = cls.get(key=key, default=ANALYTIC_CACHE_DEFAULT_VERSION)
        cls.set(key=key, value=current + 1, timeout=None)

    @classmethod
    def invalidate_snapshot_cache(
        cls,
        *,
        snapshot_id,
        period_type,
    ):
        """
        Invalidate cache namespaces directly related to a snapshot mutation.
        """
        cls.bump_snapshot_version(snapshot_id=snapshot_id)
        cls.bump_snapshot_period_version(period_type=period_type)
        cls.bump_management_version()

    @classmethod
    def invalidate_dashboard_cache(cls):
        """
        Invalidate analytics dashboard summary cache.
        """
        cls.bump_dashboard_version()
        cls.bump_management_version()

    @classmethod
    def invalidate_sales_cache(cls):
        """
        Invalidate analytics sales overview cache.
        """
        cls.bump_sales_version()
        cls.bump_management_version()

    @classmethod
    def invalidate_order_funnel_cache(cls):
        """
        Invalidate analytics order funnel cache.
        """
        cls.bump_order_funnel_version()
        cls.bump_management_version()

    @classmethod
    def invalidate_payment_cache(cls):
        """
        Invalidate analytics payment overview cache.
        """
        cls.bump_payment_version()
        cls.bump_management_version()

    @classmethod
    def invalidate_shipping_cache(cls):
        """
        Invalidate analytics shipping overview cache.
        """
        cls.bump_shipping_version()
        cls.bump_management_version()

    @classmethod
    def invalidate_product_cache(cls):
        """
        Invalidate analytics product performance cache.
        """
        cls.bump_product_version()
        cls.bump_management_version()

    @classmethod
    def invalidate_customer_cache(cls):
        """
        Invalidate analytics customer summary cache.
        """
        cls.bump_customer_version()
        cls.bump_management_version()

    @classmethod
    def invalidate_user_cache(cls):
        """
        Invalidate analytics user overview cache.
        """
        cls.bump_user_version()
        cls.bump_management_version()

    @classmethod
    def invalidate_review_cache(cls):
        """
        Invalidate analytics review overview cache.
        """
        cls.bump_review_version()
        cls.bump_management_version()

    @classmethod
    def invalidate_all_analytics_views(cls):
        """
        Invalidate all aggregate analytics view namespaces.
        """
        cls.bump_dashboard_version()
        cls.bump_sales_version()
        cls.bump_order_funnel_version()
        cls.bump_payment_version()
        cls.bump_shipping_version()
        cls.bump_product_version()
        cls.bump_customer_version()
        cls.bump_user_version()
        cls.bump_review_version()
        cls.bump_management_version()

    @classmethod
    def invalidate_after_snapshot_mutation(
        cls,
        *,
        snapshot_id,
        period_type,
    ):
        """
        Invalidate all relevant cache namespaces after snapshot creation
        or refresh.
        """
        cls.invalidate_snapshot_cache(
            snapshot_id=snapshot_id,
            period_type=period_type,
        )
        cls.invalidate_all_analytics_views()