from decimal import Decimal
import uuid

from django.core.cache import cache
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ech.orders.models import Order, OrderTotals
from ech.payments.models import Payment, PaymentLifecycle, PaymentTransaction
from ech.users.models import CustomUser


class PaymentProcessApiTestCase(APITestCase):

    def setUp(self):
        """Set up common test data for payment process API tests."""

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
            "payments-api:payment-process",
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

    def test_process_payment_requires_authentication(self):
        """Reject payment process request when unauthenticated."""

        response = self.client.post(
            self.url,
            {"action": "start_processing"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_cannot_process_payment(self):
        """Reject payment process request when user is not payment staff."""

        self.authenticate(self.customer)

        response = self.client.post(
            self.url,
            {"action": "start_processing"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_start_processing_updates_payment_status(self):
        """Start payment processing successfully."""

        self.authenticate(self.staff)

        response = self.client.post(
            self.url,
            {"action": "start_processing"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.payment.refresh_from_db()

        self.assertEqual(
            self.payment.status,
            Payment.PAYMENT_STATUS_PROCESSING,
        )

    def test_authorize_payment_creates_authorization_transaction(self):
        """Authorize payment successfully and create authorization transaction."""

        self.payment.status = Payment.PAYMENT_STATUS_PROCESSING
        self.payment.save(update_fields=["status"])

        self.authenticate(self.staff)

        response = self.client.post(
            self.url,
            {
                "action": "authorize",
                "gateway_transaction_id": "txn_auth_123",
                "gateway_response_code": "200",
                "gateway_response_message": "authorized",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.payment.refresh_from_db()

        self.assertEqual(
            self.payment.status,
            Payment.PAYMENT_STATUS_AUTHORIZED,
        )

        transaction = PaymentTransaction.objects.get(payment=self.payment)

        self.assertEqual(
            transaction.transaction_type,
            PaymentTransaction.TRANSACTION_TYPE_AUTHORIZATION,
        )
        self.assertEqual(
            transaction.status,
            PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
        )
        self.assertEqual(
            transaction.gateway_transaction_id,
            "txn_auth_123",
        )

    def test_capture_payment_creates_capture_transaction(self):
        """Capture payment successfully and create capture transaction."""

        self.payment.status = Payment.PAYMENT_STATUS_AUTHORIZED
        self.payment.save(update_fields=["status"])

        self.authenticate(self.staff)

        response = self.client.post(
            self.url,
            {
                "action": "capture",
                "gateway_transaction_id": "txn_capture_123",
                "gateway_response_code": "200",
                "gateway_response_message": "captured",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.payment.refresh_from_db()

        self.assertEqual(
            self.payment.status,
            Payment.PAYMENT_STATUS_CAPTURED,
        )

        transaction = PaymentTransaction.objects.get(payment=self.payment)

        self.assertEqual(
            transaction.transaction_type,
            PaymentTransaction.TRANSACTION_TYPE_CAPTURE,
        )
        self.assertEqual(
            transaction.status,
            PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
        )

    def test_charge_payment_creates_charge_transaction(self):
        """Charge payment successfully and create charge transaction."""

        self.payment.status = Payment.PAYMENT_STATUS_PROCESSING
        self.payment.save(update_fields=["status"])

        self.authenticate(self.staff)

        response = self.client.post(
            self.url,
            {
                "action": "charge",
                "gateway_transaction_id": "txn_charge_123",
                "gateway_response_code": "200",
                "gateway_response_message": "charged",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.payment.refresh_from_db()

        self.assertEqual(
            self.payment.status,
            Payment.PAYMENT_STATUS_CAPTURED,
        )

        transaction = PaymentTransaction.objects.get(payment=self.payment)

        self.assertEqual(
            transaction.transaction_type,
            PaymentTransaction.TRANSACTION_TYPE_CHARGE,
        )
        self.assertEqual(
            transaction.status,
            PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
        )

    def test_fail_payment_creates_failure_transaction(self):
        """Fail payment successfully and create failure transaction."""

        self.payment.status = Payment.PAYMENT_STATUS_PROCESSING
        self.payment.save(update_fields=["status"])

        self.authenticate(self.staff)

        response = self.client.post(
            self.url,
            {
                "action": "fail",
                "failure_code": "DECLINED",
                "failure_message": "card declined",
                "gateway_transaction_id": "txn_fail_123",
                "gateway_response_code": "402",
                "gateway_response_message": "declined",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.payment.refresh_from_db()

        self.assertEqual(
            self.payment.status,
            Payment.PAYMENT_STATUS_FAILED,
        )
        self.assertEqual(self.payment.failure_code, "DECLINED")
        self.assertEqual(self.payment.failure_message, "card declined")

        transaction = PaymentTransaction.objects.get(payment=self.payment)

        self.assertEqual(
            transaction.transaction_type,
            PaymentTransaction.TRANSACTION_TYPE_FAILURE,
        )
        self.assertEqual(
            transaction.status,
            PaymentTransaction.TRANSACTION_STATUS_FAILED,
        )

    def test_process_payment_rejects_invalid_action(self):
        """Reject payment process request when action is invalid."""

        self.authenticate(self.staff)

        response = self.client.post(
            self.url,
            {"action": "invalid_action"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_process_payment_returns_not_found_for_invalid_payment_id(self):
        """Return 404 when payment does not exist."""

        self.authenticate(self.staff)

        url = reverse(
            "payments-api:payment-process",
            kwargs={"payment_id": uuid.uuid4()},
        )

        response = self.client.post(
            url,
            {"action": "start_processing"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)