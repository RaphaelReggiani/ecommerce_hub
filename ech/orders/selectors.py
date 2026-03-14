from ech.orders.models import Order


def get_order_by_id(order_id):
    """
    Returns an order by its ID with related data.
    """

    return (
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


def list_orders_by_customer(customer):
    """
    Returns all orders from a specific customer.
    """

    return (
        Order.objects
        .filter(customer=customer)
        .select_related("totals")
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

    return (
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
