from django.urls import path

from ech.reviews.api.views import (
    ReviewCreateAPIView,
    ReviewListAPIView,
    ReviewDetailAPIView,
    ReviewUpdateAPIView,
    ReviewCancelAPIView,
    ReviewModerationAPIView,
    ProductPublicReviewListAPIView,
    ProductReviewSummaryAPIView,
    ReviewManagementListAPIView,
    ReviewManagementDetailAPIView,
)

app_name = "reviews-api"

urlpatterns = [

    # =========================
    # CUSTOMER ENDPOINTS
    # =========================

    path(
        "",
        ReviewListAPIView.as_view(),
        name="review-list",
    ),
    path(
        "create/",
        ReviewCreateAPIView.as_view(),
        name="review-create",
    ),
    path(
        "<uuid:review_id>/",
        ReviewDetailAPIView.as_view(),
        name="review-detail",
    ),

    # =========================
    # CUSTOMER ACTIONS
    # =========================

    path(
        "<uuid:review_id>/update/",
        ReviewUpdateAPIView.as_view(),
        name="review-update",
    ),
    path(
        "<uuid:review_id>/cancel/",
        ReviewCancelAPIView.as_view(),
        name="review-cancel",
    ),

    # =========================
    # MODERATION
    # =========================

    path(
        "<uuid:review_id>/moderate/",
        ReviewModerationAPIView.as_view(),
        name="review-moderate",
    ),

    # =========================
    # PUBLIC PRODUCT REVIEWS
    # =========================

    path(
        "product/<uuid:product_id>/",
        ProductPublicReviewListAPIView.as_view(),
        name="product-review-list",
    ),
    path(
        "product/<uuid:product_id>/summary/",
        ProductReviewSummaryAPIView.as_view(),
        name="product-review-summary",
    ),

    # =========================
    # MANAGEMENT ENDPOINTS
    # =========================

    path(
        "management/",
        ReviewManagementListAPIView.as_view(),
        name="review-management-list",
    ),
    path(
        "management/<uuid:review_id>/",
        ReviewManagementDetailAPIView.as_view(),
        name="review-management-detail",
    ),
]