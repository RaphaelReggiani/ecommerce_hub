from decimal import Decimal
import uuid

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.orders.models import (
    Order, 
    OrderTotals,
)
from ech.payments.models import (
    Payment, 
    PaymentLifecycle, 
    PaymentTransaction,
)
from ech.users.models import CustomUser


class PaymentCancelApiTestCase(APITestCase):

    def setUp(self):
        """Set up common test data for payment cancel API tests."""

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

        self.payment = self.create_payment(customer=self.customer)

        self.url = reverse(
            "payments-api:payment-cancel",
            kwargs={"payment_id": self.payment.id},
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
        status_value=Payment.PAYMENT_STATUS_PENDING,
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
            refunded_amount=Decimal("0.00"),
            currency="USD",
            gateway_name="",
            gateway_payment_id="",
            gateway_customer_id="",
            metadata={},
        )

        PaymentLifecycle.objects.create(payment=payment)

        return payment

    def test_cancel_payment_requires_authentication(self):
        """Reject payment cancel request when unauthenticated."""

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_cannot_cancel_payment(self):
        """Reject payment cancel request when user is not payment staff."""

        self.authenticate(self.customer)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cancel_payment_success(self):
        """Cancel payment successfully and create cancellation transaction."""

        self.payment.status = Payment.PAYMENT_STATUS_PROCESSING
        self.payment.save(update_fields=["status"])

        self.authenticate(self.staff)

        response = self.client.post(
            self.url,
            {
                "gateway_transaction_id": "txn_cancel_123",
                "gateway_response_code": "200",
                "gateway_response_message": "cancelled",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.payment.refresh_from_db()

        self.assertEqual(
            self.payment.status,
            Payment.PAYMENT_STATUS_CANCELLED,
        )

        transaction = PaymentTransaction.objects.get(payment=self.payment)

        self.assertEqual(
            transaction.transaction_type,
            PaymentTransaction.TRANSACTION_TYPE_CANCELLATION,
        )
        self.assertEqual(
            transaction.status,
            PaymentTransaction.TRANSACTION_STATUS_CANCELLED,
        )
        self.assertEqual(
            transaction.gateway_transaction_id,
            "txn_cancel_123",
        )

    def test_cancel_payment_returns_not_found_for_invalid_payment_id(self):
        """Return 404 when payment does not exist."""

        self.authenticate(self.staff)

        url = reverse(
            "payments-api:payment-cancel",
            kwargs={"payment_id": uuid.uuid4()},
        )

        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_payment_rejects_already_cancelled_payment(self):
        """Reject cancellation when payment is already cancelled."""

        self.payment.status = Payment.PAYMENT_STATUS_CANCELLED
        self.payment.save(update_fields=["status"])

        self.authenticate(self.staff)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_payment_rejects_captured_payment(self):
        """Reject cancellation when payment is in a non-cancellable state."""

        self.payment.status = Payment.PAYMENT_STATUS_CAPTURED
        self.payment.save(update_fields=["status"])

        self.authenticate(self.staff)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)