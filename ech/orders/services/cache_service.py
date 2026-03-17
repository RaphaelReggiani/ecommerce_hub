from django.core.cache import cache

from ech.orders.utils.cache_keys import (
    order_detail_cache_key,
    order_management_detail_cache_key,
    customer_orders_list_cache_key,
    management_orders_list_cache_key,
)


def invalidate_order_detail_cache(order_id):
    cache.delete(order_detail_cache_key(order_id))
    cache.delete(order_management_detail_cache_key(order_id))


def invalidate_customer_orders_cache(customer_id):
    cache.delete(customer_orders_list_cache_key(customer_id))


def invalidate_management_orders_cache():
    cache.delete(management_orders_list_cache_key())


def invalidate_order_related_caches(order):
    """
    Invalidates all relevant cache entries affected by an order change.
    """
    invalidate_order_detail_cache(order.id)
    invalidate_customer_orders_cache(order.customer_id)
    invalidate_management_orders_cache()