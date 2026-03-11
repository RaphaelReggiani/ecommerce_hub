from django.core.cache import cache

from ech.products.constants.cache import (
    PRODUCT_CACHE_TIMEOUT,
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