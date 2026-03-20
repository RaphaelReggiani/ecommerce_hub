from django.core.cache import cache
import hashlib

from ech.products.constants.cache import (
    PRODUCT_CACHE_TIMEOUT,
    PRODUCT_LIST_CACHE_PREFIX,
)


def get_product_from_cache(product_id):
    """
    Retrieves a product from cache.
    """
    return cache.get(f"product:{product_id}")


def set_product_cache(product):
    """
    Stores a product in cache.
    """
    cache.set(
        f"product:{product.id}",
        product,
        timeout=PRODUCT_CACHE_TIMEOUT,
    )


def invalidate_product_cache(product_id):
    """
    Removes product from cache.
    """
    cache.delete(f"product:{product_id}")


def get_product_list_cache(cache_key):
    """
    Retrieves cached product list response.
    """
    return cache.get(cache_key)


def set_product_list_cache(cache_key, data, timeout=300):
    """
    Stores product list response in cache.
    """
    cache.set(cache_key, data, timeout)


def build_product_list_cache_key(request):
    """
    Builds a cache key based on query parameters.
    Ensures pagination, filters, search and ordering are respected.
    """

    query_string = request.META.get("QUERY_STRING", "")

    raw_key = f"{PRODUCT_LIST_CACHE_PREFIX}:{query_string}"

    return hashlib.md5(raw_key.encode()).hexdigest()