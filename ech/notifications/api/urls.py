from django.urls import path

from ech.notifications.api.views import (
    NotificationCreateAPIView,
    NotificationListAPIView,
    NotificationDetailAPIView,
    NotificationMarkAsReadAPIView,
    NotificationArchiveAPIView,
    NotificationManagementListAPIView,
    NotificationManagementDetailAPIView,
    NotificationDispatchAPIView,
    NotificationCancelAPIView,
)

app_name = "notifications-api"

urlpatterns = [

    # =========================
    # CUSTOMER ENDPOINTS
    # =========================

    path(
        "",
        NotificationListAPIView.as_view(),
        name="notification-list",
    ),
    path(
        "<uuid:notification_id>/",
        NotificationDetailAPIView.as_view(),
        name="notification-detail",
    ),
    path(
        "<uuid:notification_id>/read/",
        NotificationMarkAsReadAPIView.as_view(),
        name="notification-mark-read",
    ),
    path(
        "<uuid:notification_id>/archive/",
        NotificationArchiveAPIView.as_view(),
        name="notification-archive",
    ),

    # =========================
    # MANAGEMENT ENDPOINTS
    # =========================

    path(
        "create/",
        NotificationCreateAPIView.as_view(),
        name="notification-create",
    ),
    path(
        "management/",
        NotificationManagementListAPIView.as_view(),
        name="notification-management-list",
    ),
    path(
        "management/<uuid:notification_id>/",
        NotificationManagementDetailAPIView.as_view(),
        name="notification-management-detail",
    ),
    path(
        "management/<uuid:notification_id>/dispatch/",
        NotificationDispatchAPIView.as_view(),
        name="notification-dispatch",
    ),
    path(
        "management/<uuid:notification_id>/cancel/",
        NotificationCancelAPIView.as_view(),
        name="notification-cancel",
    ),
]