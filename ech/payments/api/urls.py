from django.urls import path

from ech.payments.api.views import (
    PaymentListApi,
    PaymentCreateApi,
    PaymentDetailApi,
    PaymentManagementDetailApi,
    PaymentTransactionListApi,
    PaymentProcessApi,
    PaymentCancelApi,
    PaymentRefundApi,
    RefundManagementApi,
)


app_name = "payments-api"


urlpatterns = [

    # ======================
    # PAYMENT LIST / CREATE
    # ======================

    path(
        "",
        PaymentListApi.as_view(),
        name="payment-list",
    ),

    path(
        "create/",
        PaymentCreateApi.as_view(),
        name="payment-create",
    ),

    # ======================
    # PAYMENT DETAIL
    # ======================

    path(
        "<uuid:payment_id>/",
        PaymentDetailApi.as_view(),
        name="payment-detail",
    ),

    path(
        "management/<uuid:payment_id>/",
        PaymentManagementDetailApi.as_view(),
        name="payment-management-detail",
    ),

    # ======================
    # PAYMENT TRANSACTIONS
    # ======================

    path(
        "<uuid:payment_id>/transactions/",
        PaymentTransactionListApi.as_view(),
        name="payment-transaction-list",
    ),

    # ======================
    # PAYMENT PROCESSING
    # ======================

    path(
        "<uuid:payment_id>/process/",
        PaymentProcessApi.as_view(),
        name="payment-process",
    ),

    path(
        "<uuid:payment_id>/cancel/",
        PaymentCancelApi.as_view(),
        name="payment-cancel",
    ),

    # ======================
    # PAYMENT REFUNDS
    # ======================

    path(
        "<uuid:payment_id>/refund/",
        PaymentRefundApi.as_view(),
        name="payment-refund-request",
    ),

    path(
        "refund/<uuid:refund_id>/manage/",
        RefundManagementApi.as_view(),
        name="refund-management",
    ),
]