from django.urls import path

from ech.shipping.api.views import (
    ShipmentCreateAPIView,
    ShipmentListAPIView,
    ShipmentDetailAPIView,
    ShipmentUpdateAPIView,
    ShipmentProcessAPIView,
    ShipmentCancelAPIView,
    ShipmentTrackingAPIView,
    ShipmentManagementListAPIView,
    ShipmentManagementDetailAPIView,
)

app_name = "shipping-api"

urlpatterns = [

    # =========================
    # CUSTOMER ENDPOINTS
    # =========================

    path(
        "",
        ShipmentListAPIView.as_view(),
        name="shipment-list",
    ),
    path(
        "<uuid:shipment_id>/",
        ShipmentDetailAPIView.as_view(),
        name="shipment-detail",
    ),

    # =========================
    # OPERATIONAL ACTIONS
    # =========================
    
    path(
        "create/",
        ShipmentCreateAPIView.as_view(),
        name="shipment-create",
    ),

    path(
        "<uuid:shipment_id>/update/",
        ShipmentUpdateAPIView.as_view(),
        name="shipment-update",
    ),
    path(
        "<uuid:shipment_id>/process/",
        ShipmentProcessAPIView.as_view(),
        name="shipment-process",
    ),
    path(
        "<uuid:shipment_id>/cancel/",
        ShipmentCancelAPIView.as_view(),
        name="shipment-cancel",
    ),
    path(
        "<uuid:shipment_id>/tracking/",
        ShipmentTrackingAPIView.as_view(),
        name="shipment-tracking",
    ),

    # =========================
    # MANAGEMENT ENDPOINTS
    # =========================

    path(
        "management/",
        ShipmentManagementListAPIView.as_view(),
        name="shipment-management-list",
    ),
    path(
        "management/<uuid:shipment_id>/",
        ShipmentManagementDetailAPIView.as_view(),
        name="shipment-management-detail",
    ),
]