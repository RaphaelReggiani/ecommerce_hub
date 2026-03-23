from decimal import Decimal
import uuid

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from ech.orders.models import (
    Order, 
    OrderTotals,
)
from ech.payments.models import (
    Payment, 
    PaymentTransaction,
)
from ech.users.models import CustomUser


class PaymentTransactionListApiTestCase(APITestCase):

    def setUp(self):
        """Set up common test data for payment transaction list API tests."""

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

        self.other_customer = CustomUser.objects.create_user(
            email="customer2@test.com",
            password=self.password,
            user_name="Customer Two",
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
            "payments-api:payment-transaction-list",
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
        method=Payment.PAYMENT_METHOD_CREDIT_CARD,
        status_value=Payment.PAYMENT_STATUS_PENDING,
    ):
        """Create and return a payment."""

        order = self.create_order(
            customer=customer,
            amount=amount,
        )

        return Payment.objects.create(
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

    def create_transaction(
        self,
        *,
        payment,
        transaction_type=PaymentTransaction.TRANSACTION_TYPE_AUTHORIZATION,
        status_value=PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
        amount=Decimal("100.00"),
        performed_by=None,
    ):
        """Create and return a payment transaction."""

        return PaymentTransaction.objects.create(
            payment=payment,
            transaction_type=transaction_type,
            status=status_value,
            amount=amount,
            currency=payment.currency,
            gateway_transaction_id=f"txn_{uuid.uuid4().hex[:10]}",
            gateway_response_code="200",
            gateway_response_message="ok",
            metadata={},
            performed_by=performed_by,
            processed_at=timezone.now(),
        )

    def test_transaction_list_requires_authentication(self):
        """Reject payment transaction list request when unauthenticated."""

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_can_view_own_payment_transactions(self):
        """Return transactions when requested by the payment owner."""

        transaction = self.create_transaction(
            payment=self.payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_AUTHORIZATION,
            performed_by=self.staff,
        )

        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(transaction.id),
        )
        self.assertEqual(
            response.data["results"][0]["transaction_type"],
            PaymentTransaction.TRANSACTION_TYPE_AUTHORIZATION,
        )

    def test_other_customer_cannot_view_payment_transactions(self):
        """Reject access when customer tries to view another customer's payment transactions."""

        self.create_transaction(payment=self.payment, performed_by=self.staff)

        self.authenticate(self.other_customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_payment_staff_can_view_any_payment_transactions(self):
        """Allow payment staff to view any payment transactions."""

        transaction = self.create_transaction(
            payment=self.payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_CAPTURE,
            performed_by=self.staff,
        )

        self.authenticate(self.staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(transaction.id),
        )
        self.assertEqual(
            response.data["results"][0]["transaction_type"],
            PaymentTransaction.TRANSACTION_TYPE_CAPTURE,
        )

    def test_transaction_list_returns_only_transactions_from_requested_payment(self):
        """Return only transactions belonging to the requested payment."""

        other_payment = self.create_payment(customer=self.customer)

        expected_transaction = self.create_transaction(
            payment=self.payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_AUTHORIZATION,
            performed_by=self.staff,
        )
        self.create_transaction(
            payment=other_payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_CAPTURE,
            performed_by=self.staff,
        )

        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(expected_transaction.id),
        )

    def test_transaction_list_returns_not_found_for_invalid_payment_id(self):
        """Return 404 when payment does not exist."""

        self.authenticate(self.customer)

        url = reverse(
            "payments-api:payment-transaction-list",
            kwargs={"payment_id": uuid.uuid4()},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)