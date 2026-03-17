from ech.orders.models import Order

from django.core.cache import cache

from ech.orders.utils.cache_keys import (
    order_detail_cache_key,
    order_management_detail_cache_key,
)

from ech.orders.constants.cache import (
    ORDER_DETAIL_CACHE_TIMEOUT,
    ORDER_MANAGEMENT_DETAIL_CACHE_TIMEOUT,
)


"""
Order selectors with read-side caching.

Note:
These selectors currently cache materialized ORM objects / lists for simplicity.
This is acceptable for the current project stage, but if cache serialization
or stale-object issues appear in the future, prefer caching IDs or serialized payloads.
"""


def get_order_by_id(order_id):
    """
    Returns an order by its ID with related data.
    """

    cache_key = order_detail_cache_key(order_id)
    cached_order = cache.get(cache_key)

    if cached_order is not None:
        return cached_order

    order = (
        Order.objects
        .select_related(
            "customer",
            "totals",
            "address",
            "lifecycle",
        )
        .prefetch_related(
            "items",
            "events",
            "notes",
        )
        .filter(id=order_id)
        .first()
    )

    cache.set(cache_key, order, ORDER_DETAIL_CACHE_TIMEOUT)
    return order


def list_orders_by_customer(customer):
    """
    Returns all orders from a specific customer.
    """

    return (
        Order.objects
        .filter(customer=customer)
        .select_related("customer", "totals")
        .order_by("-created_at")
    )


def list_orders_by_status(status):
    """
    Returns orders filtered by status.
    Useful for operational dashboards.
    """

    return (
        Order.objects
        .filter(status=status)
        .select_related("customer", "totals")
        .order_by("-created_at")
    )


def list_orders_by_payment_status(payment_status):
    """
    Returns orders filtered by payment status.
    Useful for payment monitoring.
    """

    return (
        Order.objects
        .filter(payment_status=payment_status)
        .select_related("customer", "totals")
        .order_by("-created_at")
    )


def list_orders_by_shipping_status(shipping_status):
    """
    Returns orders filtered by shipping status.
    """

    return (
        Order.objects
        .filter(shipping_status=shipping_status)
        .select_related("customer", "totals")
        .order_by("-created_at")
    )


def list_recent_orders(limit=20):
    """
    Returns the most recent orders.
    Useful for dashboards.
    """

    return (
        Order.objects
        .select_related("customer", "totals")
        .order_by("-created_at")[:limit]
    )


def list_all_orders():
    """
    Returns all orders.
    Typically used by admin dashboards.
    """

    return (
        Order.objects
        .select_related("customer", "totals")
        .order_by("-created_at")
    )


def get_order_for_update(order_id):
    """
    Returns an order locked for update.
    Prevents race conditions.
    """

    return (
        Order.objects
        .select_for_update()
        .select_related(
            "customer",
            "totals",
            "address",
            "lifecycle",
        )
        .prefetch_related(
            "items",
            "events",
            "notes",
        )
        .filter(id=order_id)
        .first()
    )


def list_orders_for_management():
    """
    Returns all orders for staff management dashboards.

    Optimized for operational listing views.
    """

    return (
        Order.objects
        .select_related(
            "customer",
            "totals",
        )
        .order_by("-created_at")
    )


def get_order_detail_for_management(order_id):
    """
    Returns a specific order with full related data
    for staff management detail views.
    """

    cache_key = order_management_detail_cache_key(order_id)
    cached_order = cache.get(cache_key)

    if cached_order is not None:
        return cached_order

    order = (
        Order.objects
        .select_related(
            "customer",
            "totals",
            "address",
            "lifecycle",
        )
        .prefetch_related(
            "items",
            "events",
            "notes",
        )
        .filter(id=order_id)
        .first()
    )

    cache.set(cache_key, order, ORDER_MANAGEMENT_DETAIL_CACHE_TIMEOUT)
    return order
