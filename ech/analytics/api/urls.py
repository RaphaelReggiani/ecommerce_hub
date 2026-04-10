from django.urls import path

from ech.analytics.api.views import (
    AnalyticsDashboardSummaryAPIView,
    AnalyticsSalesOverviewAPIView,
    AnalyticsOrderFunnelAPIView,
    AnalyticsPaymentOverviewAPIView,
    AnalyticsShippingOverviewAPIView,
    AnalyticsProductPerformanceAPIView,
    AnalyticsCustomerSummaryAPIView,
    AnalyticsUserOverviewAPIView,
    AnalyticsReviewOverviewAPIView,
    AnalyticsSnapshotListAPIView,
    AnalyticsSnapshotDetailAPIView,
    AnalyticsSnapshotRefreshAPIView,
)

app_name = "analytics-api"

urlpatterns = [

    # =========================
    # DASHBOARD ENDPOINTS
    # =========================

    path(
        "dashboard/",
        AnalyticsDashboardSummaryAPIView.as_view(),
        name="analytics-dashboard",
    ),
    path(
        "sales/",
        AnalyticsSalesOverviewAPIView.as_view(),
        name="analytics-sales-overview",
    ),
    path(
        "orders/funnel/",
        AnalyticsOrderFunnelAPIView.as_view(),
        name="analytics-order-funnel",
    ),
    path(
        "payments/",
        AnalyticsPaymentOverviewAPIView.as_view(),
        name="analytics-payment-overview",
    ),
    path(
        "shipping/",
        AnalyticsShippingOverviewAPIView.as_view(),
        name="analytics-shipping-overview",
    ),
    path(
        "products/performance/",
        AnalyticsProductPerformanceAPIView.as_view(),
        name="analytics-product-performance",
    ),
    path(
        "customers/",
        AnalyticsCustomerSummaryAPIView.as_view(),
        name="analytics-customer-summary",
    ),
    path(
        "users/",
        AnalyticsUserOverviewAPIView.as_view(),
        name="analytics-user-overview",
    ),
    path(
        "reviews/",
        AnalyticsReviewOverviewAPIView.as_view(),
        name="analytics-review-overview",
    ),

    # =========================
    # SNAPSHOT MANAGEMENT
    # =========================

    path(
        "snapshots/",
        AnalyticsSnapshotListAPIView.as_view(),
        name="analytics-snapshot-list",
    ),
    path(
        "snapshots/<uuid:snapshot_id>/",
        AnalyticsSnapshotDetailAPIView.as_view(),
        name="analytics-snapshot-detail",
    ),
    path(
        "snapshots/<uuid:snapshot_id>/refresh/",
        AnalyticsSnapshotRefreshAPIView.as_view(),
        name="analytics-snapshot-refresh",
    ),
]