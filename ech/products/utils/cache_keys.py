import hashlib

from django.core.cache import cache

from ech.products.constants.cache import (
    PRODUCT_CACHE_PREFIX,
    PRODUCT_CACHE_TIMEOUT,
    PRODUCT_LIST_CACHE_PREFIX,
    PRODUCT_LIST_CACHE_TIMEOUT,
)

PRODUCT_LIST_CACHE_VERSION_KEY = f"{PRODUCT_LIST_CACHE_PREFIX}:version"


def get_product_from_cache(product_id):
    """
    Retrieves a product from cache.
    """

    cache_key = f"{PRODUCT_CACHE_PREFIX}:{product_id}"

    return cache.get(cache_key)


def set_product_cache(product):
    """
    Stores a product in cache.
    """

    cache_key = f"{PRODUCT_CACHE_PREFIX}:{product.id}"

    cache.set(
        cache_key,
        product,
        timeout=PRODUCT_CACHE_TIMEOUT,
    )


def invalidate_product_cache(product_id):
    """
    Removes product from cache.
    """

    cache_key = f"{PRODUCT_CACHE_PREFIX}:{product_id}"

    cache.delete(cache_key)


def get_product_list_cache(cache_key):
    """
    Retrieves cached product list response.
    """

    return cache.get(cache_key)


def set_product_list_cache(cache_key, data, timeout=None):
    """
    Stores product list response in cache.
    """

    if timeout is None:
        timeout = PRODUCT_LIST_CACHE_TIMEOUT

    cache.set(cache_key, data, timeout)


def invalidate_product_list_cache():
    """
    Invalidates all product list cache entries by bumping the cache version.

    This strategy is backend-agnostic and works with LocMemCache, Redis,
    and other Django cache backends.
    """

    current_version = cache.get(PRODUCT_LIST_CACHE_VERSION_KEY, 1)
    cache.set(PRODUCT_LIST_CACHE_VERSION_KEY, current_version + 1, None)


def build_product_list_cache_key(request):
    """
    Builds a cache key based on query parameters.
    Ensures pagination, filters, search and ordering are respected.
    """

    query_string = request.META.get("QUERY_STRING", "")
    version = cache.get(PRODUCT_LIST_CACHE_VERSION_KEY, 1)

    raw_key = f"{PRODUCT_LIST_CACHE_PREFIX}:v{version}:{query_string}"
    hashed_key = hashlib.md5(raw_key.encode()).hexdigest()

    return f"{PRODUCT_LIST_CACHE_PREFIX}:{hashed_key}"