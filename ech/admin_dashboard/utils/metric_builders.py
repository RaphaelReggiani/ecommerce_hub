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


def safe_int(value):
    """
    Safely normalize numeric values into int.
    """

    if value is None:
        return zero_int()

    return int(value)


def safe_decimal(value):
    """
    Safely normalize numeric values into Decimal.
    """

    if value is None:
        return zero_decimal()

    if isinstance(value, Decimal):
        return value

    return Decimal(str(value))


def build_admin_dashboard_summary_payload(
    *,
    orders_metrics=None,
    payments_metrics=None,
    shipping_metrics=None,
    users_metrics=None,
    reviews_metrics=None,
    products_metrics=None,
):
    """
    Build the main admin dashboard summary payload.
    """

    return {
        "orders": orders_metrics or {},
        "payments": payments_metrics or {},
        "shipping": shipping_metrics or {},
        "users": users_metrics or {},
        "reviews": reviews_metrics or {},
        "products": products_metrics or {},
    }


def build_operational_metrics_payload(
    *,
    order_metrics=None,
    payment_metrics=None,
    shipping_metrics=None,
    review_metrics=None,
    notification_metrics=None,
    product_metrics=None,
):
    """
    Build the operational metrics payload used for system monitoring.
    """

    return {
        "orders": order_metrics or {},
        "payments": payment_metrics or {},
        "shipping": shipping_metrics or {},
        "reviews": review_metrics or {},
        "notifications": notification_metrics or {},
        "products": product_metrics or {},
    }


def build_recent_activity_payload(
    *,
    order_activity=None,
    payment_activity=None,
    shipping_activity=None,
    review_activity=None,
    notification_activity=None,
    admin_activity=None,
    product_activity=None,
    limit=50,
):
    """
    Build the recent activity payload for the admin dashboard.

    The resulting activity list is merged, ordered by created_at
    descending when present, and trimmed to the requested limit.
    """

    activities = []

    activities.extend(order_activity or [])
    activities.extend(payment_activity or [])
    activities.extend(shipping_activity or [])
    activities.extend(review_activity or [])
    activities.extend(notification_activity or [])
    activities.extend(admin_activity or [])
    activities.extend(product_activity or [])

    def sort_key(item):
        created_at = item.get("created_at")
        return created_at if created_at is not None else ""

    activities = sorted(
        activities,
        key=sort_key,
        reverse=True,
    )[:limit]

    return {
        "activities": activities,
        "total": safe_int(len(activities)),
        "limit": safe_int(limit),
    }


def build_admin_dashboard_alerts_payload(
    *,
    order_metrics=None,
    payment_metrics=None,
    shipping_metrics=None,
    review_metrics=None,
    notification_metrics=None,
    product_metrics=None,
):
    """
    Build alerts payload derived from operational metrics.
    """

    order_metrics = order_metrics or {}
    payment_metrics = payment_metrics or {}
    shipping_metrics = shipping_metrics or {}
    review_metrics = review_metrics or {}
    notification_metrics = notification_metrics or {}
    product_metrics = product_metrics or {}

    alerts = []

    pending_orders = safe_int(order_metrics.get("pending_orders"))
    if pending_orders > 0:
        alerts.append(
            {
                "type": "pending_orders",
                "severity": "warning",
                "message": "There are pending orders requiring attention.",
                "value": pending_orders,
            }
        )

    failed_payments = safe_int(payment_metrics.get("failed_payments"))
    if failed_payments > 0:
        alerts.append(
            {
                "type": "failed_payments",
                "severity": "critical",
                "message": "Failed payments detected.",
                "value": failed_payments,
            }
        )

    delayed_shipments = safe_int(shipping_metrics.get("delayed_shipments"))
    if delayed_shipments > 0:
        alerts.append(
            {
                "type": "delayed_shipments",
                "severity": "warning",
                "message": "Delayed shipments detected.",
                "value": delayed_shipments,
            }
        )

    flagged_reviews = safe_int(review_metrics.get("flagged_reviews"))
    if flagged_reviews > 0:
        alerts.append(
            {
                "type": "flagged_reviews",
                "severity": "info",
                "message": "Flagged reviews require moderation.",
                "value": flagged_reviews,
            }
        )

    failed_notifications = safe_int(
        notification_metrics.get("failed_notifications")
    )
    if failed_notifications > 0:
        alerts.append(
            {
                "type": "failed_notifications",
                "severity": "warning",
                "message": "Failed notifications detected.",
                "value": failed_notifications,
            }
        )

    low_stock_products = safe_int(product_metrics.get("low_stock_products"))
    if low_stock_products > 0:
        alerts.append(
            {
                "type": "low_stock_products",
                "severity": "warning",
                "message": "Products with low stock detected.",
                "value": low_stock_products,
            }
        )

    out_of_stock_products = safe_int(product_metrics.get("out_of_stock_products"))
    if out_of_stock_products > 0:
        alerts.append(
            {
                "type": "out_of_stock_products",
                "severity": "critical",
                "message": "Out-of-stock products detected.",
                "value": out_of_stock_products,
            }
        )

    products_without_images = safe_int(
        product_metrics.get("products_without_images")
    )
    if products_without_images > 0:
        alerts.append(
            {
                "type": "products_without_images",
                "severity": "info",
                "message": "Products without images detected.",
                "value": products_without_images,
            }
        )

    return {
        "alerts": alerts,
        "total_alerts": safe_int(len(alerts)),
        "critical_alerts": safe_int(
            sum(1 for alert in alerts if alert["severity"] == "critical")
        ),
        "warning_alerts": safe_int(
            sum(1 for alert in alerts if alert["severity"] == "warning")
        ),
        "info_alerts": safe_int(
            sum(1 for alert in alerts if alert["severity"] == "info")
        ),
    }


def build_empty_dashboard_metrics():
    """
    Return a fully initialized empty admin dashboard payload.
    """

    return {
        "orders": {},
        "payments": {},
        "shipping": {},
        "users": {},
        "reviews": {},
        "notifications": {},
        "products": {},
        "activities": [],
        "alerts": [],
        "total": 0,
        "limit": 0,
        "total_alerts": 0,
        "critical_alerts": 0,
        "warning_alerts": 0,
        "info_alerts": 0,
    }