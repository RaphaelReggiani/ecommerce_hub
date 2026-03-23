from decimal import Decimal
import uuid

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.orders.models import Order, OrderTotals
from ech.payments.models import (
    Payment,
    PaymentLifecycle,
    PaymentRefund,
    PaymentTransaction,
)
from ech.users.models import CustomUser


class PaymentRefundApiTestCase(APITestCase):

    def setUp(self):
        """Set up common test data for payment refund API tests."""

        cache.clear()

        self.password = "StrongPassword123"

        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password=self.password,
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.staff = CustomUser.objects.create_user(
            email="staff@company.com",
            password=self.password,
            user_name="Payment Staff",
            role=CustomUser.ROLE_PAYMENT_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        self.captured_payment = self.create_payment(
            customer=self.customer,
            status_value=Payment.PAYMENT_STATUS_CAPTURED,
            amount=Decimal("100.00"),
        )

        self.refund_url = reverse(
            "payments-api:payment-refund-request",
            kwargs={"payment_id": self.captured_payment.id},
        )

    def authenticate(self, user):
        """Authenticate API client with the given user."""
        self.client.force_authenticate(user=user)

    def create_order(
        self,
        *,
        customer,
        amount=Decimal("100.00"),
    ):
        """Create and return an order with totals."""

        order = Order.objects.create(
            customer=customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )

        OrderTotals.objects.create(
            order=order,
            subtotal=amount,
            grand_total=amount,
        )

        return order

    def create_payment(
        self,
        *,
        customer,
        amount=Decimal("100.00"),
        status_value=Payment.PAYMENT_STATUS_CAPTURED,
        refunded_amount=Decimal("0.00"),
        method=Payment.PAYMENT_METHOD_CREDIT_CARD,
    ):
        """Create and return a payment with lifecycle."""

        order = self.create_order(
            customer=customer,
            amount=amount,
        )

        payment = Payment.objects.create(
            order=order,
            customer=customer,
            payment_reference=f"PAY-{uuid.uuid4().hex[:12].upper()}",
            method=method,
            status=status_value,
            amount=amount,
            refunded_amount=refunded_amount,
            currency="USD",
            gateway_name="",
            gateway_payment_id="",
            gateway_customer_id="",
            metadata={},
        )

        PaymentLifecycle.objects.create(payment=payment)

        return payment

    def create_refund(
        self,
        *,
        payment,
        amount=Decimal("20.00"),
        status_value=PaymentRefund.REFUND_STATUS_PENDING,
        reason="Customer request",
        requested_by=None,
    ):
        """Create and return a payment refund."""

        return PaymentRefund.objects.create(
            payment=payment,
            amount=amount,
            reason=reason,
            status=status_value,
            gateway_refund_id="",
            metadata={},
            requested_by=requested_by,
        )

    def test_refund_request_requires_authentication(self):
        """Reject refund request when unauthenticated."""

        response = self.client.post(
            self.refund_url,
            {"amount": "20.00", "reason": "Customer request"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_cannot_request_refund(self):
        """Reject refund request when user is not payment staff."""

        self.authenticate(self.customer)

        response = self.client.post(
            self.refund_url,
            {"amount": "20.00", "reason": "Customer request"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_refund_request_success(self):
        """Create refund request successfully for a refundable payment."""

        self.authenticate(self.staff)

        response = self.client.post(
            self.refund_url,
            {
                "amount": "20.00",
                "reason": "Customer request",
                "gateway_refund_id": "refund_123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        refund = PaymentRefund.objects.get(payment=self.captured_payment)

        self.assertEqual(refund.amount, Decimal("20.00"))
        self.assertEqual(refund.reason, "Customer request")
        self.assertEqual(refund.status, PaymentRefund.REFUND_STATUS_PENDING)
        self.assertEqual(refund.gateway_refund_id, "refund_123")

    def test_refund_request_returns_not_found_for_invalid_payment_id(self):
        """Return 404 when payment does not exist."""

        self.authenticate(self.staff)

        url = reverse(
            "payments-api:payment-refund-request",
            kwargs={"payment_id": uuid.uuid4()},
        )

        response = self.client.post(
            url,
            {"amount": "20.00", "reason": "Customer request"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_refund_request_rejects_non_refundable_payment(self):
        """Reject refund request when payment is not refundable."""

        pending_payment = self.create_payment(
            customer=self.customer,
            status_value=Payment.PAYMENT_STATUS_PENDING,
        )

        url = reverse(
            "payments-api:payment-refund-request",
            kwargs={"payment_id": pending_payment.id},
        )

        self.authenticate(self.staff)

        response = self.client.post(
            url,
            {"amount": "20.00", "reason": "Customer request"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refund_management_process_success(self):
        """Process refund successfully and update payment totals and status."""

        refund = self.create_refund(
            payment=self.captured_payment,
            amount=Decimal("20.00"),
            requested_by=self.staff,
        )

        url = reverse(
            "payments-api:refund-management",
            kwargs={"refund_id": refund.id},
        )

        self.authenticate(self.staff)

        response = self.client.post(
            url,
            {
                "action": "process",
                "gateway_transaction_id": "txn_refund_123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refund.refresh_from_db()
        self.captured_payment.refresh_from_db()

        self.assertEqual(refund.status, PaymentRefund.REFUND_STATUS_PROCESSED)
        self.assertEqual(
            self.captured_payment.refunded_amount,
            Decimal("20.00"),
        )
        self.assertEqual(
            self.captured_payment.status,
            Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED,
        )

        transaction = PaymentTransaction.objects.get(payment=self.captured_payment)

        self.assertEqual(
            transaction.transaction_type,
            PaymentTransaction.TRANSACTION_TYPE_PARTIAL_REFUND,
        )
        self.assertEqual(
            transaction.status,
            PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
        )

    def test_refund_management_fail_success(self):
        """Mark pending refund as failed successfully."""

        refund = self.create_refund(
            payment=self.captured_payment,
            requested_by=self.staff,
        )

        url = reverse(
            "payments-api:refund-management",
            kwargs={"refund_id": refund.id},
        )

        self.authenticate(self.staff)

        response = self.client.post(
            url,
            {
                "action": "fail",
                "metadata": {"reason_code": "gateway_error"},
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refund.refresh_from_db()

        self.assertEqual(refund.status, PaymentRefund.REFUND_STATUS_FAILED)
        self.assertEqual(
            refund.metadata["reason_code"],
            "gateway_error",
        )

    def test_refund_management_cancel_success(self):
        """Cancel pending refund successfully."""

        refund = self.create_refund(
            payment=self.captured_payment,
            requested_by=self.staff,
        )

        url = reverse(
            "payments-api:refund-management",
            kwargs={"refund_id": refund.id},
        )

        self.authenticate(self.staff)

        response = self.client.post(
            url,
            {
                "action": "cancel",
                "metadata": {"note": "cancelled manually"},
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refund.refresh_from_db()

        self.assertEqual(refund.status, PaymentRefund.REFUND_STATUS_CANCELLED)
        self.assertEqual(
            refund.metadata["note"],
            "cancelled manually",
        )

    def test_refund_management_rejects_invalid_action(self):
        """Reject refund management request when action is invalid."""

        refund = self.create_refund(
            payment=self.captured_payment,
            requested_by=self.staff,
        )

        url = reverse(
            "payments-api:refund-management",
            kwargs={"refund_id": refund.id},
        )

        self.authenticate(self.staff)

        response = self.client.post(
            url,
            {"action": "invalid_action"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refund_management_returns_not_found_for_invalid_refund_id(self):
        """Return 404 when refund does not exist."""

        self.authenticate(self.staff)

        url = reverse(
            "payments-api:refund-management",
            kwargs={"refund_id": uuid.uuid4()},
        )

        response = self.client.post(
            url,
            {"action": "process"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_cannot_manage_refund(self):
        """Reject refund management request when user is not payment staff."""

        refund = self.create_refund(
            payment=self.captured_payment,
            requested_by=self.staff,
        )

        url = reverse(
            "payments-api:refund-management",
            kwargs={"refund_id": refund.id},
        )

        self.authenticate(self.customer)

        response = self.client.post(
            url,
            {"action": "process"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)