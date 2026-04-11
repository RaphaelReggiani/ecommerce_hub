from ech.admin_dashboard.models import (
    AdminDashboardEvent,
    AdminDashboardLog,
)
from ech.notifications.models import Notification
from ech.orders.models import Order
from ech.payments.models import Payment
from ech.products.models import Product
from ech.reviews.models import Review
from ech.shipping.models import Shipment
from ech.users.models import CustomUser


def admin_dashboard_event_base_queryset():
    """
    Base queryset for admin dashboard events.
    """

    return AdminDashboardEvent.objects.select_related(
        "performed_by",
        "related_log",
    )


def admin_dashboard_log_base_queryset():
    """
    Base queryset for admin dashboard logs.
    """

    return AdminDashboardLog.objects.select_related(
        "performed_by",
    )


def order_admin_base_queryset():
    """
    Base queryset for order admin operations.
    """

    return Order.objects.select_related(
        "customer",
        "totals",
        "lifecycle",
        "address",
    ).prefetch_related(
        "items",
        "events",
    )


def payment_admin_base_queryset():
    """
    Base queryset for payment admin operations.
    """

    return Payment.objects.select_related(
        "order",
        "customer",
        "lifecycle",
    ).prefetch_related(
        "transactions",
        "refunds",
        "events",
    )


def shipment_admin_base_queryset():
    """
    Base queryset for shipment admin operations.
    """

    return Shipment.objects.select_related(
        "order",
        "customer",
        "address",
        "lifecycle",
    ).prefetch_related(
        "events",
        "tracking_updates",
        "notes",
    )


def review_admin_base_queryset():
    """
    Base queryset for review admin operations.
    """

    return Review.objects.select_related(
        "customer",
        "product",
        "moderated_by",
        "lifecycle",
    ).prefetch_related(
        "events",
    )


def notification_admin_base_queryset():
    """
    Base queryset for notification admin operations.
    """

    return Notification.objects.select_related(
        "recipient",
        "created_by",
        "lifecycle",
    ).prefetch_related(
        "deliveries",
        "events",
    )


def product_admin_base_queryset():
    """
    Base queryset for product admin operations.
    """

    return Product.objects.select_related(
        "sold_by",
        "inventory_record",
    ).prefetch_related(
        "images",
        "reviews",
        "event_logs",
    )


def get_orders_summary_metrics():
    """
    Return summary metrics for orders.
    """

    queryset = order_admin_base_queryset()

    return {
        "total_orders": queryset.count(),
        "pending_orders": queryset.filter(
            status=Order.ORDER_STATUS_PENDING
        ).count(),
        "processing_orders": queryset.filter(
            status=Order.ORDER_STATUS_PROCESSING
        ).count(),
        "shipped_orders": queryset.filter(
            status=Order.ORDER_STATUS_SHIPPED
        ).count(),
        "delivered_orders": queryset.filter(
            status=Order.ORDER_STATUS_DELIVERED
        ).count(),
        "cancelled_orders": queryset.filter(
            status=Order.ORDER_STATUS_CANCELLED
        ).count(),
    }


def get_payments_summary_metrics():
    """
    Return summary metrics for payments.
    """

    queryset = payment_admin_base_queryset()

    return {
        "total_payments": queryset.count(),
        "captured_payments": queryset.filter(
            status=Payment.PAYMENT_STATUS_CAPTURED
        ).count(),
        "failed_payments": queryset.filter(
            status=Payment.PAYMENT_STATUS_FAILED
        ).count(),
        "refunded_payments": queryset.filter(
            status=Payment.PAYMENT_STATUS_REFUNDED
        ).count(),
        "partially_refunded_payments": queryset.filter(
            status=Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED
        ).count(),
    }


def get_shipping_summary_metrics():
    """
    Return summary metrics for shipping.
    """

    queryset = shipment_admin_base_queryset()

    return {
        "total_shipments": queryset.count(),
        "pending_shipments": queryset.filter(
            status=Shipment.STATUS_PENDING
        ).count(),
        "in_transit_shipments": queryset.filter(
            status=Shipment.STATUS_IN_TRANSIT
        ).count(),
        "delivered_shipments": queryset.filter(
            status=Shipment.STATUS_DELIVERED
        ).count(),
        "failed_shipments": queryset.filter(
            status=Shipment.STATUS_FAILED
        ).count(),
        "returned_shipments": queryset.filter(
            status=Shipment.STATUS_RETURNED
        ).count(),
    }


def get_users_summary_metrics():
    """
    Return summary metrics for users.
    """

    queryset = CustomUser.objects.all()

    return {
        "total_users": queryset.count(),
        "active_users": queryset.filter(is_active=True).count(),
        "inactive_users": queryset.filter(is_active=False).count(),
        "staff_users": queryset.exclude(
            user_role=CustomUser.ROLE_CUSTOMER_USER
        ).count(),
        "customer_users": queryset.filter(
            user_role=CustomUser.ROLE_CUSTOMER_USER
        ).count(),
        "confirmed_users": queryset.filter(email_confirmed=True).count(),
        "unconfirmed_users": queryset.filter(email_confirmed=False).count(),
    }


def get_reviews_summary_metrics():
    """
    Return summary metrics for reviews.
    """

    queryset = review_admin_base_queryset()

    return {
        "total_reviews": queryset.count(),
        "pending_reviews": queryset.filter(
            status=Review.REVIEW_STATUS_PENDING
        ).count(),
        "approved_reviews": queryset.filter(
            status=Review.REVIEW_STATUS_APPROVED
        ).count(),
        "rejected_reviews": queryset.filter(
            status=Review.REVIEW_STATUS_REJECTED
        ).count(),
        "hidden_reviews": queryset.filter(
            status=Review.REVIEW_STATUS_HIDDEN
        ).count(),
        "cancelled_reviews": queryset.filter(
            status=Review.REVIEW_STATUS_CANCELLED
        ).count(),
    }


def get_products_summary_metrics():
    """
    Return summary metrics for products.
    """

    queryset = product_admin_base_queryset()

    return {
        "total_products": queryset.count(),
        "active_products": queryset.filter(is_active=True).count(),
        "inactive_products": queryset.filter(is_active=False).count(),
    }


def get_order_operational_metrics():
    """
    Return operational order metrics.
    """

    queryset = order_admin_base_queryset()

    return {
        "pending_orders": queryset.filter(
            status=Order.ORDER_STATUS_PENDING
        ).count(),
        "processing_orders": queryset.filter(
            status=Order.ORDER_STATUS_PROCESSING
        ).count(),
        "cancelled_orders": queryset.filter(
            status=Order.ORDER_STATUS_CANCELLED
        ).count(),
    }


def get_payment_operational_metrics():
    """
    Return operational payment metrics.
    """

    queryset = payment_admin_base_queryset()

    return {
        "failed_payments": queryset.filter(
            status=Payment.PAYMENT_STATUS_FAILED
        ).count(),
        "processing_payments": queryset.filter(
            status=Payment.PAYMENT_STATUS_PROCESSING
        ).count(),
        "refunded_payments": queryset.filter(
            status=Payment.PAYMENT_STATUS_REFUNDED
        ).count(),
    }


def get_shipping_operational_metrics():
    """
    Return operational shipping metrics.
    """

    queryset = shipment_admin_base_queryset()

    return {
        "delayed_shipments": queryset.filter(
            status=Shipment.STATUS_FAILED
        ).count(),
        "failed_shipments": queryset.filter(
            status=Shipment.STATUS_FAILED
        ).count(),
        "in_transit_shipments": queryset.filter(
            status=Shipment.STATUS_IN_TRANSIT
        ).count(),
    }


def get_review_operational_metrics():
    """
    Return operational review metrics.
    """

    queryset = review_admin_base_queryset()

    return {
        "pending_moderation": queryset.filter(
            status=Review.REVIEW_STATUS_PENDING
        ).count(),
        "flagged_reviews": queryset.filter(
            status=Review.REVIEW_STATUS_REJECTED
        ).count(),
        "hidden_reviews": queryset.filter(
            status=Review.REVIEW_STATUS_HIDDEN
        ).count(),
    }


def get_notification_operational_metrics():
    """
    Return operational notification metrics.
    """

    queryset = notification_admin_base_queryset()

    return {
        "failed_notifications": queryset.filter(
            status=Notification.STATUS_FAILED
        ).count(),
        "pending_notifications": queryset.filter(
            status=Notification.STATUS_PENDING
        ).count(),
        "unread_notifications": queryset.filter(
            status=Notification.STATUS_UNREAD
        ).count(),
    }


def get_product_operational_metrics():
    """
    Return operational product metrics.
    """

    queryset = product_admin_base_queryset()

    return {
        "low_stock_products": queryset.filter(
            is_active=True,
            inventory_record__quantity__gt=0,
            inventory_record__quantity__lt=5,
        ).count(),
        "out_of_stock_products": queryset.filter(
            is_active=True,
            inventory_record__quantity=0,
        ).count(),
        "products_without_images": queryset.filter(
            is_active=True,
            images__isnull=True,
        ).distinct().count(),
    }


def get_recent_order_activity(*, limit=50):
    """
    Return recent order activity payload.
    """

    queryset = order_admin_base_queryset().order_by("-created_at")[:limit]

    return [
        {
            "source": "orders",
            "type": "order",
            "entity_id": str(order.id),
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
        }
        for order in queryset
    ]


def get_recent_payment_activity(*, limit=50):
    """
    Return recent payment activity payload.
    """

    queryset = payment_admin_base_queryset().order_by("-created_at")[:limit]

    return [
        {
            "source": "payments",
            "type": "payment",
            "entity_id": str(payment.id),
            "status": payment.status,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
        }
        for payment in queryset
    ]


def get_recent_shipping_activity(*, limit=50):
    """
    Return recent shipping activity payload.
    """

    queryset = shipment_admin_base_queryset().order_by("-created_at")[:limit]

    return [
        {
            "source": "shipping",
            "type": "shipment",
            "entity_id": str(shipment.id),
            "status": shipment.status,
            "created_at": shipment.created_at.isoformat() if shipment.created_at else None,
        }
        for shipment in queryset
    ]


def get_recent_review_activity(*, limit=50):
    """
    Return recent review activity payload.
    """

    queryset = review_admin_base_queryset().order_by("-created_at")[:limit]

    return [
        {
            "source": "reviews",
            "type": "review",
            "entity_id": str(review.id),
            "status": review.status,
            "created_at": review.created_at.isoformat() if review.created_at else None,
        }
        for review in queryset
    ]


def get_recent_notification_activity(*, limit=50):
    """
    Return recent notification activity payload.
    """

    queryset = notification_admin_base_queryset().order_by("-created_at")[:limit]

    return [
        {
            "source": "notifications",
            "type": "notification",
            "entity_id": str(notification.id),
            "status": notification.status,
            "created_at": (
                notification.created_at.isoformat()
                if notification.created_at else None
            ),
        }
        for notification in queryset
    ]


def get_recent_admin_activity(*, limit=50):
    """
    Return recent admin dashboard activity payload.
    """

    queryset = admin_dashboard_log_base_queryset().order_by("-created_at")[:limit]

    return [
        {
            "source": "admin_dashboard",
            "type": "admin_action",
            "entity_id": str(log.id),
            "action_type": log.action_type,
            "target_module": log.target_module,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in queryset
    ]


def get_recent_product_activity(*, limit=50):
    """
    Return recent product activity payload.
    """

    queryset = product_admin_base_queryset().order_by("-created_at")[:limit]

    return [
        {
            "source": "products",
            "type": "product",
            "entity_id": str(product.id),
            "status": "active" if product.is_active else "inactive",
            "created_at": product.created_at.isoformat() if product.created_at else None,
        }
        for product in queryset
    ]