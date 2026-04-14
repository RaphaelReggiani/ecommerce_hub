from django.urls import path

from ech.admin_dashboard.api.views import (
    AdminDashboardSummaryAPIView,
    AdminDashboardOperationalMetricsAPIView,
    AdminDashboardRecentActivityAPIView,
    AdminDashboardAlertsAPIView,
    AdminDashboardBulkOrderActionAPIView,
    AdminDashboardBulkReviewModerationAPIView,
    AdminDashboardBulkNotificationRetryAPIView,
    AdminDashboardLogListAPIView,
    AdminDashboardLogDetailAPIView,
    AdminDashboardEventListAPIView,
)

app_name = "admin-dashboard-api"

urlpatterns = [

    # =========================
    # DASHBOARD OVERVIEW
    # =========================

    path(
        "dashboard/summary/",
        AdminDashboardSummaryAPIView.as_view(),
        name="admin-dashboard-summary",
    ),
    path(
        "dashboard/operational-metrics/",
        AdminDashboardOperationalMetricsAPIView.as_view(),
        name="admin-dashboard-operational-metrics",
    ),
    path(
        "dashboard/activity/",
        AdminDashboardRecentActivityAPIView.as_view(),
        name="admin-dashboard-activity",
    ),
    path(
        "dashboard/alerts/",
        AdminDashboardAlertsAPIView.as_view(),
        name="admin-dashboard-alerts",
    ),

    # =========================
    # BULK ADMIN OPERATIONS
    # =========================

    path(
        "orders/bulk-action/",
        AdminDashboardBulkOrderActionAPIView.as_view(),
        name="admin-dashboard-bulk-order-action",
    ),
    path(
        "reviews/bulk-moderation/",
        AdminDashboardBulkReviewModerationAPIView.as_view(),
        name="admin-dashboard-bulk-review-moderation",
    ),
    path(
        "notifications/retry/",
        AdminDashboardBulkNotificationRetryAPIView.as_view(),
        name="admin-dashboard-notification-retry",
    ),

    # =========================
    # AUDIT & EVENT TRACKING
    # =========================

    path(
        "logs/",
        AdminDashboardLogListAPIView.as_view(),
        name="admin-dashboard-log-list",
    ),
    path(
        "logs/<uuid:log_id>/",
        AdminDashboardLogDetailAPIView.as_view(),
        name="admin-dashboard-log-detail",
    ),
    path(
        "events/",
        AdminDashboardEventListAPIView.as_view(),
        name="admin-dashboard-event-list",
    ),
]