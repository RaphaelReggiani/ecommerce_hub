from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound

from ech.payments.models import Payment
from ech.payments.exceptions import (
    PaymentError,
    PaymentNotFound,
    PaymentRefundNotFound,
)

from ech.payments.selectors import (
    get_payment_by_id,
    get_payment_for_customer,
    get_payment_management_detail,
    get_payment_refund_by_id,
    list_payment_transactions,
)

from ech.payments.filters import PaymentFilter

from ech.payments.api.pagination import PaymentPagination
from ech.payments.api.permissions import (
    IsAuthenticatedForPayments,
    IsPaymentManagementRole,
)

from ech.payments.api.serializers import (
    CreatePaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer,
    PaymentManagementDetailSerializer,
    PaymentTransactionSerializer,
    PaymentStartProcessingSerializer,
    PaymentAuthorizeSerializer,
    PaymentCaptureSerializer,
    PaymentChargeSerializer,
    PaymentFailSerializer,
    PaymentCancelSerializer,
    PaymentRefundRequestSerializer,
    PaymentRefundProcessSerializer,
    PaymentRefundFailSerializer,
    PaymentRefundCancelSerializer,
)

from ech.payments.constants.roles_management import (
    ALLOWED_PAYMENT_ROLES,
)

from ech.payments.constants.messages import (
    MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND,
    MSG_EXCEPTIONS_ERROR_PAYMENT_REFUND_NOT_FOUND,
)


class PaymentListApi(generics.ListAPIView):
    """
    List payments.

    Customers see only their own payments.
    Staff users with payment roles can see all payments.
    """

    serializer_class = PaymentListSerializer
    permission_classes = [IsAuthenticatedForPayments]

    pagination_class = PaymentPagination

    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter

    def get_queryset(self):
        user = self.request.user

        if user.user_role in ALLOWED_PAYMENT_ROLES:
            return Payment.objects.select_related(
                "customer",
                "order",
            ).order_by("-created_at")

        return Payment.objects.select_related(
            "customer",
            "order",
        ).filter(customer=user).order_by("-created_at")


class PaymentCreateApi(generics.CreateAPIView):
    """
    Create a new payment.
    """

    serializer_class = CreatePaymentSerializer
    permission_classes = [IsAuthenticatedForPayments]


class PaymentDetailApi(generics.RetrieveAPIView):
    """
    Retrieve payment detail for the authenticated customer.
    """

    serializer_class = PaymentDetailSerializer
    permission_classes = [IsAuthenticatedForPayments]

    def get_object(self):
        """Return payment detail for the authenticated customer."""

        payment_id = self.kwargs["payment_id"]

        try:
            return get_payment_for_customer(
                payment_id=payment_id,
                customer_id=self.request.user.id,
            )
        except PaymentNotFound:
            raise NotFound(MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND)


class PaymentManagementDetailApi(generics.RetrieveAPIView):
    """
    Retrieve payment detail for management.
    """

    serializer_class = PaymentManagementDetailSerializer
    permission_classes = [IsPaymentManagementRole]

    def get_object(self):
        """Return payment detail for management users."""

        payment_id = self.kwargs["payment_id"]

        try:
            return get_payment_management_detail(payment_id=payment_id)
        except PaymentNotFound:
            raise NotFound(MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND)


class PaymentTransactionListApi(generics.ListAPIView):
    """
    List transactions related to a payment.
    """

    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticatedForPayments]
    pagination_class = PaymentPagination

    def get_queryset(self):
        """Return transactions for the requested payment when access is allowed."""

        payment_id = self.kwargs["payment_id"]
        user = self.request.user

        try:
            if user.user_role in ALLOWED_PAYMENT_ROLES:
                payment = get_payment_by_id(payment_id=payment_id)
            else:
                payment = get_payment_for_customer(
                    payment_id=payment_id,
                    customer_id=user.id,
                )
        except PaymentNotFound:
            raise NotFound(MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND)

        return list_payment_transactions(payment_id=payment.id)


class PaymentProcessApi(APIView):
    """
    Handle payment processing operations.
    """

    permission_classes = [IsPaymentManagementRole]

    def post(self, request, payment_id):
        """Execute a payment processing action."""

        try:
            payment = get_payment_by_id(payment_id=payment_id)
        except PaymentNotFound:
            raise NotFound(MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND)

        action = request.data.get("action")

        serializer_map = {
            "start_processing": PaymentStartProcessingSerializer,
            "authorize": PaymentAuthorizeSerializer,
            "capture": PaymentCaptureSerializer,
            "charge": PaymentChargeSerializer,
            "fail": PaymentFailSerializer,
        }

        serializer_class = serializer_map.get(action)

        if serializer_class is None:
            return Response(
                {"detail": "Invalid payment action."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = serializer_class(
            data=request.data,
            context={
                "request": request,
                "payment": payment,
            },
        )

        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
        except PaymentError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Payment operation completed."},
            status=status.HTTP_200_OK,
        )


class PaymentCancelApi(APIView):
    """
    Cancel a payment.
    """

    permission_classes = [IsPaymentManagementRole]

    def post(self, request, payment_id):
        """Cancel the requested payment."""

        try:
            payment = get_payment_by_id(payment_id=payment_id)
        except PaymentNotFound:
            raise NotFound(MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND)

        serializer = PaymentCancelSerializer(
            data=request.data,
            context={
                "request": request,
                "payment": payment,
            },
        )

        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
        except PaymentError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Payment cancelled."},
            status=status.HTTP_200_OK,
        )


class PaymentRefundApi(APIView):
    """
    Handle payment refund request creation.
    """

    permission_classes = [IsPaymentManagementRole]

    def post(self, request, payment_id):
        """Create a refund request for the given payment."""

        try:
            payment = get_payment_by_id(payment_id=payment_id)
        except PaymentNotFound:
            raise NotFound(MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND)

        serializer = PaymentRefundRequestSerializer(
            data=request.data,
            context={
                "request": request,
                "payment": payment,
            },
        )

        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
        except PaymentError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Refund request created."},
            status=status.HTTP_201_CREATED,
        )

class RefundManagementApi(APIView):
    """
    Manage refund lifecycle.
    """

    permission_classes = [IsPaymentManagementRole]

    def post(self, request, refund_id):
        """Execute a refund management action."""

        try:
            refund = get_payment_refund_by_id(refund_id=refund_id)
        except PaymentRefundNotFound:
            raise NotFound(MSG_EXCEPTIONS_ERROR_PAYMENT_REFUND_NOT_FOUND)

        action = request.data.get("action")

        serializer_map = {
            "process": PaymentRefundProcessSerializer,
            "fail": PaymentRefundFailSerializer,
            "cancel": PaymentRefundCancelSerializer,
        }

        serializer_class = serializer_map.get(action)

        if serializer_class is None:
            return Response(
                {"detail": "Invalid refund action."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = serializer_class(
            data=request.data,
            context={
                "request": request,
                "refund": refund,
            },
        )

        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
        except PaymentError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Refund operation completed."},
            status=status.HTTP_200_OK,
        )