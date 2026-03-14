from django.urls import path

from ech.orders.api.views import (
    OrderCreateAPIView,
    OrderListAPIView,
    OrderDetailAPIView,
    OrderCancelAPIView,
    OrderManagementListAPIView,
    OrderManagementDetailAPIView,
    OrderConfirmAPIView,
    OrderStartProcessingAPIView,
    OrderShipAPIView,
    OrderDeliverAPIView,
    OrderManagementCancelAPIView,
)

app_name = "orders-api"

urlpatterns = [

    # =========================
    # CUSTOMER ORDERS
    # =========================

    path(
        "",
        OrderListAPIView.as_view(),
        name="order-list",
    ),

    path(
        "create/",
        OrderCreateAPIView.as_view(),
        name="order-create",
    ),

    path(
        "<uuid:order_id>/",
        OrderDetailAPIView.as_view(),
        name="order-detail",
    ),

    path(
        "<uuid:order_id>/cancel/",
        OrderCancelAPIView.as_view(),
        name="order-cancel",
    ),

    # =========================
    # MANAGEMENT ORDERS
    # =========================

    path(
        "management/",
        OrderManagementListAPIView.as_view(),
        name="order-management-list",
    ),

    path(
        "management/<uuid:order_id>/",
        OrderManagementDetailAPIView.as_view(),
        name="order-management-detail",
    ),

    path(
        "management/<uuid:order_id>/confirm/",
        OrderConfirmAPIView.as_view(),
        name="order-confirm",
    ),

    path(
        "management/<uuid:order_id>/start-processing/",
        OrderStartProcessingAPIView.as_view(),
        name="order-start-processing",
    ),

    path(
        "management/<uuid:order_id>/ship/",
        OrderShipAPIView.as_view(),
        name="order-ship",
    ),

    path(
        "management/<uuid:order_id>/deliver/",
        OrderDeliverAPIView.as_view(),
        name="order-deliver",
    ),

    path(
        "management/<uuid:order_id>/cancel/",
        OrderManagementCancelAPIView.as_view(),
        name="order-management-cancel",
    ),
]


