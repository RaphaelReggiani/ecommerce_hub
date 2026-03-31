from django.core.cache import cache

from ech.reviews.constants.cache import (
    REVIEW_DETAIL_CACHE_PREFIX,
    CUSTOMER_REVIEW_LIST_CACHE_PREFIX,
    MANAGEMENT_REVIEW_LIST_CACHE_PREFIX,
    PUBLIC_PRODUCT_REVIEW_LIST_CACHE_PREFIX,
    PRODUCT_REVIEW_SUMMARY_CACHE_PREFIX,
    REVIEW_DETAIL_VERSION_PREFIX,
    CUSTOMER_REVIEW_LIST_VERSION_PREFIX,
    MANAGEMENT_REVIEW_LIST_VERSION_PREFIX,
    PUBLIC_PRODUCT_REVIEW_LIST_VERSION_PREFIX,
    PRODUCT_REVIEW_SUMMARY_VERSION_PREFIX,
    REVIEW_DETAIL_CACHE_TTL,
    CUSTOMER_REVIEW_LIST_CACHE_TTL,
    MANAGEMENT_REVIEW_LIST_CACHE_TTL,
    PUBLIC_PRODUCT_REVIEW_LIST_CACHE_TTL,
    PRODUCT_REVIEW_SUMMARY_CACHE_TTL,
    DEFAULT_CACHE_NAMESPACE_VERSION,
)

from ech.reviews.utils.cache_keys import (
    build_review_detail_cache_key,
    build_customer_review_list_cache_key,
    build_management_review_list_cache_key,
    build_public_product_review_list_cache_key,
    build_product_review_summary_cache_key,
    build_namespace_version_cache_key,
)


class ReviewsCacheService:
    """
    Centralized cache service for reviews read operations.

    This service provides:
    - versioned cache keys
    - deterministic invalidation
    - scoped cache namespaces for read models
    """

    @staticmethod
    def get(key):
        """
        Return a cached value for the given key.
        """
        return cache.get(key)

    @staticmethod
    def set(key, value, ttl):
        """
        Store a value in cache using the given TTL.
        """
        cache.set(key, value, ttl)

    @staticmethod
    def delete(key):
        """
        Delete a cache entry by key.
        """
        cache.delete(key)

    @classmethod
    def get_or_set(cls, *, key, ttl, callback):
        """
        Return cached value or compute/store it using the callback.
        """
        cached_value = cls.get(key)

        if cached_value is not None:
            return cached_value

        value = callback()
        cls.set(key, value, ttl)
        return value

    @classmethod
    def _get_namespace_version(cls, *, version_prefix, identifier=None):
        """
        Return the current namespace version for a cache scope.
        """
        version_key = build_namespace_version_cache_key(
            prefix=version_prefix,
            identifier=identifier,
        )

        version = cache.get(version_key)

        if version is None:
            cache.set(version_key, DEFAULT_CACHE_NAMESPACE_VERSION, None)
            return DEFAULT_CACHE_NAMESPACE_VERSION

        return version

    @classmethod
    def _bump_namespace_version(cls, *, version_prefix, identifier=None):
        """
        Invalidate a cache namespace by incrementing its version.
        """
        version_key = build_namespace_version_cache_key(
            prefix=version_prefix,
            identifier=identifier,
        )

        current_version = cache.get(version_key)

        if current_version is None:
            cache.set(
                version_key,
                DEFAULT_CACHE_NAMESPACE_VERSION + 1,
                None,
            )
            return

        try:
            cache.incr(version_key)
        except ValueError:
            cache.set(version_key, current_version + 1, None)

    @classmethod
    def get_review_detail_cache_key(cls, *, review_id):
        """
        Build cache key for review detail by review ID.
        """
        version = cls._get_namespace_version(
            version_prefix=REVIEW_DETAIL_VERSION_PREFIX,
            identifier=review_id,
        )

        return build_review_detail_cache_key(
            prefix=REVIEW_DETAIL_CACHE_PREFIX,
            review_id=review_id,
            version=version,
        )

    @classmethod
    def get_review_detail(cls, *, review_id):
        """
        Retrieve cached review detail.
        """
        key = cls.get_review_detail_cache_key(review_id=review_id)
        return cls.get(key)

    @classmethod
    def set_review_detail(cls, *, review_id, value):
        """
        Cache review detail.
        """
        key = cls.get_review_detail_cache_key(review_id=review_id)
        cls.set(key, value, REVIEW_DETAIL_CACHE_TTL)

    @classmethod
    def get_or_set_review_detail(cls, *, review_id, callback):
        """
        Return cached review detail or populate it.
        """
        key = cls.get_review_detail_cache_key(review_id=review_id)
        return cls.get_or_set(
            key=key,
            ttl=REVIEW_DETAIL_CACHE_TTL,
            callback=callback,
        )

    @classmethod
    def invalidate_review_detail(cls, *, review_id):
        """
        Invalidate cached review detail by review ID.
        """
        cls._bump_namespace_version(
            version_prefix=REVIEW_DETAIL_VERSION_PREFIX,
            identifier=review_id,
        )

    @classmethod
    def get_customer_review_list_cache_key(
        cls,
        *,
        customer_id,
        filters=None,
    ):
        """
        Build cache key for customer review lists.
        """
        version = cls._get_namespace_version(
            version_prefix=CUSTOMER_REVIEW_LIST_VERSION_PREFIX,
            identifier=customer_id,
        )

        return build_customer_review_list_cache_key(
            prefix=CUSTOMER_REVIEW_LIST_CACHE_PREFIX,
            customer_id=customer_id,
            version=version,
            filters=filters,
        )

    @classmethod
    def get_customer_review_list(cls, *, customer_id, filters=None):
        """
        Retrieve cached customer review list.
        """
        key = cls.get_customer_review_list_cache_key(
            customer_id=customer_id,
            filters=filters,
        )
        return cls.get(key)

    @classmethod
    def set_customer_review_list(cls, *, customer_id, filters=None, value):
        """
        Cache customer review list.
        """
        key = cls.get_customer_review_list_cache_key(
            customer_id=customer_id,
            filters=filters,
        )
        cls.set(key, value, CUSTOMER_REVIEW_LIST_CACHE_TTL)

    @classmethod
    def get_or_set_customer_review_list(
        cls,
        *,
        customer_id,
        filters=None,
        callback,
    ):
        """
        Return cached customer review list or populate it.
        """
        key = cls.get_customer_review_list_cache_key(
            customer_id=customer_id,
            filters=filters,
        )
        return cls.get_or_set(
            key=key,
            ttl=CUSTOMER_REVIEW_LIST_CACHE_TTL,
            callback=callback,
        )

    @classmethod
    def invalidate_customer_review_lists(cls, *, customer_id):
        """
        Invalidate all cached review lists for a given customer.
        """
        cls._bump_namespace_version(
            version_prefix=CUSTOMER_REVIEW_LIST_VERSION_PREFIX,
            identifier=customer_id,
        )

    @classmethod
    def get_management_review_list_cache_key(cls, *, filters=None):
        """
        Build cache key for management review lists.
        """
        version = cls._get_namespace_version(
            version_prefix=MANAGEMENT_REVIEW_LIST_VERSION_PREFIX,
        )

        return build_management_review_list_cache_key(
            prefix=MANAGEMENT_REVIEW_LIST_CACHE_PREFIX,
            version=version,
            filters=filters,
        )

    @classmethod
    def get_management_review_list(cls, *, filters=None):
        """
        Retrieve cached management review list.
        """
        key = cls.get_management_review_list_cache_key(filters=filters)
        return cls.get(key)

    @classmethod
    def set_management_review_list(cls, *, filters=None, value):
        """
        Cache management review list.
        """
        key = cls.get_management_review_list_cache_key(filters=filters)
        cls.set(key, value, MANAGEMENT_REVIEW_LIST_CACHE_TTL)

    @classmethod
    def get_or_set_management_review_list(cls, *, filters=None, callback):
        """
        Return cached management review list or populate it.
        """
        key = cls.get_management_review_list_cache_key(filters=filters)
        return cls.get_or_set(
            key=key,
            ttl=MANAGEMENT_REVIEW_LIST_CACHE_TTL,
            callback=callback,
        )

    @classmethod
    def invalidate_management_review_lists(cls):
        """
        Invalidate all cached management review lists.
        """
        cls._bump_namespace_version(
            version_prefix=MANAGEMENT_REVIEW_LIST_VERSION_PREFIX,
        )

    @classmethod
    def get_public_product_review_list_cache_key(
        cls,
        *,
        product_id,
        filters=None,
    ):
        """
        Build cache key for public product review lists.
        """
        version = cls._get_namespace_version(
            version_prefix=PUBLIC_PRODUCT_REVIEW_LIST_VERSION_PREFIX,
            identifier=product_id,
        )

        return build_public_product_review_list_cache_key(
            prefix=PUBLIC_PRODUCT_REVIEW_LIST_CACHE_PREFIX,
            product_id=product_id,
            version=version,
            filters=filters,
        )

    @classmethod
    def get_public_product_review_list(cls, *, product_id, filters=None):
        """
        Retrieve cached public product review list.
        """
        key = cls.get_public_product_review_list_cache_key(
            product_id=product_id,
            filters=filters,
        )
        return cls.get(key)

    @classmethod
    def set_public_product_review_list(
        cls,
        *,
        product_id,
        filters=None,
        value,
    ):
        """
        Cache public product review list.
        """
        key = cls.get_public_product_review_list_cache_key(
            product_id=product_id,
            filters=filters,
        )
        cls.set(key, value, PUBLIC_PRODUCT_REVIEW_LIST_CACHE_TTL)

    @classmethod
    def get_or_set_public_product_review_list(
        cls,
        *,
        product_id,
        filters=None,
        callback,
    ):
        """
        Return cached public product review list or populate it.
        """
        key = cls.get_public_product_review_list_cache_key(
            product_id=product_id,
            filters=filters,
        )
        return cls.get_or_set(
            key=key,
            ttl=PUBLIC_PRODUCT_REVIEW_LIST_CACHE_TTL,
            callback=callback,
        )

    @classmethod
    def invalidate_public_product_review_lists(cls, *, product_id):
        """
        Invalidate all cached public review lists for a product.
        """
        cls._bump_namespace_version(
            version_prefix=PUBLIC_PRODUCT_REVIEW_LIST_VERSION_PREFIX,
            identifier=product_id,
        )

    @classmethod
    def get_product_review_summary_cache_key(cls, *, product_id):
        """
        Build cache key for product review summary.
        """
        version = cls._get_namespace_version(
            version_prefix=PRODUCT_REVIEW_SUMMARY_VERSION_PREFIX,
            identifier=product_id,
        )

        return build_product_review_summary_cache_key(
            prefix=PRODUCT_REVIEW_SUMMARY_CACHE_PREFIX,
            product_id=product_id,
            version=version,
        )

    @classmethod
    def get_product_review_summary(cls, *, product_id):
        """
        Retrieve cached product review summary.
        """
        key = cls.get_product_review_summary_cache_key(product_id=product_id)
        return cls.get(key)

    @classmethod
    def set_product_review_summary(cls, *, product_id, value):
        """
        Cache product review summary.
        """
        key = cls.get_product_review_summary_cache_key(product_id=product_id)
        cls.set(key, value, PRODUCT_REVIEW_SUMMARY_CACHE_TTL)

    @classmethod
    def get_or_set_product_review_summary(cls, *, product_id, callback):
        """
        Return cached product review summary or populate it.
        """
        key = cls.get_product_review_summary_cache_key(product_id=product_id)
        return cls.get_or_set(
            key=key,
            ttl=PRODUCT_REVIEW_SUMMARY_CACHE_TTL,
            callback=callback,
        )

    @classmethod
    def invalidate_product_review_summary(cls, *, product_id):
        """
        Invalidate cached product review summary.
        """
        cls._bump_namespace_version(
            version_prefix=PRODUCT_REVIEW_SUMMARY_VERSION_PREFIX,
            identifier=product_id,
        )

    @classmethod
    def invalidate_review_aggregate(
        cls,
        *,
        review_id,
        customer_id,
        product_id,
    ):
        """
        Invalidate all cache entries affected by a review mutation.
        """
        cls.invalidate_review_detail(review_id=review_id)
        cls.invalidate_customer_review_lists(customer_id=customer_id)
        cls.invalidate_management_review_lists()
        cls.invalidate_public_product_review_lists(product_id=product_id)
        cls.invalidate_product_review_summary(product_id=product_id)