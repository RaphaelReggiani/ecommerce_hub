from decimal import Decimal


def zero_int():
    """
    Return zero for integer-based metrics.
    """
    return 0


def zero_decimal():
    """
    Return zero for decimal-based metrics.
    """
    return Decimal("0.00")


def safe_decimal(value):
    """
    Safely normalize numeric values into Decimal.
    """

    if value is None:
        return zero_decimal()

    if isinstance(value, Decimal):
        return value

    return Decimal(str(value))


def safe_int(value):
    """
    Safely normalize numeric values into int.
    """

    if value is None:
        return zero_int()

    return int(value)


def build_order_metrics(
    *,
    total_orders=0,
    orders_pending=0,
    orders_processing=0,
    orders_shipped=0,
    orders_delivered=0,
    orders_cancelled=0,
):
    """
    Build the order metrics payload.
    """
    return {
        "total_orders": safe_int(total_orders),
        "orders_pending": safe_int(orders_pending),
        "orders_processing": safe_int(orders_processing),
        "orders_shipped": safe_int(orders_shipped),
        "orders_delivered": safe_int(orders_delivered),
        "orders_cancelled": safe_int(orders_cancelled),
    }


def build_revenue_metrics(
    *,
    total_revenue=None,
    total_refunds=None,
    net_revenue=None,
):
    """
    Build the revenue metrics payload.
    """
    return {
        "total_revenue": safe_decimal(total_revenue),
        "total_refunds": safe_decimal(total_refunds),
        "net_revenue": safe_decimal(net_revenue),
    }


def build_payment_metrics(
    *,
    payments_captured=0,
    payments_failed=0,
    payments_refunded=0,
):
    """
    Build the payment metrics payload.
    """
    return {
        "payments_captured": safe_int(payments_captured),
        "payments_failed": safe_int(payments_failed),
        "payments_refunded": safe_int(payments_refunded),
    }


def build_shipping_metrics(
    *,
    shipments_in_transit=0,
    shipments_delivered=0,
    shipments_failed=0,
):
    """
    Build the shipping metrics payload.
    """
    return {
        "shipments_in_transit": safe_int(shipments_in_transit),
        "shipments_delivered": safe_int(shipments_delivered),
        "shipments_failed": safe_int(shipments_failed),
    }


def build_product_metrics(
    *,
    products_sold=0,
    top_product_id=None,
):
    """
    Build the product metrics payload.
    """
    return {
        "products_sold": safe_int(products_sold),
        "top_product_id": top_product_id,
    }


def build_customer_metrics(
    *,
    active_customers=0,
    new_customers=0,
):
    """
    Build the customer metrics payload.
    """
    return {
        "active_customers": safe_int(active_customers),
        "new_customers": safe_int(new_customers),
    }


def build_user_metrics(
    *,
    total_registered_users=0,
    active_users=0,
    inactive_users=0,
    confirmed_users=0,
    unconfirmed_users=0,
    staff_users=0,
    customer_users=0,
):
    """
    Build the user metrics payload.
    """
    return {
        "total_registered_users": safe_int(total_registered_users),
        "active_users": safe_int(active_users),
        "inactive_users": safe_int(inactive_users),
        "confirmed_users": safe_int(confirmed_users),
        "unconfirmed_users": safe_int(unconfirmed_users),
        "staff_users": safe_int(staff_users),
        "customer_users": safe_int(customer_users),
    }


def build_review_metrics(
    *,
    total_reviews=0,
    approved_reviews=0,
    rejected_reviews=0,
    hidden_reviews=0,
    cancelled_reviews=0,
    verified_purchase_reviews=0,
    average_rating=None,
    low_rated_products_count=0,
    high_rated_products_count=0,
):
    """
    Build the review metrics payload.
    """
    return {
        "total_reviews": safe_int(total_reviews),
        "approved_reviews": safe_int(approved_reviews),
        "rejected_reviews": safe_int(rejected_reviews),
        "hidden_reviews": safe_int(hidden_reviews),
        "cancelled_reviews": safe_int(cancelled_reviews),
        "verified_purchase_reviews": safe_int(verified_purchase_reviews),
        "average_rating": safe_decimal(average_rating),
        "low_rated_products_count": safe_int(low_rated_products_count),
        "high_rated_products_count": safe_int(high_rated_products_count),
    }


def build_snapshot_metrics(
    *,
    order_metrics=None,
    revenue_metrics=None,
    payment_metrics=None,
    shipping_metrics=None,
    product_metrics=None,
    customer_metrics=None,
    user_metrics=None,
    review_metrics=None,
):
    """
    Merge all analytics metric groups into a single payload
    suitable for snapshot creation/update flows.
    """

    payload = {}

    payload.update(order_metrics or {})
    payload.update(revenue_metrics or {})
    payload.update(payment_metrics or {})
    payload.update(shipping_metrics or {})
    payload.update(product_metrics or {})
    payload.update(customer_metrics or {})
    payload.update(user_metrics or {})
    payload.update(review_metrics or {})

    return payload


def build_empty_snapshot_metrics():
    """
    Return a fully initialized empty analytics metrics payload.
    """

    return build_snapshot_metrics(
        order_metrics=build_order_metrics(),
        revenue_metrics=build_revenue_metrics(),
        payment_metrics=build_payment_metrics(),
        shipping_metrics=build_shipping_metrics(),
        product_metrics=build_product_metrics(),
        customer_metrics=build_customer_metrics(),
        user_metrics=build_user_metrics(),
        review_metrics=build_review_metrics(),
    )